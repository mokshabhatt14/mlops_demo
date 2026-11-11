"""Friendly Streamlit interface for the California Housing model."""

from pathlib import Path

import mlflow.pyfunc
import pandas as pd
import streamlit as st


MODEL_PATH = Path(__file__).resolve().parent / "models" / "california_housing"
FEATURES = (
    "MedInc",
    "HouseAge",
    "AveRooms",
    "AveBedrms",
    "Population",
    "AveOccup",
    "Latitude",
    "Longitude",
)
LOCATIONS = {
    "San Francisco": (37.77, -122.42),
    "Los Angeles": (34.05, -118.24),
    "San Diego": (32.72, -117.16),
    "Sacramento": (38.58, -121.49),
    "Oakland": (37.80, -122.27),
    "Fresno": (36.74, -119.79),
    "Enter a different location": None,
}


@st.cache_resource
def load_model():
    return mlflow.pyfunc.load_model(str(MODEL_PATH))


st.set_page_config(
    page_title="California Home Value Estimator",
    page_icon="🏡",
    layout="centered",
)

st.title("🏡 California Home Value Estimator")
st.markdown(
    "Get a quick estimate for a **neighborhood**, not an individual house. "
    "Start with the three details below. You can add more information if you "
    "have it."
)

with st.container(border=True):
    st.subheader("1. Where is the neighborhood?")
    city = st.selectbox(
        "Choose the closest city",
        options=list(LOCATIONS),
        help=(
            "The city gives the model an approximate location. Choose the "
            "closest city, or enter coordinates for another California location."
        ),
    )
    coordinates = LOCATIONS[city]
    if coordinates is None:
        location_col1, location_col2 = st.columns(2)
        with location_col1:
            latitude = st.number_input(
                "Location latitude",
                min_value=32.0,
                max_value=42.5,
                value=37.77,
                step=0.01,
                format="%.2f",
                help="California is roughly between 32 and 42.5 degrees north.",
            )
        with location_col2:
            longitude = st.number_input(
                "Location longitude",
                min_value=-125.0,
                max_value=-113.0,
                value=-122.42,
                step=0.01,
                format="%.2f",
                help="California is roughly between 125 and 113 degrees west.",
            )
    else:
        latitude, longitude = coordinates
        st.caption(f"Approximate location: {latitude:.2f}, {longitude:.2f}")

with st.form("prediction_form"):
    with st.container(border=True):
        st.subheader("2. Two details about the neighborhood")
        st.caption(
            "Estimates are fine. Leave the starting examples or change them."
        )
        income = st.number_input(
            "Typical yearly household income ($)",
            min_value=0,
            max_value=200_000,
            value=83_000,
            step=1_000,
            format="%d",
            help="Enter an approximate yearly amount in dollars. For example, enter 85,000 for $85,000.",
        )
        house_age = st.number_input(
            "Typical age of homes (years)",
            min_value=1.0,
            max_value=100.0,
            value=21.0,
            step=1.0,
            help="About how old are homes in this neighborhood?",
        )

        with st.expander("Add more neighborhood details (optional)"):
            st.caption(
                "Don't know these numbers? Leave the example values as they "
                "are. These are averages for the area, not your own home."
            )
            extra_col1, extra_col2 = st.columns(2)
            with extra_col1:
                average_rooms = st.number_input(
                    "Average rooms per household",
                    min_value=0.0,
                    max_value=150.0,
                    value=6.9,
                    step=0.1,
                    help="Approximate average number of rooms, including bedrooms.",
                )
                population = st.number_input(
                    "People in the local area",
                    min_value=0.0,
                    max_value=40000.0,
                    value=240.0,
                    step=10.0,
                    help="Approximate population of the small surrounding area.",
                )
            with extra_col2:
                average_bedrooms = st.number_input(
                    "Average bedrooms per household",
                    min_value=0.0,
                    max_value=40.0,
                    value=1.1,
                    step=0.1,
                    help="Approximate average number of bedrooms.",
                )
                average_occupancy = st.number_input(
                    "Average people per household",
                    min_value=0.01,
                    max_value=1500.0,
                    value=2.1,
                    step=0.1,
                    help="Approximate number of people living in each household.",
                )

        submitted = st.form_submit_button(
            "Estimate neighborhood value",
            type="primary",
            width="stretch",
        )

if submitted:
    model = load_model()
    values = [
        income / 10_000,
        house_age,
        average_rooms,
        average_bedrooms,
        population,
        average_occupancy,
        latitude,
        longitude,
    ]
    features = pd.DataFrame(
        [[float(value) for value in values]],
        columns=FEATURES,
    )
    prediction = float(model.predict(features)[0])
    estimated_value = prediction * 100_000

    st.divider()
    st.subheader("Your estimated neighborhood home value")
    st.metric(
        label="Estimated value",
        value=f"${estimated_value:,.0f}",
        help="An estimate for the neighborhood's median home value, not an individual home's price.",
    )
    st.caption(
        "This is a rough computer estimate, not an appraisal or guaranteed "
        "selling price. The model's training data capped recorded values at "
        "$500,000, so expensive-area estimates may be lower than actual prices."
    )

    with st.expander("See what information went into the estimate"):
        entered_values = dict(zip(FEATURES, values))
        st.dataframe(
            pd.DataFrame(
                [
                    {"Neighborhood detail": name, "Value": value}
                    for name, value in entered_values.items()
                ]
            ),
            hide_index=True,
            width="stretch",
        )

with st.sidebar:
    st.header("About this estimate")
    st.write(
        "This tool estimates the **median home value for a neighborhood** in "
        "California. It does not estimate the value of a specific house."
    )
    st.info(
        "Neighborhood income means the typical household income for the area. "
        "Enter the yearly amount in dollars; we'll convert it for the model."
    )
    st.warning(
        "The original data caps recorded home values at $500,000. Estimates "
        "near this limit may be lower than actual prices in expensive areas."
    )
    st.caption("For learning and demonstration only — not financial advice.")
