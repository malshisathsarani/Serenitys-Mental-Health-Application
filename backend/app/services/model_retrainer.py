"""
Model Retraining Service - STEP 3 Bias Reduction
Retrains ML model using original data + feedback-corrected data.
"""
import logging
import json
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

logger = logging.getLogger(__name__)


class ModelRetrainer:
    """Retrain ML model with feedback-corrected data for bias reduction."""

    _instance: Optional["ModelRetrainer"] = None

    def __new__(cls):
        if cls._instance is None:
            inst = super().__new__(cls)
            inst._initialized = False
            cls._instance = inst
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        logger.info("Initializing Model Retrainer (STEP 3 - Bias Reduction)")
        self._initialized = True
        
        # Paths
        self.model_dir = Path(__file__).parent.parent.parent / "ml" / "models"
        self.model_path = self.model_dir / "text_classifier.joblib"
        self.model_backup_dir = self.model_dir / "backups"
        self.model_backup_dir.mkdir(exist_ok=True, parents=True)

    async def retrain_with_feedback(
        self,
        feedback_texts: List[str],
        feedback_labels: List[str],
        original_data_path: Optional[Path] = None,
        mix_ratio: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Retrain model combining original training data + feedback-corrected data.
        
        Strategy:
        1. Load original training data (if provided)
        2. Combine with feedback data (70% original, 30% feedback by default)
        3. Retrain TF-IDF + Logistic Regression
        4. Backup old model
        5. Save new model with version info
        6. Return performance metrics
        
        Args:
            feedback_texts: List of user inputs with biased predictions
            feedback_labels: List of corrected labels
            original_data_path: Path to original CSV with training data
            mix_ratio: Ratio of original data to include (0.0-1.0)
            
        Returns:
            Dict with training results, metrics, and version info
        """
        try:
            logger.info(
                f"Starting model retraining with {len(feedback_texts)} feedback corrections. "
                f"Mix ratio: {mix_ratio} original / {1-mix_ratio} feedback"
            )
            
            # Step 1: Load original training data
            original_texts, original_labels = await self._load_original_data(
                original_data_path
            )
            
            # Step 2: Combine datasets
            combined_texts, combined_labels = self._mix_training_data(
                original_texts, original_labels,
                feedback_texts, feedback_labels,
                mix_ratio=mix_ratio
            )
            
            logger.info(f"Combined training dataset: {len(combined_texts)} samples")
            
            # Step 3: Split data
            X_train, X_test, y_train, y_test = train_test_split(
                combined_texts, combined_labels,
                test_size=0.2, random_state=42, stratify=combined_labels
            )
            
            # Step 4: Vectorize
            logger.info("Training TF-IDF vectorizer...")
            vectorizer = TfidfVectorizer(max_features=20000)
            X_train_vec = vectorizer.fit_transform(X_train)
            X_test_vec = vectorizer.transform(X_test)
            
            # Step 5: Train model
            logger.info("Training Logistic Regression classifier...")
            model = LogisticRegression(
                max_iter=3000,
                class_weight="balanced",
                random_state=42
            )
            model.fit(X_train_vec, y_train)
            
            # Step 6: Evaluate
            y_pred = model.predict(X_test_vec)
            metrics = self._calculate_metrics(y_test, y_pred, model.classes_)
            
            # Step 7: Backup old model
            await self._backup_current_model()
            
            # Step 8: Save new model
            new_model_data = {
                "model": model,
                "vectorizer": vectorizer,
                "classes": list(model.classes_)
            }
            joblib.dump(new_model_data, self.model_path)
            logger.info(f"New model saved to {self.model_path}")
            
            # Step 9: Save version metadata
            version_info = {
                "version": datetime.utcnow().isoformat(),
                "training_samples": len(combined_texts),
                "feedback_samples": len(feedback_texts),
                "original_samples": len(original_texts),
                "mix_ratio_original": mix_ratio,
                "test_accuracy": metrics["accuracy"],
                "metrics": metrics,
            }
            await self._save_version_info(version_info)
            
            result = {
                "status": "success",
                "message": f"Model retrained successfully with {len(feedback_texts)} feedback corrections",
                "version": version_info["version"],
                "metrics": metrics,
                "training_summary": {
                    "total_samples": len(combined_texts),
                    "feedback_samples": len(feedback_texts),
                    "original_samples": len(original_texts),
                    "train_test_split": f"{len(X_train)}/{len(X_test)}",
                }
            }
            
            logger.info(
                f"Retraining complete! "
                f"Test accuracy: {metrics['accuracy']:.2%}, "
                f"Macro F1: {metrics['macro_f1']:.2%}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error during model retraining: {e}", exc_info=True)
            raise

    async def _load_original_data(
        self,
        data_path: Optional[Path],
    ) -> Tuple[List[str], List[str]]:
        """Load original training data from CSV."""
        try:
            if not data_path:
                # Default location from ML project
                data_path = Path(__file__).parent.parent.parent / "ml" / "data" / "raw" / "combined_dataset.csv"
            
            if not data_path.exists():
                logger.warning(f"Original data not found at {data_path}. Using empty original dataset.")
                return [], []
            
            df = pd.read_csv(data_path)
            texts = df["text"].dropna().tolist()
            labels = df["status"].dropna().tolist()
            
            logger.info(f"Loaded original training data: {len(texts)} samples")
            return texts, labels
            
        except Exception as e:
            logger.error(f"Error loading original data: {e}")
            return [], []

    def _mix_training_data(
        self,
        original_texts: List[str],
        original_labels: List[str],
        feedback_texts: List[str],
        feedback_labels: List[str],
        mix_ratio: float,
    ) -> Tuple[List[str], List[str]]:
        """Combine original and feedback data with weighted sampling."""
        # Sample from original data (keeping some proportion)
        if original_texts:
            sample_size = int(len(original_texts) * mix_ratio)
            import random
            sampled_indices = random.sample(range(len(original_texts)), min(sample_size, len(original_texts)))
            sampled_original_texts = [original_texts[i] for i in sampled_indices]
            sampled_original_labels = [original_labels[i] for i in sampled_indices]
        else:
            sampled_original_texts = []
            sampled_original_labels = []
        
        # Combine all
        combined_texts = sampled_original_texts + feedback_texts
        combined_labels = sampled_original_labels + feedback_labels
        
        logger.info(
            f"Mixed datasets: {len(sampled_original_texts)} original + {len(feedback_texts)} feedback = "
            f"{len(combined_texts)} total"
        )
        
        return combined_texts, combined_labels

    def _calculate_metrics(
        self,
        y_true: List[str],
        y_pred: List[str],
        classes: List[str],
    ) -> Dict[str, Any]:
        """Calculate comprehensive classification metrics."""
        metrics = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
            "weighted_f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        }
        
        # Per-class metrics
        per_class = {}
        for label in classes:
            y_true_binary = [1 if y == label else 0 for y in y_true]
            y_pred_binary = [1 if y == label else 0 for y in y_pred]
            
            per_class[label] = {
                "precision": float(precision_score(y_true_binary, y_pred_binary, zero_division=0)),
                "recall": float(recall_score(y_true_binary, y_pred_binary, zero_division=0)),
                "f1": float(f1_score(y_true_binary, y_pred_binary, zero_division=0)),
            }
        
        metrics["per_class"] = per_class
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=classes)
        metrics["confusion_matrix"] = cm.tolist()
        
        return metrics

    async def _backup_current_model(self) -> None:
        """Backup current model before overwriting."""
        try:
            if not self.model_path.exists():
                logger.info("No existing model to backup")
                return
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = self.model_backup_dir / f"model_backup_{timestamp}.joblib"
            shutil.copy2(self.model_path, backup_path)
            logger.info(f"Model backed up to {backup_path}")
        except Exception as e:
            logger.error(f"Error backing up model: {e}")

    async def _save_version_info(self, version_info: Dict[str, Any]) -> None:
        """Save model version metadata."""
        try:
            versions_file = self.model_dir / "versions.json"
            
            versions = []
            if versions_file.exists():
                with open(versions_file) as f:
                    versions = json.load(f)
            
            versions.append(version_info)
            
            # Keep last 10 versions
            versions = versions[-10:]
            
            with open(versions_file, "w") as f:
                json.dump(versions, f, indent=2)
            
            logger.info(f"Version info saved: {version_info['version']}")
        except Exception as e:
            logger.error(f"Error saving version info: {e}")

    async def compare_models(self) -> Dict[str, Any]:
        """Compare current model with previous version."""
        try:
            versions_file = self.model_dir / "versions.json"
            
            if not versions_file.exists() or not versions_file.stat().st_size > 0:
                return {"error": "No version history available"}
            
            with open(versions_file) as f:
                versions = json.load(f)
            
            if len(versions) < 2:
                return {"info": "Only one version exists"}
            
            current = versions[-1]
            previous = versions[-2]
            
            comparison = {
                "current_accuracy": current["test_accuracy"],
                "previous_accuracy": previous["test_accuracy"],
                "accuracy_improvement": current["test_accuracy"] - previous["test_accuracy"],
                "current_timestamp": current["version"],
                "previous_timestamp": previous["version"],
                "current_samples_trained": current["training_samples"],
                "feedback_samples_used": current["feedback_samples"],
            }
            
            return comparison
        except Exception as e:
            logger.error(f"Error comparing models: {e}")
            return {"error": str(e)}


def get_model_retrainer() -> ModelRetrainer:
    """FastAPI dependency provider."""
    return ModelRetrainer()
