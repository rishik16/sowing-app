# =========================================
# 🌱 SMART FARMING ASSISTANT (FINAL)
# =========================================

import streamlit as st
import requests
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# =========================================
# ✅ WEATHER API KEY
# =========================================
WEATHER_API_KEY = "bfe85d836e312b4bf32a886bc8fa4433"

# =========================================
# 🎨 UI CONFIG
# =========================================
st.set_page_config(page_title="Smart Farming", layout="wide")
st.title("🌱 Smart Farming Assistant")

# =========================================
# 🌍 LOCATION INPUT
# =========================================
state_districts = {
    "Maharashtra": ["Nashik", "Pune", "Nagpur", "Mumbai"],
    "Gujarat": ["Ahmedabad", "Surat"],
    "Karnataka": ["Bangalore", "Mysore"],
}

col1, col2, col3 = st.columns(3)

with col1:
    state = st.selectbox("🌍 State", list(state_districts.keys()))

with col2:
    district = st.selectbox("🏙 District", state_districts[state])

with col3:
    city = st.text_input("📍 City", district)

veg = st.selectbox("🥦 Vegetable", ["Tomato", "Potato", "Onion"])

# =========================================
# 📅 MONTH NAMES
# =========================================
months = [
    "January", "February", "March", "April",
    "May", "June", "July", "August",
    "September", "October", "November", "December"
]

# =========================================
# 📊 PRICE DATA
# =========================================
price_data = {
    "Tomato": [10, 12, 15, 20, 25, 40, 60, 80, 50, 30, 20, 15],
    "Potato": [20, 18, 17, 16, 15, 14, 15, 16, 18, 20, 22, 24],
    "Onion": [15, 18, 20, 25, 30, 35, 50, 70, 60, 40, 30, 20],
}

# =========================================
# 🌦 WEATHER FUNCTION
# =========================================
def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url)
        data = res.json()

        if "main" not in data:
            return None, None, "Weather API error"

        return data["main"]["temp"], data["main"]["humidity"], None
    except:
        return None, None, "Weather error"

# =========================================
# 🤖 AI MODEL
# =========================================
def predict_prices(prices):
    X = np.array(range(len(prices))).reshape(-1, 1)
    y = np.array(prices)

    model = LinearRegression()
    model.fit(X, y)

    future = np.array(range(len(prices), len(prices)+3)).reshape(-1, 1)
    return model.predict(future)

# =========================================
# 🌱 WEATHER CHECK
# =========================================
def weather_check(veg, temp):
    if temp is None:
        return False

    if veg == "Tomato":
        return 20 <= temp <= 30
    elif veg == "Potato":
        return 15 <= temp <= 25
    elif veg == "Onion":
        return 18 <= temp <= 30

    return False

# =========================================
# 🚀 BUTTON ACTION
# =========================================
if st.button("🚀 Get Smart Recommendation"):

    # -------- WEATHER --------
    st.subheader("🌦 Weather Overview")

    temp, humidity, err = get_weather(city)

    if err:
        st.error(err)
    else:
        c1, c2 = st.columns(2)
        c1.metric("🌡 Temperature", f"{temp} °C")
        c2.metric("💧 Humidity", f"{humidity} %")

    st.markdown("---")

    # -------- PRICE DATA --------
    st.subheader("📊 Last 12 Months Prices")

    prices = price_data[veg]

    for month, price in zip(months, prices):
        st.write(f"{month} : ₹{price}")

    st.markdown("---")

    # -------- AI PREDICTION --------
    st.subheader("🤖 Price Prediction")

    preds = predict_prices(prices)

    for i, p in enumerate(preds, 1):
        st.write(f"Next Month {i}: ₹{round(p,2)}")

    # =========================================
    # 📈 CHART WITH MONTH LABELS (FIXED)
    # =========================================

    future_months = ["Next 1", "Next 2", "Next 3"]
    all_months = months + future_months
    all_prices = prices + list(preds)

    df = pd.DataFrame({
        "Price": all_prices
    }, index=all_months)

    st.line_chart(df)

    st.markdown("---")

    # -------- FINAL --------
    st.subheader("🌱 Final Recommendation")

    if temp:
        if weather_check(veg, temp):
            st.success(f"✅ Good time to grow {veg}")
        else:
            st.error(f"❌ Weather not suitable for {veg}")
    else:
        st.warning("Weather data not available")
