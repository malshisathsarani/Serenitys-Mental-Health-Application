"""
Deprecated wrapper: use backend/scripts/train_baseline.py
This file forwards execution to the consolidated training script.
"""
from pathlib import Path
import sys


def main():
    # Ensure scripts package is importable
    backend_dir = Path(__file__).parent
    if str(backend_dir) not in sys.path:
        sys.path.append(str(backend_dir))

    try:
        from scripts.train_baseline import train_baseline_model
    except Exception as e:
        print("ERROR: Unable to import consolidated training script.")
        print("Please run: python backend/scripts/train_baseline.py")
        print(f"Details: {e}")
        return

    print("[Deprecated] Using consolidated trainer at backend/scripts/train_baseline.py")
    train_baseline_model()


if __name__ == "__main__":
    main()
