import pandas as pd
from agents.analyzer_agent import AnalyzerAgent

class ValidationAgent:
    """
    Validation Agent: Compares dataset state before and after cleaning,
    calculates comparative metrics, and checks integrity.
    """
    def __init__(self, original_df: pd.DataFrame, cleaned_df: pd.DataFrame):
        self.original_df = original_df.copy()
        self.cleaned_df = cleaned_df.copy()

    def validate(self) -> dict:
        orig_analyzer = AnalyzerAgent(self.original_df)
        orig_report = orig_analyzer.analyze()

        clean_analyzer = AnalyzerAgent(self.cleaned_df)
        clean_report = clean_analyzer.analyze()

        # Before & After comparative statistics
        stats = {
            'before': {
                'rows': orig_report['rows'],
                'columns': orig_report['columns'],
                'total_missing': orig_report['total_missing'],
                'duplicates': orig_report['duplicate_rows'],
                'total_outliers': orig_report['total_outliers'],
                'quality_score': orig_report['quality_score']
            },
            'after': {
                'rows': clean_report['rows'],
                'columns': clean_report['columns'],
                'total_missing': clean_report['total_missing'],
                'duplicates': clean_report['duplicate_rows'],
                'total_outliers': clean_report['total_outliers'],
                'quality_score': clean_report['quality_score']
            },
            'fixed': {
                'missing_fixed': orig_report['total_missing'] - clean_report['total_missing'],
                'duplicates_fixed': orig_report['duplicate_rows'] - clean_report['duplicate_rows'],
                'outliers_handled': orig_report['total_outliers'] - clean_report['total_outliers'],
                'quality_gain': clean_report['quality_score'] - orig_report['quality_score']
            }
        }

        # Warnings / Remaining Issues
        warnings = []
        if clean_report['total_missing'] > 0:
            warnings.append(f"Cleaned dataset still contains {clean_report['total_missing']} missing values.")
        if clean_report['duplicate_rows'] > 0:
            warnings.append(f"Cleaned dataset still contains {clean_report['duplicate_rows']} duplicate row(s).")
        if clean_report['total_outliers'] > 0:
            warnings.append(f"Cleaned dataset contains {clean_report['total_outliers']} retained potential outlier(s).")

        stats['warnings'] = warnings
        return stats
