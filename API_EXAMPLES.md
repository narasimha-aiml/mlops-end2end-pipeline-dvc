# API Testing Examples

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Health Check
**GET /health**

Check if the service is running and model is loaded.

**Example:**
```bash
curl -X GET http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "message": "Model loaded and ready"
}
```

---

### 2. Predict (Image File)
**POST /predict**

Predict class for an uploaded image file.

**Parameters:**
- `file` (multipart/form-data): Image file (jpg, png, etc.)

**Example:**
```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@/path/to/cat_image.jpg"
```

**Response:**
```json
{
  "class_name": "cat",
  "confidence": 0.92,
  "probabilities": {
    "cat": 0.92,
    "dog": 0.08
  }
}
```

---

### 3. Predict (Base64 Image)
**POST /predict-base64**

Predict using base64 encoded image data.

**Request Body:**
```json
{
  "base64_image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/predict-base64 \
  -H "Content-Type: application/json" \
  -d '{"base64_image": "iVBORw0KGgo..."}'
```

**Response:**
```json
{
  "class_name": "dog",
  "confidence": 0.87,
  "probabilities": {
    "cat": 0.13,
    "dog": 0.87
  }
}
```

---

### 4. Metrics
**GET /metrics**

Get API performance metrics.

**Example:**
```bash
curl -X GET http://localhost:8000/metrics
```

**Response:**
```json
{
  "total_requests": 42,
  "successful_requests": 40,
  "average_latency_ms": 245.3,
  "success_rate": 0.952
}
```

---

### 5. Model Info
**GET /model-info**

Get information about the loaded model.

**Example:**
```bash
curl -X GET http://localhost:8000/model-info
```

**Response:**
```json
{
  "status": "Ready",
  "model_path": "models/cats_dogs_model.h5",
  "input_shape": [224, 224, 3],
  "classes": ["cat", "dog"],
  "num_parameters": 1234567
}
```

---

## Python Client Examples

### Using requests library

```python
import requests
import json

API_URL = "http://localhost:8000"

# 1. Health check
response = requests.get(f"{API_URL}/health")
print(response.json())

# 2. Predict with image file
files = {'file': open('cat_image.jpg', 'rb')}
response = requests.post(f"{API_URL}/predict", files=files)
print(response.json())

# 3. Get metrics
response = requests.get(f"{API_URL}/metrics")
print(response.json())

# 4. Model info
response = requests.get(f"{API_URL}/model-info")
print(response.json())
```

### Using base64 encoding

```python
import requests
import base64

API_URL = "http://localhost:8000"

# Read image and encode to base64
with open('dog_image.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode()

# Make prediction
response = requests.post(
    f"{API_URL}/predict-base64",
    json={"base64_image": image_data}
)

print(response.json())
```

---

## cURL Testing Commands

### Batch predict multiple images

```bash
#!/bin/bash

for image in images/*.jpg; do
    echo "Predicting for: $image"
    curl -X POST http://localhost:8000/predict \
      -F "file=@$image" \
      -H "Accept: application/json" | jq .
    echo "---"
done
```

### Load test

```bash
#!/bin/bash

for i in {1..100}; do
    curl -X POST http://localhost:8000/predict \
      -F "file=@test_image.jpg" \
      -o /dev/null \
      -s -w "Time: %{time_total}s\n"
done
```

---

## HTTP Status Codes

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad request (invalid image format) |
| 500 | Server error (processing failed) |
| 503 | Service unavailable (model not loaded) |

---

## Error Handling

### Missing model
```json
{
  "detail": "Model not loaded"
}
```
Status: 503

### Invalid image format
```json
{
  "detail": "Invalid image format"
}
```
Status: 400

### Processing error
```json
{
  "detail": "Prediction failed: [error details]"
}
```
Status: 500

---

## Performance Tips

1. **Batch Predictions**: Make multiple requests concurrently
2. **Image Size**: Ensure images are reasonably sized
3. **Connection Pooling**: Use session objects in Python client
4. **Compression**: Enable gzip compression for large payloads

---

## OpenAPI Documentation

When service is running, access interactive docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
