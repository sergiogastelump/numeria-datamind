import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# ================================
#   CONFIGURACIÓN DEL SERVIDOR
# ================================
app = Flask(__name__)
CORS(app)

# Puerto estándar para Render
PORT = int(os.environ.get("PORT", 10000))


# ================================
#   ENDPOINT PRINCIPAL (SALUD)
# ================================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "DataMind activo", "message": "OK"}), 200


# ================================
#   ENDPOINT DE PREDICCIÓN
# ================================
@app.route("/predict", methods=["POST"])
def predict():
    """
    Endpoint que recibe algo como:
    {
        "query": "Liverpool vs City"
    }
    o también:
    {
        "text": "Liverpool vs City"
    }

    NumerIA Bot puede enviar ambos campos.
    """

    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "No se recibió JSON válido"}), 400

        # Acepta tanto 'query' como 'text'
        user_query = data.get("query") or data.get("text")

        if not user_query:
            return jsonify(
                {"error": "Falta el campo 'query' o 'text' en el cuerpo JSON"}
            ), 400

        # ================================
        #  LÓGICA TEMPORAL DE PREDICCIÓN
        #  (para pruebas en NumerIA)
        # ================================
        response = {
            "ok": True,
            "query": user_query,
            "prediction": f"🔮 Predicción simulada para: {user_query}",
            "confidence": "78%",
            "tip": "Este es un resultado provisional mientras conectamos el modelo real.",
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================================
#   INICIO DEL SERVIDOR
# ================================
if __name__ == "__main__":
    print(f"🚀 DataMind ejecutándose en puerto {PORT}")
    app.run(host="0.0.0.0", port=PORT)
