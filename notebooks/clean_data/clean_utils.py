import re
import pandas as pd

def clean_name(text):
    if not isinstance(text, str):
        return None
    
    text = re.sub(r"^\s*Xe\s+", "", text, flags=re.IGNORECASE)
    
    text = re.sub(r"[^a-zA-Z0-9À-ỹ\s]", " ", text)
    
    text = re.sub(r"\s+", " ", text)
    
    return text.strip()


def cv_price(price_str):
    if not isinstance(price_str, str):
        return None

    price_str = price_str.strip().lower()
    total = 0

    ty_match = re.search(r'(\d+(\.\d+)?)\s*t[ỷi]', price_str)
    if ty_match:
        ty = float(ty_match.group(1))
        total += int(ty * 1_000_000_000)

    trieu_match = re.search(r'(\d+(\.\d+)?)\s*triệu', price_str)
    if trieu_match:
        trieu = float(trieu_match.group(1))
        total += int(trieu * 1_000_000)

    return total if total > 0 else None

def remove_outliers_iqr(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    df_filtered = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)].copy()
    return df_filtered

def clean_km(df, col_name):
    df[col_name] = (
        df[col_name]
        .astype(str)
        .str.replace("Km", "", case=False, regex=False)
        .str.replace(" ", "")
        .str.replace(",", "")
        .replace(["None", "nan", "NaN", ""], None)
        .astype(float)
    )
    return df


def clean_fuel(x):
    if pd.isna(x) or x == "-":
        return "Khác"
    if "Xăng" in x:
        return "Xăng"
    if "Dầu" in x:
        return "Dầu"
    if "Điện" in x:
        return "Điện"
    if "Hybrid" in x:
        return "Hybrid"
    return None

