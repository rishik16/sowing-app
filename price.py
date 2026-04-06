import streamlit as st

# Dummy historical price data (₹/kg monthly avg simplified)
price_data = {
    "tomato": [10, 12, 15, 20, 25, 40, 60, 80, 50, 30, 20, 15],
    "potato": [20, 18, 17, 16, 15, 14, 15, 16, 18, 20, 22, 24],
    "onion": [15, 18, 20, 25, 30, 35, 50, 70, 60, 40, 30, 20],
}

months = [
    "Jan","Feb","Mar","Apr","May","Jun",
    "Jul","Aug","Sep","Oct","Nov","Dec"
]

def get_best_sowing_month(data):
    max_price = max(data)
    index = data.index(max_price)
    # Assume harvest after 2 months
    sowing_index = (index - 2) % 12
    return months[sowing_index]

# UI
st.title("🌱 Sowing Recommendation App")

vegetable = st.text_input("Enter vegetable (tomato/potato/onion)")

if st.button("Get Recommendation"):
    veg = vegetable.lower()
    if veg not in price_data:
        st.error("Vegetable not found. Try tomato, potato, onion.")
    else:
        best_month = get_best_sowing_month(price_data[veg])
        st.success(f"Best sowing month for {veg} is {best_month}")