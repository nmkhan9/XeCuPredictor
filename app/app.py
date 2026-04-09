from flask import Flask, request, render_template, jsonify
import pandas as pd
import numpy as np
import os
import json
from joblib import load

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ===== LOAD MODEL =====
svr_model = load(os.path.join(BASE_DIR, "model", "svr_best.joblib"))
dt_model = load(os.path.join(BASE_DIR, "model", "dt_best.joblib"))
lr_model = load(os.path.join(BASE_DIR, "model", "lr_best.joblib"))
rr_model = load(os.path.join(BASE_DIR, "model", "rr_best.joblib"))

# ===== LOAD PREPROCESS =====
ohe = load(os.path.join(BASE_DIR, "model", "onehot_encoder.pkl"))
scaler = load(os.path.join(BASE_DIR, "model", "scaler.pkl"))

with open(os.path.join(BASE_DIR, "model", "unique_values.json"), 'r', encoding='utf-8') as f:
    unique_values = json.load(f)

categorical_cols = list(ohe.feature_names_in_)
numerical_cols = list(scaler.feature_names_in_)

# ===== FEATURE ENGINEERING =====
def feature_engineering(df):
    df = df.copy()

    df["age_group"] = pd.cut(
        df["age"],
        bins=[-1, 5, 10, 15, 100],
        labels=["New", "Young", "Mid", "Old"]
    )

    df["km_per_year"] = df["km"] / (df["age"] + 1)
    df["log_age"] = np.log1p(df["age"])

    # ⚠️ FIX: không dùng value_counts() (vì input chỉ có 1 dòng)
    df["body_group"] = df["body"]
    df["brand_group"] = df["brand"]

    df["is_imported"] = (df["origin"] == "Nhập Khẩu").astype(object)
    df["imported_age"] = df["is_imported"].astype(str) + "_" + df["age_group"].astype(str)

    return df

# ===== HOME =====
@app.route('/')
def home():
    return render_template('index.html', unique_values=unique_values)

# ===== PREDICT =====
@app.route('/predict', methods=['POST'])
def predict():
    try:
        age = float(request.form['age'])
        km = float(request.form['km'])

        selected_models = request.form.getlist("models")

        if not selected_models:
            return jsonify({'error': 'Vui lòng chọn ít nhất 1 mô hình'}), 400

        # ===== INPUT =====
        data = {
            'origin': request.form['origin'],
            'body': request.form['body'],
            'fuel': request.form['fuel'],
            'brand': request.form['brand'],
            'gearbox': request.form['gearbox'],
            'age': age,
            'km': km
        }

        input_df = pd.DataFrame([data])

        # ===== FEATURE ENGINEERING =====
        input_df = feature_engineering(input_df)

        # ===== FIX LỖI THIẾU CỘT =====
        for col in numerical_cols:
            if col not in input_df.columns:
                input_df[col] = 0

        for col in categorical_cols:
            if col not in input_df.columns:
                input_df[col] = "Unknown"

        # reorder đúng thứ tự
        input_df = input_df[numerical_cols + categorical_cols]

        # ===== ENCODE =====
        encoded_categorical = ohe.transform(input_df[categorical_cols])
        encoded_categorical_df = pd.DataFrame(
            encoded_categorical,
            columns=ohe.get_feature_names_out(categorical_cols),
            index=input_df.index
        )

        # ===== SCALE =====
        scaled_numerical = scaler.transform(input_df[numerical_cols])
        scaled_numerical_df = pd.DataFrame(
            scaled_numerical,
            columns=numerical_cols,
            index=input_df.index
        )

        processed_data = pd.concat([scaled_numerical_df, encoded_categorical_df], axis=1)

        # ===== MODEL MAP =====
        model_map = {
            "svr": svr_model,
            "dt": dt_model,
            "lr": lr_model,
            "rr": rr_model
        }

        results = {}

        # ===== PREDICT MULTI MODEL =====
        for m in selected_models:
            pred = model_map[m].predict(processed_data)[0]

            # nếu bạn train log(price)
            pred = np.expm1(pred)

            results[m] = {
                "lower": round(pred * 0.6, 2),
                "upper": round(pred * 1.4, 2)
            }

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ===== RUN =====
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)