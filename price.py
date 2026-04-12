# =========================================
# 🌱 SMART FARMING ASSISTANT (FINAL ML VERSION)
# =========================================

import streamlit as st
import requests
import numpy as np
import pandas as pd
import datetime
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder

# =========================================
# 🔑 API KEYS
# =========================================
WEATHER_API_KEY = "bfe85d836e312b4bf32a886bc8fa4433"
MANDI_API_KEY = "579b464db66ec23bdd000001cf1ffff34623416e485cb74e3ce6a4c7"

# =========================================
# 📍 LOCAL MANDIS
# =========================================
maharashtra_mandis = {
    "Nashik": ["Lasalgaon", "Nashik", "Pimpalgaon"],
    "Pune": ["Pune Market Yard", "Baramati", "Shirur"],
    "Nagpur": ["Nagpur", "Kalmeshwar", "Kamptee"],
}

# =========================================
# 🌱 CROP ROTATION DATASET (ML TRAINING)
# =========================================
data = [
    ("Wheat", "Legumes"),
    ("Wheat", "Maize"),
    ("Rice", "Pulses"),
    ("Rice", "Vegetables"),
    ("Sugarcane", "Wheat"),
    ("Sugarcane", "Pulses"),
    ("Cotton", "Groundnut"),
    ("Cotton", "Wheat"),
    ("Tomato", "Onion"),
    ("Potato", "Peas"),
    ("Onion", "Soybean"),
]

# =========================================
# 🤖 TRAIN ML MODEL
# =========================================
le_input = LabelEncoder()
le_output = LabelEncoder()

X = [d[0] for d in data]
y = [d[1] for d in data]

X_encoded = le_input.fit_transform(X).reshape(-1, 1)
y_encoded = le_output.fit_transform(y)

model_crop = DecisionTreeClassifier()
model_crop.fit(X_encoded, y_encoded)

# =========================================
# 🌍 UI
# =========================================
st.title("🌱 Smart Farming Assistant (AI + ML)")

state = st.selectbox("State", ["Maharashtra"])
district = st.text_input("District", "Nashik")
city = st.text_input("City", "Nashik")

veg = st.selectbox("Vegetable", ["Tomato", "Potato", "Onion"])

previous_crop = st.text_input("Previous Crop")

# =========================================
# 🌦 WEATHER
# =========================================
def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()

        if "main" not in data:
            return None, None

        return data["main"]["temp"], data["main"]["humidity"]
    except:
        return None, None

# =========================================
# 📊 MANDI DATA (WITH FALLBACK)
# =========================================
def get_mandi_data(commodity, state, district):
    try:
        district = district.strip().title()

        url = (
            "https://api.data.gov.in/resource/"
            "9ef84268-d588-465a-a308-a864a43d0070"
            f"?api-key={MANDI_API_KEY}"
            f"&format=json&limit=50"
            f"&filters[state]={state}"
            f"&filters[district]={district}"
            f"&filters[commodity]={commodity}"
        )

        data = requests.get(url).json()
        records = data.get("records", [])

        # fallback
        if not records:
            url = (
                "https://api.data.gov.in/resource/"
                "9ef84268-d588-465a-a308-a864a43d0070"
                f"?api-key={MANDI_API_KEY}"
                f"&format=json&limit=50"
                f"&filters[state]={state}"
                f"&filters[commodity]={commodity}"
            )
            data = requests.get(url).json()
            records = data.get("records", [])

        mandi_info = []
        for r in records:
            if r.get("modal_price") and r.get("market"):
                mandi_info.append({
                    "market": r["market"],
                    "price": int(r["modal_price"])
                })

        return mandi_info if mandi_info else None
    except:
        return None

# =========================================
# 🤖 PRICE PREDICTION
# =========================================
def predict_prices(prices):
    X = np.arange(len(prices)).reshape(-1, 1)
    model = LinearRegression().fit(X, prices)
    future = np.arange(len(prices), len(prices)+3).reshape(-1, 1)
    return model.predict(future)

# =========================================
# 🌱 ML CROP ROTATION + REASON
# =========================================
def predict_next_crop_with_reason(prev_crop):
    try:
        encoded = le_input.transform([prev_crop])[0]
        pred = model_crop.predict([[encoded]])
        next_crop = le_output.inverse_transform(pred)[0]

        reasons = {
            "Legumes": "Fix nitrogen in soil and improve fertility",
            "Maize": "Balances nutrients after heavy crops",
            "Pulses": "Restore soil nutrients naturally",
            "Vegetables": "Short duration and high profit crop",
            "Groundnut": "Improves soil structure and nitrogen",
            "Soybean": "Enhances nitrogen content in soil",
            "Peas": "Excellent nitrogen fixing crop"
        }

        reason = reasons.get(next_crop, "Improves soil health and yield")

        return next_crop, reason
    except:
        return "No data", "No reason available"

# =========================================
# 🚀 MAIN BUTTON
# =========================================
if st.button("Get Recommendation"):

    # 🌦 WEATHER
    st.subheader("🌦 Weather")
    temp, hum = get_weather(city)

    if temp:
        st.write(f"🌡 Temp: {temp} °C | 💧 Humidity: {hum}%")
    else:
        st.warning("Weather data not available")

    # 📊 MANDI DATA
    st.subheader("📊 Live Mandi Prices")
    mandi = get_mandi_data(veg, state, district)

    if mandi:
        for m in mandi[:5]:
            st.write(f"📍 {m['market']} → ₹{m['price']}")

        prices = [m["price"] for m in mandi]

        # 🤖 Prediction with REAL MONTH NAMES
        st.subheader("🤖 AI Price Prediction")

        preds = predict_prices(prices)

        current_month = datetime.datetime.now().month

        month_names = [
            "January","February","March","April","May","June",
            "July","August","September","October","November","December"
        ]

        for i, p in enumerate(preds, 1):
            future_month = month_names[(current_month + i - 1) % 12]
            st.write(f"{future_month}: ₹{round(p,2)}")

        # 📊 WEEK BASED GRAPH
        weeks = list(range(1, len(prices) + len(preds) + 1))

        df = pd.DataFrame({
            "Week": weeks,
            "Price": prices + list(preds)
        })

        df.set_index("Week", inplace=True)

        st.subheader("📊 Price Trend (Weekly)")
        st.line_chart(df)

    else:
        st.error("No mandi data found")

    # 🌱 CROP ROTATION ML
    st.subheader("🌱 Crop Rotation (ML Based)")

    if previous_crop:
        crop, reason = predict_next_crop_with_reason(previous_crop.title())

        st.success(f"Recommended Next Crop: {crop}")
        st.info(f"🌾 Reason: {reason}")
    else:
        st.info("Enter previous crop")
