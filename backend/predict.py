import joblib

# Load model and vectorizer from combined file
model_data = joblib.load("models/text_classifier.joblib")
model = model_data["model"]
vectorizer = model_data["vectorizer"]

while True:
    text = input("Enter text: ")

    if text == "exit":
        break

    X = vectorizer.transform([text])
    prediction = model.predict(X)[0]

    print("Prediction:", prediction)
