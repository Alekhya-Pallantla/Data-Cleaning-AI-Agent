import pandas as pd
import numpy as np

def detect_outliers_iqr(series: pd.Series) -> tuple[pd.Series, float, float]:
    """
    Detect outliers in a numeric Series using IQR method.
    Returns (boolean_mask, lower_bound, upper_bound).
    """
    numeric_series = pd.to_numeric(series, errors='coerce').dropna()
    if len(numeric_series) < 4:
        return pd.Series(False, index=series.index), 0.0, 0.0

    q1 = numeric_series.quantile(0.25)
    q3 = numeric_series.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    is_outlier = series.apply(
        lambda x: False if pd.isna(x) or not isinstance(x, (int, float, np.number))
        else (x < lower_bound or x > upper_bound)
    )
    return is_outlier, lower_bound, upper_bound

def detect_all_outliers(df: pd.DataFrame) -> dict:
    """
    Detect numerical outliers across all numeric columns in DataFrame.
    Returns dict: col -> {count: int, lower_bound: float, upper_bound: float}
    """
    outlier_report = {}
    numeric_cols = df.select_dtypes(include=[np.number]).columns

    for col in numeric_cols:
        is_outlier, lb, ub = detect_outliers_iqr(df[col])
        count = int(is_outlier.sum())
        if count > 0:
            outlier_report[col] = {
                'count': count,
                'lower_bound': round(float(lb), 2),
                'upper_bound': round(float(ub), 2)
            }
    return outlier_report

def clean_outliers(df: pd.DataFrame, strategy: str = 'detect_only') -> tuple[pd.DataFrame, list[str]]:
    """
    Handle outliers based on strategy:
      - 'detect_only': Log and retain outliers (default & conservative)
      - 'cap': Cap/Winsorize outliers to lower/upper bound
      - 'remove': Drop rows containing numerical outliers
    """
    df_clean = df.copy()
    logs = []
    
    numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
    total_outliers_found = 0

    for col in numeric_cols:
        is_outlier, lb, ub = detect_outliers_iqr(df_clean[col])
        count = int(is_outlier.sum())
        if count > 0:
            total_outliers_found += count
            if strategy == 'detect_only':
                logs.append(f"Detected {count} potential outlier(s) in column '{col}' (bounds: [{lb:.2f}, {ub:.2f}]). Retained as per conservative rule.")
            elif strategy == 'cap':
                df_clean[col] = df_clean[col].apply(
                    lambda x: x if pd.isna(x) or not isinstance(x, (int, float, np.number))
                    else (lb if x < lb else (ub if x > ub else x))
                )
                logs.append(f"Capped {count} outlier(s) in column '{col}' to range [{lb:.2f}, {ub:.2f}].")
            elif strategy == 'remove':
                df_clean = df_clean[~is_outlier].reset_index(drop=True)
                logs.append(f"Removed {count} row(s) containing outliers in column '{col}'.")

    if total_outliers_found == 0:
        logs.append("No numerical outliers detected.")

    return df_clean, logs
