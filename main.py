import streamlit as st
import requests
import os
from dotenv import load_dotenv
import openai

# 🔐 Load API Keys
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

openai.api_key = OPENAI_API_KEY

# 🔣 Map condition to emoji
def condition_icon(condition: str) -> str:
    condition = condition.lower()
    if "clear" in condition: return "☀️"
    if "cloud" in condition: return "☁️"
    if "rain" in condition: return "🌧️"
    if "snow" in condition: return "❄️"
    if "mist" in condition or "fog" in condition: return "🌫️"
    return "🌤️"

# 🌦️ Weather Info Fetcher
def get_weather(city: str) -> str:
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temp = data["current"]["temp_c"]
            condition = data["current"]["condition"]["text"]
            wind = data["current"]["wind_kph"]
            icon = condition_icon(condition)
            return f"📍 **{city}**\n\n{icon} {condition}\n🌡️ {temp}°C\n💨 {wind} km/h"
        else:
            return f"⚠️ Weather data unavailable for '{city}'"
    except Exception as e:
        return f"❌ Error: {e}"

# 🧠 Extract City from Query
def extract_city(query: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "Extract only the city name from this query. Respond with only the city name, no explanation."
        },
        {"role": "user", "content": query}
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        result = response.choices[0].message["content"].strip()
        return result if result else query.strip()
    except:
        return query.strip()

# 🌤️ Streamlit UI
st.set_page_config(page_title="WeatherBot", page_icon="🌦️")
st.title("🌦️ WeatherBot Agent")

# 🚀 Init Session State
if "query" not in st.session_state:
    st.session_state.query = ""
if "weather" not in st.session_state:
    st.session_state.weather = ""
if "clear_flag" not in st.session_state:
    st.session_state.clear_flag = False

# 🎯 Use placeholder input box to handle clear logic safely
input_box = st.empty()

if st.session_state.clear_flag:
    input_query = input_box.text_input("🗣️ City Name:", value="", key="new_input")
else:
    input_query = input_box.text_input("🗣️ City Name:", value=st.session_state.query, key="input_query")

# 🔘 Buttons for search and clear
col1, col2 = st.columns([2, 1])
with col1:
    if st.button("🔍Search Weather "):
        query_text = input_query if not st.session_state.clear_flag else st.session_state.get("new_input", "")
        city = extract_city(query_text)
        st.session_state.query = query_text
        st.session_state.weather = get_weather(city)
        st.session_state.clear_flag = False  # Reset clear flag

with col2:
    if st.button(" Clear"):
        st.session_state.query = ""
        st.session_state.weather = ""
        st.session_state.clear_flag = True
        st.rerun()

# 📋 Show Results
if st.session_state.weather:
    st.markdown("### ⛅ Result:")
    st.success(st.session_state.weather)