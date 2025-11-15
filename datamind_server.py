import os
import json
import sqlite3
import logging
from datetime import datetime
from typing import Tuple, Dict, Any, Optional

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- KeepAlive imports ---
import threading
import time

# ==========================================
#  CONFIGURACIÓN BÁSICA
# ==========================================
app = Flask(__name__)
CORS(app)

PORT = int(os.environ.get("PORT", 10000))

# API-FOOTBALL (stats reales para fútbol)
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "").strip()
API_FOOTBALL_BASE = os.getenv(
    "API_FOOTBALL_BASE_URL",
    "https://v3.football.api-sports.io"
).rstrip("/")

TIMEZONE = os.getenv("TIMEZONE", "America/Mexico_City")

DB_PATH = os.getenv("DATAMIND_DB_PATH", "datamind_memory.db")

# URL pública del servicio para KeepAlive
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - DataMind - %(levelname)s - %(message)s",
)
log = logging.getLogger("DataMind")


# ==========================================
#  DB: MEMORIA PARA APRENDER DESPUÉS
# ==========================================
def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            sport TEXT,
            raw_query TEXT,
            match_date TEXT,
            main_pick TEXT,
            extra_info TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def log_prediction(
    sport: str,
    query: str,
    match_date: str,
    main_pick: str,
    extra_info: Dict[str, Any],
) -> None:
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO predictions (created_at, sport, raw_query, match_date, main_pick, extra_info)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                sport,
                query,
                match_date,
                main_pick,
                json.dumps(extra_info, ensure_ascii=False),
            ),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        log.error(f"Error guardando predicción en DB: {e}")


init_db()


# ==========================================
#  UTILIDADES GENERALES
# ==========================================
def detect_sport(text: str) -> str:
    t = text.lower()

    if any(k in t for k in ["nba", "canastas", "rebotes", "triples", "puntos"]):
        return "basket"

    if any(k in t for k in ["mlb", "home run", "bases llenas", "pitcheo", "innings"]):
        return "beisbol"

    if any(k in t for k in ["nfl", "touchdown", "yardas", "quarterback"]):
        return "nfl"

    return "futbol"


def extract_match_date(text: str) -> str:
    import re

    patterns = [
        r"(\d{1,2}/\d{1,2}/\d{4})",
        r"(\d{1,2}-\d{1,2}-\d{4})",
        r"(\d{1,2}\.\d{1,2}\.\d{4})",
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1)

    return "Fecha no especificada"


def split_teams(text: str) -> Tuple[str, str]:
    lowered = text.lower()
    for sep in [" vs ", " v ", " - ", " contra ", " vs. "]:
        if sep in lowered:
            parts = lowered.split(sep)
            if len(parts) >= 2:
                return parts[0].strip().title(), parts[1].strip().title()
    return text.title(), ""


# ==========================================
#  API-FOOTBALL HELPERS
# ==========================================
def api_football_headers() -> Dict[str, str]:
    return {
        "x-apisports-key": API_FOOTBALL_KEY,
    }


def get_team_id(team_name: str) -> Optional[int]:
    if not API_FOOTBALL_KEY or not team_name:
        return None

    try:
        r = requests.get(
            f"{API_FOOTBALL_BASE}/teams",
            params={"search": team_name},
            headers=api_football_headers(),
            timeout=10,
        )
        data = r.json()
        res = data.get("response") or []
        if not res:
            return None
        return res[0]["team"]["id"]
    except Exception as e:
        log.error(f"Error buscando ID de equipo '{team_name}': {e}")
        return None


def get_next_fixture(team1_name: str, team2_name: str) -> Dict[str, Any]:
    if not API_FOOTBALL_KEY:
        return {}

    try:
        id1 = get_team_id(team1_name)
        id2 = get_team_id(team2_name)
        if not id1 or not id2:
            return {}

        r = requests.get(
            f"{API_FOOTBALL_BASE}/fixtures",
            params={
                "h2h": f"{id1}-{id2}",
                "next": 1,
                "timezone": TIMEZONE,
            },
            headers=api_football_headers(),
            timeout=15,
        )
        data = r.json()
        fixtures = data.get("response") or []
        if not fixtures:
            return {}

        fx = fixtures[0]
        fixture_info = fx["fixture"]
        league_info = fx["league"]

        return {
            "fixture_id": fixture_info.get("id"),
            "datetime": fixture_info.get("date"),
            "venue": (fixture_info.get("venue") or {}).get("name"),
            "league_id": league_info.get("id"),
            "league_name": league_info.get("name"),
            "season": league_info.get("season"),
            "home_name": fx["teams"]["home"]["name"],
            "away_name": fx["teams"]["away"]["name"],
        }

    except Exception as e:
        log.error(f"Error obteniendo fixture head-to-head: {e}")
        return {}


def get_team_statistics(team_id: int, league_id: int, season: int) -> Dict[str, Any]:
    if not API_FOOTBALL_KEY:
        return {}

    try:
        r = requests.get(
            f"{API_FOOTBALL_BASE}/teams/statistics",
            params={
                "team": team_id,
                "league": league_id,
                "season": season,
            },
            headers=api_football_headers(),
            timeout=15,
        )
        return r.json().get("response") or {}
    except Exception as e:
        log.error(f"Error obteniendo estadísticas de equipo: {e}")
        return {}


# ==========================================
#  NARRATIVAS POR DEPORTE (FÚTBOL, NBA, MLB, NFL)
# ==========================================
# (TU LÓGICA COMPLETA SE QUEDA EXACTAMENTE IGUAL)
# ¡AQUÍ NO SE TOCA NADA!
# ==========================================

# (TODO EL CÓDIGO QUE ME PASASTE PERMANECE IGUAL AQUÍ)
# (No lo repito para ahorrar espacio, va idéntico)


# ==========================================
#  ENDPOINTS FLASK
# ==========================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "DataMind activo", "message": "OK"}), 200


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(silent=True) or {}
        user_text = data.get("query") or data.get("text")

        if not user_text:
            return jsonify(
                {
                    "ok": False,
                    "error": "Falta el campo 'query' o 'text' en el cuerpo JSON",
                }
            ), 400

        sport = detect_sport(user_text)

        if sport == "futbol":
            result = build_soccer_analysis(user_text)
        elif sport == "basket":
            result = build_basket_analysis(user_text)
        elif sport == "beisbol":
            result = build_baseball_analysis(user_text)
        elif sport == "nfl":
            result = build_nfl_analysis(user_text)
        else:
            result = build_soccer_analysis(user_text)

        log_prediction(
            sport=result["sport"],
            query=user_text,
            match_date=result.get("match_date", ""),
            main_pick=result.get("main_pick", ""),
            extra_info=result.get("extra_info", {}),
        )

        response = {
            "ok": True,
            "sport": result["sport"],
            "match_date": result.get("match_date"),
            "prediction": result.get("prediction"),
            "visualmind_payload": result.get("visualmind_payload"),
        }

        return jsonify(response), 200

    except Exception as e:
        log.error(f"Error general en /predict: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


# ==========================================
#  🔥 KEEPALIVE (NUEVO)
# ==========================================
def keep_alive_loop():
    """Evita que Render apague DataMind."""
    if not RENDER_EXTERNAL_URL:
        log.warning("⚠️ RENDER_EXTERNAL_URL no está definida. KeepAlive desactivado.")
        return

    while True:
        try:
            ping_url = f"{RENDER_EXTERNAL_URL}/"
            resp = requests.get(ping_url, timeout=10)
            log.info(f"🔄 KeepAlive DataMind → {ping_url} (status={resp.status_code})")
        except Exception as e:
            log.warning(f"⚠️ Error en KeepAlive: {e}")
        time.sleep(40)  # mantiene el contenedor despierto


# Lanzamos el hilo KeepAlive en cuanto arranca el módulo
threading.Thread(target=keep_alive_loop, daemon=True).start()


# ==========================================
#  MAIN
# ==========================================
if __name__ == "__main__":
    log.info(f"🚀 DataMind ejecutándose en puerto {PORT}")
    app.run(host="0.0.0.0", port=PORT)
