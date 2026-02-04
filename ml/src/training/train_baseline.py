"""
Training Script - Baseline Model
Production-level training pipeline for mental health text classification
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import json
import logging
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.config import (
    DEFAULT_DATASET, TRAINED_MODEL_PATH, LABELS_PATH,
    MODEL_CONFIG, TRAINING_CONFIG, PREPROCESSING_CONFIG,
    PROCESSED_DATA_DIR, LOGS_DIR
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MentalHealthClassifier:
    """Mental Health Text Classification Model Trainer"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.classes = None
        
    def load_data(self, data_path: Path) -> pd.DataFrame:
        """Load dataset from CSV file"""
        logger.info(f"Loading dataset from: {data_path}")
        
        if not data_path.exists():
            raise FileNotFoundError(f"Dataset not found at {data_path}")
        
        df = pd.read_csv(data_path)
        logger.info(f"Dataset loaded. Shape: {df.shape}")
        logger.info(f"Columns: {df.columns.tolist()}")
        
        return df
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the dataset"""
        logger.info("Starting data preprocessing...")
        
        text_col = PREPROCESSING_CONFIG['text_column']
        label_col = PREPROCESSING_CONFIG['label_column']
        
        # Validate columns
        if text_col not in df.columns or label_col not in df.columns:
            raise ValueError(
                f"Required columns not found. Expected: {text_col}, {label_col}. "
                f"Found: {df.columns.tolist()}"
            )
        
        # Remove missing values
        initial_len = len(df)
        df = df.dropna(subset=[text_col, label_col])
        logger.info(f"Removed {initial_len - len(df)} rows with missing values")
        
        # Remove duplicates if configured
        if PREPROCESSING_CONFIG['remove_duplicates']:
            initial_len = len(df)
            df = df.drop_duplicates(subset=[text_col])
            logger.info(f"Removed {initial_len - len(df)} duplicate rows")
        
        # Filter by minimum text length
        min_length = PREPROCESSING_CONFIG['min_text_length']
        df = df[df[text_col].str.len() >= min_length]
        logger.info(f"Filtered texts with minimum length: {min_length}")
        
        # Display label distribution
        logger.info(f"\nLabel distribution:\n{df[label_col].value_counts()}")
        
        return df
    
    def prepare_features(self, X_train, X_test):
        """Vectorize text features using TF-IDF"""
        logger.info("Vectorizing text with TF-IDF...")
        
        config = MODEL_CONFIG['text_classifier']
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=config['max_features'],
            min_df=2,
            max_df=0.95,
            ngram_range=(1, 2)
        )
        
        X_train_vec = self.vectorizer.fit_transform(X_train)
        X_test_vec = self.vectorizer.transform(X_test)
        
        logger.info(f"Vocabulary size: {len(self.vectorizer.vocabulary_)}")
        logger.info(f"Feature matrix shape: {X_train_vec.shape}")
        
        return X_train_vec, X_test_vec
    
    def train_model(self, X_train, y_train):
        """Train the classification model"""
        logger.info("Training Logistic Regression model...")
        
        config = MODEL_CONFIG['text_classifier']
        self.model = LogisticRegression(
            max_iter=config['max_iter'],
            class_weight=config['class_weight'],
            random_state=config['random_state'],
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        self.classes = self.model.classes_.tolist()
        
        logger.info("Training completed successfully")
        
    def evaluate_model(self, X_test, y_test):
        """Evaluate model performance"""
        logger.info("Evaluating model...")
        
        y_pred = self.model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"\nAccuracy: {accuracy:.4f}")
        
        logger.info("\nClassification Report:")
        logger.info("\n" + classification_report(y_test, y_pred))
        
        # Generate confusion matrix
        self._plot_confusion_matrix(y_test, y_pred)
        
        return y_pred
    
    def _plot_confusion_matrix(self, y_test, y_pred):
        """Generate and save confusion matrix visualization"""
        logger.info("Generating confusion matrix...")
        
        cm = confusion_matrix(y_test, y_pred)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=self.classes,
            yticklabels=self.classes
        )
        plt.title('Confusion Matrix - Mental Health Classification', fontsize=16)
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()
        
        # Save plot
        plot_path = PROCESSED_DATA_DIR / 'confusion_matrix.png'
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        logger.info(f"Confusion matrix saved to: {plot_path}")
        plt.close()
    
    def save_model(self):
        """Save trained model, vectorizer, and metadata"""
        logger.info("Saving model artifacts...")
        
        # Save model and vectorizer
        model_data = {
            'model': self.model,
            'vectorizer': self.vectorizer,
            'classes': self.classes,
            'config': MODEL_CONFIG['text_classifier']
        }
        
        joblib.dump(model_data, TRAINED_MODEL_PATH)
        logger.info(f"Model saved to: {TRAINED_MODEL_PATH}")
        
        # Save labels separately
        with open(LABELS_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.classes, f, indent=2)
        logger.info(f"Labels saved to: {LABELS_PATH}")
    
    def run_training_pipeline(self, data_path: Path = DEFAULT_DATASET):
        """Execute the complete training pipeline"""
        logger.info("="*80)
        logger.info("Mental Health Text Classifier - Training Pipeline")
        logger.info("="*80)
        
        try:
            # Step 1: Load data
            df = self.load_data(data_path)
            
            # Step 2: Preprocess
            df = self.preprocess_data(df)
            
            # Step 3: Split data
            text_col = PREPROCESSING_CONFIG['text_column']
            label_col = PREPROCESSING_CONFIG['label_column']
            
            logger.info(f"Splitting data (test_size={TRAINING_CONFIG['test_size']})")
            X_train, X_test, y_train, y_test = train_test_split(
                df[text_col],
                df[label_col],
                test_size=TRAINING_CONFIG['test_size'],
                random_state=TRAINING_CONFIG['random_state'],
                stratify=df[label_col]
            )
            logger.info(f"Training set: {len(X_train)} samples")
            logger.info(f"Test set: {len(X_test)} samples")
            
            # Step 4: Vectorize features
            X_train_vec, X_test_vec = self.prepare_features(X_train, X_test)
            
            # Step 5: Train model
            self.train_model(X_train_vec, y_train)
            
            # Step 6: Evaluate
            self.evaluate_model(X_test_vec, y_test)
            
            # Step 7: Save model
            self.save_model()
            
            logger.info("="*80)
            logger.info("Training pipeline completed successfully!")
            logger.info("="*80)
            
        except Exception as e:
            logger.error(f"Training pipeline failed: {str(e)}", exc_info=True)
            raise


def main():
    """Main entry point for training script"""
    trainer = MentalHealthClassifier()
    trainer.run_training_pipeline()


if __name__ == "__main__":
    main()
