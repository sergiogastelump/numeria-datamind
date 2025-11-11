from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route("/")
def home():
    return "🧠 DataMind activo y esperando solicitudes."

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    user = data.get("user", "Usuario")
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Texto vacío"}), 400
    responses = [
        f"{user}, el código '{text}' vibra con energía positiva y equilibrio.",
        f"El mensaje '{text}' sugiere una conexión profunda con el número 7 y la intuición.",
        f"'{text}' parece tener una resonancia mística relacionada con la transformación interior.",
        f"{user}, el patrón de '{text}' indica una oportunidad oculta que pronto se revelará.",
        f"La secuencia '{text}' refleja equilibrio entre mente y propósito."
    ]
    interpretation = random.choice(responses)
    return jsonify({"interpretation": interpretation})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
