import pandas as pd
import numpy as np

# Common sentinel missing value strings
SENTINEL_MISSING = {
    'na', 'n/a', 'null', 'none', 'unknown', 'nan', '', '-', '?', 'missing'
}

def is_cell_missing(val):
    """Check if an individual cell value is missing or matches a sentinel missing string."""
    if pd.isna(val):
        return True
    if isinstance(val, str):
        val_clean = val.strip().lower()
        if val_clean in SENTINEL_MISSING:
            return True
    return False

def detect_missing_values(df: pd.DataFrame) -> dict:
    """
    Detect missing values across all columns including NaN, empty strings, and sentinel values.
    Returns a dictionary of column -> missing count.
    """
    missing_report = {}
    for col in df.columns:
        # Check standard pd.isna OR string matches sentinel missing
        count = 0
        for val in df[col]:
            if is_cell_missing(val):
                count += 1
        missing_report[col] = count
    return missing_report

def clean_missing_values(df: pd.DataFrame, config: dict = None) -> tuple[pd.DataFrame, list[str]]:
    """
    Impute or clean missing values in DataFrame based on config.
    
    config keys:
      - numeric_strategy: 'median' (default), 'mean', 'none'
      - categorical_strategy: 'mode' (default), 'unknown', 'none'
      - drop_threshold: optional float (0.0 to 1.0)
    
    Returns (cleaned_df, audit_log_entries)
    """
    df_clean = df.copy()
    logs = []

    numeric_strategy = config.get('numeric_strategy', 'median') if config else 'median'
    categorical_strategy = config.get('categorical_strategy', 'mode') if config else 'mode'

    # Standardize sentinel missing values to np.nan first
    for col in df_clean.columns:
        df_clean[col] = df_clean[col].apply(lambda x: np.nan if is_cell_missing(x) else x)

    for col in df_clean.columns:
        missing_count = df_clean[col].isna().sum()
        if missing_count == 0:
            continue

        # Check if numeric
        # Attempt coercion to see if numeric
        converted_series = pd.to_numeric(df_clean[col], errors='coerce')
        non_na_converted = converted_series.dropna()
        
        is_numeric_col = len(non_na_converted) > 0 and (len(non_na_converted) / max(1, len(df_clean[col].dropna())) >= 0.5)

        if is_numeric_col:
            df_clean[col] = converted_series
            if numeric_strategy == 'median':
                median_val = df_clean[col].median()
                if pd.isna(median_val):
                    median_val = 0
                df_clean[col] = df_clean[col].fillna(median_val)
                logs.append(f"Filled {missing_count} missing values in numerical column '{col}' using median = {median_val}.")
            elif numeric_strategy == 'mean':
                mean_val = round(df_clean[col].mean(), 2)
                if pd.isna(mean_val):
                    mean_val = 0
                df_clean[col] = df_clean[col].fillna(mean_val)
                logs.append(f"Filled {missing_count} missing values in numerical column '{col}' using mean = {mean_val}.")
            elif numeric_strategy == 'none':
                logs.append(f"Retained {missing_count} missing values in numerical column '{col}' (user selected 'Do not modify').")
        else:
            # Categorical column
            if categorical_strategy == 'mode':
                mode_series = df_clean[col].mode()
                mode_val = mode_series.iloc[0] if not mode_series.empty else "Unknown"
                df_clean[col] = df_clean[col].fillna(mode_val)
                logs.append(f"Filled {missing_count} missing values in categorical column '{col}' using mode = '{mode_val}'.")
            elif categorical_strategy == 'unknown':
                df_clean[col] = df_clean[col].fillna("Unknown")
                logs.append(f"Filled {missing_count} missing values in categorical column '{col}' with label 'Unknown'.")
            elif categorical_strategy == 'none':
                logs.append(f"Retained {missing_count} missing values in categorical column '{col}' (user selected 'Do not modify').")

    return df_clean, logs
