import pandas as pd
from cleaning.duplicates import clean_duplicates
from cleaning.text_cleaning import clean_text_formatting
from cleaning.type_conversion import clean_type_and_invalid_values
from cleaning.missing_values import clean_missing_values
from cleaning.date_cleaning import clean_dates
from cleaning.outliers import clean_outliers

class CleaningAgent:
    """
    Cleaning Agent: Applies configurable data cleaning operations step-by-step
    and maintains an audit log.
    """
    def __init__(self, df: pd.DataFrame, config: dict = None):
        self.df = df.copy()
        self.config = config or {}

    def execute(self) -> tuple[pd.DataFrame, list[str]]:
        df_cleaned = self.df.copy()
        logs = []

        # 1. Handle Duplicates
        remove_dup = self.config.get('remove_duplicates', True)
        df_cleaned, dup_logs = clean_duplicates(df_cleaned, remove=remove_dup)
        logs.extend(dup_logs)

        # 2. Text Normalization & Whitespace Trimming
        trim_space = self.config.get('trim_whitespace', True)
        case_norm = self.config.get('normalize_case', 'none') # 'none', 'title', 'lower', 'upper'
        df_cleaned, text_logs = clean_text_formatting(df_cleaned, trim_whitespace=trim_space, normalize_case=case_norm)
        logs.extend(text_logs)

        # 3. Type Conversion & Invalid Value Handling
        convert_num = self.config.get('convert_numeric_strings', True)
        fix_invalid = self.config.get('fix_invalid_values', True)
        df_cleaned, type_logs = clean_type_and_invalid_values(df_cleaned, convert_numeric_text=convert_num, fix_invalid=fix_invalid)
        logs.extend(type_logs)

        # 4. Impute Missing Values
        num_strat = self.config.get('numeric_missing_strategy', 'median')
        cat_strat = self.config.get('categorical_missing_strategy', 'mode')
        missing_cfg = {
            'numeric_strategy': num_strat,
            'categorical_strategy': cat_strat
        }
        df_cleaned, missing_logs = clean_missing_values(df_cleaned, config=missing_cfg)
        logs.extend(missing_logs)

        # 5. Standardize Date Formatting
        std_dates = self.config.get('standardize_dates', True)
        df_cleaned, date_logs = clean_dates(df_cleaned, standardize=std_dates)
        logs.extend(date_logs)

        # 6. Handle Outliers
        outlier_strat = self.config.get('outlier_strategy', 'detect_only') # 'detect_only', 'cap', 'remove'
        df_cleaned, outlier_logs = clean_outliers(df_cleaned, strategy=outlier_strat)
        logs.extend(outlier_logs)

        return df_cleaned, logs
