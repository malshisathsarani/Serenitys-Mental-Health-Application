"""Create a tiny TF-IDF + LogisticRegression bundle if the trained model is missing (local dev only)."""
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

ML_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = ML_ROOT / "models" / "text_classifier.joblib"


def main():
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if MODEL_PATH.exists():
        print(f"Model already exists: {MODEL_PATH}")
        return
    texts = [
        "I am happy today",
        "I feel sad and hopeless",
        "I am very anxious",
        "I want to end my life",
    ]
    labels = ["Normal", "Depression", "Anxiety", "Suicidal"]
    vec = TfidfVectorizer()
    X = vec.fit_transform(texts)
    clf = LogisticRegression(max_iter=2000)
    clf.fit(X, labels)
    joblib.dump(
        {"model": clf, "vectorizer": vec, "classes": list(clf.classes_)},
        MODEL_PATH,
    )
    print(f"Wrote dev placeholder model: {MODEL_PATH}")


if __name__ == "__main__":
    main()
