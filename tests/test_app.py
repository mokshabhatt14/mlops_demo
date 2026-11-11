import unittest
from pathlib import Path

from flask.testing import FlaskClient
from streamlit.testing.v1 import AppTest

from app import create_app


class PredictionApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config.update(TESTING=True)
        cls.client: FlaskClient = cls.app.test_client()
        cls.sample = {
            "MedInc": 8.3,
            "HouseAge": 21,
            "AveRooms": 6.9,
            "AveBedrms": 1.1,
            "Population": 240,
            "AveOccup": 2.1,
            "Latitude": 37.77,
            "Longitude": -122.42,
        }

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "ok")

    def test_single_prediction(self):
        response = self.client.post("/predict", json={"instances": [self.sample]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["predictions"]), 1)
        self.assertGreater(response.json["predictions"][0], 0)
        self.assertEqual(response.json["unit"], "$100,000")

    def test_batch_prediction(self):
        response = self.client.post(
            "/predict",
            json={"instances": [self.sample, self.sample]},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json["predictions"]), 2)

    def test_invalid_feature_names_return_bad_request(self):
        response = self.client.post(
            "/predict",
            json={"instances": [{"MedInc": 8.3}]},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("missing_features", response.json)

    def test_non_numeric_feature_returns_bad_request(self):
        instance = {**self.sample, "HouseAge": "old"}
        response = self.client.post("/predict", json={"instances": [instance]})
        self.assertEqual(response.status_code, 400)

    def test_streamlit_form_displays_prediction(self):
        app_test = AppTest.from_file(
            str(Path(__file__).resolve().parents[1] / "streamlit_app.py"),
            default_timeout=90,
        ).run()
        self.assertFalse(app_test.exception)
        income = next(
            item
            for item in app_test.number_input
            if item.label == "Typical yearly household income ($)"
        )
        self.assertEqual(income.value, 83000)
        submit_index = next(
            index
            for index, button in enumerate(app_test.button)
            if button.label == "Estimate neighborhood value"
        )
        app_test.button[submit_index].click().run(timeout=90)
        self.assertFalse(app_test.exception)
        self.assertTrue(
            any(metric.label == "Estimated value" for metric in app_test.metric)
        )


if __name__ == "__main__":
    unittest.main()
