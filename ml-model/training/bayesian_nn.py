#!/usr/bin/env python3
"""
Bayesian Neural Network Model
==============================
Neural network with Bayesian approach using MC Dropout for uncertainty estimation.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score


class FocalLoss(nn.Module):
    """Focal Loss for handling class imbalance."""
    
    def __init__(self, alpha: float = 0.75, gamma: float = 2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
    
    def forward(self, inputs, targets):
        bce_loss = nn.functional.binary_cross_entropy(inputs, targets, reduction='none')
        pt = torch.where(targets == 1, inputs, 1 - inputs)
        alpha_t = torch.where(targets == 1, self.alpha, 1 - self.alpha)
        focal_weight = alpha_t * (1 - pt) ** self.gamma
        return (focal_weight * bce_loss).mean()


class BayesianNeuralNetwork(nn.Module):
    """
    Bayesian Neural Network using MC Dropout.
    Provides uncertainty estimation through dropout at inference time.
    """
    
    VERSION = "1.0.0"
    MODEL_NAME = "BayesianNeuralNetwork"
    
    def __init__(self, input_dim: int, hidden_dims: list = [128, 64, 32], 
                 dropout: float = 0.3):
        super().__init__()
        
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.dropout_rate = dropout
        
        # Build layers
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(dropout)  # MC Dropout
            ])
            prev_dim = hidden_dim
        
        self.layers = nn.Sequential(*layers)
        self.output = nn.Linear(prev_dim, 1)
    
    def forward(self, x):
        """Forward pass."""
        x = self.layers(x)
        logits = self.output(x)
        return torch.sigmoid(logits).squeeze(-1)
    
    def predict_with_uncertainty(self, x, n_samples: int = 50):
        """
        MC Dropout prediction with uncertainty estimation.
        Returns mean prediction and standard deviation (uncertainty).
        
        Note: We enable dropout but keep BatchNorm in eval mode to handle single samples.
        """
        self.eval()  # Set to eval mode first (for BatchNorm)
        
        # Enable only dropout layers for MC sampling
        for module in self.modules():
            if isinstance(module, nn.Dropout):
                module.train()
        
        predictions = []
        
        with torch.no_grad():
            for _ in range(n_samples):
                pred = self.forward(x)
                predictions.append(pred)
        
        predictions = torch.stack(predictions)
        mean_pred = predictions.mean(dim=0)
        std_pred = predictions.std(dim=0)  # Uncertainty
        
        # Restore full eval mode
        self.eval()
        
        return mean_pred, std_pred
    
    def get_config(self):
        """Return model configuration."""
        return {
            'model_name': self.MODEL_NAME,
            'version': self.VERSION,
            'input_dim': self.input_dim,
            'hidden_dims': self.hidden_dims,
            'dropout_rate': self.dropout_rate,
            'total_params': sum(p.numel() for p in self.parameters())
        }


class BayesianNNTrainer:
    """Trainer class for Bayesian Neural Network."""
    
    def __init__(self, model: BayesianNeuralNetwork, device: str = 'cpu'):
        self.model = model.to(device)
        self.device = device
        self.history = {'train_loss': [], 'val_auc': [], 'val_f1': []}
    
    def train(self, X_train, y_train, X_val, y_val,
              epochs: int = 100, batch_size: int = 32,
              lr: float = 0.001, patience: int = 15):
        """Train the model with early stopping."""
        
        # Prepare data
        X_train_t = torch.FloatTensor(X_train.values if hasattr(X_train, 'values') else X_train).to(self.device)
        y_train_t = torch.FloatTensor(y_train.values if hasattr(y_train, 'values') else y_train).to(self.device)
        X_val_t = torch.FloatTensor(X_val.values if hasattr(X_val, 'values') else X_val).to(self.device)
        y_val_t = torch.FloatTensor(y_val.values if hasattr(y_val, 'values') else y_val).to(self.device)
        
        train_loader = DataLoader(
            TensorDataset(X_train_t, y_train_t),
            batch_size=batch_size, shuffle=True
        )
        
        # Setup
        criterion = FocalLoss(alpha=0.75, gamma=2.0)
        optimizer = optim.Adam(self.model.parameters(), lr=lr, weight_decay=1e-5)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=5)
        
        best_auc = 0
        best_state = None
        no_improve = 0
        
        print(f"\n  Training {self.model.MODEL_NAME}:")
        print("-" * 60)
        
        for epoch in range(epochs):
            # Training phase
            self.model.train()
            train_loss = 0
            
            for X_batch, y_batch in train_loader:
                optimizer.zero_grad()
                output = self.model(X_batch)
                loss = criterion(output, y_batch)
                loss.backward()
                optimizer.step()
                train_loss += loss.item()
            
            avg_loss = train_loss / len(train_loader)
            self.history['train_loss'].append(avg_loss)
            
            # Validation phase
            self.model.eval()
            with torch.no_grad():
                val_pred = self.model(X_val_t).cpu().numpy()
            
            val_auc = roc_auc_score(y_val_t.cpu().numpy(), val_pred)
            val_f1 = f1_score(y_val_t.cpu().numpy(), (val_pred > 0.5).astype(int))
            
            self.history['val_auc'].append(val_auc)
            self.history['val_f1'].append(val_f1)
            
            scheduler.step(val_auc)
            
            # Early stopping check
            if val_auc > best_auc:
                best_auc = val_auc
                best_state = self.model.state_dict().copy()
                no_improve = 0
                marker = "★"
            else:
                no_improve += 1
                marker = ""
            
            if (epoch + 1) % 10 == 0 or marker:
                print(f"  Epoch {epoch+1:3d}: Loss={avg_loss:.4f}, "
                      f"AUC={val_auc:.4f}, F1={val_f1:.4f} {marker}")
            
            if no_improve >= patience:
                print(f"\n  Early stopping at epoch {epoch+1}")
                break
        
        # Restore best model
        self.model.load_state_dict(best_state)
        print(f"\n  ✓ Best Validation AUC: {best_auc:.4f}")
        
        return self.history
    
    def predict(self, X, with_uncertainty: bool = True):
        """Make predictions."""
        X_t = torch.FloatTensor(X.values if hasattr(X, 'values') else X).to(self.device)
        
        if with_uncertainty:
            mean_pred, uncertainty = self.model.predict_with_uncertainty(X_t)
            return mean_pred.cpu().numpy(), uncertainty.cpu().numpy()
        else:
            self.model.eval()
            with torch.no_grad():
                pred = self.model(X_t)
            return pred.cpu().numpy()
    
    def save(self, path: str):
        """Save model."""
        import joblib
        
        model_data = {
            'model_state_dict': self.model.state_dict(),
            'model_config': self.model.get_config(),
            'history': self.history
        }
        joblib.dump(model_data, path)
    
    @classmethod
    def load(cls, path: str, device: str = 'cpu'):
        """Load model."""
        import joblib
        
        model_data = joblib.load(path)
        config = model_data['model_config']
        
        model = BayesianNeuralNetwork(
            input_dim=config['input_dim'],
            hidden_dims=config['hidden_dims'],
            dropout=config['dropout_rate']
        )
        model.load_state_dict(model_data['model_state_dict'])
        
        trainer = cls(model, device)
        trainer.history = model_data['history']
        
        return trainer
