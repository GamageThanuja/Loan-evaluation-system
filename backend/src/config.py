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
    
    # Data paths - Use ml-model directory for actual data
    DATA_DIR = OVERALL_PROJECT_ROOT / 'ml-model' / 'data'
    DATA_RAW = DATA_DIR / 'raw'
    DATA_PROCESSED = DATA_DIR / 'processed'
    DATA_EXTERNAL = DATA_DIR / 'external'
    
    # Model paths - Use ml-model directory for trained models
    MODELS_DIR = OVERALL_PROJECT_ROOT / 'ml-model' / 'models'
    TABNET_DIR = MODELS_DIR  # All models now in root models folder
    BAYESIAN_DIR = MODELS_DIR
    HYBRID_DIR = MODELS_DIR
    
    # Output paths
    REPORTS_DIR = OVERALL_PROJECT_ROOT / 'reports'
    FIGURES_DIR = REPORTS_DIR / 'figures'
    
    # Config path
    CONFIG_DIR = OVERALL_PROJECT_ROOT / 'config'
    APP_CONFIG = CONFIG_DIR / 'app_config.yaml'
    
    # Model files (single model file)
    TABNET_MODEL = MODELS_DIR / 'tabnet.zip'
    OPTIMAL_THRESHOLD = 0.309  # Default threshold
    BAYESIAN_MODEL = MODELS_DIR / 'bayesian_network.pkl'
    HYBRID_MODEL = MODELS_DIR / 'tabnet.pkl'
    HYBRID_WEIGHTS = None  # Not used anymore
    
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
            'tabnet': cls.TABNET_MODEL,
            'bayesian': cls.BAYESIAN_MODEL,
            'hybrid': cls.HYBRID_MODEL
        }
        return paths.get(model_type)
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories"""
        for dir_path in [cls.DATA_PROCESSED, cls.MODELS_DIR, cls.REPORTS_DIR, cls.FIGURES_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)


# Initialize
Config.ensure_directories()
