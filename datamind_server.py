# ============================================================
#  DataMind IA Server — Versión 3.3 Estable
#  Autor: Sergio Gastelum
# ============================================================

from flask import Flask, request, jsonify
import random
import traceback

app = Flask(__name__)

# ============================================================
# Función principal de interpretación simbólica
# ============================================================
def interpretar_texto(user: str, text: str) -> str:
    """Genera una interpretación simbólica simple (base)."""
    text_lower = text.lower().strip()
    
    # Interpretaciones numerológicas simples
    numeros = {
        "7": "El número 7 representa la sabiduría, la introspección y la búsqueda de la verdad.",
        "33": "El 33 es un número maestro asociado a la compasión y el despertar espiritual.",
        "111": "Simboliza alineación y apertura de caminos. Señal de sincronía.",
        "777": "Triple perfección: conexión divina, expansión mental y propósito elevado.",
        "13": "Transformación profunda, cierre de ciclos y renacimiento."
    }

    # Interpretaciones simbólicas simples
    simbolos = {
        "sol": "El sol representa vitalidad, conciencia y energía creadora.",
        "luna": "La luna es intuición, misterio y poder femenino interior.",
        "messi": "Símbolo del genio terrenal que transforma su talento en arte.",
        "código": "Un código es una señal cifrada del universo, esperando ser comprendida."
    }

    # Evaluar tipo de texto recibido
    if text_lower in numeros:
        return numeros[text_lower]
    for n in numeros:
        if n in text_lower:
            return numeros[n]
    for s in simbolos:
        if s in text_lower:
            return simbolos[s]

    # Interpretación genérica
    frases = [
        f"El mensaje '{text}' emite una vibración de equilibrio y propósito oculto.",
        f"'{text}' contiene una energía simbólica que conecta con tu camino de crecimiento.",
        f"'{text}' refleja una frecuencia asociada a la transformación interior.",
        f"'{text}' podría ser una señal del universo para enfocarte en tu misión personal.",
    ]
    return random.choice(frases)

# ============================================================
# Endpoint principal
# ============================================================
@app.route("/")
def home():
    return jsonify({
        "message": "Servidor activo y funcionando correctamente 🔥",
        "service": "DataMind IA Server",
        "status": "ok"
    }), 200

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        user = data.get("user", "Anónimo")
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"error": "No se proporcionó texto para analizar."}), 400

        print(f"🧠 Solicitud recibida de {user}: {text}")

        interpretation = interpretar_texto(user, text)

        print(f"✅ Interpretación generada: {interpretation}")

        return jsonify({
            "user": user,
            "input": text,
            "interpretation": interpretation,
            "status": "ok"
        }), 200

    except Exception as e:
        print(f"[ERROR /predict] {e}")
        traceback.print_exc()
        return jsonify({"error": str(e), "status": "fail"}), 500

# ============================================================
# Iniciar servidor
# ============================================================
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Iniciando DataMind IA Server en puerto {port}...")
    app.run(host="0.0.0.0", port=port)
