# Mental Health Risk API - Backend

Production-ready FastAPI backend for mental health text analysis and risk assessment.

## 📁 Project Structure

```
backend/
├── app/                    # Main application code
│   ├── __init__.py
│   └── main.py            # FastAPI application
├── scripts/               # Data processing and training scripts
│   ├── __init__.py
│   ├── combine_csv.py     # Combine multiple CSV datasets
│   ├── train_baseline.py  # Train the ML model
│   └── predict.py         # Interactive prediction CLI
├── tests/                 # Test suite
│   ├── __init__.py
│   ├── test_api.py        # API endpoint tests
│   ├── test_config.py     # Configuration tests
│   └── test_model.py      # Model and safety rule tests
├── data/                  # Data files (gitignored)
│   └── .gitkeep
├── models/                # Trained ML models (gitignored)
│   └── .gitkeep
├── logs/                  # Application logs (gitignored)
│   └── .gitkeep
├── config.py              # Configuration management
├── logging_config.py      # Logging setup
├── requirements.txt       # Python dependencies
├── pytest.ini            # Pytest configuration
├── .env.example          # Environment variables template
└── README.md             # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. **Create and activate a virtual environment:**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**

```bash
# Copy the example env file
copy .env.example .env   # Windows
cp .env.example .env     # Linux/Mac

# Edit .env with your settings
```

4. **Prepare your data:**

Place your CSV files in the `data/` directory, then combine them:

```bash
python scripts/combine_csv.py
```

5. **Train the model:**

```bash
python scripts/train_baseline.py
```

This will create `text_classifier.joblib` in the `models/` directory.

## 🏃 Running the Application

### Development Server

```bash
# From the backend directory
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### Production Server

```bash
# Set environment to production in .env
ENV=production

# Run with Gunicorn (recommended for production)
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📡 API Endpoints

### Health Check

```http
GET /health
```

Returns API health status.

### Analyze Text

```http
POST /analyze
Content-Type: application/json

{
  "text": "Your text to analyze",
  "context": ["optional", "conversation", "history"]
}
```

**Response:**

```json
{
  "risk_label": "normal",
  "confidence": 0.85,
  "flags": [],
  "recommended_action": "normal"
}
```

### Root

```http
GET /
```

Returns API information.

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov=config

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::TestHealthEndpoint::test_health_check
```

## 📝 Configuration

All configuration is managed through environment variables. Key settings:

| Variable     | Default                | Description                          |
| ------------ | ---------------------- | ------------------------------------ |
| `ENV`        | development            | Environment (development/production) |
| `DEBUG`      | True                   | Enable debug mode                    |
| `PORT`       | 8000                   | Server port                          |
| `LOG_LEVEL`  | INFO                   | Logging level                        |
| `MODEL_FILE` | text_classifier.joblib | Model filename                       |
| `SECRET_KEY` | (required in prod)     | Secret key for security              |

See [.env.example](.env.example) for all available options.

## 📊 Scripts

### Combine CSV Files

Combines multiple CSV files in the `data/` directory:

```bash
python scripts/combine_csv.py
```

### Train Model

Trains a new baseline model:

```bash
python scripts/train_baseline.py
```

### Interactive Prediction

Test the model interactively:

```bash
python scripts/predict.py
```

## 🔒 Security Considerations

- **Never commit `.env` files** - Use `.env.example` as a template
- **Change SECRET_KEY in production** - Generate a secure key
- **Use HTTPS** - Enable SSL/TLS in production
- **Rate limiting** - Configure rate limits in production
- **Data encryption** - Encrypt sensitive data at rest
- **CORS** - Configure allowed origins properly

## 📦 Deployment

### Environment Setup

1. Set `ENV=production` in `.env`
2. Change `SECRET_KEY` to a secure value
3. Disable `DEBUG` mode
4. Configure proper CORS origins
5. Set up SSL certificates

### Production Checklist

- [ ] Environment variables configured
- [ ] Model file exists in `models/`
- [ ] Logs directory is writable
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Monitoring/alerting set up
- [ ] Backups configured
- [ ] Security headers enabled

## 🐛 Troubleshooting

### Model file not found

Ensure you've trained the model: `python scripts/train_baseline.py`

### Import errors

Make sure you're in the virtual environment and dependencies are installed:

```bash
pip install -r requirements.txt
```

### Port already in use

Change the port in `.env` or kill the process using the port:

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

## 📚 Development

### Code Style

- Use `black` for formatting: `black .`
- Use `flake8` for linting: `flake8 .`
- Use `mypy` for type checking: `mypy .`

### Adding Dependencies

```bash
pip install <package>
pip freeze > requirements.txt
```

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass: `pytest`
5. Format code: `black .`
6. Submit a pull request

## 📄 License

[Your License Here]

## 🆘 Support

For issues and questions:

- Check the troubleshooting section
- Review logs in `logs/app.log`
- Open an issue on GitHub
