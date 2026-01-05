#!/bin/bash
# Training Pipeline Script

echo "================================"
echo "Home Credit Training Pipeline"
echo "================================"

# Step 1: Data Merging
echo "\n[1/5] Merging data files..."
python src/data/merge_home_credit.py

# Step 2: Preprocessing
echo "\n[2/5] Preprocessing data..."
python src/data/preprocess.py

# Step 3: Data Splitting
echo "\n[3/5] Splitting data..."
python src/data/data_loader.py

# Step 4: Train TabNet
echo "\n[4/5] Training TabNet..."
python src/models/tabnet_train.py

# Step 5: Train Bayesian Network
echo "\n[5/5] Training Bayesian Network..."
python src/models/bayesian_network.py

# Step 6: Train Hybrid Ensemble
echo "\n[6/6] Training Hybrid Ensemble..."
python src/models/hybrid_ensemble.py

echo "\n================================"
echo "Training Pipeline Complete!"
echo "================================"
