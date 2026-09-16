import pandas as pd
import re

def detect_text_issues(df: pd.DataFrame) -> dict:
    """
    Detect text formatting issues (leading/trailing whitespace, inconsistent case variants).
    Returns dict col -> issue info.
    """
    report = {}
    str_cols = df.select_dtypes(include=['object', 'string']).columns

    for col in str_cols:
        whitespace_count = 0
        casing_variants = {}
        
        non_null_series = df[col].dropna().astype(str)
        for val in non_null_series:
            if val != val.strip() or "  " in val:
                whitespace_count += 1
            
            cleaned_val = val.strip().lower()
            if cleaned_val not in casing_variants:
                casing_variants[cleaned_val] = set()
            casing_variants[cleaned_val].add(val)
        
        # Check if there are multiple casing/formatting representations for the same string
        inconsistent_groups = {k: list(v) for k, v in casing_variants.items() if len(v) > 1}

        if whitespace_count > 0 or len(inconsistent_groups) > 0:
            report[col] = {
                'whitespace_issues': whitespace_count,
                'inconsistent_category_groups': len(inconsistent_groups),
                'examples': inconsistent_groups
            }

    return report

def clean_text_formatting(df: pd.DataFrame, trim_whitespace: bool = True, normalize_case: str = 'none') -> tuple[pd.DataFrame, list[str]]:
    """
    Clean text formatting issues in string columns.
    
    normalize_case options: 'none', 'title', 'lower', 'upper'
    """
    df_clean = df.copy()
    logs = []
    
    str_cols = df_clean.select_dtypes(include=['object', 'string']).columns

    for col in str_cols:
        trimmed_count = 0
        cased_count = 0

        def process_text(val):
            nonlocal trimmed_count, cased_count
            if pd.isna(val) or not isinstance(val, str):
                return val
            
            new_val = val
            if trim_whitespace:
                stripped = re.sub(r'\s+', ' ', val.strip())
                if stripped != val:
                    trimmed_count += 1
                new_val = stripped

            if normalize_case == 'title':
                cased = new_val.title()
                if cased != new_val:
                    cased_count += 1
                new_val = cased
            elif normalize_case == 'lower':
                cased = new_val.lower()
                if cased != new_val:
                    cased_count += 1
                new_val = cased
            elif normalize_case == 'upper':
                cased = new_val.upper()
                if cased != new_val:
                    cased_count += 1
                new_val = cased

            return new_val

        df_clean[col] = df_clean[col].apply(process_text)

        if trimmed_count > 0:
            logs.append(f"Trimmed leading/trailing and extra whitespace from {trimmed_count} cell(s) in column '{col}'.")
        if cased_count > 0:
            logs.append(f"Normalized case ({normalize_case}) for {cased_count} cell(s) in column '{col}'.")

    return df_clean, logs
