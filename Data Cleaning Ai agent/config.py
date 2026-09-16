import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Directory settings
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
OUTPUT_FOLDER = os.path.join(BASE_DIR, 'outputs')
REPORT_FOLDER = os.path.join(BASE_DIR, 'reports')
SAMPLE_DATA_FOLDER = os.path.join(BASE_DIR, 'sample_data')

# Security & Upload settings
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-data-cleaning-agent')

# Ensure directories exist
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, REPORT_FOLDER, SAMPLE_DATA_FOLDER]:
    os.makedirs(folder, exist_ok=True)
