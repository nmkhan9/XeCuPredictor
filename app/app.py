from flask import Flask, request, render_template, jsonify
import pandas as pd
import numpy as np
import os
import json
from joblib import load

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

gbm_model = load(os.path.join(BASE_DIR, "model", "gradient_boosting_best.joblib"))
ohe = load(os.path.join(BASE_DIR, "model", "onehot_encoder.pkl"))
scaler = load(os.path.join(BASE_DIR, "model", "scaler.pkl"))

with open(os.path.join(BASE_DIR, "model", "unique_values.json"), 'r', encoding='utf-8') as f:
    unique_values = json.load(f)

categorical_cols = list(ohe.feature_names_in_)
numerical_cols = list(scaler.feature_names_in_)

def feature_engineering(df, km_col="km", age_col="age"):
    df = df.copy()
    
    df["km_group"] = pd.cut(
        df[km_col],
        bins=[0, 50000, 100000, 150000, 300000, 1e8],
        labels=["very_low", "low", "medium", "high", "very_high"]
    )
    
    def age_risk(age):
        if age <= 3: return "new"
        elif age <= 7: return "mid"
        elif age <= 15: return "old"
        else: return "very_old"
    
    df["age_risk"] = df[age_col].apply(age_risk)
    
    return df

@app.route('/')
def home():
    return render_template('index.html', unique_values=unique_values)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        age = float(request.form['age'])
        km = float(request.form['km'])
        data = {
            'origin': request.form['origin'],
            'body': request.form['body'],
            'fuel': request.form['fuel'],
            'brand': request.form['brand'],
            'age': age,
            'km': km
        }
        input_df = pd.DataFrame([data])
        input_df = feature_engineering(input_df)

        input_df = input_df[numerical_cols + categorical_cols]
        
        encoded_categorical = ohe.transform(input_df[categorical_cols])
        encoded_categorical_df = pd.DataFrame(
            encoded_categorical,
            columns=ohe.get_feature_names_out(categorical_cols),
            index=input_df.index
        )
        
        scaled_numerical = scaler.transform(input_df[numerical_cols])
        scaled_numerical_df = pd.DataFrame(
            scaled_numerical,
            columns=numerical_cols,
            index=input_df.index
        )
        
        processed_data = pd.concat([scaled_numerical_df, encoded_categorical_df], axis=1)
        gbm_pred = gbm_model.predict(processed_data)[0]
        prediction = np.expm1(gbm_pred)
        
        return jsonify({'prediction': round(prediction, 2)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)