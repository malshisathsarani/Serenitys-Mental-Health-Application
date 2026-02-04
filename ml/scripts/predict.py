"""
Prediction Module
Interactive CLI and programmatic interface for model predictions
"""
import joblib
import logging
from pathlib import Path
import sys
from typing import Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from config.config import TRAINED_MODEL_PATH, LOGS_DIR

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_DIR / 'prediction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MentalHealthPredictor:
    """Mental Health Text Classification Predictor"""
    
    def __init__(self, model_path: Path = TRAINED_MODEL_PATH):
        self.model_path = model_path
        self.model = None
        self.vectorizer = None
        self.classes = None
        
    def load_model(self):
        """Load trained model and vectorizer"""
        logger.info(f"Loading model from: {self.model_path}")
        
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {self.model_path}. "
                "Please train the model first using train_baseline.py"
            )
        
        model_data = joblib.load(self.model_path)
        self.model = model_data['model']
        self.vectorizer = model_data['vectorizer']
        self.classes = model_data['classes']
        
        logger.info("Model loaded successfully!")
        logger.info(f"Classes: {self.classes}")
    
    def predict(self, text: str) -> Tuple[str, Dict[str, float]]:
        """
        Predict mental health status from text
        
        Args:
            text: Input text to classify
            
        Returns:
            Tuple of (prediction, probabilities_dict)
        """
        if self.model is None:
            self.load_model()
        
        # Vectorize input
        X = self.vectorizer.transform([text])
        
        # Predict
        prediction = self.model.predict(X)[0]
        
        # Get probabilities
        probabilities = {}
        if hasattr(self.model, 'predict_proba'):
            probs = self.model.predict_proba(X)[0]
            probabilities = {
                label: float(prob) 
                for label, prob in zip(self.classes, probs)
            }
        
        return prediction, probabilities
    
    def predict_batch(self, texts: List[str]) -> List[Tuple[str, Dict[str, float]]]:
        """
        Predict mental health status for multiple texts
        
        Args:
            texts: List of input texts to classify
            
        Returns:
            List of tuples (prediction, probabilities_dict)
        """
        if self.model is None:
            self.load_model()
        
        results = []
        for text in texts:
            prediction, probabilities = self.predict(text)
            results.append((prediction, probabilities))
        
        return results
    
    def interactive_predict(self):
        """Interactive CLI for testing predictions"""
        logger.info("="*80)
        logger.info("Mental Health Text Classifier - Interactive Prediction")
        logger.info("="*80)
        
        # Load model
        self.load_model()
        
        print("\nType 'exit' or 'quit' to exit")
        print("Type 'help' for usage instructions\n")
        
        while True:
            try:
                text = input("Enter text to analyze: ").strip()
                
                if text.lower() in ['exit', 'quit']:
                    print("Exiting...")
                    break
                
                if text.lower() == 'help':
                    self._print_help()
                    continue
                
                if not text:
                    print("Please enter some text\n")
                    continue
                
                # Make prediction
                prediction, probabilities = self.predict(text)
                
                # Display results
                print(f"\n{'='*60}")
                print(f"Prediction: {prediction}")
                print(f"\nProbabilities:")
                
                # Sort probabilities by value
                sorted_probs = sorted(
                    probabilities.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
                
                for label, prob in sorted_probs:
                    bar = '█' * int(prob * 50)
                    print(f"  {label:15s}: {prob:.4f} ({prob*100:5.2f}%) {bar}")
                
                print(f"{'='*60}\n")
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                logger.error(f"Prediction error: {str(e)}", exc_info=True)
                print(f"Error: {str(e)}\n")
    
    def _print_help(self):
        """Print help message"""
        help_text = """
        Usage:
        - Enter any text to classify its mental health status
        - Type 'exit' or 'quit' to exit the program
        - Type 'help' to see this message
        
        The classifier will return:
        - Predicted mental health status
        - Confidence probabilities for each class
        """
        print(help_text)


def main():
    """Main entry point for prediction script"""
    predictor = MentalHealthPredictor()
    predictor.interactive_predict()


if __name__ == "__main__":
    main()
