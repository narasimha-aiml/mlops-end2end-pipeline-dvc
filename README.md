# MLOps Pipeline: Cats vs Dogs Binary Classification

An end-to-end MLOps pipeline demonstrating model development, containerization, CI/CD, and deployment for binary image classification.

## Project Structure

```
├── data/
│   ├── raw/                 # Original dataset
│   └── processed/           # DVC-tracked preprocessed data
├── notebooks/
│   └── exploration.ipynb    # EDA and model development
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   └── preprocessing.py # Data preprocessing functions
│   ├── models/
│   │   ├── __init__.py
│   │   └── train.py         # Model training script
│   ├── inference/
│   │   ├── __init__.py
│   │   └── predictor.py     # Model loading and prediction
│   └── api/
│       ├── __init__.py
│       ├── main.py          # FastAPI application
│       └── schemas.py       # Request/response schemas
├── tests/
│   ├── __init__.py
│   ├── test_preprocessing.py
│   └── test_inference.py
├── deployment/
│   ├── kubernetes/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── docker-compose/
│       └── docker-compose.yml
├── .github/workflows/       # CI/CD pipelines
├── .dvc/                    # DVC configuration
├── .gitignore
├── Dockerfile
├── requirements.txt
├── setup.py
└── dvc.yaml
```

## Modules Overview

### M1: Model Development & Experiment Tracking (10M)
- Git versioning with DVC for datasets
- Baseline CNN model training
- MLflow experiment tracking

### M2: Model Packaging & Containerization (10M)
- FastAPI REST API with health check and prediction endpoints
- Pinned dependencies in requirements.txt
- Docker containerization

### M3: CI Pipeline (10M)
- GitHub Actions workflow
- Automated testing with pytest
- Docker image building and pushing

### M4: CD Pipeline & Deployment (10M)
- Kubernetes or Docker Compose deployment
- Automated smoke tests
- Health checks

### M5: Monitoring & Submission (10M)
- Request/response logging
- Metrics tracking
- Final submission package

## Setup & Usage

```bash
# Clone and setup
git clone <repo>
cd MLOPS
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Initialize DVC
dvc init

# Download dataset and preprocess
python src/data/download_data.py
python src/data/preprocessing.py

# Train model
python src/models/train.py

# Run tests
pytest tests/

# Run API locally
uvicorn src.api.main:app --reload

# Build and run Docker
docker build -t cats-dogs-model .
docker run -p 8000:8000 cats-dogs-model

# Deploy (choose one)
kubectl apply -f deployment/kubernetes/
# or
docker-compose -f deployment/docker-compose/docker-compose.yml up
```

## CI/CD Pipelines

- **GitHub Actions**: Automated testing, building, and pushing on push to main
- **Smoke Tests**: Post-deployment health checks
- **Model Registry**: Artifact versioning and tracking

## Monitoring

- Request/response logging
- Latency tracking
- Model performance metrics
- Health endpoint monitoring