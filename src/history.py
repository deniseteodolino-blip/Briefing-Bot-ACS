import os
import json
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def _get_local_db():
    """Get SQLite connection for local history (fallback)."""
    db_path = Path.home() / '.briefing-bot-cache' / 'history.db'
    db_path.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS processamento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            spe TEXT,
            acs_num INTEGER,
            data_corte TEXT,
            processed_at TEXT,
            resultado_json TEXT,
            mensagem TEXT
        )
    """)
    return conn


def get_supabase():
    """Get Supabase client if configured."""
    if SUPABASE_URL and SUPABASE_KEY:
        from supabase import create_client
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    return None


def save_processamento(
    filename: str,
    spe: str,
    acs_num: int,
    data_corte: str,
    classificacao: dict,
    mensagem: str
) -> dict:
    """Save a processing record to Supabase (or local fallback)."""
    supabase = get_supabase()

    if supabase:
        data = {
            "filename": filename,
            "spe": spe,
            "acs_num": acs_num,
            "data_corte": data_corte,
            "processed_at": "now",
            "resultado_json": json.dumps(classificacao),
            "mensagem": mensagem
        }
        result = supabase.table("processamento").insert(data).execute()
        return result.data[0] if result.data else None
    else:
        # Fallback to local SQLite
        conn = _get_local_db()
        cursor = conn.execute(
            """INSERT INTO processamento
               (filename, spe, acs_num, data_corte, processed_at, resultado_json, mensagem)
               VALUES (?, ?, ?, ?, datetime('now'), ?, ?)""",
            (filename, spe, acs_num, data_corte, json.dumps(classificacao), mensagem)
        )
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return {"id": record_id, "filename": filename, "spe": spe}


def get_all_processamentos() -> list:
    """Get all processing records from Supabase (or local fallback)."""
    supabase = get_supabase()

    if supabase:
        result = supabase.table("processamento").select("*").order("processed_at", desc=True).execute()

        registros = []
        for row in result.data:
            classificacao = {}
            try:
                if row.get('resultado_json'):
                    classificacao = json.loads(row['resultado_json'])
            except:
                pass

            registros.append({
                "id": row['id'],
                "filename": row['filename'],
                "spe": row['spe'],
                "acs_num": row['acs_num'],
                "data_corte": row['data_corte'],
                "processed_at": str(row['processed_at']),
                "classificacao": classificacao,
                "mensagem": row['mensagem']
            })
        return registros
    else:
        # Fallback to local SQLite
        conn = _get_local_db()
        cursor = conn.execute(
            """SELECT id, filename, spe, acs_num, data_corte, processed_at, resultado_json, mensagem
               FROM processamento ORDER BY processed_at DESC"""
        )
        rows = cursor.fetchall()
        conn.close()

        registros = []
        for row in rows:
            classificacao = {}
            try:
                if row[6]:
                    classificacao = json.loads(row[6])
            except:
                pass

            registros.append({
                "id": row[0],
                "filename": row[1],
                "spe": row[2],
                "acs_num": row[3],
                "data_corte": row[4],
                "processed_at": row[5] or "",
                "classificacao": classificacao,
                "mensagem": row[7]
            })
        return registros


def get_processamento_by_id(record_id: int) -> dict:
    """Get a specific processing record by ID."""
    supabase = get_supabase()

    if supabase:
        result = supabase.table("processamento").select("*").eq("id", record_id).execute()

        if not result.data:
            return None

        row = result.data[0]
        classificacao = {}
        try:
            if row.get('resultado_json'):
                classificacao = json.loads(row['resultado_json'])
        except:
            pass

        return {
            "id": row['id'],
            "filename": row['filename'],
            "spe": row['spe'],
            "acs_num": row['acs_num'],
            "data_corte": row['data_corte'],
            "processed_at": str(row['processed_at']),
            "classificacao": classificacao,
            "mensagem": row['mensagem']
        }
    else:
        # Fallback to local SQLite
        conn = _get_local_db()
        cursor = conn.execute(
            """SELECT id, filename, spe, acs_num, data_corte, processed_at, resultado_json, mensagem
               FROM processamento WHERE id = ?""",
            (record_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        classificacao = {}
        try:
            if row[6]:
                classificacao = json.loads(row[6])
        except:
            pass

        return {
            "id": row[0],
            "filename": row[1],
            "spe": row[2],
            "acs_num": row[3],
            "data_corte": row[4],
            "processed_at": row[5] or "",
            "classificacao": classificacao,
            "mensagem": row[7]
        }


def delete_processamento(record_id: int) -> bool:
    """Delete a processing record."""
    supabase = get_supabase()

    if supabase:
        result = supabase.table("processamento").delete().eq("id", record_id).execute()
        return len(result.data) > 0
    else:
        # Fallback to local SQLite
        conn = _get_local_db()
        cursor = conn.execute("DELETE FROM processamento WHERE id = ?", (record_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted