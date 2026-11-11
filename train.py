"""Train and track a California Housing regression model with MLflow."""

import argparse

import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.models import infer_signature
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tracking-uri",
        default=None,
        help="MLflow tracking URI (defaults to the local mlflow.db SQLite database).",
    )
    parser.add_argument(
        "--experiment-name",
        default="california-housing",
        help="Name of the MLflow experiment.",
    )
    parser.add_argument(
        "--n-estimators",
        type=int,
        default=100,
        help="Number of trees in the random forest.",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Fraction of the dataset reserved for evaluation.",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=42,
        help="Random seed for the split and model.",
    )
    args = parser.parse_args()
    if args.n_estimators < 1:
        parser.error("--n-estimators must be at least 1")
    if not 0 < args.test_size < 1:
        parser.error("--test-size must be between 0 and 1")
    return args


def main():
    args = parse_args()
    tracking_uri = args.tracking_uri or "sqlite:///mlflow.db"
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(args.experiment_name)

    housing = fetch_california_housing(as_frame=True)
    features = housing.data
    target = housing.target
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=args.test_size,
        random_state=args.random_state,
    )

    model = RandomForestRegressor(
        n_estimators=args.n_estimators,
        random_state=args.random_state,
        n_jobs=-1,
    )

    with mlflow.start_run() as run:
        mlflow.log_params(
            {
                "model_type": "RandomForestRegressor",
                "n_estimators": args.n_estimators,
                "test_size": args.test_size,
                "random_state": args.random_state,
                "training_rows": len(x_train),
                "test_rows": len(x_test),
            }
        )
        mlflow.set_tag("dataset", "California Housing")
        mlflow.set_tag("dataset_source", "scikit-learn")

        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        metrics = {
            "rmse": mean_squared_error(y_test, predictions) ** 0.5,
            "mae": mean_absolute_error(y_test, predictions),
            "r2": r2_score(y_test, predictions),
        }
        mlflow.log_metrics(metrics)

        input_example = x_test.head(5)
        signature = infer_signature(input_example, model.predict(input_example))
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            signature=signature,
            input_example=input_example,
            skops_trusted_types=["sklearn.tree._tree.Tree"],
        )

    print(f"MLflow run ID: {run.info.run_id}")
    print(f"Experiment: {args.experiment_name}")
    print(f"Tracking URI: {tracking_uri}")
    for metric_name, value in metrics.items():
        print(f"{metric_name}: {value:.4f}")
    print(
        "Start the MLflow UI with: "
        "py -3.11 -m mlflow ui --backend-store-uri sqlite:///mlflow.db"
    )


if __name__ == "__main__":
    main()
