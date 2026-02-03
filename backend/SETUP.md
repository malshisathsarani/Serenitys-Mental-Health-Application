# Quick Setup Guide

## ⚡ Fast Track Setup (5 minutes)

### 1. Set up Python environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
# Windows:
copy .env.example .env

# Linux/Mac:
cp .env.example .env

# Edit .env if needed (defaults work for development)
```

### 4. Prepare data and train model

```bash
# If you have multiple CSV files in data/:
python scripts/combine_csv.py

# Train the model (requires dataset.csv in data/):
python scripts/train_baseline.py
```

### 5. Run the API

```bash
cd app
uvicorn main:app --reload
```

Visit: http://localhost:8000

## 🧪 Verify Installation

```bash
# Run tests
pytest

# Test the API manually
curl http://localhost:8000/health

# Interactive prediction
python scripts/predict.py
```

## 🚨 Common Issues

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`
**Solution:** Activate virtual environment and install requirements

**Problem:** `FileNotFoundError: Model file not found`
**Solution:** Train the model first: `python scripts/train_baseline.py`

**Problem:** Port 8000 already in use
**Solution:** Change PORT in .env or use: `uvicorn main:app --port 8001`

## 📂 What You Need

Before training:

- CSV files in `backend/data/` with columns: `text` and `status`

The system will create:

- `backend/models/text_classifier.joblib` - Trained model
- `backend/models/labels.json` - Label mappings
- `backend/logs/app.log` - Application logs

## ✅ Success Indicators

You're ready when:

- ✅ Virtual environment activated
- ✅ All dependencies installed (no errors)
- ✅ `.env` file exists
- ✅ Model file exists in `models/`
- ✅ API responds at http://localhost:8000/health
- ✅ Tests pass: `pytest`

## 🎯 Next Steps

1. **Test the API**: Use Postman or curl to test `/analyze`
2. **Review logs**: Check `logs/app.log` for any issues
3. **Run tests**: `pytest --cov` for coverage report
4. **Configure for production**: Update `.env` with production settings
