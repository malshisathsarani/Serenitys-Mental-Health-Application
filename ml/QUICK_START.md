# Mental Health ML Module - Quick Start Guide

This guide will help you get started with the ML module for the Serenity Mental Health Application.

## Quick Start Commands

### 1. Setup Environment

```bash
cd ml
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Prepare Data

Place your CSV files in `ml/data/raw/` and combine them:

```bash
python src/preprocessing/combine_csv.py
```

### 3. Train Model

```bash
python src/training/train_baseline.py
```

This will:

- Load and preprocess the data
- Train a Logistic Regression classifier
- Evaluate the model
- Save the trained model to `ml/models/`

### 4. Make Predictions

Interactive mode:

```bash
python scripts/predict.py
```

### 5. Run Tests

```bash
pytest
```

## Directory Structure

```
ml/
├── config/          # Configuration
├── data/
│   ├── raw/        # Place your CSV files here
│   └── processed/  # Processed data and visualizations
├── models/         # Trained models stored here
├── src/
│   ├── training/   # Training scripts
│   ├── preprocessing/  # Data preprocessing
│   ├── evaluation/     # Model evaluation
│   └── utils/          # Helper functions
├── scripts/        # Utility scripts
├── tests/          # Unit tests
├── notebooks/      # Jupyter notebooks
└── logs/           # Log files
```

## Common Issues

### Import Errors

Make sure you're running scripts from the ML module root directory.

### Model Not Found

Train the model first using `python src/training/train_baseline.py`

### Data Not Found

Ensure CSV files are in `ml/data/raw/` directory.

## Next Steps

1. Explore notebooks in `ml/notebooks/` for data analysis
2. Customize configuration in `ml/config/config.py`
3. Add more preprocessing steps in `ml/src/preprocessing/`
4. Integrate with backend API for production deployment
