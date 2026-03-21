"""
Temporary script to recreate and save the PCA transformer.

This script loads the normalized data and applies PCA to create
the PCA transformer that was used during training, then saves it.
"""

import pandas as pd
import joblib
from pathlib import Path
from sklearn.decomposition import PCA

# Paths
BASE_PATH = Path(__file__).parent.parent
PROCESSED_PATH = BASE_PATH / 'data' / 'processed'

print("="*60)
print("RECREATING AND SAVING PCA TRANSFORMER")
print("="*60)

# Load the normalized training data
print("\nLoading normalized training data...")
X_train = pd.read_csv(PROCESSED_PATH / 'X_train.csv')
print(f"  Loaded: {X_train.shape}")

# Apply PCA with same settings as training
print("\nApplying PCA (variance_threshold=0.95)...")
pca = PCA(n_components=0.95, random_state=42)
X_train_pca = pca.fit_transform(X_train)

print(f"  Components retained: {pca.n_components_}")
print(f"  Explained variance: {pca.explained_variance_ratio_.sum()*100:.2f}%")
print(f"  Original features: {X_train.shape[1]}")
print(f"  Reduced features: {X_train_pca.shape[1]}")

# Save PCA transformer
pca_path = PROCESSED_PATH / 'pca.joblib'
joblib.dump(pca, pca_path)
print(f"\n✅ PCA transformer saved to: {pca_path}")

print("\n" + "="*60)
print("DONE")
print("="*60)
