# California Housing Estimator

A trained California Housing model with a friendly Streamlit interface, Flask
prediction API, and Docker Compose deployment.

## Run with Docker

Install Docker Desktop, then run:

```powershell
docker compose up --build
```

- Web app: <http://localhost:8501>
- Prediction API health: <http://localhost:5001/health>

Stop both containers with `docker compose down`.

The trained model is stored with Git LFS. Install Git LFS before cloning:

```powershell
git lfs install
git clone <repository-url>
```

See [OVERVIEW.md](OVERVIEW.md) for setup details, the Postman request example,
training instructions, and an explanation of the model's estimates.

## Continuous integration

GitHub Actions runs the app tests and builds the Docker image whenever changes
are pushed to `main`/`master` or a pull request targets those branches. The
workflow checks out the model from Git LFS.
