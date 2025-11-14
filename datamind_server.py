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
#   ENDPOINT PRINCIPAL
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
    Endpoint que recibe:
    {
        "query": "Liverpool vs City"
    }

    Y devuelve una predicción simple simulada.
    NumerIA Bot se conecta a este endpoint.
    """

    try:
        data = request.get_json()

        if not data or "query" not in data:
            return jsonify({"error": "Falta el campo 'query'"}), 400

        user_query = data["query"]

        # ================================
        #  LÓGICA TEMPORAL DE PREDICCIÓN
        #  (para pruebas en NumerIA)
        # ================================
        response = {
            "ok": True,
            "query": user_query,
            "prediction": f"Predicción simulada para: {user_query}",
            "confidence": "78%",
            "tip": "Este es un resultado provisional mientras conectamos el modelo real."
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
