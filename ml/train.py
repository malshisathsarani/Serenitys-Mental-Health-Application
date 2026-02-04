"""
Quick Training Script
Train the model quickly with default settings
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.training.train_baseline import main

if __name__ == "__main__":
    print("Starting quick training with default settings...")
    main()
