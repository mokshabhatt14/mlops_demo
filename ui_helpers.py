"""Reusable input mapping and illustration helpers for the Streamlit app."""

from html import escape

import pandas as pd


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


def build_model_features(
    income_dollars,
    house_age,
    bedrooms,
    bathrooms,
    kitchens,
    population,
    occupancy,
    latitude,
    longitude,
):
    """Translate the home-design controls into the model's neighborhood inputs."""
    approximate_rooms = bedrooms + bathrooms + kitchens + 1
    return pd.DataFrame(
        [
            [
                float(income_dollars) / 10_000,
                float(house_age),
                float(approximate_rooms),
                float(bedrooms),
                float(population),
                float(occupancy),
                float(latitude),
                float(longitude),
            ]
        ],
        columns=FEATURES,
    )


def make_house_scene(bedrooms, bathrooms, kitchens, floors, door_open):
    """Create a small self-contained animated house-and-dog illustration."""
    bottom = 258
    house_top = bottom - floors * 48
    windows = "".join(
        f'<rect x="{x}" y="{bottom - 35 - floor * 48}" width="32" height="25" '
        'rx="5" class="window"/>'
        for floor in range(floors)
        for x in (288, 432)
    )
    door_class = "door open" if door_open else "door"
    door_label = "Door open" if door_open else "Door closed"
    accessibility_label = escape(
        f"Animated home with {bedrooms} bedrooms, {bathrooms} bathrooms, "
        f"{kitchens} kitchens and {floors} floors. A dog is waiting outside. "
        f"{door_label}."
    )
    return f"""
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
          * {{ box-sizing: border-box; }}
          body {{ margin: 0; font-family: system-ui, sans-serif; color: #233044; }}
          .scene {{ overflow: hidden; border-radius: 22px; background: #eaf6ff; }}
          svg {{ display: block; width: 100%; height: auto; }}
          .cloud {{ animation: drift 16s ease-in-out infinite alternate; }}
          .cloud.second {{ animation-delay: -7s; animation-duration: 21s; }}
          .window {{ fill: #b7e5f4; stroke: #8d6a52; stroke-width: 4; }}
          .door {{ transform-box: view-box; transform-origin: 350px 224px;
                   transition: transform 650ms cubic-bezier(.2,.8,.2,1); }}
          .door.open {{ transform: perspective(350px) rotateY(-66deg); }}
          .tail {{ transform-box: fill-box; transform-origin: 0% 100%;
                   animation: wag .35s ease-in-out infinite alternate; }}
          .dog {{ animation: happy 1.5s ease-in-out infinite; }}
          .badge {{ display: flex; flex-wrap: wrap; gap: 8px; padding: 12px 14px; }}
          .pill {{ border-radius: 999px; padding: 6px 12px; background: #f0f6ee;
                   font-size: 13px; font-weight: 650; }}
          @keyframes drift {{ to {{ transform: translateX(32px); }} }}
          @keyframes wag {{ to {{ transform: rotate(26deg); }} }}
          @keyframes happy {{ 50% {{ transform: translateY(-4px); }} }}
          @media (prefers-reduced-motion: reduce) {{
            *, *::before, *::after {{ animation-duration: .01ms !important;
                                      animation-iteration-count: 1 !important;
                                      transition-duration: .01ms !important; }}
          }}
        </style>
      </head>
      <body>
        <div class="scene" role="img" aria-label="{accessibility_label}">
          <svg viewBox="0 0 760 320" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="sky" x2="0" y2="1">
                <stop stop-color="#c9eaff"/><stop offset="1" stop-color="#f6fbff"/>
              </linearGradient>
            </defs>
            <rect width="760" height="320" fill="url(#sky)"/>
            <circle cx="650" cy="58" r="30" fill="#ffd66b"/>
            <g class="cloud" fill="white" opacity=".92">
              <ellipse cx="145" cy="75" rx="45" ry="17"/>
              <circle cx="122" cy="68" r="20"/><circle cx="150" cy="58" r="25"/>
              <circle cx="175" cy="70" r="18"/>
            </g>
            <g class="cloud second" fill="white" opacity=".8">
              <ellipse cx="520" cy="84" rx="36" ry="14"/>
              <circle cx="501" cy="78" r="16"/><circle cx="525" cy="69" r="21"/>
              <circle cx="546" cy="79" r="15"/>
            </g>
            <path d="M0 235 Q170 210 330 239 T760 225 V320 H0Z" fill="#acd993"/>
            <path d="M0 270 Q175 246 370 268 T760 255 V320 H0Z" fill="#83c879"/>
            <rect x="205" y="{house_top + 15}" width="350" height="{bottom - house_top - 15}"
                  rx="9" fill="#fff4dd" stroke="#9e704c" stroke-width="5"/>
            <path d="M185 {house_top + 20} L380 24 L575 {house_top + 20} Z"
                  fill="#d8795b" stroke="#9e4f42" stroke-width="6"
                  stroke-linejoin="round"/>
            <path d="M210 {house_top + 20} H550" stroke="#f3a681" stroke-width="9"/>
            {windows}
            <g class="{door_class}">
              <rect x="350" y="194" width="62" height="64" rx="5"
                    fill="#83b9dc" stroke="#76513e" stroke-width="5"/>
              <circle cx="399" cy="228" r="3.5" fill="#fff1a8"/>
            </g>
            <path d="M317 272 Q380 254 445 272" fill="none"
                  stroke="#e7d2ab" stroke-width="17" stroke-linecap="round"/>
            <g class="dog">
              <ellipse cx="612" cy="258" rx="35" ry="24" fill="#d99454"/>
              <circle cx="640" cy="235" r="22" fill="#e6ad70"/>
              <path d="M626 219 Q617 197 638 219Z M645 217 Q659 198 656 225Z"
                    fill="#9e6244"/>
              <ellipse cx="648" cy="241" rx="11" ry="8" fill="#fff0d9"/>
              <circle cx="646" cy="231" r="2.6" fill="#302b28"/>
              <circle cx="657" cy="240" r="3" fill="#49352d"/>
              <path d="M578 250 Q557 231 563 215" fill="none" stroke="#b87748"
                    stroke-width="8" stroke-linecap="round" class="tail"/>
              <path d="M590 272v10 M625 272v10" stroke="#9e6244" stroke-width="8"
                    stroke-linecap="round"/>
              <path d="M602 235 Q617 247 629 237" fill="none" stroke="#f1d781"
                    stroke-width="5" stroke-linecap="round"/>
              <rect x="600" y="236" width="29" height="7" rx="3" fill="#6cae76"/>
            </g>
            <path d="M115 276v-38 M100 250l15-14 15 14" stroke="#5e9f57"
                  stroke-width="5" fill="none" stroke-linecap="round"/>
            <path d="M676 280v-42 M660 254l16-15 16 15" stroke="#5e9f57"
                  stroke-width="5" fill="none" stroke-linecap="round"/>
            <text x="380" y="302" text-anchor="middle" fill="#375d47"
                  font-size="15" font-weight="650">Your little California home</text>
          </svg>
          <div class="badge">
            <span class="pill">🛏️ {bedrooms} bedrooms</span>
            <span class="pill">🛁 {bathrooms} bathrooms</span>
            <span class="pill">🍳 {kitchens} kitchen{'s' if kitchens != 1 else ''}</span>
            <span class="pill">🏠 {floors} floor{'s' if floors != 1 else ''}</span>
            <span class="pill">🐶 Your dog says hi!</span>
          </div>
        </div>
      </body>
    </html>
    """
