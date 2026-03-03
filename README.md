# 📘 Used Car Price Prediction in Vietnam

## 🚗 Introduction

This project develops a **machine learning model** to predict **used car prices in Vietnam** based on real-world data collected from multiple online car marketplaces.

The solution provides practical value by helping:
- Buyers estimate fair market prices before purchasing  
- Sellers price their vehicles competitively  
- Online platforms improve pricing and recommendation systems  

---

## 📥 1. Data Collection (Web Scraping)

Data was collected both manually and automatically from three major car-selling websites in Vietnam:

- **oto.com.vn** – 1,479 records  
- **bonbanh.com** – 9,989 records  
- **chotot.com** – 8,937 records  

After scraping, raw datasets were stored in **Google BigQuery** and processed as follows:

- Standardized data schema  
- Removed special characters  
- Normalized units (price, mileage, model year, fuel type, body type, etc.)  
- Unified brand names, car origins, body types, and fuel categories  

All raw data was also archived in **Google Cloud Storage**.

---

## 🧹 2. Data Cleaning

Each dataset was cleaned independently, including:

- Removing duplicate records  
- Standardizing key fields: `km`, `price`, `brand`, `fuel`, `body`, `origin`  
- Converting string values to numeric format  

The three datasets were then merged into a single DataFrame: **`df_unique`**.

Additional cleaning steps on `df_unique`:
- Unified brand names, origins, body types, and fuel categories  
- Handled missing values  
- Removed outliers  
- Removed remaining duplicates  

After data cleaning and deduplication, the final dataset df_unique contains 11,305 records, representing a wide range of used car segments in the Vietnamese market.

The final cleaned dataset was written back to **Google BigQuery** for analysis and modeling.

---

## 📊 3. Exploratory Data Analysis (EDA)

After merging the datasets, **SQL queries and Python analysis** were used to perform:

- Descriptive statistical analysis  
- Distribution analysis of mileage, car age, and price  
- Distribution analysis by brand, fuel type, and body type  
- Correlation analysis between variables  
- Price analysis by brand, fuel type, origin, body type, and car age  

Key insights were extracted to provide **practical recommendations for buyers and sellers**.

---

## ⚙️ 4. Feature Engineering

To improve model performance, several additional features were created based on domain knowledge and exploratory analysis:

- **Age grouping**: Cars were grouped into four age categories (New, Young, Mid, Old) to capture nonlinear depreciation effects.  
- **Mileage per year**: Average annual mileage was calculated to better represent vehicle usage intensity.  
- **Log transformation**: Log transformation was applied to car age to reduce skewness and stabilize variance.  
- **Brand and body grouping**: Rare car brands and body types were grouped into an "Other" category to reduce sparsity after encoding.  
- **Origin-based features**: A binary flag indicating whether a car is imported was created, along with an interaction feature combining origin and age group.

All features were processed using **One-Hot Encoding** for categorical variables and **Standard Scaling** for numerical variables before model training.

⚠️ **No features related to `price` were used to prevent data leakage.**

---

## 🤖 5. Model Training

Four machine learning models were trained and evaluated:

| Model | R² Train | R² Test | RMSE Train | RMSE Test |
|------|---------|---------|------------|-----------|
| Linear Regression | 0.7748 | 0.7604 | 0.3971 | 0.4076 |
| Ridge Regression | 0.7747 | 0.7605 | 0.3972 | 0.4075 |
| Random Forest | 0.9800 | 0.8353 | 0.1183 | 0.3380 |
| Gradient Boosting | 0.8176 | 0.7978 | 0.3574 | 0.3745 |

### Hyperparameter Tuning (GridSearchCV)

- **Random Forest**
  - Best parameters: `max_depth=20`, `min_samples_split=2`, `n_estimators=300`
  - R² Test: **0.8371**
  - RMSE Test: **0.3361**

- **Gradient Boosting**
  - Best parameters: `learning_rate=0.1`, `max_depth=5`, `n_estimators=300`
  - R² Test: **0.8342**
  - RMSE Test: **0.3391**

---

## 🏆 6. Final Model Selection

The **GradientBoostingRegressor** was selected as the final model due to:

- Strong and stable overall performance  
- Effective handling of nonlinear relationships  
- Lower risk of overfitting compared to Random Forest  
- Better suitability for real-world deployment  

Final model details:
- Trained on the full dataset  
- Saved as **`gradient_boosting_model.joblib`**  
- Used in the Flask web application  

---

## 🌐 7. Flask Web Deployment

A Flask web application was developed to allow users to input:

- Car brand  
- Body type  
- Fuel type  
- Mileage  
- Car age  
- Origin  

Backend workflow:
1. Data preprocessing using the saved pipeline  
2. One-hot encoding and feature scaling  
3. Price range prediction using the trained model  
4. Returning the estimated price to the user interface  

---

## 🎯 8. Conclusion

This project successfully:
- Collected real-world data from three major car-selling platforms  
- Cleaned, standardized, and merged multiple datasets  
- Engineered meaningful features based on domain knowledge  
- Trained and evaluated multiple machine learning models  
- Selected Gradient Boosting as the final model  
- Deployed a functional Flask web application for used car price prediction  
