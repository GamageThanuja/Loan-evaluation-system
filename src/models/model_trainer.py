"""
Model Trainer Utility
Unified interface for training all models
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.tabnet_train import TabNetTrainer
from src.models.bayesian_network import BayesianNetworkModel
from src.models.hybrid_ensemble import HybridEnsemble


def train_tabnet(data_path, model_path):
    """Train TabNet model"""
    print("\n" + "="*50)
    print("Training TabNet Model")
    print("="*50)
    
    trainer = TabNetTrainer(data_path=data_path, model_path=model_path)
    metrics = trainer.train_pipeline()
    
    print(f"\nTabNet Training Complete!")
    print(f"Test AUC: {metrics['auc']:.4f}")
    print(f"Test Accuracy: {metrics['accuracy']:.4f}")
    
    return metrics


def train_bayesian_network(data_path, model_path):
    """Train Bayesian Network"""
    print("\n" + "="*50)
    print("Training Bayesian Network")
    print("="*50)
    
    bn_model = BayesianNetworkModel(data_path=data_path, model_path=model_path)
    metrics = bn_model.train_pipeline()
    
    print(f"\nBayesian Network Training Complete!")
    print(f"Test AUC: {metrics['auc']:.4f}")
    print(f"Test Accuracy: {metrics['accuracy']:.4f}")
    
    return metrics


def train_hybrid_ensemble(data_path, tabnet_path, bn_path, output_path):
    """Train Hybrid Ensemble"""
    print("\n" + "="*50)
    print("Training Hybrid Ensemble")
    print("="*50)
    
    ensemble = HybridEnsemble(
        data_path=data_path,
        tabnet_path=tabnet_path,
        bn_path=bn_path,
        output_path=output_path
    )
    metrics = ensemble.train_pipeline()
    
    print(f"\nHybrid Ensemble Training Complete!")
    print(f"Test AUC: {metrics['auc']:.4f}")
    print(f"Test Accuracy: {metrics['accuracy']:.4f}")
    
    return metrics


def train_all(data_path=None, models_path=None):
    """Train all models in sequence"""
    from src.config import Config
    
    data_path = data_path or str(Config.DATA_PROCESSED)
    models_path = models_path or str(Config.MODELS_DIR)
    
    print("\n" + "="*60)
    print("Training All Models")
    print("="*60)
    
    results = {}
    
    # Train TabNet
    results['tabnet'] = train_tabnet(
        data_path=data_path,
        model_path=f"{models_path}/tabnet"
    )
    
    # Train Bayesian Network
    results['bayesian'] = train_bayesian_network(
        data_path=data_path,
        model_path=f"{models_path}/bayesian"
    )
    
    # Train Hybrid Ensemble
    results['hybrid'] = train_hybrid_ensemble(
        data_path=data_path,
        tabnet_path=f"{models_path}/tabnet",
        bn_path=f"{models_path}/bayesian",
        output_path=f"{models_path}/hybrid"
    )
    
    # Print summary
    print("\n" + "="*60)
    print("Training Summary")
    print("="*60)
    
    for model_name, metrics in results.items():
        print(f"\n{model_name.upper()}:")
        print(f"  AUC: {metrics['auc']:.4f}")
        print(f"  Accuracy: {metrics['accuracy']:.4f}")
    
    return results


def main():
    """Main execution"""
    from src.config import Config
    
    parser = argparse.ArgumentParser(description='Train Home Credit models')
    parser.add_argument('--model', type=str, choices=['tabnet', 'bayesian', 'hybrid', 'all'],
                       default='all', help='Model to train')
    parser.add_argument('--data-path', type=str, default=str(Config.DATA_PROCESSED),
                       help='Path to processed data')
    parser.add_argument('--models-path', type=str, default=str(Config.MODELS_DIR),
                       help='Path to save models')
    
    args = parser.parse_args()
    
    if args.model == 'all':
        train_all(data_path=args.data_path, models_path=args.models_path)
    elif args.model == 'tabnet':
        train_tabnet(data_path=args.data_path, model_path=f"{args.models_path}/tabnet")
    elif args.model == 'bayesian':
        train_bayesian_network(data_path=args.data_path, model_path=f"{args.models_path}/bayesian")
    elif args.model == 'hybrid':
        train_hybrid_ensemble(
            data_path=args.data_path,
            tabnet_path=f"{args.models_path}/tabnet",
            bn_path=f"{args.models_path}/bayesian",
            output_path=f"{args.models_path}/hybrid"
        )


if __name__ == "__main__":
    main()
