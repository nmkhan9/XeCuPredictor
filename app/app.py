from flask import Flask, request, render_template, jsonify
import pandas as pd
import numpy as np
import os, json
from joblib import load

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AGE_MIN, AGE_MAX = 0, 30
KM_MIN, KM_MAX = 50, 500_000

# Utils

def parse_number(val):
    if val is None or val.strip() == "":
        raise ValueError("Thiếu dữ liệu")

    val = val.replace(".", "").replace(",", "")
    return float(val)


def validate_input(form):
    errors = {}

    try:
        age = parse_number(form.get('age'))
        if not (AGE_MIN <= age <= AGE_MAX):
            errors["age"] = f"Tuổi xe không hợp lệ !"
    except:
        errors["age"] = "Tuổi xe không hợp lệ !"

    try:
        km = parse_number(form.get('km'))
        if not (KM_MIN <= km <= KM_MAX):
            errors["km"] = f"Số km không hợp lệ !"
    except:
        errors["km"] = "Số km không hợp lệ !"

    if errors:
        return None, None, errors

    return age, km, None

# model
models = {
    "dt": load(os.path.join(BASE_DIR, "model", "dt_best.joblib")),
    "lr": load(os.path.join(BASE_DIR, "model", "lr_best.joblib")),
    "rr": load(os.path.join(BASE_DIR, "model", "rr_best.joblib"))
}

ohe = load(os.path.join(BASE_DIR, "model", "onehot_encoder.pkl"))
scaler = load(os.path.join(BASE_DIR, "model", "scaler.pkl"))

with open(os.path.join(BASE_DIR, "model", "unique_values.json"), 'r', encoding='utf-8') as f:
    unique_values = json.load(f)

categorical_cols = list(ohe.feature_names_in_)
numerical_cols = list(scaler.feature_names_in_)

# Feature Engineering

def feature_engineering(df):
    df["age_group"] = pd.cut(df["age"], bins=[-1,5,10,15,100],
                            labels=["New","Young","Mid","Old"])
    df["km_per_year"] = df["km"] / (df["age"] + 1)
    df["log_age"] = np.log1p(df["age"])
    df["is_imported"] = (df["origin"] == "Nhập Khẩu").astype(object)
    return df


# Preprocess
def preprocess(data):
    df = pd.DataFrame([data])
    df = feature_engineering(df)

    # fill thiếu cột
    for col in numerical_cols:
        if col not in df:
            df[col] = 0

    for col in categorical_cols:
        if col not in df:
            df[col] = "Unknown"

    df_num = df[numerical_cols].astype(float)
    df_cat = df[categorical_cols].astype(str)

    X_num = scaler.transform(df_num)
    X_cat = ohe.transform(df_cat)

    X = pd.concat([
        pd.DataFrame(X_num, columns=numerical_cols),
        pd.DataFrame(X_cat, columns=ohe.get_feature_names_out(categorical_cols))
    ], axis=1)

    return X


# Predict

def predict_models(X, selected_models):
    error_map = {
        "lr": 0.31,
        "rr": 0.31,
        "dt": 0.25
    }

    results = {}

    for m in selected_models:
        pred_log = models[m].predict(X)[0]
        pred = np.exp(pred_log)

        err = error_map[m]

        results[m] = {
            "prediction": round(pred, 2),
            "lower": round(pred * (1 - err), 2),
            "upper": round(pred * (1 + err), 2)
        }

    return results


# Routes
@app.route('/')
def home():
    return render_template('index.html', unique_values=unique_values)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        selected_models = request.form.getlist("models")
        if not selected_models:
            return jsonify({'error': 'Chọn ít nhất 1 model'}), 400

        # validate
        age, km, errors = validate_input(request.form)
        if errors:
            return jsonify({'error': errors}), 400

        # build data
        data = {
            'origin': request.form['origin'],
            'body': request.form['body'],
            'gearbox': request.form['gearbox'],
            'fuel': request.form['fuel'],
            'brand': request.form['brand'],
            'age': age,
            'km': km
        }

        X = preprocess(data)
        results = predict_models(X, selected_models)

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Run

if __name__ == "__main__":
    app.run(debug=True)