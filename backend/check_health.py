#!/usr/bin/env python3
"""
Codebase Health Check
Verifies all paths and configurations after cleanup
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import Config


def check_paths():
    """Verify all critical paths exist"""
    print("🔍 Checking Critical Paths...\n")
    
    checks = [
        ("Data Directory", Config.DATA_DIR),
        ("Data Processed", Config.DATA_PROCESSED),
        ("Models Directory", Config.MODELS_DIR),
        ("TabNet Directory", Config.TABNET_DIR),
        ("Reports Directory", Config.REPORTS_DIR),
        ("Figures Directory", Config.FIGURES_DIR),
    ]
    
    all_good = True
    for name, path in checks:
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {name}: {path}")
        if not exists:
            all_good = False
    
    return all_good


def check_model_files():
    """Verify model files exist"""
    print("\n🤖 Checking Model Files...\n")
    
    files = [
        ("TabNet Optimized", Config.TABNET_OPTIMIZED),
        ("Optimal Threshold", Config.OPTIMAL_THRESHOLD),
        ("Bayesian Network", Config.BAYESIAN_MODEL),
        ("Hybrid Model", Config.HYBRID_MODEL),
    ]
    
    all_good = True
    for name, path in files:
        exists = path.exists()
        status = "✅" if exists else "⚠️"
        size = f"({path.stat().st_size / 1024:.1f} KB)" if exists else ""
        print(f"{status} {name}: {path.name} {size}")
        if not exists and name in ["TabNet Optimized", "Optimal Threshold"]:
            all_good = False
    
    return all_good


def check_data_splits():
    """Verify data splits exist"""
    print("\n📊 Checking Data Splits...\n")
    
    splits = ['train_split.parquet', 'val_split.parquet', 'test_split.parquet']
    all_good = True
    
    for split_file in splits:
        path = Config.DATA_PROCESSED / split_file
        exists = path.exists()
        status = "✅" if exists else "❌"
        size = f"({path.stat().st_size / (1024*1024):.1f} MB)" if exists else ""
        print(f"{status} {split_file} {size}")
        if not exists:
            all_good = False
    
    return all_good


def check_shap_outputs():
    """Verify SHAP visualizations exist"""
    print("\n🎨 Checking SHAP Visualizations...\n")
    
    shap_files = [
        'shap_summary.png',
        'shap_waterfall.png',
        'feature_importance_shap.png',
        'feature_importance_shap.csv'
    ]
    
    all_good = True
    for shap_file in shap_files:
        path = Config.FIGURES_DIR / shap_file
        exists = path.exists()
        status = "✅" if exists else "⚠️"
        size = f"({path.stat().st_size / 1024:.1f} KB)" if exists else ""
        print(f"{status} {shap_file} {size}")
        if not exists:
            all_good = False
    
    return all_good


def check_no_hardcoded_paths():
    """Check for any remaining hardcoded paths"""
    print("\n🔧 Checking for Hardcoded Paths...\n")
    
    import subprocess
    
    patterns = [
        "data/processed",
        "data/raw",
        "models/tabnet",
        "models/bayesian"
    ]
    
    issues_found = False
    for pattern in patterns:
        try:
            result = subprocess.run(
                ["grep", "-r", pattern, "src/", "--include=*.py"],
                capture_output=True,
                text=True
            )
            
            # Filter out imports and comments
            lines = result.stdout.split('\n')
            actual_issues = [
                line for line in lines 
                if line and 'from src.config import Config' not in line
                and '# ' not in line
            ]
            
            if actual_issues:
                print(f"⚠️ Found '{pattern}' in:")
                for line in actual_issues[:3]:  # Show first 3
                    print(f"   {line}")
                issues_found = True
        except:
            pass
    
    if not issues_found:
        print("✅ No hardcoded paths found in src/")
    
    return not issues_found


def main():
    """Run all checks"""
    print("="*60)
    print("CODEBASE HEALTH CHECK")
    print("="*60)
    print()
    
    results = {
        "Paths": check_paths(),
        "Model Files": check_model_files(),
        "Data Splits": check_data_splits(),
        "SHAP Outputs": check_shap_outputs(),
        "No Hardcoded Paths": check_no_hardcoded_paths()
    }
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "⚠️ WARNING"
        print(f"{status}: {name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED - Codebase is clean!")
    else:
        print("⚠️ Some checks have warnings (may be expected)")
    print("="*60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
