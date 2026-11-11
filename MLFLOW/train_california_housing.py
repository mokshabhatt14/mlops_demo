from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


def main():
    housing = fetch_california_housing()
    x_train, x_test, y_train, y_test = train_test_split(
        housing.data, housing.target, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    print(f"R² score: {r2_score(y_test, predictions):.3f}")
    print(f"Mean absolute error: {mean_absolute_error(y_test, predictions):.3f}")
    print(f"Root mean squared error: {mean_squared_error(y_test, predictions) ** 0.5:.3f}")


if __name__ == "__main__":
    main()