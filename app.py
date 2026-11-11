"""Flask REST API for the trained California Housing MLflow model."""

import math
import os
from pathlib import Path

import mlflow
import pandas as pd
from flask import Flask, jsonify, request


DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "models" / "california_housing"
FEATURES = (
    "MedInc",
    "HouseAge",
    "AveRooms",
    "AveBedrms",
    "Population",
    "AveOccup",
    "Latitude",
    "Longitude",
)
MAX_BATCH_SIZE = 1000


def create_app():
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "sqlite:///mlflow.db")
    model_uri = os.environ.get("MODEL_URI", str(DEFAULT_MODEL_PATH))
    mlflow.set_tracking_uri(tracking_uri)
    model = mlflow.pyfunc.load_model(model_uri)

    app = Flask(__name__)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "model_uri": model_uri})

    @app.post("/predict")
    def predict():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Request body must be a JSON object."}), 400

        instances = payload.get("instances")
        if not isinstance(instances, list) or not instances:
            return jsonify(
                {"error": "'instances' must be a non-empty list of feature objects."}
            ), 400
        if len(instances) > MAX_BATCH_SIZE:
            return jsonify(
                {"error": f"A request may contain at most {MAX_BATCH_SIZE} instances."}
            ), 400

        rows = []
        expected = set(FEATURES)
        for index, instance in enumerate(instances):
            if not isinstance(instance, dict):
                return jsonify(
                    {"error": f"Instance {index} must be a JSON object."}
                ), 400
            supplied = set(instance)
            missing = sorted(expected - supplied)
            extra = sorted(supplied - expected)
            if missing or extra:
                details = {}
                if missing:
                    details["missing_features"] = missing
                if extra:
                    details["unexpected_features"] = extra
                return jsonify(
                    {"error": f"Instance {index} has incorrect features.", **details}
                ), 400

            row = {}
            for feature in FEATURES:
                value = instance[feature]
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    return jsonify(
                        {
                            "error": (
                                f"Instance {index} feature '{feature}' "
                                "must be a finite number."
                            )
                        }
                    ), 400
                try:
                    numeric_value = float(value)
                except OverflowError:
                    numeric_value = math.inf
                if not math.isfinite(numeric_value):
                    return jsonify(
                        {
                            "error": (
                                f"Instance {index} feature '{feature}' "
                                "must be a finite number."
                            )
                        }
                    ), 400
                row[feature] = numeric_value
            rows.append(row)

        predictions = model.predict(pd.DataFrame(rows, columns=FEATURES))
        return jsonify(
            {
                "predictions": [float(value) for value in predictions],
                "unit": "$100,000",
            }
        )

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(
        host=os.environ.get("FLASK_HOST", "127.0.0.1"),
        port=int(os.environ.get("FLASK_PORT", "5001")),
        debug=False,
    )
