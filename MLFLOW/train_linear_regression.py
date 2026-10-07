from pathlib import Path

import mlflow
import mlflow.sklearn
from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from mlflow.tracking import MlflowClient


MLFLOW_DIR = Path(__file__).resolve().parent
TRACKING_DB = MLFLOW_DIR / "mlflow.db"
ARTIFACT_DIR = MLFLOW_DIR / "artifacts"
EXPERIMENT_NAME = "california-housing-linear-regression"


def main():
    tracking_uri = f"sqlite:///{TRACKING_DB.as_posix()}"
    mlflow.set_tracking_uri(tracking_uri)

    client = MlflowClient()
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    if experiment is None:
        experiment_id = client.create_experiment(
            EXPERIMENT_NAME, artifact_location=ARTIFACT_DIR.as_uri()
        )
    else:
        experiment_id = experiment.experiment_id
    mlflow.set_experiment(experiment_id=experiment_id)

    housing = fetch_california_housing()
    x_train, x_test, y_train, y_test = train_test_split(
        housing.data, housing.target, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    metrics = {
        "r2_score": r2_score(y_test, predictions),
        "mean_absolute_error": mean_absolute_error(y_test, predictions),
        "root_mean_squared_error": mean_squared_error(y_test, predictions) ** 0.5,
    }

    with mlflow.start_run():
        mlflow.log_params(
            {
                "model": "LinearRegression",
                "test_size": 0.2,
                "random_state": 42,
            }
        )
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model, name="model")

    for name, value in metrics.items():
        print(f"{name}: {value:.3f}")


if __name__ == "__main__":
    main()