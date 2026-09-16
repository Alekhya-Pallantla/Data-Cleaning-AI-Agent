import pandas as pd
import numpy as np
from cleaning.missing_values import detect_missing_values
from cleaning.duplicates import detect_duplicates
from cleaning.outliers import detect_all_outliers
from cleaning.text_cleaning import detect_text_issues
from cleaning.date_cleaning import detect_date_columns
from cleaning.type_conversion import detect_type_and_domain_issues

class AnalyzerAgent:
    """
    Analyzer Agent: Inspects raw dataset and detects all data-quality issues.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def analyze(self) -> dict:
        rows, cols = self.df.shape
        col_names = list(self.df.columns)
        
        # Data types
        dtypes = {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        
        # Missing values
        missing_by_col = detect_missing_values(self.df)
        total_missing = sum(missing_by_col.values())
        
        # Duplicates
        duplicate_rows = detect_duplicates(self.df)
        
        # Outliers
        outliers_by_col = detect_all_outliers(self.df)
        total_outliers = sum(item['count'] for item in outliers_by_col.values())

        # Text issues
        text_issues = detect_text_issues(self.df)

        # Date columns
        date_issues = detect_date_columns(self.df)

        # Type & Domain issues
        type_domain_issues = detect_type_and_domain_issues(self.df)

        # Unique counts & Special column detection
        unique_counts = {}
        numerical_cols = []
        categorical_cols = []
        constant_cols = []
        potential_id_cols = []

        for col in self.df.columns:
            n_unique = self.df[col].nunique(dropna=True)
            unique_counts[col] = n_unique

            # Constant columns
            if n_unique <= 1 and len(self.df) > 1:
                constant_cols.append(col)

            # Potential ID columns (high uniqueness, sequential or 'id' in name)
            if 'id' in col.lower() or (n_unique == rows and rows > 5):
                potential_id_cols.append(col)

            # Categorical vs Numerical
            if pd.api.types.is_numeric_dtype(self.df[col]):
                if col not in potential_id_cols:
                    numerical_cols.append(col)
            else:
                if col not in date_issues:
                    categorical_cols.append(col)

        # Calculate overall quality score (0-100)
        quality_score = self._calculate_quality_score(
            rows, total_missing, duplicate_rows, total_outliers, len(type_domain_issues['invalid_values'])
        )

        analysis_report = {
            'rows': rows,
            'columns': cols,
            'column_names': col_names,
            'dtypes': dtypes,
            'missing_by_column': missing_by_col,
            'total_missing': total_missing,
            'duplicate_rows': duplicate_rows,
            'outliers_by_column': outliers_by_col,
            'total_outliers': total_outliers,
            'text_issues': text_issues,
            'date_issues': date_issues,
            'type_domain_issues': type_domain_issues,
            'unique_counts': unique_counts,
            'numerical_columns': numerical_cols,
            'categorical_columns': categorical_cols,
            'date_columns': list(date_issues.keys()),
            'constant_columns': constant_cols,
            'potential_id_columns': potential_id_cols,
            'quality_score': quality_score
        }

        return analysis_report

    def _calculate_quality_score(self, rows: int, total_missing: int, duplicates: int, outliers: int, invalid: int) -> int:
        """
        Simple heuristic data quality score out of 100.
        """
        if rows == 0:
            return 0
        total_cells = rows * max(1, len(self.df.columns))
        
        penalty_missing = (total_missing / total_cells) * 40
        penalty_dup = (duplicates / rows) * 30
        penalty_outliers = (outliers / rows) * 15
        penalty_invalid = (invalid / rows) * 15

        score = max(0, min(100, 100 - (penalty_missing + penalty_dup + penalty_outliers + penalty_invalid)))
        return int(round(score))
