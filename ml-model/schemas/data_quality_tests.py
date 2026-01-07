"""
Data Quality Tests using Great Expectations
"""

import great_expectations as ge
import pandas as pd
from pathlib import Path


class DataQualityTester:
    """Run data quality tests"""
    
    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        
    def test_basic_expectations(self, df):
        """Test basic data expectations"""
        ge_df = ge.from_pandas(df)
        
        # Test for null values in critical columns
        if 'TARGET' in df.columns:
            ge_df.expect_column_values_to_not_be_null('TARGET')
        
        if 'SK_ID_CURR' in df.columns:
            ge_df.expect_column_values_to_be_unique('SK_ID_CURR')
        
        # Test numeric columns are within expected ranges
        if 'AMT_INCOME_TOTAL' in df.columns:
            ge_df.expect_column_values_to_be_between('AMT_INCOME_TOTAL', min_value=0)
        
        if 'AMT_CREDIT' in df.columns:
            ge_df.expect_column_values_to_be_between('AMT_CREDIT', min_value=0)
        
        # Test target distribution
        if 'TARGET' in df.columns:
            ge_df.expect_column_values_to_be_in_set('TARGET', [0, 1])
        
        return ge_df.get_expectation_suite()
    
    def run_validation(self, filename: str):
        """Run validation on a dataset"""
        df = pd.read_csv(self.data_path / filename)
        
        print(f"Running data quality tests on {filename}...")
        expectations = self.test_basic_expectations(df)
        
        print(f"Total expectations: {len(expectations['expectations'])}")
        
        return expectations


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.config import Config
    
    tester = DataQualityTester(data_path=str(Config.DATA_PROCESSED))
    
    # Test preprocessed data
    expectations = tester.run_validation('home_credit_consolidated_preprocessed.csv')
    
    print("\nData quality tests complete!")
