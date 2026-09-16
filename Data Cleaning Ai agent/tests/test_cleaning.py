import unittest
import pandas as pd
import numpy as np

from cleaning.missing_values import detect_missing_values, clean_missing_values
from cleaning.duplicates import detect_duplicates, clean_duplicates
from cleaning.outliers import detect_all_outliers, clean_outliers
from cleaning.text_cleaning import clean_text_formatting
from cleaning.date_cleaning import clean_dates
from cleaning.type_conversion import clean_type_and_invalid_values
from agents.analyzer_agent import AnalyzerAgent
from agents.cleaning_agent import CleaningAgent
from agents.validation_agent import ValidationAgent

class TestDataCleaningPipeline(unittest.TestCase):

    def setUp(self):
        """Create sample DataFrame with deliberate data quality flaws."""
        self.raw_data = {
            'ID': [1, 2, 3, 3, 5],
            'Name': [' John Doe ', 'Jane Smith', 'Robert Johnson', 'Robert Johnson', 'Michael Brown '],
            'Age': [28, np.nan, 45, 45, -10],
            'Gender': ['Male', 'female', 'MALE', 'MALE', 'Male'],
            'Salary': [65000, 72000, 85000, 85000, 9500000], # 9500000 is an outlier
            'Join_Date': ['2022-01-15', '12/03/2021', '2020-07-22', '2020-07-22', '15-May-2019']
        }
        self.df = pd.DataFrame(self.raw_data)

    def test_missing_values(self):
        missing = detect_missing_values(self.df)
        self.assertEqual(missing['Age'], 1)
        
        cleaned_df, logs = clean_missing_values(self.df, {'numeric_strategy': 'median', 'categorical_strategy': 'mode'})
        self.assertEqual(cleaned_df['Age'].isna().sum(), 0)

    def test_duplicates(self):
        dup_count = detect_duplicates(self.df)
        self.assertEqual(dup_count, 1)
        
        cleaned_df, logs = clean_duplicates(self.df, remove=True)
        self.assertEqual(len(cleaned_df), 4)

    def test_text_cleaning(self):
        cleaned_df, logs = clean_text_formatting(self.df, trim_whitespace=True, normalize_case='none')
        self.assertEqual(cleaned_df.loc[0, 'Name'], 'John Doe')

    def test_outliers(self):
        outliers = detect_all_outliers(self.df)
        self.assertIn('Salary', outliers)
        self.assertEqual(outliers['Salary']['count'], 1)
        
        cleaned_df, logs = clean_outliers(self.df, strategy='detect_only')
        self.assertEqual(len(cleaned_df), 5) # Retained per conservative policy

    def test_full_pipeline(self):
        analyzer = AnalyzerAgent(self.df)
        report = analyzer.analyze()
        self.assertGreater(report['quality_score'], 0)

        agent = CleaningAgent(self.df, {
            'numeric_missing_strategy': 'median',
            'categorical_missing_strategy': 'mode',
            'remove_duplicates': True,
            'trim_whitespace': True,
            'standardize_dates': True,
            'outlier_strategy': 'detect_only'
        })
        cleaned_df, logs = agent.execute()

        validator = ValidationAgent(self.df, cleaned_df)
        stats = validator.validate()
        self.assertGreater(stats['after']['quality_score'], stats['before']['quality_score'])

if __name__ == '__main__':
    unittest.main()
