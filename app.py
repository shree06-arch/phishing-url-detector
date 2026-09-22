"""
app.py
A minimal Flask web app that serves a form for checking whether a URL
looks like phishing, using the model trained by src/train.py.

Run with:
    python app.py
Then open http://localhost:5000
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from flask import Flask, render_template, request

from predict import load_model, predict_url

app = Flask(__name__)

MODEL, FEATURE_NAMES = None, None


def get_model():
    global MODEL, FEATURE_NAMES
    if MODEL is None:
        MODEL, FEATURE_NAMES = load_model()
    return MODEL, FEATURE_NAMES


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    url_value = ""

    if request.method == "POST":
        url_value = request.form.get("url", "").strip()
        if not url_value:
            error = "Please enter a URL."
        else:
            try:
                model, feature_names = get_model()
                result = predict_url(url_value, model, feature_names)
            except FileNotFoundError:
                error = "Model not found. Run 'python src/train.py' first."

    return render_template("index.html", result=result, error=error, url_value=url_value)


@app.route("/api/predict", methods=["POST"])
def api_predict():
    from flask import jsonify

    data = request.get_json(silent=True) or {}
    url_value = data.get("url", "").strip()
    if not url_value:
        return jsonify({"error": "Missing 'url' field."}), 400
    try:
        model, feature_names = get_model()
        result = predict_url(url_value, model, feature_names)
        return jsonify(result)
    except FileNotFoundError:
        return jsonify({"error": "Model not found. Run 'python src/train.py' first."}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
