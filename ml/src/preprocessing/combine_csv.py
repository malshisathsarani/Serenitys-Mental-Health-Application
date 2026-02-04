"""
Data Preprocessing Module
Combines multiple CSV files and performs data cleaning
"""
import pandas as pd
import glob
import logging
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, LOGS_DIR

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'preprocessing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataCombiner:
    """Combine multiple CSV files into a single dataset"""
    
    def __init__(self, input_dir: Path = RAW_DATA_DIR, output_dir: Path = PROCESSED_DATA_DIR):
        self.input_dir = input_dir
        self.output_dir = output_dir
        
    def find_csv_files(self, exclude_patterns: list = None) -> list:
        """Find all CSV files in the input directory"""
        if exclude_patterns is None:
            exclude_patterns = ['dataset.csv', 'combined.csv']
        
        csv_pattern = str(self.input_dir / "*.csv")
        csv_files = glob.glob(csv_pattern)
        
        # Exclude specified patterns
        csv_files = [
            f for f in csv_files 
            if not any(pattern in Path(f).name for pattern in exclude_patterns)
        ]
        
        logger.info(f"Found {len(csv_files)} CSV files in {self.input_dir}")
        for file in csv_files:
            logger.info(f"  - {Path(file).name}")
        
        return csv_files
    
    def read_csv_files(self, csv_files: list) -> list:
        """Read all CSV files and return list of DataFrames"""
        dfs = []
        
        for file in csv_files:
            try:
                logger.info(f"Reading: {Path(file).name}")
                df = pd.read_csv(file)
                logger.info(f"  Shape: {df.shape}")
                logger.info(f"  Columns: {df.columns.tolist()}")
                dfs.append(df)
            except Exception as e:
                logger.error(f"  ERROR: Failed to read {file}: {str(e)}")
                continue
        
        logger.info(f"Successfully loaded {len(dfs)} dataframes")
        return dfs
    
    def combine_dataframes(self, dfs: list) -> pd.DataFrame:
        """Combine multiple DataFrames into one"""
        if not dfs:
            raise ValueError("No dataframes to combine")
        
        logger.info(f"Combining {len(dfs)} dataframes...")
        
        # Check if all dataframes have the same columns
        columns_sets = [set(df.columns) for df in dfs]
        common_columns = set.intersection(*columns_sets)
        
        if len(common_columns) < len(dfs[0].columns):
            logger.warning("DataFrames have different columns. Using common columns only.")
            logger.warning(f"Common columns: {list(common_columns)}")
            dfs = [df[list(common_columns)] for df in dfs]
        
        # Combine all dataframes
        combined_df = pd.concat(dfs, ignore_index=True)
        logger.info(f"Combined shape: {combined_df.shape}")
        
        return combined_df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Perform basic data cleaning"""
        logger.info("Cleaning data...")
        
        initial_rows = len(df)
        
        # Remove duplicates
        df = df.drop_duplicates()
        logger.info(f"  Removed {initial_rows - len(df)} duplicate rows")
        
        # Display statistics
        logger.info(f"\nData Statistics:")
        logger.info(f"  Total rows: {len(df)}")
        logger.info(f"  Total columns: {len(df.columns)}")
        logger.info(f"  Missing values: {df.isnull().sum().sum()}")
        
        if df.isnull().sum().sum() > 0:
            logger.info(f"\nMissing values per column:")
            for col in df.columns:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    logger.info(f"  {col}: {null_count}")
        
        return df
    
    def save_combined_data(self, df: pd.DataFrame, filename: str = "dataset.csv"):
        """Save combined dataset to file"""
        output_path = self.input_dir / filename
        logger.info(f"Saving combined dataset to: {output_path}")
        
        df.to_csv(output_path, index=False)
        logger.info(f"Dataset saved successfully!")
        
        return output_path
    
    def run_combination_pipeline(self, output_filename: str = "dataset.csv"):
        """Execute the complete data combination pipeline"""
        logger.info("="*80)
        logger.info("Data Combination Pipeline")
        logger.info("="*80)
        
        try:
            # Step 1: Find CSV files
            csv_files = self.find_csv_files()
            
            if not csv_files:
                logger.warning(f"No CSV files found in {self.input_dir}")
                logger.warning("Please add CSV files to combine")
                return None
            
            # Step 2: Read CSV files
            dfs = self.read_csv_files(csv_files)
            
            if not dfs:
                logger.error("No dataframes loaded successfully")
                return None
            
            # Step 3: Combine dataframes
            combined_df = self.combine_dataframes(dfs)
            
            # Step 4: Clean data
            combined_df = self.clean_data(combined_df)
            
            # Step 5: Save combined data
            output_path = self.save_combined_data(combined_df, output_filename)
            
            logger.info("="*80)
            logger.info(f"Data combination completed successfully!")
            logger.info(f"Output: {output_path}")
            logger.info("="*80)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Data combination pipeline failed: {str(e)}", exc_info=True)
            raise


def main():
    """Main entry point for data combination script"""
    combiner = DataCombiner()
    combiner.run_combination_pipeline()


if __name__ == "__main__":
    main()
