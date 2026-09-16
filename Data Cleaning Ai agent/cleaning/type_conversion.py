import pandas as pd
import numpy as np

def detect_type_and_domain_issues(df: pd.DataFrame) -> dict:
    """
    Detect columns stored as strings that look like numeric data,
    and detect logically invalid values (e.g., negative Age, Rating out of 1-5 range).
    """
    report = {
        'numeric_as_text': {},
        'invalid_values': {}
    }

    for col in df.columns:
        col_lower = col.lower()
        
        # 1. Check for numeric data stored as strings
        if df[col].dtype == 'object' or df[col].dtype == 'string':
            non_null = df[col].dropna().astype(str)
            if len(non_null) > 0:
                converted = pd.to_numeric(non_null.str.strip(), errors='coerce')
                numeric_ratio = converted.notna().sum() / len(non_null)
                if 0.5 <= numeric_ratio < 1.0 or (numeric_ratio == 1.0 and df[col].dtype == 'object'):
                    report['numeric_as_text'][col] = {
                        'convertible_count': int(converted.notna().sum()),
                        'total': len(non_null)
                    }

        # 2. Check for domain invalid values
        # Age column validation
        if 'age' in col_lower:
            numeric_vals = pd.to_numeric(df[col], errors='coerce')
            invalid_age = numeric_vals[(numeric_vals < 0) | (numeric_vals > 120)]
            if len(invalid_age) > 0:
                report['invalid_values'][col] = {
                    'rule': 'Age must be between 0 and 120',
                    'invalid_count': len(invalid_age),
                    'invalid_examples': list(invalid_age.head(5).values)
                }

        # Rating column validation
        elif 'rating' in col_lower or 'score' in col_lower:
            numeric_vals = pd.to_numeric(df[col], errors='coerce')
            invalid_rating = numeric_vals[(numeric_vals < 0) | (numeric_vals > 10)]
            if len(invalid_rating) > 0:
                report['invalid_values'][col] = {
                    'rule': 'Rating must be between 0.0 and 10.0',
                    'invalid_count': len(invalid_rating),
                    'invalid_examples': list(invalid_rating.head(5).values)
                }

    return report

def clean_type_and_invalid_values(df: pd.DataFrame, convert_numeric_text: bool = True, fix_invalid: bool = True) -> tuple[pd.DataFrame, list[str]]:
    """
    Safely convert numeric string columns and handle domain-invalid values.
    """
    df_clean = df.copy()
    logs = []
    
    issues = detect_type_and_domain_issues(df_clean)

    # 1. Convert numeric strings
    if convert_numeric_text:
        for col in issues['numeric_as_text'].keys():
            converted = pd.to_numeric(df_clean[col].astype(str).str.strip(), errors='coerce')
            # Replace converted numeric values while preserving non-convertible if any
            mask = converted.notna()
            if mask.sum() > 0:
                df_clean.loc[mask, col] = converted[mask]
                logs.append(f"Safely converted {mask.sum()} numeric string value(s) in column '{col}' to numeric data type.")

    # 2. Fix domain invalid values (e.g. set Age < 0 or Age > 120 to NaN for imputation)
    if fix_invalid:
        for col, info in issues['invalid_values'].items():
            col_lower = col.lower()
            if 'age' in col_lower:
                numeric_vals = pd.to_numeric(df_clean[col], errors='coerce')
                invalid_mask = (numeric_vals < 0) | (numeric_vals > 120)
                invalid_count = invalid_mask.sum()
                if invalid_count > 0:
                    df_clean.loc[invalid_mask, col] = np.nan
                    logs.append(f"Flagged and set {invalid_count} invalid Age value(s) (e.g., negative or > 120) to NaN for safe imputation.")
            elif 'rating' in col_lower or 'score' in col_lower:
                numeric_vals = pd.to_numeric(df_clean[col], errors='coerce')
                invalid_mask = (numeric_vals < 0) | (numeric_vals > 10)
                invalid_count = invalid_mask.sum()
                if invalid_count > 0:
                    df_clean.loc[invalid_mask, col] = np.nan
                    logs.append(f"Flagged and set {invalid_count} invalid Rating value(s) (outside 0-10 range) to NaN for safe imputation.")

    return df_clean, logs
