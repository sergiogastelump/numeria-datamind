# =========================================================
#  DataMind IA Server — Numer IA / Neurobet Ecosystem
#  Autor: Sergio Gastelum
#  Versión: 1.0 estable (listo para despliegue en Render)
# =========================================================

from flask import Flask, jsonify, request
from flask_cors import CORS
import traceback

# Inicializa la app Flask
app = Flask(__name__)
CORS(app)  # Habilita CORS para permitir peticiones externas (bot, dashboard, etc.)

# =========================================================
#  ENDPOINT PRINCIPAL
# =========================================================
@app.route("/", methods=["GET"])
def home():
    """
    Endpoint raíz: confirma que el servidor está activo.
    """
    return jsonify({
        "status": "ok",
        "service": "DataMind IA Server",
        "message": "Servidor activo y funcionando correctamente 🔥"
    }), 200


# =========================================================
#  ENDPOINT DE PRUEBA
# =========================================================
@app.route("/test", methods=["GET"])
def test():
    """
    Endpoint simple para verificar conexión y respuesta del servidor.
    """
    return jsonify({
        "success": True,
        "message": "✅ Prueba exitosa — DataMind IA responde correctamente"
    }), 200


# =========================================================
#  ENDPOINT DE PREDICCIÓN (POST)
# =========================================================
@app.route("/predict", methods=["POST"])
def predict():
    """
    Endpoint principal de predicción.
    Recibe datos JSON con la información del partido o evento a analizar.
    """
    try:
        data = request.get_json(force=True)

        # Ejemplo: simulación de respuesta de IA (puedes reemplazarlo luego con modelo real)
        input_summary = str(data)[:200] + "..." if data else "sin datos"
        result = {
            "success": True,
            "prediction": "⚙️ IA funcionando — predicción simulada exitosa",
            "received_data": input_summary,
            "confidence": "98.5%",  # ejemplo fijo, reemplazar por valor real del modelo
        }

        return jsonify(result), 200

    except Exception as e:
        traceback_str = traceback.format_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback_str
        }), 500


# =========================================================
#  EJECUCIÓN LOCAL / DEPLOY
# =========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
