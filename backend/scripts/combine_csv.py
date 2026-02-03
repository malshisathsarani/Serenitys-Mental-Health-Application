"""
Data Preprocessing Script - Combine CSV Files
Combines multiple CSV files from the data directory into a single dataset
"""
import pandas as pd
import glob
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from config import settings

def combine_csv_files():
    """Combine all CSV files in the data directory"""
    
    print("="*80)
    print("CSV Combiner - Data Preprocessing")
    print("="*80)
    
    # Find all CSV files
    csv_pattern = str(settings.DATA_DIR / "*.csv")
    csv_files = glob.glob(csv_pattern)
    
    # Exclude the output file if it exists
    output_path = settings.DATA_DIR / "dataset.csv"
    csv_files = [f for f in csv_files if Path(f).name != "dataset.csv"]
    
    if not csv_files:
        print(f"\nNo CSV files found in {settings.DATA_DIR}")
        print("Please add CSV files to combine")
        return
    
    print(f"\nFound {len(csv_files)} CSV files:")
    for file in csv_files:
        print(f"  - {Path(file).name}")
    
    # Read and combine
    print(f"\nCombining CSV files...")
    dfs = []
    
    for file in csv_files:
        try:
            print(f"Reading: {Path(file).name}")
            df = pd.read_csv(file)
            print(f"  Shape: {df.shape}")
            dfs.append(df)
        except Exception as e:
            print(f"  ERROR: Failed to read {file}: {str(e)}")
            continue
    
    if not dfs:
        print("\nERROR: No data frames loaded successfully")
        return
    
    # Combine all dataframes
    print(f"\nCombining {len(dfs)} dataframes...")
    combined_df = pd.concat(dfs, ignore_index=True)
    
    print(f"Combined shape: {combined_df.shape}")
    print(f"Columns: {combined_df.columns.tolist()}")
    
    # Show statistics
    print(f"\nData Statistics:")
    print(f"  Total rows: {len(combined_df)}")
    print(f"  Duplicates: {combined_df.duplicated().sum()}")
    print(f"  Missing values: {combined_df.isnull().sum().sum()}")
    
    # Save combined dataset
    print(f"\nSaving combined dataset to: {output_path}")
    combined_df.to_csv(output_path, index=False)
    print("Done!")
    
    print("\n" + "="*80)
    print(f"Combined CSV saved as: {output_path}")
    print("="*80)

if __name__ == "__main__":
    combine_csv_files()
