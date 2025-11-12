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
        print(f"❌ Error interno en /predict:\n{error_trace}")
        return jsonify({
            "error": str(e),
            "trace": error_trace,
            "status": "error"
        }), 500


def interpretar_texto(texto):
    texto = texto.lower()

    if "777" in texto:
        return "🔮 El 777 simboliza perfección espiritual, equilibrio y buena fortuna."
    elif "11" in texto:
        return "⚡ El 11 representa intuición, inspiración y despertar espiritual."
    elif "13" in texto:
        return "🌑 El 13 indica transformación, cambio profundo y renacimiento."
    elif "999" in texto:
        return "🌀 El 999 anuncia cierre de ciclo y expansión de conciencia."
    else:
        return "🤔 No se encontró un significado simbólico definido para este código."


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
