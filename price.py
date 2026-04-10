import streamlit as st
import requests
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# -------------------------------
# CONFIG
# -------------------------------
WEATHER_API_KEY = "bfe85d836e312b4bf32a886bc8fa4433"
CITY = "Nashik"

# -------------------------------
# DISTRICTS
# -------------------------------
districts = [
    "Nashik", "Pune", "Mumbai", "Nagpur", "Ahmednagar",
    "Solapur", "Kolhapur", "Satara", "Jalgaon", "Aurangabad"
]

# -------------------------------
# MANDI LOCATIONS
# -------------------------------
mandi_locations = {
    "Nashik": [
        {"name": "Lasalgaon APMC", "map": "https://maps.google.com/?q=Lasalgaon+APMC"},
        {"name": "Pimpalgaon Baswant APMC", "map": "https://maps.google.com/?q=Pimpalgaon+Baswant+APMC"}
    ],
    "Pune": [
        {"name": "Pune Market Yard APMC", "map": "https://maps.google.com/?q=Pune+APMC"},
        {"name": "Chakan Mandi", "map": "https://maps.google.com/?q=Chakan+Mandi"}
    ],
    "Mumbai": [
        {"name": "Vashi APMC", "map": "https://maps.google.com/?q=Vashi+APMC"}
    ],
    "Nagpur": [
        {"name": "Kalamna APMC", "map": "https://maps.google.com/?q=Kalamna+APMC"}
    ],
    "Ahmednagar": [
        {"name": "Ahmednagar APMC", "map": "https://maps.google.com/?q=Ahmednagar+APMC"}
    ],
    "Solapur": [
        {"name": "Solapur APMC", "map": "https://maps.google.com/?q=Solapur+APMC"}
    ],
    "Kolhapur": [
        {"name": "Kolhapur APMC", "map": "https://maps.google.com/?q=Kolhapur+APMC"}
    ],
    "Satara": [
        {"name": "Satara APMC", "map": "https://maps.google.com/?q=Satara+APMC"}
    ],
    "Jalgaon": [
        {"name": "Jalgaon APMC", "map": "https://maps.google.com/?q=Jalgaon+APMC"}
    ],
    "Aurangabad": [
        {"name": "Aurangabad APMC", "map": "https://maps.google.com/?q=Aurangabad+APMC"}
    ]
}

# -------------------------------
# PRICE DATA
# -------------------------------
price_data = {
    "tomato": [10, 12, 15, 20, 25, 40, 60, 80, 50, 30, 20, 15],
    "potato": [20, 18, 17, 16, 15, 14, 15, 16, 18, 20, 22, 24],
    "onion": [15, 18, 20, 25, 30, 35, 50, 70, 60, 40, 30, 20],
}

months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

crop_duration = {
    "tomato": 2,
    "potato": 3,
    "onion": 3
}

# -------------------------------
# FUNCTIONS
# -------------------------------

def get_weather():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()

        if "main" not in data:
            return None, None, "Weather API error"

        return data["main"]["temp"], data["main"]["humidity"], None

    except:
        return None, None, "Connection error"


def get_best_sowing_month(veg):
    data = price_data[veg]
    peak_index = data.index(max(data))
    sowing_index = (peak_index - crop_duration[veg]) % 12
    return months[sowing_index], months[peak_index], peak_index


def weather_check(veg, temp):
    if temp is None:
        return False

    conditions = {
        "tomato": (20, 30),
        "potato": (15, 25),
        "onion": (18, 30)
    }

    min_t, max_t = conditions[veg]
    return min_t <= temp <= max_t


def predict_prices(veg):
    X = np.array(range(12)).reshape(-1, 1)
    y = np.array(price_data[veg])

    model = LinearRegression()
    model.fit(X, y)

    future = np.array([12, 13, 14]).reshape(-1, 1)
    return model.predict(future)


# -------------------------------
# STREAMLIT UI
# -------------------------------

st.title("🌱 Smart Vegetable Sowing App")

veg = st.selectbox("Select Vegetable", ["tomato", "potato", "onion"])
district = st.selectbox("Select District", districts)

if st.button("Get Recommendation"):

    # PRICE INSIGHT
    sow, peak, peak_index = get_best_sowing_month(veg)

    st.subheader("📈 Price Insight")
    st.write(f"💰 Peak price month: {peak}")
    st.write(f"🌱 Best sowing month: {sow}")

    # WEATHER
    temp, humidity, error = get_weather()

    st.subheader("🌦 Weather")

    if error:
        st.error(error)
    else:
        st.write(f"🌡 Temperature: {temp} °C")
        st.write(f"💧 Humidity: {humidity}%")

        if weather_check(veg, temp):
            st.success("✅ Good time to sow")
        else:
            st.error("❌ Not suitable currently")

    # AI PREDICTION
    st.subheader("🤖 Price Prediction (Next 3 Months)")

    preds = predict_prices(veg)

    future_months = [
        months[(peak_index + i + 1) % 12]
        for i in range(3)
    ]

    for m, p in zip(future_months, preds):
        st.write(f"📅 {m}: ₹{round(p,2)}")

    # -------------------------------
    # FIXED GRAPH WITH MONTH NAMES
    # -------------------------------
    st.subheader("📊 Price Trend")

    all_months = months + future_months
    all_prices = price_data[veg] + list(preds)

    df = pd.DataFrame({
        "Month": all_months,
        "Price": all_prices
    })

    df.set_index("Month", inplace=True)
    st.line_chart(df)

    # -------------------------------
    # MANDI LOCATIONS
    # -------------------------------
    st.subheader("📍 Nearby Mandi Locations")

    mandis = mandi_locations.get(district, [])

    if not mandis:
        st.warning("No mandi data available")
    else:
        for mandi in mandis:
            st.write(f"🏪 {mandi['name']}")
            st.markdown(f"[📌 View on Map]({mandi['map']})")
            st.write("---")
