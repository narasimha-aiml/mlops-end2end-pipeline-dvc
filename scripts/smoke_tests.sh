#!/bin/bash

set -e

API_URL="http://localhost:8000"
MAX_RETRIES=60
RETRY_INTERVAL=2

echo "Running smoke tests..."

echo "Waiting for API to be ready..."
for i in $(seq 1 $MAX_RETRIES); do
    if curl -f "$API_URL/health" > /dev/null 2>&1; then
        echo "API is ready!"
        break
    fi
    if [ $i -eq $MAX_RETRIES ]; then
        echo "API failed to start after $((MAX_RETRIES * RETRY_INTERVAL)) seconds"
        exit 1
    fi
    echo "Attempt $i/$MAX_RETRIES. Waiting..."
    sleep $RETRY_INTERVAL
done

echo "Testing health check endpoint..."
HEALTH_RESPONSE=$(curl -s "$API_URL/health")
echo "Health response: $HEALTH_RESPONSE"

if echo "$HEALTH_RESPONSE" | grep -q '"status"'; then
    echo "✓ Health check passed"
else
    echo "✗ Health check failed"
    exit 1
fi

echo "Testing model info endpoint..."
MODEL_INFO=$(curl -s "$API_URL/model-info")
echo "Model info: $MODEL_INFO"

if echo "$MODEL_INFO" | grep -q '"status"'; then
    echo "✓ Model info endpoint working"
else
    echo "✗ Model info endpoint failed"
    exit 1
fi

echo "All smoke tests passed!"
exit 0