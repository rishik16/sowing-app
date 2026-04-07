import streamlit as st
import requests

# -------------------------------
# CONFIG
# -------------------------------
API_KEY = "bfe85d836e312b4bf32a886bc8fa4433"
CITY = "Nashik"

# -------------------------------
# PRICE DATA (dummy monthly avg)
# -------------------------------
price_data = {
    "tomato": [10, 12, 15, 20, 25, 40, 60, 80, 50, 30, 20, 15],
    "potato": [20, 18, 17, 16, 15, 14, 15, 16, 18, 20, 22, 24],
    "onion": [15, 18, 20, 25, 30, 35, 50, 70, 60, 40, 30, 20],
}

months = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

# Crop duration (months approx)
crop_duration = {
    "tomato": 2,
    "potato": 3,
    "onion": 3
}

# -------------------------------
# FUNCTIONS
# -------------------------------

def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    
    return temp, humidity


def get_best_sowing_month(veg):
    data = price_data[veg]
    max_price = max(data)
    peak_index = data.index(max_price)
    
    sowing_index = (peak_index - crop_duration[veg]) % 12
    return months[sowing_index], months[peak_index]


def weather_check(veg, temp):
    if veg == "tomato":
        return 20 <= temp <= 30
    elif veg == "potato":
        return 15 <= temp <= 25
    elif veg == "onion":
        return 18 <= temp <= 30
    return False


# -------------------------------
# STREAMLIT UI
# -------------------------------

st.title("🌱 Smart Vegetable Sowing App")

veg = st.selectbox("Select Vegetable", ["tomato", "potato", "onion"])

if st.button("Get Recommendation"):
    
    # Get weather
    temp, humidity = get_weather()
    
    # Get price-based suggestion
    sow_month, peak_month = get_best_sowing_month(veg)
    
    # Weather check
    suitable = weather_check(veg, temp)
    
    # -------------------------------
    # OUTPUT
    # -------------------------------
    
    st.subheader("📊 Weather Conditions")
    st.write(f"🌡 Temperature: {temp} °C")
    st.write(f"💧 Humidity: {humidity} %")
    
    st.subheader("📈 Price Insight")
    st.write(f"💰 Expected high price month: {peak_month}")
    
    st.subheader("🌱 Recommendation")
    
    if suitable:
        st.success(f"✅ Best sowing month: {sow_month}")
    else:
        st.error(f"❌ Weather not suitable now for {veg}")
        st.warning("👉 Wait for better temperature conditions")
