# 📘 Used Car Price Prediction in Vietnam

## 🚗 Introduction
This project builds a machine learning model to predict **used car prices in Vietnam** using real-world data collected from multiple online platforms.  
The problem has significant practical value, helping buyers, sellers, and e-commerce platforms estimate fair and accurate market prices.

---

## 📥 1. Data Collection (Web Scraping)

Data was collected manually and automatically from three major car-selling websites in Vietnam:

- **oto.com.vn**
- **bonbanh.com**
- **chotot.com**

After scraping, the raw datasets were processed:

- ✔ Standardized structure  
- ✔ Removed special characters  
- ✔ Normalized units (price, mileage, model year, fuel type, body type…)  
- ✔ Unified brand names, car origins, and body categories  

All raw data was uploaded and stored in **Google Cloud Storage**.

---

## 🧹 2. Data Cleaning

Each dataset was cleaned individually, including:

- Removing duplicated records  
- Standardizing key fields: `km`, `price`, `brand`, `fuel`, `body`, `origin`  
- Handling missing values  
- Converting strings to numeric  
- Removing outliers  
- Merging the three datasets into a single cleaned DataFrame: **`df_unique`**

---

## 📊 3. Exploratory Data Analysis (EDA)

After combining the datasets, several analyses were performed:

- Statistical summary  
- Distribution of mileage, car age, and price  
- Correlation between variables  
- Outlier detection and removal  
- Price analysis by brand, fuel type, origin, and body type  

The cleaned dataset was then prepared for model training.

---

## ⚙️ 4. Feature Engineering

Additional features were created to improve model performance:

### ➤ Mileage grouping  
### ➤ Age grouping  
### ➤ Simple binary flags  
- High mileage flag  
- Old car flag  

**No feature related to `price` was used to avoid data leakage.**

---

## 🤖 5. Model Training

Five machine learning models were trained and compared.

### **Linear Models**

| Model              | R2 Train   | R2 Test   | RMSE Train       | RMSE Test        |
|-------------------|------------|-----------|------------------|------------------|
| Linear Regression | 0.471449   | 0.463941  | 1.9969e+08       | 2.0886e+08       |
| Ridge Regression  | 0.471030   | 0.464131  | 1.9977e+08       | 2.0882e+08       |
| Lasso Regression  | 0.471449   | 0.463941  | 1.9969e+08       | 2.0886e+08       |

### **Tree-based Models**

| Model             | R2 Train  | R2 Test  | RMSE Train       | RMSE Test        |
|-------------------|-----------|----------|------------------|------------------|
| GradientBoosting  | ⭐ 0.8021 | ⭐ 0.6442 | 1.2218e+08       | 1.7016e+08       |
| RandomForest      | 0.6728    | 0.5958   | 1.5709e+08       | 1.8134e+08       |

---

## 🏆 6. Best Model Selection

The **GradientBoostingRegressor** was chosen because:

- ✔ Strong overall performance  
- ✔ High model stability  
- ✔ Excellent handling of nonlinear relationships  
- ✔ Well-balanced bias–variance trade-off  

The final model was:

- Trained on the full dataset  
- Saved as **`gradient_boosting_model.joblib`**  
- Used in the Flask web application

---

## 🌐 7. Flask Web Deployment

The Flask application allows users to input car details:

- Brand  
- Body type  
- Fuel type  
- Mileage  
- Car age  
- Origin  
- ...

The backend performs:

1. Preprocessing using the saved pipeline  
2. One-hot encoding and normalization  
3. Model prediction  
4. Returning the estimated car price to the UI

---

## 🎯 8. Conclusion

The project successfully:

- ✔ Crawled real-world data from 3 major automotive websites  
- ✔ Cleaned, standardized, and merged datasets  
- ✔ Engineered meaningful additional features  
- ✔ Trained and evaluated 5 machine learning models  
- ✔ Selected Gradient Boosting as the final model  
- ✔ Deployed a working Flask web app for used car price prediction  

### Future Improvements

- Dynamic price recommendation  
- Market trend analysis by region  
- Adding more car attributes (color, number of owners, maintenance history, etc.)  

---