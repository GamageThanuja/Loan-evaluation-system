"""
LSTM + Bayesian Network Hybrid Model
======================================
Long Short-Term Memory network applied to tabular loan data
by reshaping the feature vector into a sequence of feature groups,
combined with Bayesian Network risk embeddings.
"""

import logging
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from src.configuration.config import Config

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# PyTorch LSTM network
# ----------------------------------------------------------------------
class _LSTMNetwork(nn.Module):
    """LSTM that treats each feature as a time-step of length 1."""

    def __init__(self, input_dim: int, hidden_size: int = 64,
                 num_layers: int = 2, dropout: float = 0.3):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size=1,            # each feature is a 1-D time-step
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x: (batch, features) → (batch, seq_len=features, 1)
        x = x.unsqueeze(-1)
        lstm_out, _ = self.lstm(x)          # (batch, seq, hidden)
        last_hidden = lstm_out[:, -1, :]    # take last time-step
        out = self.dropout(last_hidden)
        out = self.fc(out)
        return self.sigmoid(out)


# ----------------------------------------------------------------------
# Trainer / wrapper
# ----------------------------------------------------------------------
class LSTMBayesianHybrid:
    """LSTM + Bayesian Network hybrid model."""

    MODEL_TAG = "LSTM_BN"

    def __init__(self, input_dim: int, hidden_size: int = 64,
                 num_layers: int = 2, dropout: float = 0.3,
                 learning_rate: float = 1e-3, batch_size: int = 64,
                 epochs: int = 100, patience: int = 15, device: str = None):
        self.device = device or Config.DEVICE
        self.network = _LSTMNetwork(input_dim, hidden_size, num_layers, dropout).to(self.device)
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self.epochs = epochs
        self.patience = patience
        self.history = {"train_loss": [], "val_loss": [], "val_auc": []}
        self.is_fitted = False

    # ------------------------------------------------------------------
    def train(self, X_train, y_train, X_val, y_val):
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

            self.network.eval()
            with torch.no_grad():
                val_pred = self.network(X_val_t)
                val_loss = criterion(val_pred, y_val_t).item()
                val_auc = roc_auc_score(y_val, val_pred.cpu().numpy())

            self.history["train_loss"].append(epoch_loss)
            self.history["val_loss"].append(val_loss)
            self.history["val_auc"].append(val_auc)

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

        self.network.load_state_dict(best_state)
        self.is_fitted = True
        return self.history

    # ------------------------------------------------------------------
    def predict_proba(self, X) -> np.ndarray:
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
        }, path)
        logger.info(f"  ✓ {self.MODEL_TAG} saved → {path}")

    @classmethod
    def load_from_checkpoint(cls, path, input_dim, hidden_size=64,
                             num_layers=2, dropout=0.3, device=None):
        obj = cls(input_dim, hidden_size, num_layers, dropout, device=device)
        ckpt = torch.load(path, map_location=obj.device, weights_only=False)
        obj.network.load_state_dict(ckpt["state_dict"])
        obj.history = ckpt.get("history", {})
        obj.is_fitted = True
        return obj
