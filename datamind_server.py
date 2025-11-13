@app.route("/predict", methods=["POST"])
def predict():
    try:
        print("🟢 Petición recibida en /predict", file=sys.stderr)

        # Intento normal
        try:
            data = request.get_json(force=True)
        except Exception:
            # Reintento forzando codificación tolerante UTF-8
            raw_data = request.get_data(as_text=True)
            import json
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
