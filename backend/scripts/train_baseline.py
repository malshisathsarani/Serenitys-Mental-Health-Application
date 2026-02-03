"""
Training Script - Baseline Model
Trains a baseline Logistic Regression model for mental health text classification
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from config import settings

# Configuration
CSV_PATH = settings.DATA_DIR / "dataset.csv"
TEXT_COLUMN = "text"
LABEL_COLUMN = "status"
OUTPUT_MODEL = settings.MODEL_DIR / "text_classifier.joblib"

def train_baseline_model():
    """Train and evaluate a baseline mental health classification model"""
    
    print("="*80)
    print("Mental Health Text Classifier - Training Script")
    print("="*80)
    
    # Load dataset
    print(f"\n[1/6] Loading dataset from: {CSV_PATH}")
    if not CSV_PATH.exists():
        print(f"ERROR: Dataset not found at {CSV_PATH}")
        print(f"Please ensure dataset.csv is in {settings.DATA_DIR}")
        return
    
    df = pd.read_csv(CSV_PATH)
    print(f"Dataset loaded. Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Check columns exist
    if TEXT_COLUMN not in df.columns or LABEL_COLUMN not in df.columns:
        print(f"ERROR: Required columns not found")
        print(f"Expected: {TEXT_COLUMN}, {LABEL_COLUMN}")
        print(f"Found: {df.columns.tolist()}")
        return
    
    # Clean data
    print(f"\n[2/6] Cleaning data")
    print(f"Rows before cleaning: {len(df)}")
    df = df.dropna(subset=[TEXT_COLUMN, LABEL_COLUMN])
    print(f"Rows after cleaning: {len(df)}")
    print(f"\nLabel distribution:")
    print(df[LABEL_COLUMN].value_counts())
    
    # Split data
    print(f"\n[3/6] Splitting data (80% train, 20% test)")
    X_train, X_test, y_train, y_test = train_test_split(
        df[TEXT_COLUMN], 
        df[LABEL_COLUMN], 
        test_size=0.2, 
        random_state=42,
        stratify=df[LABEL_COLUMN]
    )
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Vectorize text
    print(f"\n[4/6] Vectorizing text with TF-IDF")
    vectorizer = TfidfVectorizer(
        stop_words="english", 
        max_features=20000,
        min_df=2,
        max_df=0.95
    )
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    print(f"Vocabulary size: {len(vectorizer.vocabulary_)}")
    print(f"Feature matrix shape: {X_train_vec.shape}")
    
    # Train model
    print(f"\n[5/6] Training Logistic Regression model")
    model = LogisticRegression(
        max_iter=3000,
        class_weight='balanced',  # Handle class imbalance
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_vec, y_train)
    print("Training completed")
    
    # Evaluate
    print(f"\n[6/6] Evaluating model")
    y_pred = model.predict(X_test_vec)
    
    print("\nClassification Report:")
    print("-"*80)
    print(classification_report(y_test, y_pred))
    
    # Confusion Matrix
    try:
        print("\nGenerating confusion matrix visualization...")
        cm = confusion_matrix(y_test, y_pred)
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            xticklabels=model.classes_,
            yticklabels=model.classes_,
        )
        plt.title("Confusion Matrix - Mental Health Text Classification")
        plt.ylabel("True Label")
        plt.xlabel("Predicted Label")
        plt.tight_layout()

        # Save plot
        plot_path = settings.DATA_DIR / "confusion_matrix.png"
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        print(f"Confusion matrix saved to: {plot_path}")
    except Exception as e:
        print(f"Skipping confusion matrix plot due to plotting error: {e}")
    finally:
        plt.close("all")
    
    # Save model
    print(f"\n[FINAL] Saving model and vectorizer")
    settings.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    model_data = {
        "model": model,
        "vectorizer": vectorizer,
        "classes": model.classes_.tolist()
    }
    joblib.dump(model_data, OUTPUT_MODEL)
    print(f"Model saved to: {OUTPUT_MODEL}")
    
    # Save labels separately
    import json
    labels_path = settings.LABELS_PATH
    with open(labels_path, 'w', encoding='utf-8') as f:
        json.dump(model.classes_.tolist(), f)
    print(f"Labels saved to: {labels_path}")
    
    print("\n" + "="*80)
    print("Training completed successfully!")
    print("="*80)

if __name__ == "__main__":
    train_baseline_model()
