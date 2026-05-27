import os
import re
import json
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))


class InvalidExtractionError(Exception):
    """Raised when Claude fails to extract investors from minuta."""
    pass


def load_minuta(path: str) -> bytes:
    """Load minuta file (.docx or PDF) and return bytes."""
    path_obj = Path(path)

    if not path_obj.exists():
        raise FileNotFoundError(f"Minuta not found: {path}")

    ext = path_obj.suffix.lower()
    if ext not in ('.docx', '.pdf'):
        raise ValueError(f"Unsupported file type: {ext}. Use .docx or .pdf")

    with open(path, 'rb') as f:
        return f.read()


def _extract_text_from_docx(content: bytes) -> str:
    """Extract text from DOCX using python-docx."""
    import io
    from docx import Document

    doc = Document(io.BytesIO(content))
    return '\n'.join([p.text for p in doc.paragraphs])


def _extract_text_from_pdf(content: bytes) -> str:
    """Extract text from PDF using pypdf."""
    from pypdf import PdfReader
    import io

    reader = PdfReader(io.BytesIO(content))
    text_parts = []
    for page in reader.pages:
        # Extract text and replace multiple spaces/newlines to help regex
        text = page.extract_text() or ''
        text_parts.append(text)

    return '\n'.join(text_parts)


def extract_pendencias(minuta_path: str) -> dict:
    """
    Extract pendencies from minuta by finding text inside {} brackets.
    """
    content = load_minuta(minuta_path)
    ext = Path(minuta_path).suffix.lower()

    if ext == '.docx':
        text_content = _extract_text_from_docx(content)
    else:
        text_content = _extract_text_from_pdf(content)

    # Limpar texto para lidar com quebras de linha dentro dos brackets e erros de OCR
    cleaned_text = re.sub(r'[\r\n]+', ' ', text_content)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)

    # Extract all text inside {} brackets (now handles multiline since we cleaned it)
    bracketed_texts = re.findall(r'\{([^}]+)\}', cleaned_text)

    # Print what we found inside brackets for debugging
    combined = ' | '.join(bracketed_texts)
    print(f"\n  [DEBUG] Texto extraído de {{}}: {combined[:800]}...")

    # Extract data from minuta header
    prompt_data = """Analise esta minuta de ACS e extraia:
1. SPE/Empresa: está no título (ex: "FOZ SPOT", "Ponta das Canas")
2. Número da ACS: está no título (ex: "1ª ACS", "4ª ACS")
3. DATA DE ASSINATURA/FECHAMENTO: está no final do documento (procure por datas como "31 de janeiro de 2026", "28 de maio de 2026", etc.)

Retorne em JSON:
{
    "spe": "nome da SPE",
    "acs_num": número da ACS (ex: 1, 4),
    "data_corte": "DD/MM/AAAA"
}

Se não encontrar algum campo, use null."""

    try:
        response_data = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=1024,
            thinking={"type": "disabled"},
            messages=[{"role": "user", "content": prompt_data + "\n\n--- MINUTA COMPLETA ---\n" + text_content}]
        )

        data_info = _extract_json_from_response(response_data)
        if not data_info:
            data_info = {"spe": None, "acs_num": None, "data_corte": None}
    except Exception as e:
        print(f"Erro ao extrair dados: {e}")
        data_info = {"spe": None, "acs_num": None, "data_corte": None}

    # Remove the second (redundant) extraction block that was replacing the first one
    # Use Claude to parse the full minuta and identify ALL pendencies
    prompt = f"""Você é um assistente jurídico especializado em extrair pendências de ACS (Alteração de Capital Social).

ANALISE A MINUTA COMPLETA e identifique TODOS os investidores que possuem OBSERVAÇÕES entre {{}} no documento.

REGRA PRINCIPAL: Qualquer texto entre {{}} na seção de QUALIFICAÇÃO DOS SÓCIOS indica uma pendência que precisa ser tratada.

O texto extraído de dentro das chaves {{}} é este:
---
{combined}
---

CATEGORIAS DE PENDÊNCIA:

1. RESIDENTES NO EXTERIOR (PF):
   - Sócios PF com observação contendo:
     • "INFORMAR RNM E ENDEREÇO NO BRASIL OU PROCURADOR"
     • "procurador domiciliado no Brasil"
   - Extraia o nome exato do sócio e sua nacionalidade

2. EMPRESAS ME/EPP (que precisam alterar porte para DEMAIS):
   - Empresas com observação "NECESSÁRIO ALTERAR O PORTE PARA DEMAIS"
   - Extraia o nome da empresa e CNPJ

3. EMPRESAS SIMPLES NACIONAL:
   - Empresas com menção de "Simples Nacional"
   - Extrair: nome da empresa e CNPJ

CRÍTICO: Você deve buscar o nome dos investidores que possuem as chaves {{}} ao lado ou logo após seus dados na minuta.
EXEMPLO 1: Se a minuta diz "JUAN ARIEL HOLSVAK ... telefone: 123. {{INFORMAR RNM...}}", você deve listar JUAN ARIEL HOLSVAK na categoria 1.
EXEMPLO 2: Se a minuta diz "H2O INVESTIMENTOS SA ... email: a@b.com {{NECESSÁRIO ALTERAR O PORTE...}}", você deve listar H2O INVESTIMENTOS SA na categoria 2.

PRESTE MUITA ATENÇÃO aos seguintes nomes na minuta:
- JUAN ARIEL HOLSVAK (veja se há {{INFORMAR RNM...}} após ele)
- SANTIAGO ORLANDO PORTEL (veja se há {{INFORMAR RNM...}} após ele)
- GABRIELA VICTORIA VISACHO TAPIA LTDA (veja se há {{NECESSÁRIO ALTERAR O PORTE...}} após ele)
Se esses textos em chaves estiverem lá, você DEVE incluí-los no JSON!

Retorne em JSON com TODOS os investidores encontrados em cada categoria:

{{
    "estrangeiros": [
        {{"nome": "NOME COMPLETO", "nacionalidade": "país", "observacao": "o que diz o {{}}"}}
    ],
    "me_epp": [
        {{"nome": "NOME DA EMPRESA", "cnpj": "XX.XXX.XXX/XXXX-XX", "observacao": "o que diz o {{}}"}}
    ],
    "simples_nacional": [
        {{"nome": "NOME DA EMPRESA", "cnpj": "XX.XXX.XXX/XXXX-XX", "observacao": "o que diz o {{}}"}}
    ]
}}

Se não encontrar nenhum em uma categoria, retorne array vazio []."""

    try:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=8192,
            thinking={"type": "disabled"},
            messages=[{"role": "user", "content": prompt + "\n\n--- MINUTA COMPLETA ---\n" + cleaned_text}]
        )

        pendencias = _extract_json_from_response(response)
        if not pendencias:
            pendencias = {"estrangeiros": [], "simples_nacional": [], "me_epp": []}

    except Exception as e:
        print(f"Erro ao extrair pendências: {e}")
        pendencias = {"estrangeiros": [], "simples_nacional": [], "me_epp": []}

    result = {
        "spe": data_info.get("spe"),
        "acs_num": data_info.get("acs_num"),
        "data_corte": data_info.get("data_corte"),
        "estrangeiros": pendencias.get("estrangeiros", []),
        "simples_nacional": pendencias.get("simples_nacional", []),
        "me_epp": pendencias.get("me_epp", []),
        "observacoes_raw": combined
    }

    return result


def _extract_json_from_response(response) -> dict:
    """Extract JSON from Claude response, handling thinking blocks."""
    raw_text = ""
    for block in response.content:
        if hasattr(block, 'type') and block.type == 'text':
            raw_text += block.text
        elif hasattr(block, 'text'):
            raw_text += block.text

    raw_text = raw_text.strip()

    # Try to find JSON in the text
    if raw_text.startswith('[') or raw_text.startswith('{'):
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            pass

    # Try to extract JSON from markdown fences
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', raw_text)
    if json_match:
        try:
            return json.loads(json_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find JSON-like structure
    json_match = re.search(r'\{[\s\S]*\}', raw_text)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def extract_pendencias_with_retry(minuta_path: str, max_retries: int = 2) -> dict:
    """Extract pendencies with retry on failure."""
    last_error = None

    for attempt in range(max_retries):
        try:
            return extract_pendencias(minuta_path)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                print(f"Retry {attempt + 2}/{max_retries} after error: {e}")

    raise last_error or Exception(f"Failed after {max_retries} attempts")