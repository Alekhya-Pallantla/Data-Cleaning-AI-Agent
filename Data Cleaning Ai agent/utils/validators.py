import pandas as pd

def validate_dataset_structure(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Validate dataset structure for minimum usability.
    Returns (is_valid, error_message).
    """
    if df is None:
        return False, "Dataset could not be loaded."
    
    if df.empty:
        return False, "Uploaded dataset is completely empty."
    
    if len(df.columns) == 0:
        return False, "Dataset contains no columns."
        
    if len(df) == 0:
        return False, "Dataset contains no rows of data."
        
    return True, "Dataset structure is valid."
