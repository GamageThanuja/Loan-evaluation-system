"""
Configuration Management
Centralized configuration for paths and settings
"""

from pathlib import Path
import os
from typing import Dict

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
# Overall project root (parent of backend)
OVERALL_PROJECT_ROOT = PROJECT_ROOT.parent

class Config:
    """Application configuration"""
    
    # Project roots
    PROJECT_ROOT = PROJECT_ROOT
    OVERALL_PROJECT_ROOT = OVERALL_PROJECT_ROOT
    
    # Data paths - Try local 'dataset' folder first (for Docker/HF Spaces), else fallback to 'ml-model/dataset'
    LOCAL_DATA_DIR = PROJECT_ROOT / 'dataset'
    DATA_DIR = LOCAL_DATA_DIR if LOCAL_DATA_DIR.exists() else OVERALL_PROJECT_ROOT / 'ml-model' / 'dataset'
    DATA_RAW = DATA_DIR / 'raw_data'
    DATA_PROCESSED = DATA_DIR / 'processed_data'
    
    # Model paths - Try local 'models' folder first (for Docker/HF Spaces), else fallback to 'ml-model/models'
    LOCAL_MODELS_DIR = PROJECT_ROOT / 'models'
    MODELS_DIR = LOCAL_MODELS_DIR if LOCAL_MODELS_DIR.exists() else OVERALL_PROJECT_ROOT / 'ml-model' / 'models'
    
    # Output paths
    REPORTS_DIR = OVERALL_PROJECT_ROOT / 'ml-model' / 'reports'
    RESULTS_DIR = OVERALL_PROJECT_ROOT / 'ml-model' / 'results'
    
    # Model files
    BEST_MODEL = MODELS_DIR / 'best_model.pth'
    BAYESIAN_MODEL = MODELS_DIR / 'bayesian_network.pkl'
    MODEL_REGISTRY = MODELS_DIR / 'model_registry.json'
    
    # API settings
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', '8000'))
    API_RELOAD = os.getenv('API_RELOAD', 'false').lower() == 'true'
    
    # Model settings
    DEFAULT_THRESHOLD = 0.5
    BATCH_SIZE = 1024
    RANDOM_SEED = 42
    
    @classmethod
    def get_model_path(cls, model_type: str) -> Path:
        """Get model path by type"""
        paths = {
            'best': cls.BEST_MODEL,
            'bayesian': cls.BAYESIAN_MODEL,
        }
        return paths.get(model_type)
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories"""
        for dir_path in [cls.DATA_PROCESSED, cls.MODELS_DIR, cls.REPORTS_DIR, cls.RESULTS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)


# Initialize
Config.ensure_directories()
