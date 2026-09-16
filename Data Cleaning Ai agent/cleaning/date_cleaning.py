import pandas as pd

def detect_date_columns(df: pd.DataFrame) -> dict:
    """
    Detect text/object columns that represent dates with potential formatting inconsistencies.
    Returns dict: col -> date_issue_info
    """
    report = {}
    str_cols = df.select_dtypes(include=['object', 'string']).columns

    for col in str_cols:
        # Exclude columns that are clearly not date columns by name or unique values
        col_lower = col.lower()
        if not any(k in col_lower for k in ['date', 'time', 'dt', 'day', 'dob', 'join', 'created', 'updated']):
            # Check sample values to see if they look like dates
            sample = df[col].dropna().head(10).astype(str)
            is_date_like = False
            for val in sample:
                if any(char in val for char in ['/', '-']) and any(c.isdigit() for c in val):
                    is_date_like = True
                    break
            if not is_date_like:
                continue

        # Try parsing dates with pd.to_datetime
        non_na = df[col].dropna().astype(str)
        if len(non_na) == 0:
            continue

        parsed = pd.to_datetime(non_na, errors='coerce', format='mixed')
        valid_count = parsed.notna().sum()
        
        # If majority of non-null values parse as dates
        if valid_count / len(non_na) >= 0.5:
            # Check for multiple raw format string variations
            formats = set()
            for raw_val in non_na:
                if '/' in raw_val:
                    formats.add('Slash separator (e.g. MM/DD/YYYY)')
                elif '-' in raw_val:
                    formats.add('Hyphen separator (e.g. YYYY-MM-DD)')
            
            report[col] = {
                'valid_date_count': int(valid_count),
                'total_non_null': len(non_na),
                'detected_formats': list(formats)
            }

    return report

def clean_dates(df: pd.DataFrame, standardize: bool = True) -> tuple[pd.DataFrame, list[str]]:
    """
    Standardize detected date columns into YYYY-MM-DD string format.
    """
    df_clean = df.copy()
    logs = []

    if not standardize:
        return df_clean, logs

    date_cols_report = detect_date_columns(df_clean)

    for col in date_cols_report.keys():
        non_na_count = df_clean[col].dropna().count()
        parsed_dates = pd.to_datetime(df_clean[col], errors='coerce', format='mixed')
        
        # Format valid dates as YYYY-MM-DD
        formatted_series = parsed_dates.dt.strftime('%Y-%m-%d')
        
        # Keep original values if date parsing failed for specific cells
        combined_series = df_clean[col].copy()
        for idx in formatted_series.dropna().index:
            combined_series.iloc[idx] = formatted_series.iloc[idx]

        df_clean[col] = combined_series
        converted_count = formatted_series.notna().sum()
        
        logs.append(f"Standardized date column '{col}' ({converted_count}/{non_na_count} valid dates) to YYYY-MM-DD format.")

    return df_clean, logs
