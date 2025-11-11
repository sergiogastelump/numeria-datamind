# app/logic/predictor.py
from datetime import datetime
import re

# Pequeño mapa de valores para gematría simple
LETTER_MAP = {chr(i + 65): i + 1 for i in range(26)}  # A=1 ... Z=26

def clean_text(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ ]", "", text).strip()

def gematria_value(text: str) -> int:
    text = clean_text(text).upper()
    total = 0
    for ch in text:
        if ch.isalpha():
            total += LETTER_MAP.get(ch, 0)
        elif ch.isdigit():
            total += int(ch)
    return total

def reduce_to_core(n: int) -> int:
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(d) for d in str(n))
    return n

def numerology_from_name(name: str) -> dict:
    if not name:
        return {"name": "", "name_value": 0, "name_core": 0}
    value = gematria_value(name)
    return {
        "name": name,
        "name_value": value,
        "name_core": reduce_to_core(value),
    }

def numerology_from_birthdate(birthdate: str) -> dict:
    if not birthdate:
        return {"birthdate": "", "birth_sum": 0, "birth_core": 0}
    try:
        dt = datetime.strptime(birthdate, "%Y-%m-%d")
        digits = list(str(dt.year)) + list(str(dt.month)) + list(str(dt.day))
        total = sum(int(d) for d in digits)
        return {
            "birthdate": birthdate,
            "birth_sum": total,
            "birth_core": reduce_to_core(total),
        }
    except ValueError:
        return {"birthdate": birthdate, "birth_sum": 0, "birth_core": 0}

def interpret(name_info: dict, birth_info: dict, power_info: dict) -> dict:
    details = []
    # base
    if name_info.get("name_core"):
        details.append(f"Vibración base del nombre: {name_info['name_core']}.")
    if birth_info.get("birth_core"):
        details.append(f"Camino de vida {birth_info['birth_core']}.")
    # power code
    if power_info and power_info.get("power_core"):
        details.append(f"Código de poder detectado con vibración {power_info['power_core']}.")
        if power_info.get("sports_hint"):
            details.append(power_info["sports_hint"])

    summary = details[0] if details else "Sin interpretación."
    return {
        "summary": summary,
        "details": details,
    }

def analyze_power_code(power_code: str) -> dict:
    """
    Aquí es donde conectamos con lo que quieres:
    - detectar palabras como LEO, MESSI, MIAMI, FINAL, GOAL, etc.
    - calcular su vibración
    - dar pistas deportivas/simbólicas
    """
    power_code = (power_code or "").strip()
    if not power_code:
        return {}

    val = gematria_value(power_code)
    core = reduce_to_core(val)

    # reglas súper básicas para que veas la idea
    text_up = power_code.upper()
    sports_hint = None

    # ejemplo Messi / Leo
    if "MESSI" in text_up or "LEO" in text_up:
        sports_hint = "Energía asociada a liderazgo / figura central del partido."

    if "MIAMI" in text_up:
        sports_hint = (sports_hint or "") + " Contexto Miami detectado, posible evento mediático."

    if any(word in text_up for word in ["GOL", "GOAL", "ANOTA"]):
        sports_hint = (sports_hint or "") + " Tendencia a momento de definición (anotar)."

    return {
        "input": power_code,
        "gematria": val,
        "power_core": core,
        "sports_hint": sports_hint,
    }

def analyze_full_input(name: str, birthdate: str, power_code: str):
    name_info = numerology_from_name(name)
    birth_info = numerology_from_birthdate(birthdate)
    power_info = analyze_power_code(power_code)

    interpretation = interpret(name_info, birth_info, power_info)

    return {
        "numerology": {
            "by_name": name_info,
            "by_birth": birth_info,
        },
        "gematria": {
            "text": name,
            "gematria": name_info.get("name_value", 0),
        },
        "power_code_analysis": power_info,
        "interpretation": interpretation,
    }
