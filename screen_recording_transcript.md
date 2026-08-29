# Screen Recording Transcript — MLOps Assignment 2
Target length: under 5 minutes. Practice once before recording so the pacing feels natural — you don't need to read this word-for-word, just hit each beat.

---

## [0:00 – 0:30] Intro + Project Structure

**Say:**
"Hi, this is my MLOps Assignment 2 demo — an end-to-end pipeline for binary cats vs dogs classification. Let me walk through the full workflow from code to deployed prediction."

**Run:**
```
cd D:\BitsPIlani\2025\sem3\MLOPS\Assignment2_MLOPS\Assignment2_MLOPS
dir
```

**Say while it shows:**
"Here's the structure — source code under src, tests, deployment manifests for Docker Compose and Kubernetes, CI/CD workflows under .github, and DVC for data and pipeline versioning."

---

## [0:30 – 1:00] Data & Pipeline Versioning (M1)

**Run:**
```
type dvc.yaml
dvc dag
```

**Say:**
"The DVC pipeline has two stages — prepare, which preprocesses raw images into train/val/test splits, and train, which trains the CNN. Both stages and the dataset itself are version-controlled with DVC, so results are reproducible."

---

## [1:00 – 1:45] Model Training & Experiment Tracking (M1)

**Run:**
```
dvc repro
```

**Say (while it runs, or cut to the tail of a completed run):**
"Running dvc repro re-executes the pipeline end to end — preprocessing then training — and everything is logged to MLflow: parameters, metrics, and artifacts."

**Switch to browser, MLflow UI at localhost:5000:**

**Say:**
"Here's the MLflow run — you can see the model type, epoch count, batch size as logged parameters, and test accuracy and loss as metrics, along with the saved model artifact."

---

## [1:45 – 2:15] Automated Testing (M3)

**Run:**
```
pytest tests/ -v --cov=src
```

**Say:**
"18 unit tests covering both the data preprocessing functions and the model inference utilities — all passing."

---

## [2:15 – 2:45] Containerization (M2)

**Run:**
```
docker build -t cats-dogs-classifier .
docker images | findstr cats-dogs
```

**Say:**
"The inference service is packaged with FastAPI and containerized with Docker. Here's the image building successfully with all pinned dependencies from requirements.txt."

---

## [2:45 – 3:45] Deployment & API Testing (M2, M4)

**Run:**
```
docker-compose -f deployment/docker-compose/docker-compose.yml up -d --build
docker ps
```

**Say:**
"Deploying via Docker Compose — here's the container running and healthy."

**Run:**
```
curl http://localhost:8000/health
curl http://localhost:8000/model-info
curl -X POST http://localhost:8000/predict -F "file=@data\raw\cats\1.jpg"
curl http://localhost:8000/metrics
```

**Say (narrate results as they appear):**
"Health check confirms the model is loaded. Model info shows the input shape and classes. Here's a live prediction on a cat image — returning class, confidence, and probabilities. And the metrics endpoint tracks request count, success rate, and latency for monitoring."

---

## [3:45 – 4:15] Smoke Tests (M4)

**Switch to Git Bash:**
```
bash scripts/smoke_tests.sh
```

**Say:**
"Post-deployment smoke tests automatically verify the health and model-info endpoints are responding correctly — this is what would gate the CI/CD pipeline from deploying a broken build."

---

## [4:15 – 4:45] CI/CD Pipeline (M3, M4)

**Switch to browser, GitHub repo → Actions tab:**

**Say:**
"On every push, GitHub Actions runs this CI pipeline — installing dependencies, running the test suite, building the Docker image, and scanning it for vulnerabilities with Trivy. Here's a successful run."

*(If you have a CD workflow run to show too, mention it briefly here.)*

---

## [4:45 – 5:00] Wrap-up

**Run:**
```
docker-compose -f deployment/docker-compose/docker-compose.yml down
```

**Say:**
"That's the complete pipeline — from a code change, through automated testing and containerization, to a deployed, monitored prediction service. Thanks for watching."

---

## Notes for recording
- Keep terminal font large enough to read on screen (14–16pt).
- If `dvc repro` or `docker build` takes long, pause recording, let it finish, then resume/cut rather than showing dead air.
- Have a real test image path ready ahead of time (e.g., `data\raw\cats\1.jpg`) so the predict command doesn't stall while you find one.
- If anything errors on camera, don't panic-edit — a single quick retry showing you diagnosing it live can actually work in your favor, but don't let it eat your 5-minute budget.
