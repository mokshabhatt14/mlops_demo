"""Interactive California home value estimator with a map and animated house."""

from pathlib import Path

import mlflow.pyfunc
import pandas as pd
import pydeck as pdk
import streamlit as st
from ui_helpers import FEATURES, build_model_features, make_house_scene


MODEL_PATH = Path(__file__).resolve().parent / "models" / "california_housing"
LOCATIONS = {
    "San Francisco": (37.77, -122.42),
    "Los Angeles": (34.05, -118.24),
    "San Diego": (32.72, -117.16),
    "Sacramento": (38.58, -121.49),
    "Oakland": (37.80, -122.27),
    "Fresno": (36.74, -119.79),
    "Bakersfield": (35.37, -119.02),
    "Monterey": (36.60, -121.89),
}


@st.cache_resource
def load_model():
    return mlflow.pyfunc.load_model(str(MODEL_PATH))


st.set_page_config(
    page_title="Little California Home",
    page_icon="🏡",
    layout="wide",
)

st.title("🏡 Find a place for your little California home")
st.markdown(
    "First pick a place on the map. Then meet your dog, open the door, and "
    "make the house your own."
)

if "selected_city" not in st.session_state:
    st.session_state.selected_city = "San Francisco"
if "last_map_city" not in st.session_state:
    st.session_state.last_map_city = None
if "door_open" not in st.session_state:
    st.session_state.door_open = False

st.subheader("1. Pick a place on the map")
st.caption("Click a dot on the map, or choose a city from the list below.")
map_data = pd.DataFrame(
    [
        {"city": city, "latitude": coordinates[0], "longitude": coordinates[1]}
        for city, coordinates in LOCATIONS.items()
    ]
)
selected_coordinates = LOCATIONS[st.session_state.selected_city]
map_layer = pdk.Layer(
    "ScatterplotLayer",
    id="cities",
    data=map_data,
    get_position="[longitude, latitude]",
    get_radius=11_000,
    get_fill_color=[53, 126, 91, 220],
    get_line_color=[255, 255, 255, 255],
    line_width_min_pixels=2,
    pickable=True,
    auto_highlight=True,
)
map_deck = pdk.Deck(
    layers=[map_layer],
    initial_view_state=pdk.ViewState(
        latitude=selected_coordinates[0],
        longitude=selected_coordinates[1],
        zoom=5.2,
        pitch=0,
    ),
    map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
    tooltip={"text": "{city}"},
)
map_event = st.pydeck_chart(
    map_deck,
    height=380,
    key=f"california_map_{st.session_state.selected_city}",
    on_select="rerun",
    selection_mode="single-object",
    width="stretch",
)
selected_map_points = map_event.selection.get("objects", {}).get("cities", [])
if selected_map_points:
    clicked_city = selected_map_points[-1].get("city")
    if clicked_city in LOCATIONS and clicked_city != st.session_state.last_map_city:
        st.session_state.selected_city = clicked_city
        st.session_state.last_map_city = clicked_city
        st.rerun()

city_names = list(LOCATIONS)
selected_city = st.selectbox(
    "Or choose a California city",
    city_names,
    index=city_names.index(st.session_state.selected_city),
    key="selected_city",
)
latitude, longitude = LOCATIONS[selected_city]
st.caption(f"Your chosen place: **{selected_city}** · {latitude:.2f}, {longitude:.2f}")

st.divider()
st.subheader("2. Meet your house and dog")
st.write("Tap the door button and watch the little door swing open.")
if st.button(
    "Close the front door" if st.session_state.door_open else "🚪 Open the front door",
    type="secondary",
    key="toggle_door",
):
    st.session_state.door_open = not st.session_state.door_open

bedroom_column, bathroom_column, kitchen_column, floor_column = st.columns(4)
with bedroom_column:
    bedrooms = st.slider("🛏️ Bedrooms", 1, 6, 3, help="How many bedrooms should the house have?")
with bathroom_column:
    bathrooms = st.slider("🛁 Bathrooms", 1, 5, 2, help="How many bathrooms should the house have?")
with kitchen_column:
    kitchens = st.slider("🍳 Kitchens", 1, 3, 1, help="How many kitchens should the house have?")
with floor_column:
    floors = st.slider("🏠 Floors", 1, 3, 1, help="Choose the number of storeys.")

st.html(
    make_house_scene(bedrooms, bathrooms, kitchens, floors, st.session_state.door_open),
    width="stretch",
)

st.divider()
st.subheader("3. Add a few neighborhood details")
st.caption(
    "These help estimate the value of the neighborhood around your home, "
    "not the exact selling price of this house."
)
income_column, age_column = st.columns(2)
with income_column:
    income = st.number_input(
        "Typical yearly household income",
        min_value=0,
        max_value=200_000,
        value=83_000,
        step=1_000,
        format="%d",
        help="An approximate yearly income for households in this area, in dollars.",
    )
with age_column:
    house_age = st.number_input(
        "Typical age of homes in this area (years)",
        min_value=1.0,
        max_value=100.0,
        value=21.0,
        step=1.0,
    )

with st.expander("If you know these neighborhood averages"):
    population_column, occupancy_column = st.columns(2)
    with population_column:
        population = st.number_input(
            "People living in a nearby area",
            min_value=0.0,
            max_value=40_000.0,
            value=240.0,
            step=10.0,
        )
    with occupancy_column:
        occupancy = st.number_input(
            "People in the average household",
            min_value=0.01,
            max_value=1_500.0,
            value=2.1,
            step=0.1,
        )

st.info(
    "The model was trained on neighborhood averages, not individual house "
    "layouts. Bedrooms help set an approximate bedroom/room count; bathrooms "
    "and kitchens only contribute to a rough room-count estimate. **The number "
    "of floors is for the animation and does not change the model prediction.**"
)

if st.button("✨ Estimate neighborhood home value", type="primary", width="stretch"):
    model_features = build_model_features(
        income_dollars=income,
        house_age=house_age,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        kitchens=kitchens,
        population=population,
        occupancy=occupancy,
        latitude=latitude,
        longitude=longitude,
    )
    prediction = float(load_model().predict(model_features)[0])
    st.balloons()
    st.success(f"Your neighborhood's estimated median home value: **${prediction * 100_000:,.0f}**")
    st.caption(
        "This is a rough educational estimate, not an appraisal. The training "
        "data caps recorded home values at $500,000, so estimates for expensive "
        "areas may be lower than actual prices."
    )
    with st.expander("See what the model received"):
        st.dataframe(
            model_features.rename(
                columns={
                    "MedInc": "Typical income (in $10,000s)",
                    "HouseAge": "Typical home age (years)",
                    "AveRooms": "Approx. rooms per household",
                    "AveBedrms": "Approx. bedrooms per household",
                    "Population": "Nearby population",
                    "AveOccup": "People per household",
                    "Latitude": "Latitude",
                    "Longitude": "Longitude",
                }
            ),
            hide_index=True,
            width="stretch",
        )

with st.sidebar:
    st.header("A note about estimates")
    st.write(
        "The California Housing model estimates a neighborhood's median value. "
        "It cannot inspect a specific home or promise what it will sell for."
    )
    st.warning(
        "The original dataset caps recorded home values at $500,000. "
        "High-value areas may be underestimated."
    )
    st.caption("For learning and demonstration only.")
