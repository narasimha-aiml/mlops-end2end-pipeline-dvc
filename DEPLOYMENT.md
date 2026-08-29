# Deployment Guide

## Option 1: Docker Compose (Recommended for Local Deployment)

### Prerequisites
- Docker and Docker Compose installed
- Model file at `models/cats_dogs_model.h5`

### Steps

1. Build and start the service:
```bash
docker-compose -f deployment/docker-compose/docker-compose.yml up -d
```

2. Verify the service is running:
```bash
curl http://localhost:8000/health
```

3. Test prediction:
```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@path/to/image.jpg"
```

4. Stop the service:
```bash
docker-compose -f deployment/docker-compose/docker-compose.yml down
```

## Option 2: Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (kind, minikube, or cloud)
- kubectl configured
- Docker image pushed to registry

### Steps

1. Build and push Docker image:
```bash
docker build -t your-registry/cats-dogs-classifier:latest .
docker push your-registry/cats-dogs-classifier:latest
```

2. Update image reference in `deployment/kubernetes/deployment.yaml`

3. Create namespace and deploy:
```bash
kubectl create namespace mlops
kubectl apply -f deployment/kubernetes/deployment.yaml -n mlops
kubectl apply -f deployment/kubernetes/service.yaml -n mlops
```

4. Check deployment status:
```bash
kubectl get deployments -n mlops
kubectl get pods -n mlops
kubectl get svc -n mlops
```

5. Port forward to access service:
```bash
kubectl port-forward svc/cats-dogs-service 8000:80 -n mlops
```

6. Test the API:
```bash
curl http://localhost:8000/health
```

7. View logs:
```bash
kubectl logs -f deployment/cats-dogs-classifier -n mlops
```

8. Delete deployment:
```bash
kubectl delete namespace mlops
```

## Monitoring

### View Request Logs
```bash
# Docker Compose
docker exec cats-dogs-classifier cat /app/logs/requests.log

# Kubernetes
kubectl logs pod/<pod-name> -n mlops
```

### View Metrics
```bash
curl http://localhost:8000/metrics
```

### Check Model Info
```bash
curl http://localhost:8000/model-info
```

## Health Check Configuration

Both deployments include health checks:
- Interval: 30 seconds
- Timeout: 10 seconds
- Failure threshold: 3
- Start period: 40 seconds

## Smoke Tests

Run smoke tests after deployment:
```bash
bash scripts/smoke_tests.sh
```

## Troubleshooting

### Service won't start
1. Check logs: `docker logs cats-dogs-classifier`
2. Verify model file exists: `ls -la models/cats_dogs_model.h5`
3. Check port availability: `lsof -i :8000`

### API responds with 503
- Model not loaded. Ensure model file exists and is accessible
- Check logs for loading errors

### Health check fails
- Service may not be ready. Wait 40 seconds for startup
- Check API logs for errors
