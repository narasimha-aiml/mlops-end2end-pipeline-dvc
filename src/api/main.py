import os
import logging
import json
import time
import base64
import io
from typing import Optional
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from PIL import Image

from src.inference.predictor import ModelPredictor
from src.api.schemas import HealthCheckResponse, PredictionResponse, ErrorResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cats vs Dogs Classification API",
    description="REST API for binary image classification",
    version="1.0.0"
)

predictor = None
request_counter = 0
latency_sum = 0.0
request_log_path = "logs/requests.log"


@app.on_event("startup")
async def startup_event():
    """Initialize model on startup."""
    global predictor

    model_path = os.getenv('MODEL_PATH', 'models/cats_dogs_model.h5')

    if os.path.exists(model_path):
        predictor = ModelPredictor(model_path)
        logger.info(f"Model loaded from {model_path}")
    else:
        logger.warning(f"Model not found at {model_path}")
        predictor = ModelPredictor()

    Path("logs").mkdir(exist_ok=True)
    logger.info("API startup complete")


def log_request(endpoint: str, status: str, latency: float, details: dict = None):
    """Log API requests for monitoring."""
    log_entry = {
        'timestamp': time.time(),
        'endpoint': endpoint,
        'status': status,
        'latency_ms': latency * 1000,
        'details': details or {}
    }

    with open(request_log_path, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    start_time = time.time()

    is_ready = predictor is not None and predictor.is_ready()

    response = HealthCheckResponse(
        status="healthy" if is_ready else "degraded",
        model_loaded=is_ready,
        message="Model loaded and ready" if is_ready else "Model not available"
    )

    latency = time.time() - start_time
    log_request("/health", response.status, latency)

    return response


@app.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    """
    Predict class for uploaded image.

    Args:
        file: Image file (jpg, png, etc.)

    Returns:
        Prediction with class name and probabilities
    """
    start_time = time.time()
    global request_counter, latency_sum

    if not predictor or not predictor.is_ready():
        raise HTTPException(status_code=503, detail="Model not loaded")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_resized = cv2.resize(image_rgb, (224, 224))
        image_normalized = image_resized.astype(np.float32) / 255.0
        image_batch = np.expand_dims(image_normalized, axis=0)

        probabilities = predictor.model.predict(image_batch, verbose=0)
        predicted_class_idx = np.argmax(probabilities[0])
        predicted_class = predictor.class_names[predicted_class_idx]
        confidence = float(probabilities[0][predicted_class_idx])

        response = PredictionResponse(
            class_name=predicted_class,
            confidence=confidence,
            probabilities={
                predictor.class_names[i]: float(probabilities[0][i])
                for i in range(len(predictor.class_names))
            }
        )

        latency = time.time() - start_time
        request_counter += 1
        latency_sum += latency

        log_request(
            "/predict",
            "success",
            latency,
            {'predicted_class': predicted_class, 'confidence': confidence}
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        log_request("/predict", "error", time.time() - start_time, {'error': str(e)})
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict-base64")
async def predict_base64(base64_image: str):
    """
    Predict from base64 encoded image.

    Args:
        base64_image: Base64 encoded image string

    Returns:
        Prediction results
    """
    start_time = time.time()

    if not predictor or not predictor.is_ready():
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        image_data = base64.b64decode(base64_image)
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image data")

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_resized = cv2.resize(image_rgb, (224, 224))
        image_normalized = image_resized.astype(np.float32) / 255.0
        image_batch = np.expand_dims(image_normalized, axis=0)

        probabilities = predictor.model.predict(image_batch, verbose=0)
        predicted_class_idx = np.argmax(probabilities[0])
        predicted_class = predictor.class_names[predicted_class_idx]
        confidence = float(probabilities[0][predicted_class_idx])

        response = PredictionResponse(
            class_name=predicted_class,
            confidence=confidence,
            probabilities={
                predictor.class_names[i]: float(probabilities[0][i])
                for i in range(len(predictor.class_names))
            }
        )

        latency = time.time() - start_time
        log_request(
            "/predict-base64",
            "success",
            latency,
            {'predicted_class': predicted_class}
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Base64 prediction error: {str(e)}")
        log_request("/predict-base64", "error", time.time() - start_time)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.get("/metrics")
async def get_metrics():
    """Get API metrics."""
    try:
        with open(request_log_path, 'r') as f:
            logs = [json.loads(line) for line in f]

        total_requests = len(logs)
        successful = len([l for l in logs if l.get('status') == 'success'])
        avg_latency = (latency_sum / request_counter * 1000) if request_counter > 0 else 0

        return {
            'total_requests': total_requests,
            'successful_requests': successful,
            'average_latency_ms': avg_latency,
            'uptime': "available"
        }
    except Exception as e:
        logger.error(f"Error retrieving metrics: {str(e)}")
        return {'error': str(e)}


@app.get("/model-info")
async def model_info():
    """Get model information."""
    if not predictor:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return predictor.get_model_info()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
