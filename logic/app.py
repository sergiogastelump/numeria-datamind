from flask import Flask, request, jsonify, render_template
from app.logic.predictor import analyze_full_input

# DataMind services
from app.datamind.services.gematria_service import gematria_value as dm_gematria_value
from app.datamind.services.numerology_service import numerology_from_name as dm_num_from_name, numerology_from_birth as dm_num_from_birth
from app.datamind.services.interpretation_service import build_interpretation as dm_build_interpretation

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    @app.route("/", methods=["GET"])
    def home():
        return render_template("index.html")

    # Predictor principal (PredictMind / Numer IA)
    @app.route("/analyze", methods=["POST"])
    def analyze():
        data = request.get_json() if request.is_json else request.form

        name = data.get("name", "").strip()
        birthdate = data.get("birthdate", "").strip()
        power_code = data.get("power_code", "").strip()

        result = analyze_full_input(name=name, birthdate=birthdate, power_code=power_code)
        return jsonify(result)

    # --- DataMind endpoints (IA modular interna) ---

    @app.route("/datamind/ping", methods=["GET"])
    def datamind_ping():
        return jsonify({"status": "ok", "module": "NumerIA DataMind", "message": "datamind online"})

    @app.route("/datamind/analyze", methods=["POST"])
    def datamind_analyze():
        """
        Endpoint que usa exclusivamente los servicios de NumerIA_DataMind,
        pensado para futuras IA deportivas/simbólicas.
        """
        data = request.get_json() if request.is_json else request.form
        name = data.get("name", "").strip()
        birthdate = data.get("birthdate", "").strip()
        text = data.get("text", "").strip() or name

        gem_val = dm_gematria_value(text) if text else 0
        num_name = dm_num_from_name(name) if name else {}
        num_birth = dm_num_from_birth(birthdate) if birthdate else {}

        interpretation = dm_build_interpretation(
            name_data=num_name,
            birth_data=num_birth,
            gematria_value=gem_val
        )

        return jsonify({
            "datamind": {
                "name": name,
                "birthdate": birthdate,
                "text": text,
                "gematria": gem_val,
                "numerology": {
                    "by_name": num_name,
                    "by_birth": num_birth,
                },
                "interpretation": interpretation
            }
        })

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
