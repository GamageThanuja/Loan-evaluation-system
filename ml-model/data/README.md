# ML Model Data Directory

This directory contains the machine learning model training and testing data.

## Directory Structure

```
data/
├── raw/              # Raw data files (NOT tracked in Git)
├── processed/        # Processed/preprocessed data (NOT tracked in Git)
└── README.md         # This file
```

## Important Notes

⚠️ **Data files are NOT tracked in Git** due to their large size (2.4GB+).

### To set up data locally:

1. **Download the raw data** from the Home Credit dataset:
   - Visit: https://www.kaggle.com/c/home-credit-default-risk/data
   - Download and extract files to `data/raw/`

2. **Run preprocessing**:
   ```bash
   cd ml-model
   python src/data/preprocess.py
   ```

3. **Files that should be in `raw/`**:
   - application_train.csv
   - application_test.csv
   - bureau.csv
   - bureau_balance.csv
   - POS_CASH_balance.csv
   - credit_card_balance.csv
   - installments_payments.csv
   - previous_application.csv
   - HomeCredit_columns_description.csv

4. **Files generated in `processed/`**:
   - home_credit_consolidated_preprocessed.csv
   - train_split.parquet
   - test_split.parquet
   - val_split.parquet

## Data Storage Best Practices

For production/team environments, consider:
- **Cloud Storage**: AWS S3, Google Cloud Storage, Azure Blob
- **Data Version Control**: DVC (Data Version Control)
- **Git LFS**: For files 100MB-1GB
- **Database**: For structured production data

## Git LFS Setup (Optional)

If your team needs to version large files:

```bash
# Install Git LFS
brew install git-lfs  # macOS
git lfs install

# Track large files
git lfs track "data/raw/*.csv"
git lfs track "data/processed/*.parquet"

# Commit .gitattributes
git add .gitattributes
git commit -m "Configure Git LFS"
```

---

**Note**: The `.gitkeep` files in each directory preserve the folder structure in Git while excluding the actual data files.
