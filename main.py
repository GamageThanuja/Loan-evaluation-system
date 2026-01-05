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


def run_data_pipeline():
    """Run the complete data processing pipeline"""
    logger.info("=" * 80)
    logger.info("STEP 1: DATA PROCESSING PIPELINE")
    logger.info("=" * 80)
    
    try:
        from src.data.merge_home_credit import merge_all_data
        from src.data.preprocess import preprocess_data
        from src.data.imbalance_fix import handle_imbalance
        from src.features.build_features import build_features
        from src.features.feature_selector import select_features
        
        # Merge all Home Credit data
        logger.info("Merging Home Credit datasets...")
        merged_data = merge_all_data()
        logger.info(f"✓ Data merged successfully. Shape: {merged_data.shape}")
        
        # Preprocess data
        logger.info("Preprocessing data...")
        preprocessed_data = preprocess_data(merged_data)
        logger.info(f"✓ Data preprocessed. Shape: {preprocessed_data.shape}")
        
        # Handle imbalance
        logger.info("Handling class imbalance...")
        balanced_data = handle_imbalance(preprocessed_data)
        logger.info(f"✓ Imbalance handled. Shape: {balanced_data.shape}")
        
        # Build features
        logger.info("Building features...")
        feature_data = build_features(balanced_data)
        logger.info(f"✓ Features built. Shape: {feature_data.shape}")
        
        # Feature selection
        logger.info("Selecting important features...")
        final_data = select_features(feature_data)
        logger.info(f"✓ Features selected. Final shape: {final_data.shape}")
        
        return final_data
        
    except Exception as e:
        logger.error(f"✗ Data pipeline failed: {str(e)}")
        raise


def run_model_training(data=None):
    """Run the complete model training pipeline"""
    logger.info("=" * 80)
    logger.info("STEP 2: MODEL TRAINING PIPELINE")
    logger.info("=" * 80)
    
    try:
        from src.models.tabnet_train import train_tabnet
        from src.models.bayesian_network import train_bayesian_network
        from src.models.hybrid_ensemble import train_hybrid_ensemble
        
        # Train TabNet model
        logger.info("Training TabNet model...")
        tabnet_model = train_tabnet(data)
        logger.info("✓ TabNet model trained successfully")
        
        # Train Bayesian Network
        logger.info("Training Bayesian Network...")
        bn_model = train_bayesian_network(data)
        logger.info("✓ Bayesian Network trained successfully")
        
        # Train Hybrid Ensemble
        logger.info("Training Hybrid Ensemble...")
        ensemble_model = train_hybrid_ensemble(tabnet_model, bn_model, data)
        logger.info("✓ Hybrid Ensemble trained successfully")
        
        return {
            'tabnet': tabnet_model,
            'bayesian': bn_model,
            'ensemble': ensemble_model
        }
        
    except Exception as e:
        logger.error(f"✗ Model training failed: {str(e)}")
        raise


def run_evaluation(models):
    """Run model evaluation and generate reports"""
    logger.info("=" * 80)
    logger.info("STEP 3: MODEL EVALUATION")
    logger.info("=" * 80)
    
    try:
        from src.evaluation.final_evaluation import evaluate_all_models
        from src.evaluation.xai_shap import generate_shap_explanations
        
        # Evaluate all models
        logger.info("Evaluating models...")
        evaluation_results = evaluate_all_models(models)
        logger.info("✓ Model evaluation complete")
        
        # Generate SHAP explanations
        logger.info("Generating SHAP explanations...")
        generate_shap_explanations(models['ensemble'])
        logger.info("✓ SHAP explanations generated")
        
        # Print results
        logger.info("\n" + "=" * 80)
        logger.info("EVALUATION RESULTS")
        logger.info("=" * 80)
        for model_name, metrics in evaluation_results.items():
            logger.info(f"\n{model_name.upper()}:")
            for metric, value in metrics.items():
                logger.info(f"  {metric}: {value:.4f}")
        
        return evaluation_results
        
    except Exception as e:
        logger.error(f"✗ Evaluation failed: {str(e)}")
        raise


def start_api_server(host='0.0.0.0', port=8000):
    """Start the FastAPI inference server"""
    logger.info("=" * 80)
    logger.info("STEP 4: STARTING API SERVER")
    logger.info("=" * 80)
    
    try:
        import uvicorn
        from src.inference.api import app
        
        logger.info(f"Starting API server on http://{host}:{port}")
        logger.info("API Documentation available at:")
        logger.info(f"  - Swagger UI: http://{host}:{port}/docs")
        logger.info(f"  - ReDoc: http://{host}:{port}/redoc")
        logger.info("\nPress CTRL+C to stop the server")
        
        uvicorn.run(app, host=host, port=port)
        
    except Exception as e:
        logger.error(f"✗ Failed to start API server: {str(e)}")
        raise


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Loan Evaluation System - Complete Pipeline'
    )
    parser.add_argument(
        '--skip-data',
        action='store_true',
        help='Skip data processing (use existing processed data)'
    )
    parser.add_argument(
        '--skip-training',
        action='store_true',
        help='Skip model training (use existing models)'
    )
    parser.add_argument(
        '--skip-evaluation',
        action='store_true',
        help='Skip model evaluation'
    )
    parser.add_argument(
        '--api-only',
        action='store_true',
        help='Only start the API server (skip all training)'
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
        logger.info("LOAN EVALUATION SYSTEM - COMPLETE PIPELINE")
        logger.info("=" * 80 + "\n")
        
        data = None
        models = None
        
        # API only mode
        if args.api_only:
            logger.info("Running in API-only mode...")
            start_api_server(host=args.host, port=args.port)
            return
        
        # Data processing
        if not args.skip_data:
            data = run_data_pipeline()
        else:
            logger.info("Skipping data processing (using existing data)")
        
        # Model training
        if not args.skip_training:
            models = run_model_training(data)
        else:
            logger.info("Skipping model training (using existing models)")
        
        # Evaluation
        if not args.skip_evaluation and models:
            run_evaluation(models)
        else:
            logger.info("Skipping model evaluation")
        
        # Start API server
        logger.info("\n" + "=" * 80)
        logger.info("PIPELINE COMPLETE!")
        logger.info("=" * 80)
        logger.info("\nStarting API server...")
        start_api_server(host=args.host, port=args.port)
        
    except KeyboardInterrupt:
        logger.info("\n\nShutdown requested... exiting")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n✗ Pipeline failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
