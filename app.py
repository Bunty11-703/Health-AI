from flask import Flask, request, jsonify, send_from_directory
import pickle
import pandas as pd
import json
import numpy as np

app = Flask(__name__, static_folder="static")

# ==================================================
# Load ML artifacts
# ==================================================
with open("model/model.pkl", "rb") as f:
    model = pickle.load(f)

with open("model/feature_names.pkl", "rb") as f:
    features = pickle.load(f)

features = [f.lower() for f in features]  # normalize once

# ==================================================
# Load disease dataset JSON (single source of truth)
# ==================================================
with open("data/disease_dataset.json", "r", encoding="utf-8") as f:
    disease_data = json.load(f)

disease_lookup = {
    item["Disease"].lower(): {
        "prevention": item.get("prevention", []),
        "treatment": item.get("treatment", [])
    }
    for item in disease_data
}

# ==================================================
# Page routes
# ==================================================
@app.route("/")
def landing():
    return send_from_directory("views", "index.html")

@app.route("/home")
def home():
    return send_from_directory("views", "home.html")

@app.route("/features")
def features_page():
    return send_from_directory("views", "features.html")

@app.route("/predict")
def predict_page():
    return send_from_directory("views", "predict.html")

@app.route("/result")
def result_page():
    return send_from_directory("views", "result.html")

@app.route("/explainability")
def explainability_page():
    return send_from_directory("views", "explainability.html")

@app.route("/guidance")
def guidance_page():
    return send_from_directory("views", "guidance.html")

@app.route("/model-info")
def model_page():
    return send_from_directory("views", "model.html")

@app.route("/contact")
def contact_page():
    return send_from_directory("views", "contact.html")

@app.route("/disclaimer")
def disclaimer_page():
    return send_from_directory("views", "disclaimer.html")

# ==================================================
# Helpers
# ==================================================
def normalize(symptom: str) -> str:
    return (
        symptom.lower()
        .strip()
        .replace(" ", "_")
        .replace("-", "_")
    )

# ==================================================
# Prediction API
# ==================================================
@app.route("/api/predict", methods=["POST"])
def api_predict():
    data = request.json or {}
    raw_symptoms = data.get("symptoms", "")

    # Normalize & filter only valid symptoms
    raw = [normalize(s) for s in raw_symptoms.split(",") if s.strip()]
    symptoms = [s for s in raw if s in features]

    # ❌ No valid symptoms
    if len(symptoms) == 0:
        return jsonify({
            "status": "error",
            "message": "None of the entered symptoms are recognized. Please select from suggested symptoms."
        })

    # ❌ Too few symptoms
    if len(symptoms) < 3:
        return jsonify({
            "status": "uncertain",
            "message": "Please provide at least 3 valid symptoms."
        })

    # Build input vector
    input_vector = dict.fromkeys(features, 0)
    for s in symptoms:
        input_vector[s] = 1

    X = pd.DataFrame([input_vector])

    # Predict probabilities
    probs = model.predict_proba(X)[0]

    # Top 3 predictions
    top_indices = np.argsort(probs)[-3:][::-1]
    top_predictions = [
        {
            "disease": model.classes_[i],
            "confidence": round(probs[i] * 100, 2)
        }
        for i in top_indices
    ]

    best = top_predictions[0]

    # ⚠️ Smart uncertainty rule
    if (top_predictions[0]["confidence"] - top_predictions[1]["confidence"]) < 10:
        return jsonify({
            "status": "uncertain",
            "disease": None,
            "top_predictions": top_predictions,
            "message": "Prediction confidence is too close. Please refine symptoms."
        })

    # Lookup disease info
    info = disease_lookup.get(best["disease"].lower(), {})
    prevention = info.get("prevention", [])
    treatment = info.get("treatment", [])

    return jsonify({
        "status": "success",
        "disease": best["disease"],
        "confidence": best["confidence"],
        "top_predictions": top_predictions,
        "prevention": prevention,
        "treatment": treatment
    })
    
# ==================================================
# Explainability API
# ==================================================
@app.route("/api/explainability", methods=["POST"])
def api_explainability():
    data = request.json or {}
    raw_symptoms = data.get("symptoms", "")

    symptoms = [
        normalize(s)
        for s in raw_symptoms.split(",")
        if normalize(s) in features
    ]

    if not symptoms:
        return jsonify({
            "status": "error",
            "message": "No valid symptoms provided for explainability."
        })

    # Build input vector
    input_vector = dict.fromkeys(features, 0)
    for s in symptoms:
        input_vector[s] = 1

    X = pd.DataFrame([input_vector])

    # Predict probabilities
    probs = model.predict_proba(X)[0]
    idx = np.argmax(probs)
    disease = model.classes_[idx]

    # Feature importance filtered to active symptoms
    importances = model.feature_importances_

    contributions = []
    for i, feature in enumerate(features):
        if input_vector[feature] == 1:
            contributions.append({
                "feature": feature.replace("_", " "),
                "importance": round(importances[i], 4)
            })

    # Sort by importance
    contributions = sorted(
        contributions,
        key=lambda x: x["importance"],
        reverse=True
    )[:8]

    return jsonify({
        "status": "success",
        "disease": disease,
        "features": contributions
    })


# ==================================================
# Symptom auto-suggest API
# ==================================================
@app.route("/api/symptoms", methods=["GET"])
def get_symptoms():
    readable = [f.replace("_", " ") for f in features]
    return jsonify(sorted(readable))

# ==================================================
# Contact API
# ==================================================
@app.route("/api/contact", methods=["POST"])
def contact_api():
    data = request.json
    print("📨 Contact message:", data)
    return jsonify({"status": "success"})

# ==================================================
# Run app
# ==================================================
if __name__ == "__main__":
    app.run()

