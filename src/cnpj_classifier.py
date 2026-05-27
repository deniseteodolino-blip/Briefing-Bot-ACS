import os
import sqlite3
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

import requests
from dotenv import load_dotenv

load_dotenv()

BRASILAPI_BASE_URL = os.getenv('BRASILAPI_BASE_URL', 'https://brasilapi.com.br/api/cnpj/v1')
CACHE_TTL_DAYS = 7


@dataclass
class CNPJData:
    cnpj: str
    razao_social: Optional[str]
    porte: Optional[str]
    optante_simples: Optional[bool]
    data_atualizacao: Optional[str]
    cached_at: float


def get_cache_db() -> sqlite3.Connection:
    """Get SQLite connection for CNPJ cache."""
    cache_dir = Path.home() / '.briefing-bot-cache'
    cache_dir.mkdir(exist_ok=True)
    db_path = cache_dir / 'cnpj_cache.db'

    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cnpj_cache (
            cnpj TEXT PRIMARY KEY,
            data TEXT,
            cached_at REAL
        )
    """)
    return conn


def _clean_cnpj(cnpj: str) -> str:
    """Remove non-digits from CNPJ."""
    return ''.join(c for c in cnpj if c.isdigit())


def get_cached_cnpj(cnpj: str) -> Optional[dict]:
    """Get CNPJ data from cache if valid."""
    conn = get_cache_db()
    cursor = conn.execute(
        "SELECT data, cached_at FROM cnpj_cache WHERE cnpj = ?",
        (_clean_cnpj(cnpj),)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    data_json, cached_at = row
    age_days = (time.time() - cached_at) / 86400

    if age_days < CACHE_TTL_DAYS:
        import json
        return json.loads(data_json)

    return None


def cache_cnpj(cnpj: str, data: dict) -> None:
    """Cache CNPJ data."""
    import json
    conn = get_cache_db()
    conn.execute(
        "INSERT OR REPLACE INTO cnpj_cache (cnpj, data, cached_at) VALUES (?, ?, ?)",
        (_clean_cnpj(cnpj), json.dumps(data), time.time())
    )
    conn.commit()
    conn.close()


def classify_pj(cnpj: str, force_refresh: bool = False) -> dict:
    """
    Classify PJ investor via CNPJ API.

    Returns: {
        "cnpj": str,
        "razao_social": str,
        "porte": str (ME/EPP/DEMAIS),
        "optante_simples": bool,
        "bucket": str (simples_nacional/me_epp/sem_pendencia),
        "erro": Optional[str]
    }
    """
    cnpj_clean = _clean_cnpj(cnpj)

    # Check cache first (unless force_refresh)
    if not force_refresh:
        cached = get_cached_cnpj(cnpj_clean)
        if cached:
            print(f"  [CACHE] {cnpj_clean}: porte={cached.get('porte')}, simples={cached.get('optante_simples')}")
            return _classify_cnpj_result(cnpj_clean, cached)

    # Fetch from API with extended timeout and retries
    url = f"{BRASILAPI_BASE_URL}/{cnpj_clean}"
    max_retries = 5
    backoff = 2

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)

            if response.status_code == 200:
                data = response.json()
                cache_cnpj(cnpj_clean, data)
                print(f"  [API] {cnpj_clean}: porte={data.get('porte')}, simples={data.get('optante_simples')}")
                return _classify_cnpj_result(cnpj_clean, data)

            elif response.status_code == 404:
                return _error_result(cnpj_clean, "CNPJ não encontrado na Receita Federal")

            elif response.status_code == 429:
                # Rate limited - wait longer and retry
                print(f"  [RATE LIMIT] aguardando {backoff}s...")
                time.sleep(backoff)
                backoff *= 2
                continue

            else:
                return _error_result(cnpj_clean, f"API error: {response.status_code}")

        except requests.RequestException as e:
            if attempt < max_retries - 1:
                print(f"  [RETRY {attempt+1}/{max_retries}] {cnpj_clean}: {str(e)[:50]}...")
                time.sleep(backoff)
                backoff *= 2
                continue

    # Se falhou após todas as tentativas, ainda assim incluir como ME/EPP
    # (assumir que precisa alterar porte se a API não respondeu)
    print(f"  [FALLBACK] {cnpj_clean}: API indisponível, assumindo ME/EPP por segurança")
    return {
        "cnpj": cnpj_clean,
        "razao_social": None,
        "porte": "ME",  # Assume ME para garantir que aparece no template
        "optante_simples": False,
        "bucket": "me_epp",
        "erro": f"API indisponível - verificar manualmente porte atual"
    }


def _classify_cnpj_result(cnpj: str, data: dict) -> dict:
    """Classify CNPJ into buckets based on rules."""
    porte = data.get('porte')
    optante_simples = data.get('optante_simples')

    # Normalize values - treat None as False
    if optante_simples is None:
        optante_simples = False
    if porte is None:
        porte = 'DEMAIS'  # Default to DEMAIS if unknown

    # Classification rules
    if optante_simples:
        bucket = 'simples_nacional'
    elif porte in ('ME', 'EPP', 'MICRO EMPRESA', 'EMPRESA DE PEQUENO PORTE'):
        bucket = 'me_epp'
    else:
        bucket = 'sem_pendencia'

    return {
        "cnpj": cnpj,
        "razao_social": data.get('razao_social') or data.get('nome'),
        "porte": porte,
        "optante_simples": optante_simples,
        "bucket": bucket,
        "erro": None
    }


def _error_result(cnpj: str, erro: str) -> dict:
    """Return error result."""
    return {
        "cnpj": cnpj,
        "razao_social": None,
        "porte": None,
        "optante_simples": None,
        "bucket": "erro",
        "erro": erro
    }


def classify_investidores(investidores: list, force_refresh: bool = False) -> dict:
    """
    Classify all PJ investors and group into buckets.

    Returns: {
        "estrangeiros": [...],
        "simples_nacional": [...],
        "me_epp": [...],
        "sem_pendencia": [...],
        "erros": [...]
    }
    """
    result = {
        "estrangeiros": [],
        "simples_nacional": [],
        "me_epp": [],
        "sem_pendencia": [],
        "erros": []
    }

    for inv in investidores:
        if inv.tipo == 'PJ':
            cnpj = inv.documento
            if cnpj:
                print(f"\nConsultando CNPJ: {inv.nome}")
                class_result = classify_pj(cnpj, force_refresh)

                entry = {
                    "nome": inv.nome,
                    "cnpj": cnpj,
                    "razao_social": class_result.get('razao_social'),
                    "bucket": class_result['bucket'],
                    "porte": class_result.get('porte'),
                    "optante_simples": class_result.get('optante_simples'),
                    "erro": class_result.get('erro'),
                    "acao": inv.acao
                }

                bucket_key = class_result['bucket']
                if bucket_key == 'erro':
                    result['erros'].append(entry)
                else:
                    result[bucket_key].append(entry)
            else:
                result['erros'].append({
                    "nome": inv.nome,
                    "cnpj": None,
                    "erro": "CNPJ não informado na minuta"
                })

        elif inv.tipo == 'PF':
            # Classify PF as foreign or national
            is_foreign = (
                inv.nacionalidade and
                inv.nacionalidade.lower() not in ('brasileira', 'brasileiro', 'brasil') and
                inv.nacionalidade.lower() != 'brazil'
            ) or (
                inv.documento_tipo in ('rnm', 'passaporte')
            )

            if is_foreign:
                result['estrangeiros'].append({
                    "nome": inv.nome,
                    "nacionalidade": inv.nacionalidade or "estrangeiro",
                    "documento_tipo": inv.documento_tipo,
                    "documento": inv.documento,
                    "acao": inv.acao
                })
            else:
                result['sem_pendencia'].append({
                    "nome": inv.nome,
                    "nacionalidade": inv.nacionalidade or "brasileiro",
                    "documento_tipo": inv.documento_tipo,
                    "documento": inv.documento
                })

    return result