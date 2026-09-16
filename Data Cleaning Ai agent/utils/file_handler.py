import os
import pandas as pd
from werkzeug.utils import secure_filename
import config

def allowed_file(filename: str) -> bool:
    """Check if the uploaded file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Load CSV or Excel file into a Pandas DataFrame using robust encoding handling.
    """
    ext = file_path.rsplit('.', 1)[1].lower()
    
    if ext == 'csv':
        encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
        for encoding in encodings:
            try:
                return pd.read_csv(file_path, encoding=encoding)
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
        raise ValueError(f"Could not parse CSV file '{file_path}' with supported encodings.")
    
    elif ext in ['xlsx', 'xls']:
        try:
            return pd.read_excel(file_path)
        except Exception as e:
            raise ValueError(f"Could not parse Excel file '{file_path}': {str(e)}")
            
    else:
        raise ValueError(f"Unsupported file format '.{ext}'. Allowed formats: .csv, .xlsx, .xls")

def save_cleaned_dataset(df: pd.DataFrame, filename: str) -> str:
    """
    Save cleaned DataFrame to output directory as CSV.
    Returns absolute path of saved file.
    """
    base_name = os.path.splitext(filename)[0]
    out_filename = f"cleaned_{base_name}.csv"
    out_path = os.path.join(config.OUTPUT_FOLDER, out_filename)
    df.to_csv(out_path, index=False)
    return out_path
