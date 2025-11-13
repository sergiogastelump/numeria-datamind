import sys
import traceback
import json
from flask import Flask, request, jsonify

# 🚀 Inicialización del servidor Flask
app = Flask(__name__)

# 💡 Función base de interpretación simbólica
def interpretar_texto(texto: str):
    texto = texto.lower()
    if "777" in texto:
        return "🔮 El 777 simboliza perfección espiritual, equilibrio y buena fortuna."
    elif "13" in texto:
        return "⚡ El 13 representa transformación profunda y renacimiento."
    elif "999" in texto:
        return "🌕 El 999 marca el cierre de un ciclo y la llegada de nuevas oportunidades."
    elif "111" in texto:
        return "✨ El 111 indica alineación espiritual y nuevos comienzos."
    elif "222" in texto:
        return "🌱 El 222 simboliza equilibrio, armonía y sincronía con el universo."
    else:
        return "🤖 No se encontró un significado simbólico directo para este código."

# 🧠 Endpoint principal de predicción
@app.route("/predict", methods=["POST"])
def predict():
    try:
        print("🟢 Petición recibida en /predict", file=sys.stderr)

        # Intento normal de parsear JSON
        try:
            data = request.get_json(force=True)
        except Exception:
            # Reintento forzando codificación tolerante UTF-8
            raw_data = request.get_data(as_text=True)
            data = json.loads(raw_data.encode('utf-8', 'ignore').decode('utf-8', 'ignore'))

        print(f"📦 Datos recibidos: {data}", file=sys.stderr)

        if not data:
            raise ValueError("No se recibió cuerpo JSON")

        user = data.get("user", "Desconocido")
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"error": "No se recibió texto para analizar", "status": "fail"}), 400

        interpretation = interpretar_texto(text)
        print(f"✅ Interpretación: {interpretation}", file=sys.stderr)

        return jsonify({
            "user": user,
            "input": text,
            "interpretation": interpretation,
            "status": "ok"
        }), 200

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ ERROR en /predict:\n{error_trace}", file=sys.stderr)
        return jsonify({
            "error": str(e),
            "trace": error_trace,
            "status": "error"
        }), 500


# 🧭 Ruta de prueba para verificar el estado del servidor
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Servidor activo y funcionando correctamente 🔥",
        "service": "DataMind IA Server",
        "status": "ok"
    })


# 🚀 Ejecución local (modo debug) o en Render
if __name__ == "__main__":
    print("🚀 Servidor DataMind iniciado en modo debug absoluto", file=sys.stderr)
    app.run(host="0.0.0.0", port=10000, debug=True)
