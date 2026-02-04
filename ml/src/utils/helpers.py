"""
Utility Functions
Common helper functions for ML pipeline
"""
import logging
import json
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


def save_json(data: Dict[str, Any], filepath: Path):
    """
    Save dictionary to JSON file
    
    Args:
        data: Dictionary to save
        filepath: Path to save JSON file
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved JSON to: {filepath}")


def load_json(filepath: Path) -> Dict[str, Any]:
    """
    Load JSON file
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Dictionary loaded from JSON
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    logger.info(f"Loaded JSON from: {filepath}")
    return data


def ensure_dir(directory: Path):
    """
    Ensure directory exists, create if it doesn't
    
    Args:
        directory: Path to directory
    """
    directory.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured directory exists: {directory}")


def get_file_size(filepath: Path) -> str:
    """
    Get human-readable file size
    
    Args:
        filepath: Path to file
        
    Returns:
        File size as string (e.g., "10.5 MB")
    """
    size_bytes = filepath.stat().st_size
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    
    return f"{size_bytes:.1f} TB"
