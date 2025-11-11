import json
import os
from datetime import datetime
from sqlalchemy import create_engine, text

_engine = None

def init_db(db_url: str):
    global _engine
    _engine = create_engine(db_url, echo=False)

    # crear tabla simple
    with _engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT,
            input_json TEXT,
            output_json TEXT,
            created_at TEXT
        )
        """))


def save_analysis(kind: str, input_data: dict, output_data: dict):
    if _engine is None:
        return
    with _engine.begin() as conn:
        conn.execute(
            text("INSERT INTO analyses (kind, input_json, output_json, created_at) VALUES (:k, :i, :o, :c)"),
            {
                "k": kind,
                "i": json.dumps(input_data, ensure_ascii=False),
                "o": json.dumps(output_data, ensure_ascii=False),
                "c": datetime.utcnow().isoformat()
            }
        )


def get_history(limit: int = 50):
    if _engine is None:
        return []
    with _engine.begin() as conn:
        rows = conn.execute(
            text("SELECT id, kind, input_json, output_json, created_at FROM analyses ORDER BY id DESC LIMIT :lim"),
            {"lim": limit}
        ).fetchall()

    out = []
    for r in rows:
        out.append({
            "id": r.id,
            "kind": r.kind,
            "input": json.loads(r.input_json),
            "output": json.loads(r.output_json),
            "created_at": r.created_at
        })
    return out
