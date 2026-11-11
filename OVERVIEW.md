# California Housing MLflow Project: Step-by-Step Guide

This project trains a machine-learning model to estimate California house
values. MLflow records each training run so you can review its settings,
evaluation results, and saved model.

## What is in this project?

- `train.py` — downloads the data, trains and evaluates the model, and logs
  everything to MLflow.
- `app.py` — loads the trained MLflow model and provides HTTP health and
  prediction endpoints.
- `streamlit_app.py` — provides an interactive web form for estimating a
  California neighborhood's median house value.
- `models/california_housing/` — portable copy of the trained model used by
  the Streamlit app, Flask API, and Docker image.
- `Dockerfile` and `compose.yaml` — build and run the web app as a container.
- `requirements.txt` — lists the Python packages the project needs.
- `mlflow.db` — local SQLite database containing MLflow experiment and run
  information. It is created when you run the pipeline.
- `mlruns/` — local MLflow model and other run artifacts. It is created when
  you run the pipeline.
- `.venv/` — the recommended Python virtual environment. Create it using the
  instructions below; it was not used for the first run.

Generated tracking files are local and are excluded from Git by `.gitignore`.

## Set up the project on Windows

Open PowerShell in the project folder:

```powershell
cd C:\Users\AIML-LAB1-35\Downloads\MLFLOWW
```

### 1. Create a virtual environment

A virtual environment keeps this project's Python packages separate from other
Python projects on your computer.

```powershell
py -3.11 -m venv .venv
```

This creates the environment here:
`C:\Users\AIML-LAB1-35\Downloads\MLFLOWW\.venv`

### 2. Activate it and install the packages

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

When activation succeeds, PowerShell usually shows `(.venv)` at the start of
the prompt. If PowerShell blocks activation, use the environment's Python
without activating it:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Run the training pipeline

With the environment activated:

```powershell
python train.py
```

Or, without activating the environment:

```powershell
.\.venv\Scripts\python.exe train.py
```

The first run downloads the California Housing dataset using scikit-learn, so
an internet connection is needed. The download is cached by scikit-learn and
the dataset is not copied into the project.

## What the pipeline does

1. **Sets up MLflow tracking.** The default tracking database is the local
   SQLite file `mlflow.db`. The experiment is named `california-housing`.
2. **Loads the dataset.** The dataset contains eight numeric features for each
   area, such as median income, house age, and location. The prediction target
   is median house value, measured in units of $100,000.
3. **Splits the data.** By default, 80% is used to train the model and 20% is
   held back to test it. A fixed random seed makes the split repeatable.
4. **Trains a model.** A Random Forest regressor with 100 decision trees learns
   patterns from the training data.
5. **Measures performance.** The model predicts values for the held-back test
   data, then calculates:
   - **RMSE** — typical prediction error, with larger errors penalized more.
     Lower is better.
   - **MAE** — average absolute prediction error. Lower is better.
   - **R-squared (`R²`)** — how much of the variation in house values the model
     explains. A value closer to 1 is generally better.
6. **Saves the run to MLflow.** MLflow records the model settings, data row
   counts, evaluation metrics, dataset information, and trained model artifact.
   The model also includes an input example and a signature describing its
   expected inputs and outputs.

## View the experiment in MLflow

In a second PowerShell window, go to the project folder and start the UI using
the same Python environment:

```powershell
cd C:\Users\AIML-LAB1-35\Downloads\MLFLOWW
.\.venv\Scripts\Activate.ps1
python -m mlflow ui --backend-store-uri sqlite:///mlflow.db
```

Open the address printed in the terminal, normally
`http://127.0.0.1:5000`. Select the `california-housing` experiment to compare
runs and inspect their metrics and model artifacts. Keep the terminal running
while you use the UI; press `Ctrl+C` there to stop it.

## Change the training settings

For example, to train with 150 trees and a 25% test set:

```powershell
python train.py --n-estimators 150 --test-size 0.25 --random-state 7
```

Available options:

- `--n-estimators` — number of trees (default: `100`).
- `--test-size` — fraction of data used for testing (default: `0.2`).
- `--random-state` — random seed for repeatable results (default: `42`).
- `--experiment-name` — MLflow experiment name (default:
  `california-housing`).
- `--tracking-uri` — MLflow tracking server or database URI. Only change this
  if you intend to use another tracking store.

Each run is saved separately in MLflow. Running the pipeline again does not
replace the earlier run.

## The run already completed

The pipeline was run once before a virtual environment was created, using the
computer's global Python 3.11 installation. Its completed MLflow run is:

- **Run ID:** `16dbfb254c4b4c94a7ca971ba85b8837`
- **Experiment:** `california-housing`
- **RMSE:** `0.5060`
- **MAE:** `0.3277`
- **R²:** `0.8046`

The run and its model artifact were verified in MLflow. Creating and activating
`.venv` is recommended for future runs; the first run remains in `mlflow.db`.

## Use the model through the Flask API

Install the requirements if you have not already done so, and make sure the
trained model and `mlflow.db` are present. Start the API from the project
folder:

```powershell
python app.py
```

By default, the API loads the bundled model and listens on
`http://127.0.0.1:5001`. You can override the model with the `MODEL_URI`
environment variable:

```powershell
$env:MODEL_URI = "runs:/16dbfb254c4b4c94a7ca971ba85b8837/model"
python app.py
```

The API has two endpoints:

- `GET /health` — returns `{"status":"ok", ...}` when the model has loaded.
- `POST /predict` — accepts one or more feature objects and returns predicted
  median house values. Predictions are in units of `$100,000` (for example,
  `2.5` means about `$250,000`).

### Try it with Postman

1. Start `python app.py` and leave its terminal open.
2. In Postman, create a **GET** request to `http://127.0.0.1:5001/health`.
3. Create a **POST** request to `http://127.0.0.1:5001/predict`.
4. Select **Body → raw → JSON** and send an object with all eight model input
   features. For example:

```json
{
  "instances": [
    {
      "MedInc": 8.3,
      "HouseAge": 21,
      "AveRooms": 6.9,
      "AveBedrms": 1.1,
      "Population": 240,
      "AveOccup": 2.1,
      "Latitude": 37.8,
      "Longitude": -122.4
    }
  ]
}
```

A successful response looks like this (the number is an example):

```json
{
  "predictions": [4.1],
  "unit": "$100,000"
}
```

You can include several objects in `instances` to make a batch prediction. Each
object must contain exactly these feature names: `MedInc`, `HouseAge`,
`AveRooms`, `AveBedrms`, `Population`, `AveOccup`, `Latitude`, and `Longitude`.
Every value must be a finite number. Invalid input gets a JSON error response
with HTTP status 400.

The included Flask server is for local development and testing, not production
deployment. To call it from another device on a trusted network, set
`FLASK_HOST` to `0.0.0.0`, allow the chosen port through the host firewall, and
use the computer's network address in Postman. Do not expose this development
server directly to the public internet.

## Use the Streamlit web interface

The Streamlit app opens with an interactive California map: click a city marker
or choose a city from the list. A small animated house and dog appear next;
open or close the door and adjust the bedroom, bathroom, kitchen, and floor
sliders to customize the scene. The app asks for neighborhood income and home
age before estimating its median home value in dollars.

The model was trained on neighborhood statistics, not individual home layouts.
Bedroom count is used as an approximate bedroom input, and bedroom, bathroom,
and kitchen counts are combined into a rough room-count input. The number of
floors changes the illustration only, not the prediction. The app explains
these limitations next to the estimate. It loads the bundled model, so it
doesn't need the MLflow tracking database or a dataset download to predict.

With the virtual environment activated, install requirements and start the
app:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Open the local address Streamlit prints, normally `http://localhost:8501`.

## Package and run with Docker

The Docker image contains the Streamlit app, its Python dependencies, and the
trained model. It does not need your local `.venv`, `mlflow.db`, or MLflow
tracking artifacts. Install and start Docker Desktop first, then open
PowerShell in the project folder.

Build the image and start the application with Docker Compose. Compose starts
both the Streamlit web interface and the Flask prediction API:

```powershell
docker compose up --build
```

Open `http://localhost:8501` in a browser. The API is available at
`http://localhost:5001`; for example, `GET /health` checks it and
`POST /predict` accepts the JSON request described above. Keep the terminal
running while using the application; press `Ctrl+C` to stop it. To stop the
Compose services:

```powershell
docker compose down
```

You can also build and run only the Streamlit interface without Compose:

```powershell
docker build -t california-housing-app .
docker run --rm -p 8501:8501 california-housing-app
```

The app's Docker health check is available at
`http://localhost:8501/_stcore/health`. Docker containers can be moved to
another Docker-compatible computer by transferring the built image or building
it from this project there. The image includes the trained model artifact.

## Stop using the virtual environment

When you are finished working in the project, deactivate the environment:

```powershell
deactivate
```
