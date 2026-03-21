"""
ANN + Bayesian Network Hybrid Model
=====================================
Feed-forward Artificial Neural Network that receives both the
original scaled features *and* Bayesian Network risk embeddings,
producing loan approval predictions with confidence scores.
"""

import logging
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from src.configuration.config import Config

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# PyTorch network definition
# ----------------------------------------------------------------------
class _ANNNetwork(nn.Module):
    """Multi-layer perceptron with batch-norm and dropout."""

    def __init__(self, input_dim: int, hidden_dims: list, dropout: float = 0.3):
        super().__init__()
        layers = []
        prev = input_dim
        for h in hidden_dims:
            layers.extend([
                nn.Linear(prev, h),
                nn.BatchNorm1d(h),
                nn.ReLU(),
                nn.Dropout(dropout),
            ])
            prev = h
        layers.append(nn.Linear(prev, 1))
        layers.append(nn.Sigmoid())
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


# ----------------------------------------------------------------------
# Trainer / wrapper
# ----------------------------------------------------------------------
class ANNBayesianHybrid:
    """ANN + Bayesian Network hybrid model."""

    MODEL_TAG = "ANN_BN"

    def __init__(self, input_dim: int, hidden_dims: list, dropout: float = 0.3,
                 learning_rate: float = 1e-3, batch_size: int = 64,
                 epochs: int = 100, patience: int = 15, device: str = None):
        self.device = device or Config.DEVICE
        self.network = _ANNNetwork(input_dim, hidden_dims, dropout).to(self.device)
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs
        self.patience = patience
        self.history = {"train_loss": [], "val_loss": [], "val_auc": []}
        self.is_fitted = False

    # ------------------------------------------------------------------
    def train(self, X_train, y_train, X_val, y_val):
        """Train the network and return training history."""
        from sklearn.metrics import roc_auc_score

        self.network.train()
        optimiser = torch.optim.Adam(self.network.parameters(), lr=self.learning_rate)
        criterion = nn.BCELoss()

        train_ds = TensorDataset(
            torch.FloatTensor(X_train).to(self.device),
            torch.FloatTensor(y_train).reshape(-1, 1).to(self.device),
        )
        train_loader = DataLoader(train_ds, batch_size=self.batch_size, shuffle=True)

        X_val_t = torch.FloatTensor(X_val).to(self.device)
        y_val_t = torch.FloatTensor(y_val).reshape(-1, 1).to(self.device)

        best_val_loss = float("inf")
        patience_counter = 0

        for epoch in range(self.epochs):
            # --- Training ---
            self.network.train()
            epoch_loss = 0.0
            for xb, yb in train_loader:
                optimiser.zero_grad()
                pred = self.network(xb)
                loss = criterion(pred, yb)
                loss.backward()
                optimiser.step()
                epoch_loss += loss.item() * len(xb)
            epoch_loss /= len(train_ds)

            # --- Validation ---
            self.network.eval()
            with torch.no_grad():
                val_pred = self.network(X_val_t)
                val_loss = criterion(val_pred, y_val_t).item()
                val_auc = roc_auc_score(y_val, val_pred.cpu().numpy())

            self.history["train_loss"].append(epoch_loss)
            self.history["val_loss"].append(val_loss)
            self.history["val_auc"].append(val_auc)

            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                best_state = {k: v.clone() for k, v in self.network.state_dict().items()}
            else:
                patience_counter += 1
                if patience_counter >= self.patience:
                    logger.info(f"    Early stopping at epoch {epoch + 1}")
                    break

            if (epoch + 1) % 20 == 0 or epoch == 0:
                logger.info(
                    f"    Epoch {epoch+1:>3}/{self.epochs} — "
                    f"loss: {epoch_loss:.4f} | val_loss: {val_loss:.4f} | val_auc: {val_auc:.4f}"
                )

        # Restore best weights
        self.network.load_state_dict(best_state)
        self.is_fitted = True
        return self.history

    # ------------------------------------------------------------------
    def predict_proba(self, X) -> np.ndarray:
        """Return P(Approved) for each sample."""
        self.network.eval()
        with torch.no_grad():
            x_t = torch.FloatTensor(X).to(self.device)
            proba = self.network(x_t).cpu().numpy().flatten()
        return proba

    def predict(self, X, threshold: float = 0.5) -> np.ndarray:
        return (self.predict_proba(X) >= threshold).astype(int)

    # ------------------------------------------------------------------
    def save(self, path):
        torch.save({
            "state_dict": self.network.state_dict(),
            "history": self.history,
            "config": {
                "input_dim": self.network.net[0].in_features,
            },
        }, path)
        logger.info(f"  ✓ {self.MODEL_TAG} saved → {path}")

    @classmethod
    def load_from_checkpoint(cls, path, input_dim, hidden_dims, dropout=0.3, device=None):
        obj = cls(input_dim, hidden_dims, dropout, device=device)
        ckpt = torch.load(path, map_location=obj.device, weights_only=False)
        obj.network.load_state_dict(ckpt["state_dict"])
        obj.history = ckpt.get("history", {})
        obj.is_fitted = True
        return obj
