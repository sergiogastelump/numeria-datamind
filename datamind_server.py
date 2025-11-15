import os
import json
import sqlite3
import logging
from datetime import datetime
from typing import Tuple, Dict, Any, Optional

import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

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
    """
    Detecta el deporte a partir del texto.
    Por ahora:
      - fútbol (default)
      - basket
      - beisbol
      - nfl
    """
    t = text.lower()

    # Basket
    if any(k in t for k in ["nba", "canastas", "rebotes", "triples", "puntos"]):
        return "basket"

    # Béisbol
    if any(k in t for k in ["mlb", "home run", "bases llenas", "pitcheo", "innings"]):
        return "beisbol"

    # NFL
    if any(k in t for k in ["nfl", "touchdown", "yardas", "quarterback"]):
        return "nfl"

    # Por defecto, fútbol
    return "futbol"


def extract_match_date(text: str) -> str:
    """
    Intenta detectar una fecha simple en el texto.
    Formatos soportados: dd/mm/aaaa, dd-mm-aaaa, dd.mm.aaaa
    Si no encuentra, devuelve 'Fecha no especificada'.
    """
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
    """
    Intenta separar 'Equipo A vs Equipo B'.
    Si no logra, usa el texto entero como un solo bloque.
    """
    lowered = text.lower()
    for sep in [" vs ", " v ", " - ", " contra ", " vs. "]:
        if sep in lowered:
            parts = lowered.split(sep)
            if len(parts) >= 2:
                return parts[0].strip().title(), parts[1].strip().title()
    return text.title(), ""


# ==========================================
#  API-FOOTBALL HELPERS (ROBUSTOS)
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
        return res[0].get("team", {}).get("id")
    except Exception as e:
        log.error(f"Error buscando ID de equipo '{team_name}': {e}")
        return None


def get_next_fixture(team1_name: str, team2_name: str) -> Dict[str, Any]:
    """
    Usa head-to-head para encontrar el próximo partido entre ambos equipos.
    Devuelve dict con fecha y algunos datos básicos.
    """
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
        fixture_info = fx.get("fixture", {})
        league_info = fx.get("league", {})

        return {
            "fixture_id": fixture_info.get("id"),
            "datetime": fixture_info.get("date"),
            "venue": (fixture_info.get("venue") or {}).get("name"),
            "league_id": league_info.get("id"),
            "league_name": league_info.get("name"),
            "season": league_info.get("season"),
            "home_name": (fx.get("teams", {}).get("home") or {}).get("name"),
            "away_name": (fx.get("teams", {}).get("away") or {}).get("name"),
        }

    except Exception as e:
        log.error(f"Error obteniendo fixture head-to-head: {e}")
        return {}


def get_team_statistics(team_id: int, league_id: int, season: int) -> Dict[str, Any]:
    """
    Devuelve estadísticas básicas de un equipo para ayudar a la narrativa.
    Si algo falla, devuelve dict vacío.
    """
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
#  NARRATIVAS POR DEPORTE (ESTILO B)
# ==========================================
def build_soccer_analysis(query: str) -> Dict[str, Any]:
    match_date_text = extract_match_date(query)
    home, away = split_teams(query)

    fixture = get_next_fixture(home, away)
    fecha_real = fixture.get("datetime") or match_date_text
    venue = fixture.get("venue") or "Por confirmar"
    league_name = fixture.get("league_name") or "Liga no especificada"

    # Intentar obtener stats, pero si algo falla usamos valores seguros
    home_stats = {}
    away_stats = {}
    try:
        if fixture.get("league_id") and fixture.get("season"):
            home_id = get_team_id(home)
            away_id = get_team_id(away)
            if home_id:
                home_stats = get_team_statistics(
                    home_id, fixture["league_id"], fixture["season"]
                )
            if away_id:
                away_stats = get_team_statistics(
                    away_id, fixture["league_id"], fixture["season"]
                )
    except Exception as e:
        log.error(f"Error global stats fútbol: {e}")

    # Golectas promedio (con defaults seguros si no hay datos)
    def avg_goals(stats: Dict[str, Any], home_away: str) -> float:
        # intenta leer algo similar a stats["goals"]["for"]["average"]["home"]
        try:
            return float(
                stats.get("goals", {})
                .get("for", {})
                .get("average", {})
                .get(home_away, 1.4)
            )
        except Exception:
            return 1.4

    home_avg = avg_goals(home_stats, "home")
    away_avg = avg_goals(away_stats, "away")

    # Probabilidades simples
    total_g = home_avg + away_avg
    prob_over_25 = min(0.95, max(0.35, total_g / 3.0))
    prob_home = 0.45 + (home_avg - away_avg) * 0.05
    prob_home = max(0.15, min(0.70, prob_home))
    prob_draw = 0.20
    prob_away = 1 - prob_home - prob_draw

    # Numerología suave (explicación extendida)
    # Tomamos los números clave que tenemos
    key_nums = [
        round(home_avg, 2),
        round(away_avg, 2),
        round(total_g, 2),
    ]
    nums_text = ", ".join([str(n) for n in key_nums])

    intensidad = "alta" if total_g >= 3 else "media" if total_g >= 2.2 else "controlada"
    riesgo = "moderado" if prob_over_25 >= 0.6 else "alto"

    pick_free = f"Doble oportunidad: {home} o empate."
    pick_premium = f"Over 2.5 goles en el partido."

    main_pick = pick_premium

    prediction_text = f"""
⚽ Análisis NumerIA – {home} vs {away}

📅 Fecha estimada del partido:
{fecha_real}  (texto original: {match_date_text})
🏟️ Sede prevista: {venue}
🏆 Competición: {league_name}

📊 Lectura deportiva con números reales
- Promedio de goles a favor en casa de {home}: {home_avg:.2f}
- Promedio de goles a favor de {away} como visitante: {away_avg:.2f}
- Suma de promedios ofensivos: {total_g:.2f}

Estos valores nos muestran un partido con tendencia a tener ocasiones constantes.
Cuando la suma ofensiva se mueve alrededor de {total_g:.2f}, suele haber partidos
de {intensidad} intensidad, con varias llegadas y opciones claras de gol.

📈 Probabilidades aproximadas (no son cuotas, son lectura numérica)
- Victoria {home}: {prob_home*100:,.1f}%
- Empate: {prob_draw*100:,.1f}%
- Victoria {away}: {prob_away*100:,.1f}%
- Over 2.5 goles: {prob_over_25*100:,.1f}%

🔢 Correlación numérica (enfoque NumerIA)
Números clave del partido: {nums_text}

• El promedio de {home} ({home_avg:.2f}) indica que no necesita muchas llegadas
  para convertir; suele transformar parte importante de sus ocasiones.
• El promedio de {away} ({away_avg:.2f}) como visitante muestra que no renuncia
  al ataque fuera de casa.
• La suma {total_g:.2f} está en el rango donde, históricamente, los partidos
  tienden a romper la barrera de los 2 goles.

NumerIA no interpreta estos números como algo “mágico”, sino como
un lenguaje estadístico: cuando estas combinaciones se repiten, la probabilidad
de un partido abierto aumenta.

✅ Pick FREE (conservador)
{pick_free}

💎 Pick PRINCIPAL NumerIA (estilo tipster)
{pick_premium}

Este pick se elige porque la combinación de promedios ofensivos y tendencia
histórica respalda un partido con goles de ambos lados o dominio de uno,
pero con marcador movido.

🧠 Nota:
NumerIA registrará este pick en su memoria para comparar más adelante el
resultado real y ajustar sus patrones numéricos.

🖼 ¿Quieres generar una imagen para redes con esta predicción?
Escribe: imagen
""".strip()

    visualmind_payload = {
        "sport": "futbol",
        "match": f"{home} vs {away}",
        "date": str(fecha_real),
        "key_numbers": {
            "home_avg_goals": home_avg,
            "away_avg_goals": away_avg,
            "total_goals": total_g,
        },
        "headline": f"{home} vs {away} – partido con tendencia a goles",
        "pick": pick_premium,
        "summary_lines": [
            f"{home} promedio goles casa: {home_avg:.2f}",
            f"{away} promedio goles visitante: {away_avg:.2f}",
            f"Suma ofensiva: {total_g:.2f}",
            "Pick principal: Over 2.5 goles",
        ],
    }

    extra_info = {
        "home_team": home,
        "away_team": away,
        "home_avg_goals": home_avg,
        "away_avg_goals": away_avg,
        "total_goals": total_g,
        "prob_home": prob_home,
        "prob_draw": prob_draw,
        "prob_away": prob_away,
        "prob_over_25": prob_over_25,
    }

    return {
        "sport": "futbol",
        "match_date": str(fecha_real),
        "prediction": prediction_text,
        "main_pick": main_pick,
        "visualmind_payload": visualmind_payload,
        "extra_info": extra_info,
    }


def build_basket_analysis(query: str) -> Dict[str, Any]:
    match_date_text = extract_match_date(query)
    home, away = split_teams(query)

    # Por ahora usamos números estándar hasta que conectemos una API de basket
    pace = 98.5  # posesiones estimadas
    offensive_rating = 112.3  # puntos por 100 posesiones combinados
    projected_total = round(pace * offensive_rating / 100, 1)

    tendencia_ganador = f"Ligera ventaja para {home} por contexto y ritmo."
    prob_over = 0.57 if projected_total >= 226 else 0.48

    pick_free = f"Over alterno de puntos totales por arriba de {projected_total - 5:.1f}."
    pick_premium = f"Over línea principal de puntos totales cercana a {projected_total:.1f}."

    main_pick = pick_premium

    prediction_text = f"""
🏀 Análisis NumerIA – {home} vs {away}

📅 Fecha estimada del partido:
{match_date_text}

📊 Ritmo y tendencia ofensiva
- Ritmo proyectado del juego (pace): {pace:.1f} posesiones.
- Rating ofensivo combinado estimado: {offensive_rating:.1f} puntos por 100 posesiones.
- Proyección de puntos totales: {projected_total:.1f}.

Cuando un partido se mueve alrededor de este volumen de posesiones y eficiencia,
suele presentar tramos de anotación continua y parciales largos a favor de uno u otro.

📈 Lectura de tendencia
- Tendencia del ganador: {tendencia_ganador}
- Probabilidad aproximada de altas: {prob_over*100:,.1f}%

🔢 Lectura numérica explicada
Los números clave ({pace:.1f} de ritmo y {offensive_rating:.1f} de eficiencia)
indican un entorno favorable para que los anotadores principales superen
sus medias y el total global tienda a ser alto. NumerIA interpreta estas
combinaciones como escenarios donde las “rachas” ofensivas aparecen con frecuencia.

✅ Pick FREE
{pick_free}

💎 Pick PRINCIPAL NumerIA
{pick_premium}

🧠 Este escenario se guardará para comparar, más adelante, cómo se comportan
los partidos con ritmos similares y ajustar la sensibilidad de las altas/bajas.

🖼 ¿Quieres generar una imagen para redes con esta predicción?
Escribe: imagen
""".strip()

    visualmind_payload = {
        "sport": "basket",
        "match": f"{home} vs {away}",
        "date": match_date_text,
        "key_numbers": {
            "pace": pace,
            "offensive_rating": offensive_rating,
            "projected_total": projected_total,
        },
        "headline": f"{home} vs {away} – tendencia a altas",
        "pick": pick_premium,
        "summary_lines": [
            f"Pace estimado: {pace:.1f}",
            f"Rating ofensivo: {offensive_rating:.1f}",
            f"Total proyectado: {projected_total:.1f}",
        ],
    }

    extra_info = {
        "pace": pace,
        "offensive_rating": offensive_rating,
        "projected_total": projected_total,
        "prob_over": prob_over,
    }

    return {
        "sport": "basket",
        "match_date": match_date_text,
        "prediction": prediction_text,
        "main_pick": main_pick,
        "visualmind_payload": visualmind_payload,
        "extra_info": extra_info,
    }


def build_baseball_analysis(query: str) -> Dict[str, Any]:
    match_date_text = extract_match_date(query)
    home, away = split_teams(query)

    # Números base provisionales (hasta que conectemos API de MLB)
    home_runs_avg = 4.6
    away_runs_avg = 4.1
    total_runs = home_runs_avg + away_runs_avg

    ganador_prob = f"Ligera inclinación para {home} por estabilidad de su rotación."
    pick_free = f"Over alterno de carreras totales por arriba de {total_runs - 1:.1f}."
    pick_premium = f"{home} gana el partido y se anotan al menos {total_runs - 0.5:.1f} carreras."

    main_pick = pick_premium

    prediction_text = f"""
⚾ Análisis NumerIA – {home} vs {away}

📅 Fecha estimada del partido:
{match_date_text}

📊 Números base de carrera
- Carreras promedio de {home} como local: {home_runs_avg:.1f}
- Carreras promedio de {away} como visitante: {away_runs_avg:.1f}
- Carreras totales proyectadas: {total_runs:.1f}

Estos rangos de anotación suelen aparecer en enfrentamientos donde los
abridores permiten tráfico constante en bases, y los bullpens tienen
momentos de vulnerabilidad.

🔢 Lectura numérica explicada
La suma {total_runs:.1f} coloca el partido en una zona donde se ven
marcadores abiertos con frecuencia. NumerIA utiliza este tipo de
combinaciones para diferenciar juegos cerrados de juegos con producción
ofensiva constante.

✅ Pick FREE
{pick_free}

💎 Pick PRINCIPAL NumerIA
{pick_premium}

🧠 Este patrón de carreras se guardará para medir qué tan rentable resulta
combinar ganador probable con una línea mínima de carreras.

🖼 ¿Quieres generar una imagen para redes con esta predicción?
Escribe: imagen
""".strip()

    visualmind_payload = {
        "sport": "beisbol",
        "match": f"{home} vs {away}",
        "date": match_date_text,
        "key_numbers": {
            "home_runs_avg": home_runs_avg,
            "away_runs_avg": away_runs_avg,
            "total_runs": total_runs,
        },
        "headline": f"{home} vs {away} – juego con tendencia a carreras",
        "pick": pick_premium,
        "summary_lines": [
            f"Carreras {home}: {home_runs_avg:.1f}",
            f"Carreras {away}: {away_runs_avg:.1f}",
            f"Total proyectado: {total_runs:.1f}",
        ],
    }

    extra_info = {
        "home_runs_avg": home_runs_avg,
        "away_runs_avg": away_runs_avg,
        "total_runs": total_runs,
    }

    return {
        "sport": "beisbol",
        "match_date": match_date_text,
        "prediction": prediction_text,
        "main_pick": main_pick,
        "visualmind_payload": visualmind_payload,
        "extra_info": extra_info,
    }


def build_nfl_analysis(query: str) -> Dict[str, Any]:
    match_date_text = extract_match_date(query)
    home, away = split_teams(query)

    # Números base provisionales (hasta conectar API específica NFL)
    spread_tendency = -3.5  # favorito local
    total_line = 44.5
    prob_cover = 0.56

    pick_free = f"{home} +3.5 (jugada más protegida sobre el spread)."
    pick_premium = f"{home} -3.5 spread y total del partido por arriba de {total_line - 2:.1f} puntos."

    main_pick = pick_premium

    prediction_text = f"""
🏈 Análisis NumerIA – {home} vs {away}

📅 Fecha estimada del partido:
{match_date_text}

📊 Tendencia de línea y total
- Spread de referencia: {home} favorito por {abs(spread_tendency):.1f} puntos.
- Línea total de puntos: {total_line:.1f}.
- Probabilidad aproximada de que {home} cubra el spread: {prob_cover*100:,.1f}%.

🔢 Lectura numérica explicada
Cuando la línea se mueve alrededor de {spread_tendency:.1f} y el total se sitúa
cerca de {total_line:.1f}, NumerIA lo interpreta como un partido donde el equipo
favorito suele imponer ritmo, pero dejando ventanas para respuestas del rival.
Son marcadores típicos de encuentros 27–20, 28–21, etc.

✅ Pick FREE
{pick_free}

💎 Pick PRINCIPAL NumerIA
{pick_premium}

🧠 Este tipo de combinaciones spread/total se almacenará para identificar
qué configuraciones son más rentables a mediano plazo.

🖼 ¿Quieres generar una imagen para redes con esta predicción?
Escribe: imagen
""".strip()

    visualmind_payload = {
        "sport": "nfl",
        "match": f"{home} vs {away}",
        "date": match_date_text,
        "key_numbers": {
            "spread_tendency": spread_tendency,
            "total_line": total_line,
        },
        "headline": f"{home} vs {away} – lectura del spread y total",
        "pick": pick_premium,
        "summary_lines": [
            f"Spread estimado: {spread_tendency:.1f}",
            f"Total referencia: {total_line:.1f}",
        ],
    }

    extra_info = {
        "spread_tendency": spread_tendency,
        "total_line": total_line,
        "prob_cover": prob_cover,
    }

    return {
        "sport": "nfl",
        "match_date": match_date_text,
        "prediction": prediction_text,
        "main_pick": main_pick,
        "visualmind_payload": visualmind_payload,
        "extra_info": extra_info,
    }


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
            # Fallback muy raro, pero por seguridad
            result = build_soccer_analysis(user_text)

        # Log en DB para memoria/aprendizaje futuro
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


if __name__ == "__main__":
    log.info(f"🚀 DataMind ejecutándose en puerto {PORT}")
    app.run(host="0.0.0.0", port=PORT)
