# app/datamind/services/interpretation_service.py

"""
Módulo de interpretación simbólica para NumerIA_DataMind.
Combina información numerológica, gemátrica y contextual
para generar una interpretación simbólica básica.
"""

def build_interpretation(name_data, birth_data, gematria_value):
    """
    Genera una interpretación simbólica con base en:
    - Numerología del nombre
    - Fecha de nacimiento
    - Valor gemátrico
    """
    details = []

    # --- Análisis del nombre ---
    if name_data and name_data.get("name_core"):
        details.append(f"Vibración del nombre: {name_data['name_core']}.")
        if name_data["name_core"] in (1, 8):
            details.append("Energía de liderazgo y manifestación.")
        elif name_data["name_core"] in (2, 6):
            details.append("Energía emocional y de conexión humana.")
        elif name_data["name_core"] in (3, 9):
            details.append("Energía creativa y expresiva.")
        elif name_data["name_core"] == 7:
            details.append("Energía introspectiva y espiritual.")

    # --- Análisis del nacimiento ---
    if birth_data and birth_data.get("birth_core"):
        details.append(f"Camino de vida: {birth_data['birth_core']}.")
        if birth_data["birth_core"] == 1:
            details.append("Camino de autodeterminación y liderazgo.")
        elif birth_data["birth_core"] == 5:
            details.append("Camino de libertad y transformación.")
        elif birth_data["birth_core"] == 7:
            details.append("Camino de sabiduría y búsqueda interior.")
        elif birth_data["birth_core"] == 9:
            details.append("Camino de servicio y propósito elevado.")

    # --- Análisis gemátrico ---
    if gematria_value:
        details.append(f"Gematría del texto: {gematria_value}.")
        if gematria_value % 7 == 0:
            details.append("Simbolismo de perfección y totalidad (múltiplo de 7).")
        elif gematria_value % 9 == 0:
            details.append("Simbolismo de cierre o culminación (múltiplo de 9).")
        elif gematria_value % 5 == 0:
            details.append("Simbolismo de cambio y movimiento (múltiplo de 5).")

    # --- Resumen final ---
    if details:
        summary = (
            f"Interpretación general: "
            f"nombre {name_data.get('name_core', '-')}, "
            f"camino {birth_data.get('birth_core', '-')}, "
            f"gematría {gematria_value}."
        )
    else:
        summary = "Sin interpretación disponible."

    return {
        "summary": summary,
        "details": details
    }
