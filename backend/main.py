#!/usr/bin/env python3
"""
Loan Evaluation System - Main Entry Point
This script runs the complete pipeline: data processing, model training, and API server
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_ml_pipeline():
    """Run the complete new Hybrid DL + BN pipeline"""
    logger.info("=" * 80)
    logger.info("TRAINING HYBRID ML PIPELINE")
    logger.info("=" * 80)
    
    try:
        import sys
        from pathlib import Path
        ml_model_dir = Path(__file__).parent.parent / 'ml-model'
        sys.path.insert(0, str(ml_model_dir))
        
        # Import and run the main pipeline function
        from train_pipeline import main as run_pipeline
        run_pipeline()
        
        logger.info("✓ ML Pipeline completed successfully")
    except Exception as e:
        logger.error(f"✗ ML Pipeline failed: {str(e)}")
        raise


def start_api_server(host='0.0.0.0', port=8000):
    """Start the FastAPI inference server"""
    logger.info("=" * 80)
    logger.info("STARTING API SERVER")
    logger.info("=" * 80)
    
    try:
        import uvicorn
        logger.info(f"Starting API server on http://{host}:{port}")
        logger.info("API Documentation available at:")
        logger.info(f"  - Swagger UI: http://{host}:{port}/docs")
        logger.info(f"  - ReDoc: http://{host}:{port}/redoc")
        logger.info("\nPress CTRL+C to stop the server")
        
        # We start it as a module import string to allow reload
        uvicorn.run("api:app", host=host, port=port, reload=True)
        
    except Exception as e:
        logger.error(f"✗ Failed to start API server: {str(e)}")
        raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Loan Evaluation System - Complete Pipeline'
    )
    parser.add_argument(
        '--train',
        action='store_true',
        help='Run the ML Training Pipeline before starting the server'
    )
    parser.add_argument(
        '--api-only',
        action='store_true',
        help='Only start the API server (default)'
    )
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='API server host (default: 0.0.0.0)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='API server port (default: 8000)'
    )
    
    args = parser.parse_args()
    
    try:
        logger.info("\n" + "=" * 80)
        logger.info("LOAN EVALUATION SYSTEM")
        logger.info("=" * 80 + "\n")
        
        if args.train:
            run_ml_pipeline()
            
        start_api_server(host=args.host, port=args.port)
        
    except KeyboardInterrupt:
        logger.info("\n\nShutdown requested... exiting")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n✗ System failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
