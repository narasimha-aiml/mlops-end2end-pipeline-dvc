#!/bin/bash

SERVICE_URL="http://localhost:8000/health"
MAX_RETRIES=90
RETRY_INTERVAL=1

echo "Waiting for service to be healthy..."

for i in $(seq 1 $MAX_RETRIES); do
    if curl -sf "$SERVICE_URL" > /dev/null 2>&1; then
        echo "Service is healthy!"
        exit 0
    fi

    if [ $((i % 10)) -eq 0 ]; then
        echo "Still waiting... ($i/$MAX_RETRIES)"
    fi

    sleep $RETRY_INTERVAL
done

echo "Service failed to become healthy after $((MAX_RETRIES * RETRY_INTERVAL)) seconds"
exit 1