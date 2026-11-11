import unittest
from pathlib import Path

from flask.testing import FlaskClient
from streamlit.testing.v1 import AppTest

from app import create_app
from ui_helpers import build_model_features, make_house_scene


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

    def test_house_details_build_model_features(self):
        features = build_model_features(
            income_dollars=90_000,
            house_age=12,
            bedrooms=4,
            bathrooms=3,
            kitchens=2,
            population=500,
            occupancy=2.5,
            latitude=36.0,
            longitude=-120.0,
        )
        self.assertEqual(
            list(features.columns),
            [
                "MedInc",
                "HouseAge",
                "AveRooms",
                "AveBedrms",
                "Population",
                "AveOccup",
                "Latitude",
                "Longitude",
            ],
        )
        self.assertEqual(features.iloc[0]["MedInc"], 9)
        self.assertEqual(features.iloc[0]["AveRooms"], 10)
        self.assertEqual(features.iloc[0]["AveBedrms"], 4)

    def test_house_animation_shows_dog_and_door_state(self):
        scene = make_house_scene(4, 3, 2, 2, True)
        self.assertIn("Your dog says hi!", scene)
        self.assertIn("4 bedrooms", scene)
        self.assertIn("Door open", scene)
        self.assertIn("prefers-reduced-motion", scene)

    def test_streamlit_house_designer_displays_prediction(self):
        app_test = AppTest.from_file(
            str(Path(__file__).resolve().parents[1] / "streamlit_app.py"),
            default_timeout=90,
        ).run()
        self.assertFalse(app_test.exception)
        self.assertEqual(
            next(
                item
                for item in app_test.number_input
                if item.label == "Typical yearly household income"
            ).value,
            83_000,
        )
        self.assertEqual(len(app_test.slider), 4)
        submit_index = next(
            index
            for index, button in enumerate(app_test.button)
            if button.label == "✨ Estimate neighborhood home value"
        )
        app_test.button[submit_index].click().run(timeout=90)
        self.assertFalse(app_test.exception)
        self.assertTrue(
            any(
                "estimated median home value" in message.value.lower()
                for message in app_test.success
            )
        )


if __name__ == "__main__":
    unittest.main()
