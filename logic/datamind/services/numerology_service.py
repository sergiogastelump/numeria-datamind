# app/datamind/services/numerology_service.py

from datetime import datetime

def reduce_to_core(n: int) -> int:
    """Reduce un número a su esencia (1–9, 11, 22, 33)."""
    while n > 9 and n not in (11, 22, 33):
        n = sum(int(d) for d in str(n))
    return n


def numerology_from_name(name: str) -> dict:
    """Calcula vibración numerológica del nombre."""
    if not name:
        return {"name": "", "name_value": 0, "name_core": 0}

    total = sum(ord(c.upper()) - 64 for c in name if c.isalpha())
    return {
        "name": name,
        "name_value": total,
        "name_core": reduce_to_core(total),
    }


def numerology_from_birth(birthdate: str) -> dict:
    """Calcula número de destino a partir de la fecha de nacimiento."""
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
