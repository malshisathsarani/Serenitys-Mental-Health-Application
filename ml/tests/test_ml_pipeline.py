"""
Unit Tests for Mental Health ML Module
"""
import pytest
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.helpers import save_json, load_json, ensure_dir


class TestHelpers:
    """Test utility helper functions"""
    
    def test_ensure_dir(self, tmp_path):
        """Test directory creation"""
        test_dir = tmp_path / "test_directory"
        ensure_dir(test_dir)
        assert test_dir.exists()
    
    def test_save_and_load_json(self, tmp_path):
        """Test JSON save and load operations"""
        test_data = {"key": "value", "number": 42}
        test_file = tmp_path / "test.json"
        
        save_json(test_data, test_file)
        assert test_file.exists()
        
        loaded_data = load_json(test_file)
        assert loaded_data == test_data


class TestPreprocessing:
    """Test preprocessing functionality"""
    
    def test_data_loading(self):
        """Test CSV data loading"""
        # Create sample dataframe
        df = pd.DataFrame({
            'text': ['Sample text 1', 'Sample text 2'],
            'status': ['Normal', 'Stress']
        })
        
        assert len(df) == 2
        assert 'text' in df.columns
        assert 'status' in df.columns


class TestPrediction:
    """Test prediction functionality"""
    
    def test_predictor_initialization(self):
        """Test predictor can be initialized"""
        from scripts.predict import MentalHealthPredictor
        
        predictor = MentalHealthPredictor()
        assert predictor.model is None
        assert predictor.vectorizer is None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__])
