import os
import shutil
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.utils import secure_filename

import config
from utils.file_handler import allowed_file, load_dataset, save_cleaned_dataset
from utils.validators import validate_dataset_structure
from utils.report_generator import generate_txt_report

from agents.analyzer_agent import AnalyzerAgent
from agents.cleaning_agent import CleaningAgent
from agents.validation_agent import ValidationAgent
from agents.explanation_agent import ExplanationAgent

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Store in-memory active data for session context
# Keyed by filename to support concurrent active sessions
SESSION_CACHE = {}

@app.route('/')
def index():
    """Home / Upload Page (Step 1)"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle raw dataset upload."""
    if 'dataset' not in request.files:
        flash('No file uploaded.', 'danger')
        return redirect(url_for('index'))
    
    file = request.files['dataset']
    if file.filename == '':
        flash('No file selected.', 'warning')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            df = load_dataset(file_path)
            is_valid, err_msg = validate_dataset_structure(df)
            if not is_valid:
                flash(f"Invalid dataset: {err_msg}", 'danger')
                return redirect(url_for('index'))

            session['filename'] = filename
            session['filepath'] = file_path
            flash(f"Successfully uploaded dataset: {filename}", 'success')
            return redirect(url_for('analyze'))
        except Exception as e:
            flash(f"Error reading file: {str(e)}", 'danger')
            return redirect(url_for('index'))
    else:
        flash('Invalid file format. Allowed formats: .csv, .xlsx, .xls', 'danger')
        return redirect(url_for('index'))

@app.route('/sample', methods=['POST'])
def load_sample():
    """Load pre-built messy sample dataset for quick demonstration."""
    sample_src = os.path.join(config.SAMPLE_DATA_FOLDER, 'messy_dataset.csv')
    sample_dest_name = 'sample_messy_dataset.csv'
    sample_dest_path = os.path.join(app.config['UPLOAD_FOLDER'], sample_dest_name)

    shutil.copy(sample_src, sample_dest_path)
    session['filename'] = sample_dest_name
    session['filepath'] = sample_dest_path

    flash('Loaded pre-configured messy sample dataset successfully!', 'info')
    return redirect(url_for('analyze'))

@app.route('/analyze')
def analyze():
    """Dataset Quality Inspection Dashboard (Step 2)"""
    filename = session.get('filename')
    filepath = session.get('filepath')

    if not filename or not filepath or not os.path.exists(filepath):
        flash('Please upload a dataset first.', 'warning')
        return redirect(url_for('index'))

    try:
        df = load_dataset(filepath)
        analyzer = AnalyzerAgent(df)
        report = analyzer.analyze()

        # Cache analysis report in SESSION_CACHE
        SESSION_CACHE[filename] = {
            'df_raw': df,
            'analysis': report
        }

        # Generate HTML table preview for first 15 rows
        preview_html = df.head(15).to_html(
            classes='table table-dark table-hover table-striped mb-0 text-nowrap',
            index=False,
            na_rep='NaN'
        )

        return render_template('analysis.html', filename=filename, report=report, preview_html=preview_html)
    except Exception as e:
        flash(f"Error analyzing dataset: {str(e)}", 'danger')
        return redirect(url_for('index'))

@app.route('/configure')
def configure():
    """Cleaning Configuration Selection Matrix (Step 3)"""
    filename = session.get('filename')
    if not filename or filename not in SESSION_CACHE:
        flash('Please analyze dataset first.', 'warning')
        return redirect(url_for('index'))

    return render_template('configure.html', filename=filename)

@app.route('/clean', methods=['POST'])
def clean_dataset():
    """Execute Data Cleaning Pipeline (Step 4 Processing)"""
    filename = session.get('filename')
    filepath = session.get('filepath')

    if not filename or filename not in SESSION_CACHE:
        flash('Session expired or dataset missing.', 'warning')
        return redirect(url_for('index'))

    cache = SESSION_CACHE[filename]
    df_raw = cache['df_raw']
    analysis_report = cache['analysis']

    # Extract user strategy choices from form
    cleaning_config = {
        'numeric_missing_strategy': request.form.get('numeric_missing_strategy', 'median'),
        'categorical_missing_strategy': request.form.get('categorical_missing_strategy', 'mode'),
        'outlier_strategy': request.form.get('outlier_strategy', 'detect_only'),
        'remove_duplicates': 'remove_duplicates' in request.form,
        'trim_whitespace': 'trim_whitespace' in request.form,
        'standardize_dates': 'standardize_dates' in request.form,
        'convert_numeric_strings': 'convert_numeric_strings' in request.form,
        'fix_invalid_values': 'convert_numeric_strings' in request.form,
        'normalize_case': 'none'
    }

    try:
        # 1. Cleaning Agent
        cleaning_agent = CleaningAgent(df_raw, config=cleaning_config)
        df_cleaned, logs = cleaning_agent.execute()

        # 2. Validation Agent
        validation_agent = ValidationAgent(df_raw, df_cleaned)
        validation_stats = validation_agent.validate()

        # 3. Explanation Agent
        explanation_agent = ExplanationAgent(analysis_report, validation_stats, logs)
        ai_explanation = explanation_agent.generate_explanation()

        # 4. Save cleaned dataset CSV & TXT report
        cleaned_path = save_cleaned_dataset(df_cleaned, filename)
        report_path = generate_txt_report(
            filename,
            validation_stats['before'],
            validation_stats['after'],
            {
                'missing_by_column': analysis_report['missing_by_column'],
                'outliers_by_column': analysis_report['outliers_by_column']
            },
            logs,
            ai_explanation
        )

        # Update cache with cleaned dataset and results
        cache['df_cleaned'] = df_cleaned
        cache['logs'] = logs
        cache['validation'] = validation_stats
        cache['ai_explanation'] = ai_explanation
        cache['cleaned_path'] = cleaned_path
        cache['report_path'] = report_path

        flash('Data cleaning completed successfully!', 'success')
        return redirect(url_for('results'))
    except Exception as e:
        flash(f"Error during data cleaning execution: {str(e)}", 'danger')
        return redirect(url_for('configure'))

@app.route('/results')
def results():
    """Results & Comparison Dashboard (Step 4 View)"""
    filename = session.get('filename')
    if not filename or filename not in SESSION_CACHE or 'df_cleaned' not in SESSION_CACHE[filename]:
        flash('Please clean a dataset first.', 'warning')
        return redirect(url_for('index'))

    cache = SESSION_CACHE[filename]
    df_raw = cache['df_raw']
    df_cleaned = cache['df_cleaned']

    cleaned_preview_html = df_cleaned.head(15).to_html(
        classes='table table-dark table-hover table-striped mb-0 text-nowrap',
        index=False,
        na_rep='NaN'
    )
    original_preview_html = df_raw.head(15).to_html(
        classes='table table-dark table-hover table-striped mb-0 text-nowrap',
        index=False,
        na_rep='NaN'
    )

    return render_template(
        'results.html',
        filename=filename,
        validation=cache['validation'],
        ai_explanation=cache['ai_explanation'],
        logs=cache['logs'],
        cleaned_preview_html=cleaned_preview_html,
        original_preview_html=original_preview_html
    )

@app.route('/download/dataset')
def download_dataset():
    """Download cleaned dataset as CSV."""
    filename = session.get('filename')
    if not filename or filename not in SESSION_CACHE or 'cleaned_path' not in SESSION_CACHE[filename]:
        flash('Cleaned file unavailable.', 'warning')
        return redirect(url_for('index'))

    cleaned_path = SESSION_CACHE[filename]['cleaned_path']
    return send_file(cleaned_path, as_attachment=True, download_name=os.path.basename(cleaned_path))

@app.route('/download/report')
def download_report():
    """Download data cleaning text report."""
    filename = session.get('filename')
    if not filename or filename not in SESSION_CACHE or 'report_path' not in SESSION_CACHE[filename]:
        flash('Report file unavailable.', 'warning')
        return redirect(url_for('index'))

    report_path = SESSION_CACHE[filename]['report_path']
    return send_file(report_path, as_attachment=True, download_name=os.path.basename(report_path))

if __name__ == '__main__':
    print("=================================================================")
    print(" Starting Data Cleaning AI Agent Application...")
    print(" Access Web App at: http://127.0.0.1:5000")
    print("=================================================================")
    app.run(host='127.0.0.1', port=5000, debug=True)
