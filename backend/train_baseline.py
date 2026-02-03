import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

CSV_PATH = "dataset.csv"

# Load dataset
df = pd.read_csv(CSV_PATH)
print("Dataset loaded. Shape:", df.shape)

# 1. Use correct columns
TEXT_COLUMN = "text"
LABEL_COLUMN = "status"

print("Using text column:", TEXT_COLUMN)
print("Using label column:", LABEL_COLUMN)

# Drop rows with missing labels
df = df.dropna(subset=[TEXT_COLUMN, LABEL_COLUMN])

# Split
X_train, X_test, y_train, y_test = train_test_split(
    df[TEXT_COLUMN], df[LABEL_COLUMN], test_size=0.2, random_state=42
)

# TF-IDF
vectorizer = TfidfVectorizer(stop_words="english", max_features=20000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train model
model = LogisticRegression(max_iter=3000)
model.fit(X_train_vec, y_train)

# Predict
y_pred = model.predict(X_test_vec)

# Results
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt="d", cmap="viridis",
            xticklabels=model.classes_,
            yticklabels=model.classes_)
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.savefig("confusion_matrix.png")
plt.close()

print(df['status'].unique())

import joblib
import os

# Create models directory if it doesn't exist
os.makedirs("models", exist_ok=True)

# Save model and vectorizer together
joblib.dump({"model": model, "vectorizer": vectorizer}, "models/text_classifier.joblib")

print("Model saved successfully to models/text_classifier.joblib!")
