"""
Data Merging Pipeline for Home Credit Default Risk
Merges all raw data files into a consolidated dataset
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HomeCreditMerger:
    """Merge all Home Credit datasets into a single consolidated file"""
    
    def __init__(self, raw_data_path: str, output_path: str):
        self.raw_data_path = Path(raw_data_path)
        self.output_path = Path(output_path)
        
    def load_application_train(self):
        """Load main application training data"""
        logger.info("Loading application_train.csv...")
        return pd.read_csv(self.raw_data_path / 'application_train.csv')
    
    def load_bureau_data(self, df_main):
        """Load and aggregate bureau data"""
        logger.info("Loading bureau data...")
        df_bureau = pd.read_csv(self.raw_data_path / 'bureau.csv')
        df_bureau_balance = pd.read_csv(self.raw_data_path / 'bureau_balance.csv')
        
        # Aggregate bureau balance
        bureau_agg = df_bureau_balance.groupby('SK_ID_BUREAU').agg({
            'MONTHS_BALANCE': ['min', 'max', 'size']
        })
        bureau_agg.columns = ['_'.join(col).strip() for col in bureau_agg.columns.values]
        
        # Merge and aggregate by SK_ID_CURR (only numeric columns)
        df_bureau = df_bureau.merge(bureau_agg, on='SK_ID_BUREAU', how='left')
        
        # Select numeric columns excluding SK_ID_CURR for aggregation
        numeric_cols = df_bureau.select_dtypes(include=[np.number]).columns.tolist()
        if 'SK_ID_CURR' in numeric_cols:
            numeric_cols.remove('SK_ID_CURR')
        
        bureau_agg_final = df_bureau.groupby('SK_ID_CURR')[numeric_cols].mean().reset_index()
        
        return df_main.merge(bureau_agg_final, on='SK_ID_CURR', how='left')
    
    def load_previous_application(self, df_main):
        """Load and aggregate previous application data"""
        logger.info("Loading previous_application.csv...")
        df_prev = pd.read_csv(self.raw_data_path / 'previous_application.csv')
        
        # Aggregate by SK_ID_CURR
        prev_agg = df_prev.groupby('SK_ID_CURR').agg({
            'AMT_ANNUITY': ['min', 'max', 'mean'],
            'AMT_APPLICATION': ['min', 'max', 'mean'],
            'AMT_CREDIT': ['min', 'max', 'mean'],
            'AMT_DOWN_PAYMENT': ['min', 'max', 'mean'],
            'CNT_PAYMENT': ['mean', 'sum']
        })
        prev_agg.columns = ['PREV_' + '_'.join(col).strip() for col in prev_agg.columns.values]
        
        return df_main.merge(prev_agg, on='SK_ID_CURR', how='left')
    
    def load_pos_cash_balance(self, df_main):
        """Load and aggregate POS_CASH_balance data"""
        logger.info("Loading POS_CASH_balance.csv...")
        df_pos = pd.read_csv(self.raw_data_path / 'POS_CASH_balance.csv')
        
        pos_agg = df_pos.groupby('SK_ID_CURR').agg({
            'MONTHS_BALANCE': ['min', 'max', 'size'],
            'CNT_INSTALMENT': ['mean', 'sum'],
            'CNT_INSTALMENT_FUTURE': ['mean', 'sum']
        })
        pos_agg.columns = ['POS_' + '_'.join(col).strip() for col in pos_agg.columns.values]
        
        return df_main.merge(pos_agg, on='SK_ID_CURR', how='left')
    
    def load_installments_payments(self, df_main):
        """Load and aggregate installments payments data"""
        logger.info("Loading installments_payments.csv...")
        df_inst = pd.read_csv(self.raw_data_path / 'installments_payments.csv')
        
        # Calculate payment differences
        df_inst['PAYMENT_DIFF'] = df_inst['AMT_PAYMENT'] - df_inst['AMT_INSTALMENT']
        df_inst['PAYMENT_RATIO'] = df_inst['AMT_PAYMENT'] / df_inst['AMT_INSTALMENT']
        
        inst_agg = df_inst.groupby('SK_ID_CURR').agg({
            'NUM_INSTALMENT_VERSION': 'nunique',
            'PAYMENT_DIFF': ['mean', 'min', 'max'],
            'PAYMENT_RATIO': ['mean', 'min', 'max'],
            'DAYS_ENTRY_PAYMENT': ['mean', 'min', 'max']
        })
        inst_agg.columns = ['INST_' + '_'.join(col).strip() for col in inst_agg.columns.values]
        
        return df_main.merge(inst_agg, on='SK_ID_CURR', how='left')
    
    def load_credit_card_balance(self, df_main):
        """Load and aggregate credit card balance data"""
        logger.info("Loading credit_card_balance.csv...")
        df_cc = pd.read_csv(self.raw_data_path / 'credit_card_balance.csv')
        
        cc_agg = df_cc.groupby('SK_ID_CURR').agg({
            'MONTHS_BALANCE': ['min', 'max', 'size'],
            'AMT_BALANCE': ['mean', 'min', 'max'],
            'AMT_CREDIT_LIMIT_ACTUAL': ['mean', 'min', 'max'],
            'AMT_DRAWINGS_ATM_CURRENT': ['mean', 'sum'],
            'AMT_DRAWINGS_CURRENT': ['mean', 'sum'],
            'AMT_PAYMENT_CURRENT': ['mean', 'sum']
        })
        cc_agg.columns = ['CC_' + '_'.join(col).strip() for col in cc_agg.columns.values]
        
        return df_main.merge(cc_agg, on='SK_ID_CURR', how='left')
    
    def merge_all(self):
        """Execute complete merge pipeline"""
        logger.info("Starting merge pipeline...")
        
        # Load main application data
        df = self.load_application_train()
        logger.info(f"Initial shape: {df.shape}")
        
        # Merge all datasets
        df = self.load_bureau_data(df)
        logger.info(f"After bureau merge: {df.shape}")
        
        df = self.load_previous_application(df)
        logger.info(f"After previous application merge: {df.shape}")
        
        df = self.load_pos_cash_balance(df)
        logger.info(f"After POS_CASH merge: {df.shape}")
        
        df = self.load_installments_payments(df)
        logger.info(f"After installments merge: {df.shape}")
        
        df = self.load_credit_card_balance(df)
        logger.info(f"Final shape: {df.shape}")
        
        # Save consolidated data
        output_file = self.output_path / 'home_credit_consolidated.csv'
        df.to_csv(output_file, index=False)
        logger.info(f"Merged data saved to {output_file}")
        
        return df


def main():
    """Main execution function"""
    from pathlib import Path
    project_root = Path(__file__).parent.parent.parent
    merger = HomeCreditMerger(
        raw_data_path=str(project_root / 'data' / 'raw'),
        output_path=str(project_root / 'data' / 'processed')
    )
    
    df_merged = merger.merge_all()
    print(f"\nMerge complete! Final dataset shape: {df_merged.shape}")
    print(f"Columns: {df_merged.shape[1]}")
    print(f"Rows: {df_merged.shape[0]}")


if __name__ == "__main__":
    main()
