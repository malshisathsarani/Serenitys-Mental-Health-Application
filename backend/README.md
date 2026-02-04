# Serenity Backend API

Production-ready FastAPI backend for mental health text analysis with ML integration.

## 🏗️ Project Structure

```
backend/
├── app/                    # Main application package
│   ├── api/               # API layer
│   │   └── routes/       # API route definitions
│   │       ├── health.py # Health check endpoints
│   │       └── ml.py     # ML prediction endpoints
│   ├── core/             # Core configuration
│   │   ├── config.py     # Application settings
│   │   └── logging.py    # Logging configuration
│   ├── services/         # Business logic layer
│   │   └── ml_service.py # ML model integration
│   ├── models/           # Data models
│   │   └── schemas.py    # Pydantic schemas
│   └── main.py          # FastAPI application entry point
├── tests/               # Test suite
├── logs/               # Application logs
├── requirements.txt    # Python dependencies
└── .env.example       # Environment variables template
```

## 🚀 Features

- **ML Integration**: Seamless integration with ML module for mental health text classification
- **Production-Ready**: Comprehensive logging, error handling, and monitoring
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Health Checks**: Monitoring endpoints for service health
- **CORS Support**: Configurable CORS for frontend integration
- **Environment-Based Config**: Easy configuration for dev/staging/prod

## 📋 Prerequisites

- Python 3.12+
- Trained ML model in `../ml/models/`

## 🛠️ Installation

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Train ML model** (if not done):
   ```bash
   cd ../ml
   python src/training/train_baseline.py
   ```

## 🏃 Running the Server

### Development Mode
```bash
# From backend/ directory
uvicorn app.main:app --reload --port 8000
```

### Production Mode
```bash
# Set environment variable
export ENV=production  # Linux/Mac
$env:ENV="production"  # Windows PowerShell

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📡 API Endpoints

### Health Checks
- `GET /` - API information
- `GET /health` - Health status

### ML Predictions
- `POST /api/ml/predict` - Analyze text for mental health indicators
  ```json
  {
    "text": "I'm feeling overwhelmed"
  }
  ```
  
- `GET /api/ml/model-info` - Model metadata

### Documentation
- `GET /docs` - Interactive Swagger UI
- `GET /redoc` - ReDoc documentation

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py
```

## 🔧 Configuration

Edit `.env` file or set environment variables:

```env
ENV=development
DEBUG=true
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
LOG_LEVEL=INFO
```

## 📦 Dependencies

Core packages:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `python-dotenv` - Environment management

See `requirements.txt` for complete list.

## 🔗 Integration with ML Module

The backend integrates with the ML module located at `../ml/`:

- **Model Loading**: `app/services/ml_service.py` loads models from `ml/models/`
- **Configuration**: `app/core/config.py` points to ML directories
- **Predictions**: ML endpoints use `MLService` singleton

## 📝 Development Guidelines

1. **Code Style**: Follow PEP 8
2. **Type Hints**: Use type annotations
3. **Error Handling**: Use FastAPI HTTPException
4. **Logging**: Use configured logger from `app.core.logging`
5. **Testing**: Write tests for new endpoints

## 🐛 Troubleshooting

### Model Not Found
```
Error: Model file not found
Solution: Train the model first (cd ../ml && python src/training/train_baseline.py)
```

### Import Errors
```
Error: ModuleNotFoundError: No module named 'app'
Solution: Run from backend/ directory, not from app/
```

### Port Already in Use
```
Error: [Errno 10048] Only one usage of each socket address
Solution: Change PORT in .env or kill process using the port
```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)

## 📄 License

Part of Serenity Mental Health Application
