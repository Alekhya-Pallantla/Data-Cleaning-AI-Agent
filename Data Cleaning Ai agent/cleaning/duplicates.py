import pandas as pd

def detect_duplicates(df: pd.DataFrame) -> int:
    """
    Detect full row duplicates in DataFrame.
    """
    return int(df.duplicated().sum())

def clean_duplicates(df: pd.DataFrame, remove: bool = True) -> tuple[pd.DataFrame, list[str]]:
    """
    Remove duplicate rows if remove is True.
    Returns (cleaned_df, audit_log_entries)
    """
    df_clean = df.copy()
    logs = []
    
    dup_count = int(df_clean.duplicated().sum())
    if dup_count > 0:
        if remove:
            df_clean = df_clean.drop_duplicates(keep='first').reset_index(drop=True)
            logs.append(f"Removed {dup_count} duplicate row(s) (kept first occurrence).")
        else:
            logs.append(f"Detected {dup_count} duplicate row(s) (retained per user configuration).")
    else:
        logs.append("No duplicate rows found.")
        
    return df_clean, logs
