# =========================================
# 🌱 SMART FARMING ASSISTANT (MOBILE READY)
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
# 📱 APP CONFIG (MOBILE FRIENDLY)
# =========================================
st.set_page_config(
    page_title="Smart Farming App",
    page_icon="🌱",
    layout="centered"
)

# =========================================
# 🔑 API KEYS
# =========================================
WEATHER_API_KEY = "bfe85d836e312b4bf32a886bc8fa4433"
MANDI_API_KEY = "579b464db66ec23bdd000001cf1ffff34623416e485cb74e3ce6a4c7"

# =========================================
# 📂 LOAD LOCAL DATASET
# =========================================
@st.cache_data
def load_dataset():
    try:
        return pd.read_csv("mandi_data.csv")
    except:
        st.warning("⚠️ Local dataset not found, using API only")
        return pd.DataFrame()

df_local = load_dataset()

# =========================================
# 🌱 ML MODEL
# =========================================
data = [
    ("Wheat", "Legumes"),
    ("Rice", "Pulses"),
    ("Cotton", "Groundnut"),
    ("Tomato", "Onion"),
    ("Potato", "Peas"),
    ("Onion", "Soybean"),
]

le_input = LabelEncoder()
le_output = LabelEncoder()

X = [d[0] for d in data]
y = [d[1] for d in data]

X_enc = le_input.fit_transform(X).reshape(-1, 1)
y_enc = le_output.fit_transform(y)

model_crop = DecisionTreeClassifier()
model_crop.fit(X_enc, y_enc)

# =========================================
# 🌦 WEATHER
# =========================================
def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()
        return data["main"]["temp"], data["main"]["humidity"]
    except:
        return None, None

# =========================================
# 📊 HYBRID MANDI DATA
# =========================================
def get_mandi_data(commodity, state, district):

    # 🔹 TRY API
    try:
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

        if records:
            mandi_info = []
            for r in records:
                if r.get("modal_price") and r.get("market"):
                    mandi_info.append({
                        "market": r["market"],
                        "price": int(r["modal_price"])
                    })
            return mandi_info

    except:
        pass

    # 🔁 FALLBACK → LOCAL DATASET
    st.warning("⚠️ Using offline dataset")

    if not df_local.empty:
        filtered = df_local[
            (df_local["state"] == state) &
            (df_local["district"] == district) &
            (df_local["commodity"].str.contains(commodity, case=False))
        ]

        if not filtered.empty:
            return filtered[["market", "price"]].to_dict(orient="records")

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
# 🌱 ML CROP ROTATION
# =========================================
def predict_crop(prev):
    try:
        enc = le_input.transform([prev])[0]
        pred = model_crop.predict([[enc]])
        crop = le_output.inverse_transform(pred)[0]

        reasons = {
            "Legumes": "Fix nitrogen in soil and improve fertility",
            "Pulses": "Restore soil nutrients naturally",
            "Groundnut": "Improves soil structure",
            "Onion": "Short duration profitable crop",
            "Peas": "Excellent nitrogen fixing crop",
            "Soybean": "Enhances soil fertility"
        }

        return crop, reasons.get(crop, "Improves soil health")

    except:
        return "Unknown", "No data available"

# =========================================
# 🌍 UI
# =========================================
st.title("🌱 Smart Farming Assistant")

state = st.selectbox("State", ["Maharashtra"])
district = st.text_input("District", "Nashik")
city = st.text_input("City", "Nashik")

veg = st.selectbox("Vegetable", ["Onion", "Tomato", "Potato"])
prev_crop = st.text_input("Previous Crop")

# =========================================
# 🚀 MAIN
# =========================================
if st.button("Get Recommendation"):

    # 🌦 WEATHER
    st.subheader("🌦 Weather")
    temp, hum = get_weather(city)

    if temp:
        st.write(f"🌡 Temp: {temp} °C | 💧 Humidity: {hum}%")
    else:
        st.warning("Weather data not available")

    # 📊 MANDI
    st.subheader("📊 Live Mandi Prices")
    mandi = get_mandi_data(veg, state, district)

    if mandi:
        for m in mandi:
            st.write(f"📍 {m['market']} → ₹{m['price']}")

        prices = [m["price"] for m in mandi]

        # 🤖 PRICE PREDICTION
        st.subheader("🤖 AI Price Prediction")

        preds = predict_prices(prices)

        month_names = [
            "January","February","March","April","May","June",
            "July","August","September","October","November","December"
        ]

        current_month = datetime.datetime.now().month

        for i, p in enumerate(preds, 1):
            future_month = month_names[(current_month + i - 1) % 12]
            st.write(f"{future_month} → ₹{round(p,2)}")

        # 📊 WEEK GRAPH
        weeks = list(range(1, len(prices) + len(preds) + 1))

        df = pd.DataFrame({
            "Week": weeks,
            "Price": prices + list(preds)
        })

        df.set_index("Week", inplace=True)

        st.subheader("📊 Price Trend (Weekly)")
        st.line_chart(df)

    else:
        st.error("No mandi data available")

    # 🌱 CROP ROTATION
    st.subheader("🌱 ML Based Crop Rotation Suggestion")

    if prev_crop:
        crop, reason = predict_crop(prev_crop.title())

        st.success(f"Next Crop: {crop}")
        st.info(f"Reason: {reason}")
    else:
        st.info("Enter previous crop")
