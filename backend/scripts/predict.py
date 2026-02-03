"""
Prediction Script - Interactive CLI
Test the trained model with interactive predictions
"""
import joblib
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from config import settings

def interactive_predict():
    """Interactive CLI for testing model predictions"""
    
    print("="*80)
    print("Mental Health Text Classifier - Interactive Prediction")
    print("="*80)
    
    # Load model
    print(f"\nLoading model from: {settings.MODEL_PATH}")
    if not settings.MODEL_PATH.exists():
        print(f"ERROR: Model not found at {settings.MODEL_PATH}")
        print("Please train the model first using train_baseline.py")
        return
    
    model_data = joblib.load(settings.MODEL_PATH)
    model = model_data["model"]
    vectorizer = model_data["vectorizer"]
    
    print("Model loaded successfully!")
    print(f"Classes: {model.classes_}")
    print("\nType 'exit' to quit\n")
    
    # Interactive loop
    while True:
        try:
            text = input("Enter text to analyze: ").strip()
            
            if text.lower() == "exit":
                print("Exiting...")
                break
            
            if not text:
                print("Please enter some text\n")
                continue
            
            # Vectorize and predict
            X = vectorizer.transform([text])
            prediction = model.predict(X)[0]
            
            # Get probabilities if available
            if hasattr(model, "predict_proba"):
                probabilities = model.predict_proba(X)[0]
                print(f"\nPrediction: {prediction}")
                print("\nProbabilities:")
                for label, prob in zip(model.classes_, probabilities):
                    print(f"  {label}: {prob:.4f} ({prob*100:.2f}%)")
            else:
                print(f"\nPrediction: {prediction}")
            
            print("-"*80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}\n")

if __name__ == "__main__":
    interactive_predict()
