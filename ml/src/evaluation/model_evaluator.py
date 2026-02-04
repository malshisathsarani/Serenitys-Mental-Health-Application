"""
Model Evaluation Module
Utilities for evaluating model performance
"""
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Comprehensive model evaluation utilities"""
    
    @staticmethod
    def calculate_metrics(y_true, y_pred, average='weighted') -> Dict[str, float]:
        """
        Calculate comprehensive evaluation metrics
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            average: Averaging method for multi-class metrics
            
        Returns:
            Dictionary of metrics
        """
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average=average, zero_division=0),
            'recall': recall_score(y_true, y_pred, average=average, zero_division=0),
            'f1': f1_score(y_true, y_pred, average=average, zero_division=0)
        }
        
        return metrics
    
    @staticmethod
    def generate_classification_report(y_true, y_pred, target_names=None) -> str:
        """
        Generate detailed classification report
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            target_names: List of class names
            
        Returns:
            Classification report as string
        """
        return classification_report(y_true, y_pred, target_names=target_names)
    
    @staticmethod
    def plot_confusion_matrix(y_true, y_pred, classes, save_path: Path = None):
        """
        Plot and save confusion matrix
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            classes: List of class names
            save_path: Path to save the plot
        """
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=classes,
            yticklabels=classes
        )
        plt.title('Confusion Matrix', fontsize=16)
        plt.ylabel('True Label', fontsize=12)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Confusion matrix saved to: {save_path}")
        
        plt.close()
    
    @staticmethod
    def evaluate_model(model, X_test, y_test, classes=None) -> Dict[str, Any]:
        """
        Comprehensive model evaluation
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels
            classes: List of class names
            
        Returns:
            Dictionary containing all evaluation metrics
        """
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        metrics = ModelEvaluator.calculate_metrics(y_test, y_pred)
        
        # Generate classification report
        report = ModelEvaluator.generate_classification_report(
            y_test, y_pred, target_names=classes
        )
        
        # Log results
        logger.info("\nModel Evaluation Results:")
        logger.info(f"Accuracy: {metrics['accuracy']:.4f}")
        logger.info(f"Precision: {metrics['precision']:.4f}")
        logger.info(f"Recall: {metrics['recall']:.4f}")
        logger.info(f"F1 Score: {metrics['f1']:.4f}")
        logger.info(f"\n{report}")
        
        return {
            'metrics': metrics,
            'classification_report': report,
            'predictions': y_pred
        }
