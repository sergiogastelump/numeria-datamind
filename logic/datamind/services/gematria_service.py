# app/datamind/services/gematria_service.py

import re
import string

# Mapa básico para gematría A=1 ... Z=26
LETTER_MAP = {chr(i + 65): i + 1 for i in range(26)}

def clean_text(text: str) -> str:
    """Limpia texto de caracteres especiales"""
    return re.sub(r"[^A-Za-z0-9ÁÉÍÓÚáéíóúÑñ ]", "", text).strip()

def gematria_value(text: str) -> int:
    """Calcula el valor gemátrico simple de un texto."""
    if not text:
        return 0
    text = clean_text(text).upper()
    total = 0
    for ch in text:
        if ch.isalpha():
            total += LETTER_MAP.get(ch, 0)
        elif ch.isdigit():
            total += int(ch)
    return total
