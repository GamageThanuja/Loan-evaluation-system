"""
Test Data Loader Module
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.data.data_loader import DataLoader


class TestDataLoader:
    """Test cases for DataLoader class"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing"""
        np.random.seed(42)
        df = pd.DataFrame({
            'SK_ID_CURR': range(1000),
            'TARGET': np.random.randint(0, 2, 1000),
            'feature1': np.random.rand(1000),
            'feature2': np.random.rand(1000),
            'feature3': np.random.rand(1000)
        })
        return df
    
    def test_data_split(self, sample_data):
        """Test data splitting"""
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.config import Config
        
        loader = DataLoader(data_path=str(Config.DATA_PROCESSED))
        
        train_data, val_data, test_data = loader.split_data(
            sample_data, 
            target_col='TARGET',
            test_size=0.2,
            val_size=0.1
        )
        
        X_train, y_train = train_data
        X_val, y_val = val_data
        X_test, y_test = test_data
        
        # Check shapes
        assert len(X_train) + len(X_val) + len(X_test) == 1000
        assert len(X_train) > len(X_val)
        assert len(X_train) > len(X_test)
        
        # Check target distribution
        assert y_train.dtype == sample_data['TARGET'].dtype
        assert y_val.dtype == sample_data['TARGET'].dtype
        assert y_test.dtype == sample_data['TARGET'].dtype
    
    def test_target_column_removed(self, sample_data):
        """Test that target column is removed from features"""
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.config import Config
        
        loader = DataLoader(data_path=str(Config.DATA_PROCESSED))
        
        train_data, _, _ = loader.split_data(sample_data, target_col='TARGET')
        X_train, _ = train_data
        
        assert 'TARGET' not in X_train.columns
        assert 'SK_ID_CURR' not in X_train.columns
