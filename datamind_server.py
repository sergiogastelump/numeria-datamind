from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "DataMind IA funcionando correctamente.", 200

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        texto = data.get("input", "")

        respuesta = {
            "prediction": f"Base para: {texto}",
            "confidence": 0.82,
            "market": "over 2.5",
            "status": "OK"
        }

        return jsonify(respuesta), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Render asigna automáticamente el puerto en la variable PORT
    import os
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
