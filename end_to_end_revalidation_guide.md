# End-to-End Revalidation Guide (Fresh venv)

Use this after deleting your Python virtual environment to rebuild and validate the entire MLOps pipeline from scratch.

**Format:** Each step has an **Instruction** (what/why) followed by the exact **Command(s)** to run — copy only the command block into your terminal.

---

## Step 1: Delete the old venv

**Instruction:** Deactivate your current environment, then remove the venv folder entirely.

**Command:**
```powershell
deactivate
cd D:\BitsPIlani\2025\sem3\MLOPS\Assignment2_MLOPS\Assignment2_MLOPS
Remove-Item -Recurse -Force venv
```

---

## Step 2: Create and activate a fresh venv

**Instruction:** Create a new isolated environment and activate it. Confirm your prompt shows `(venv)` at the start before continuing to any later step.

**Command:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

---

## Step 3: Install all dependencies

**Instruction:** Install the pinned project requirements, plus `kagglehub` (if you need to re-download data) and a `pathspec` version pin (avoids a known DVC import error from earlier).

**Command:**
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install kagglehub "pathspec<0.12,>=0.11.1"
```

---

## Step 4: Verify installs landed in the venv

**Instruction:** Each command below should print an install path inside your new `venv` folder — not a global Python path. This confirms you're actually isolated.

**Command:**
```powershell
pip show fastapi
pip show dvc
pip show tensorflow
```

---

## Step 5: Confirm your data and model are still present

**Instruction:** Deleting the venv does not delete your data or trained model — only check they survived. If they're missing, run the download script.

**Command (check):**
```powershell
dir data\raw\cats
dir data\raw\dogs
dir models\cats_dogs_model.h5
```

**Command (only if missing):**
```powershell
python src\data\download_data.py
```

---

## Step 6: Check DVC pipeline status

**Instruction:** This tells you whether anything is out of sync with `dvc.lock`. If everything is up to date, your existing outputs are trustworthy as-is.

**Command:**
```powershell
dvc status
```

---

## Step 7: Reproduce the pipeline

**Instruction:** Re-runs `prepare` and `train` stages only if something changed (data, code, or params). If nothing changed, DVC will say so and skip — that confirms reproducibility, which is the whole point of DVC. Add `--force` only if you want to force a completely fresh run regardless of change detection.

**Command:**
```powershell
dvc repro
```

**Command (force full rerun):**
```powershell
dvc repro --force
```

---

## Step 8: Verify MLflow tracking still works

**Instruction:** Open a **new terminal window**, activate the venv again in it, then start the MLflow UI. Open `http://localhost:5000` in your browser and confirm your run(s) show params, metrics, and artifacts.

**Command (in the new terminal):**
```powershell
.\venv\Scripts\Activate.ps1
mlflow ui
```

---

## Step 9: Run the test suite

**Instruction:** Back in your original terminal, run all unit tests with coverage. Expect `18 passed`.

**Command:**
```powershell
pytest tests/ -v --cov=src
```

---

## Step 10: Build the Docker image fresh

**Instruction:** Rebuilds the image using your fixed Dockerfile (with `libgl1` included), so it should complete without the earlier `libGL.so.1` error.

**Command:**
```powershell
docker build -t cats-dogs-classifier .
```

---

## Step 11: Deploy via Docker Compose

**Instruction:** Starts the full service using Docker Compose, rebuilding the image in the process. Confirm the container shows status "Up" (and eventually "healthy").

**Command:**
```powershell
docker-compose -f deployment/docker-compose/docker-compose.yml up -d --build
docker ps
```

---

## Step 12: Test all API endpoints

**Instruction:** All four calls should return valid JSON, with `model_loaded: true` on health/model-info, and a real prediction with confidence scores on predict. Swap the image filename below for any real file in your `data\raw\cats\` folder.

**Command:**
```powershell
curl http://localhost:8000/health
curl http://localhost:8000/model-info
curl -X POST http://localhost:8000/predict -F "file=@data\raw\cats\1.jpg"
curl http://localhost:8000/metrics
```

---

## Step 13: Run smoke tests

**Instruction:** This script needs Git Bash or WSL — PowerShell cannot run `.sh` files directly. Open Git Bash in the project folder for this step only. Expect it to end with "All smoke tests passed!" and exit code 0.

**Command (in Git Bash):**
```bash
bash scripts/smoke_tests.sh
```

---

## Step 14: Tear down and commit final state

**Instruction:** Stop the running containers, then commit your validated state to Git.

**Command:**
```powershell
docker-compose -f deployment/docker-compose/docker-compose.yml down
git status
git add -A
git commit -m "Final validated pipeline run"
git push
```

---

## Important reminder before you start

Deleting the venv does **not** touch your project files — only the Python environment. Before running Step 1, confirm these fixed files are still saved in your project (not reverted to originals):

- `src/data/preprocessing.py` (has a working `__main__` entry point)
- `src/models/train.py` (has a working `__main__` entry point, local MLflow URI)
- `src/inference/predictor.py` (batch prediction bug fix)
- `Dockerfile` (includes `libgl1` and `libglib2.0-0`)
- `params.yaml` (exists at project root)
- `.gitignore` (does **not** contain a bare `*.dvc` line)

If you're unsure whether any of these got overwritten or reverted, say which one and it can be resent before you proceed.
