# Serenity Mental Health ML Module

Production-level machine learning module for mental health text classification.

## 📁 Project Structure

```
ml/
├── config/                 # Configuration files
│   └── config.py          # Central configuration module
├── data/                  # Data directory
│   ├── raw/              # Raw datasets
│   └── processed/        # Processed datasets
├── models/               # Trained models
│   ├── text_classifier.joblib
│   └── labels.json
├── src/                  # Source code
│   ├── training/        # Training modules
│   │   └── train_baseline.py
│   ├── preprocessing/   # Data preprocessing
│   │   └── combine_csv.py
│   ├── evaluation/      # Model evaluation
│   └── utils/          # Utility functions
├── scripts/             # Utility scripts
│   └── predict.py      # Interactive prediction CLI
├── notebooks/           # Jupyter notebooks for exploration
├── tests/              # Unit tests
├── logs/               # Training and prediction logs
└── requirements.txt    # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Data Preparation

Place your raw CSV files in `ml/data/raw/` directory.

To combine multiple CSV files:

```bash
python src/preprocessing/combine_csv.py
```

## 🎯 Training

Train the baseline model:

```bash
python src/training/train_baseline.py
```

The script will:

- Load and preprocess data
- Train a Logistic Regression classifier
- Evaluate model performance
- Save trained model and artifacts

## 🔮 Prediction

### Interactive CLI

Run the interactive prediction interface:

```bash
python scripts/predict.py
```

### Programmatic Usage

```python
from scripts.predict import MentalHealthPredictor

predictor = MentalHealthPredictor()
prediction, probabilities = predictor.predict("I feel anxious today")

print(f"Prediction: {prediction}")
print(f"Probabilities: {probabilities}")
```

## 📊 Model Information

- **Model Type**: Logistic Regression
- **Vectorization**: TF-IDF
- **Features**: Up to 20,000 features
- **Classes**: Defined in `models/labels.json`

## 🧪 Testing

Run unit tests:

```bash
pytest tests/
```

## 📝 Logging

Logs are stored in the `logs/` directory:

- `training.log` - Training pipeline logs
- `preprocessing.log` - Data preprocessing logs
- `prediction.log` - Prediction logs

## 🔧 Configuration

Modify `config/config.py` to customize:

- Data paths
- Model hyperparameters
- Training parameters
- Preprocessing settings

## 📈 Performance

After training, check:

- Classification report in logs
- Confusion matrix: `data/processed/confusion_matrix.png`

## 🤝 Integration with Backend

The trained model can be integrated with the FastAPI backend for real-time predictions.

## 📄 License

Part of the Serenity Mental Health Application project.
