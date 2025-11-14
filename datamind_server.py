import os
import logging
import requests
from flask import Flask, request, jsonify

# -------------------------------------------------
# Configuración
# -------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")            # Tu API-Sports Key
API_HOST = os.getenv("API_HOST", "v3.football.api-sports.io")
SPORT = os.getenv("SPORT", "football")    # deporte default (football)

HEADERS = {
    "x-apisports-key": API_KEY,
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": API_HOST
}

# -------------------------------------------------
# Funciones auxiliares
# -------------------------------------------------

def fetch_api(endpoint: str, params: dict) -> dict:
    """Consulta API-Sports en el endpoint indicado."""
    url = f"https://{API_HOST}/{endpoint}"
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if resp.status_code != 200:
            logger.error("API error %s: %s", resp.status_code, resp.text)
            return {"error": f"API error {resp.status_code}"}
        return resp.json()
    except Exception as e:
        logger.exception("Exception calling API-Sports")
        return {"error": str(e)}


def parse_match_prediction(team1: str, team2: str) -> dict:
    """
    Analiza un partido usando API-Sports (fútbol por defecto).
    Retorna datos limpios para NumerIA.
    """

    # Paso 1: buscar equipos
    teams_data = fetch_api("teams", {"search": team1})
    teams_data2 = fetch_api("teams", {"search": team2})

    if "error" in teams_data or "error" in teams_data2:
        return {
            "prediction": f"No se encontraron datos suficientes para {team1} vs {team2}.",
            "confidence": 0.5,
            "market": "general",
            "extra": {"note": "Error consultando equipos."}
        }

    if not teams_data.get("response") or not teams_data2.get("response"):
        return {
            "prediction": f"No se encontraron equipos con esos nombres.",
            "confidence": 0.5,
            "market": "general",
            "extra": {"note": "Equipos no detectados."}
        }

    tid1 = teams_data["response"][0]["team"]["id"]
    tid2 = teams_data2["response"][0]["team"]["id"]

    # Paso 2: buscar enfrentamientos directos (H2H)
    h2h_data = fetch_api("fixtures/headtohead", {"h2h": f"{tid1}-{tid2}"})

    if "error" in h2h_data or not h2h_data.get("response"):
        return {
            "prediction": f"Enfrentamiento detectado pero sin estadísticas suficientes.",
            "confidence": 0.5,
            "market": "general",
            "extra": {"note": "No hay H2H disponible."}
        }

    matches = h2h_data["response"]

    # Cálculo simple: goles promedio y tendencia
    total_goals = 0
    count = 0
    wins1 = wins2 = draws = 0

    for m in matches:
        if "goals" in m and m["goals"]["home"] is not None:
            g1 = m["goals"]["home"]
            g2 = m["goals"]["away"]
            total_goals += (g1 + g2)
            count += 1

            if g1 > g2:
                wins1 += 1
            elif g2 > g1:
                wins2 += 1
            else:
                draws += 1

    avg_goals = total_goals / count if count else 2.2

    # Tendencia
    if wins1 > wins2:
        tendency = f"Gana {team1}"
    elif wins2 > wins1:
        tendency = f"Gana {team2}"
    else:
        tendency = "Empate"

    confidence = 0.45 + (abs(wins1 - wins2) * 0.05)
    confidence = min(confidence, 0.85)

    # Mercados sugeridos
    suggested = []
    if avg_goals > 2.5:
        suggested.append("Over 2.5 goles")
    else:
        suggested.append("Under 2.5 goles")

    if wins1 + wins2 + draws > 0:
        suggested.append(f"Tendencia: {tendency}")

    return {
        "prediction": tendency,
        "confidence": round(confidence, 3),
        "market": "futbol_general",
        "extra": {
            "avg_goals_h2h": avg_goals,
            "winner_text": f"{team1} {wins1} - {wins2} {team2} (Empates: {draws})",
            "suggested_markets": suggested,
            "sport": "football"
        }
    }


# -------------------------------------------------
# Función principal /predict
# -------------------------------------------------

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True, silent=True)

    if not data or "input" not in data:
        return jsonify({"error": "Falta campo 'input'"}), 400

    text = data["input"]
    logger.info("Petición recibida: %s", text)

    # Detecta formato "Equipo1 vs Equipo2"
    if " vs " in text.lower():
        parts = text.lower().split(" vs ")
        if len(parts) == 2:
            t1 = parts[0].strip().title()
            t2 = parts[1].strip().title()
            return jsonify(parse_match_prediction(t1, t2))

    # Fallback genérico si no detecta partido
    return jsonify({
        "prediction": f"Interpretación general para '{text}'.",
        "confidence": 0.5,
        "market": "general",
        "extra": {"note": "Formato no detectado, usar Equipo1 vs Equipo2."}
    })


# -------------------------------------------------
# Index
# -------------------------------------------------

@app.route("/", methods=["GET"])
def index():
    return "DataMind funcionando correctamente.", 200


# -------------------------------------------------
# MAIN
# -------------------------------------------------

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=PORT)
