from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
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
        if not data:
            raise ValueError("No se recibió cuerpo JSON")

        user = data.get("user", "Desconocido")
        text = data.get("text", "").strip()

        if not text:
            return jsonify({
                "error": "No se recibió texto para analizar",
                "status": "fail"
            }), 400

        interpretation = interpretar_texto(text)
        return jsonify({
            "user": user,
            "input": text,
            "interpretation": interpretation,
            "status": "ok"
        }), 200

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"❌ ERROR en /predict:\n{error_trace}")
        # Mostrar el error completo en la respuesta
        return jsonify({
            "error": str(e),
            "trace": error_trace,
            "status": "error"
        }), 500


def interpretar_texto(texto):
    texto = texto.lower()

    simbolos = {
        "777": "🔮 El 777 simboliza perfección espiritual, equilibrio y buena fortuna.",
        "11": "⚡ El 11 representa intuición, inspiración y despertar espiritual.",
        "13": "🌑 El 13 indica transformación, cambio profundo y renacimiento.",
        "999": "🌀 El 999 anuncia cierre de ciclo y expansión de conciencia.",
        "8": "💰 El 8 simboliza poder material y equilibrio entre el mundo físico y espiritual.",
        "22": "🏗️ El 22 representa la construcción de grandes logros con visión y disciplina."
    }

    for codigo, significado in simbolos.items():
        if codigo in texto:
            return significado

    return "🤔 No se encontró un significado simbólico definido para este código."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
