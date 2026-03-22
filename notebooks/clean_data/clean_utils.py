import re
import pandas as pd

def remove_outliers_iqr(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    df_filtered = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)].copy()
    return df_filtered


def clean_fuel(x):
    if pd.isna(x):
        return "Khác"
    
    x = str(x).lower().strip()

    if x in ["", "-"]:
        return "Khác"

    if "xăng" in x:
        return "Xăng"
    if "dầu" in x:
        return "Dầu"
    if "điện" in x:
        return "Điện"
    if "hybrid" in x:
        return "Hybrid"

    return "Khác"

