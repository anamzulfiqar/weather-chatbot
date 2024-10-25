import requests
from datetime import datetime
from collections import defaultdict
import streamlit as st
from PIL import Image
from transformers import pipeline

# API Key for OpenWeatherMap
api_key = "248cad0b7fd5b82593d13416788f774f"

# List of cities for the weather report
cities = ["London", "New York", "Sheffield", "Pakistan", "Norway", "Oslo", "Karachi", "Islamabad"]

# Initialize the Hugging Face text generation model
chatbot = pipeline("text-generation", model="microsoft/DialoGPT-small", truncation=True)


# Function to get weather data
def get_weather_data(city, forecast=False):
    current_weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    if not forecast:
        current_response = requests.get(current_weather_url)
        if current_response.status_code == 200:
            current_data = current_response.json()
            current_temp = current_data["main"]["temp"]
            current_description = current_data["weather"][0]["description"]
            current_weather = f"{current_temp}°C, {current_description}"
            icon = current_data["weather"][0]["icon"]
            return current_weather, icon
        else:
            return "Error fetching current weather.", None

    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    forecast_response = requests.get(forecast_url)
    
    if forecast_response.status_code == 200:
        forecast_data = forecast_response.json()
        daily_forecast = defaultdict(list)

        for forecast in forecast_data["list"]:
            date = datetime.utcfromtimestamp(forecast["dt"]).strftime("%Y-%m-%d")
            daily_forecast[date].append(forecast)
        
        forecast_report = "5-Day Forecast:\n"
        for date, forecasts in daily_forecast.items():
            temps = [f["main"]["temp"] for f in forecasts]
            descriptions = [f["weather"][0]["description"] for f in forecasts]
            avg_temp = sum(temps) / len(temps)
            main_description = max(set(descriptions), key=descriptions.count)
            forecast_report += f"Date: {date}, Avg Temp: {avg_temp:.1f}°C, Weather: {main_description}\n"
    else:
        forecast_report = "Error fetching forecast."
    
    return forecast_report

# Streamlit application
def main():
    st.set_page_config(page_title="Weather Chatbot", page_icon="☀️", layout="wide")
    st.title("🌦️ Weather Chatbot 🌦️")
    
    st.markdown("""
        <style>
        .main {
            background-color: #f0f8ff;  /* Light blue background */
        }
        </style>
        """, unsafe_allow_html=True)

    user_input = st.text_input("You:", "", key="user_input").strip().lower()

    # Column layout for input and output
    col1, col2 = st.columns([1, 3])

    if user_input:
        with col1:
            st.header("City Name")
            if "in" in user_input:
                city = user_input.split("in")[-1].strip()
            else:
                city = st.text_input("Specify city name:", "").strip()
            normalized_city = city.capitalize()

        with col2:
            if normalized_city in cities:
                weather_report, icon = get_weather_data(normalized_city)
                st.write("**Bot:**", weather_report)
                if icon:
                    st.image(f"http://openweathermap.org/img/wn/{icon}.png", width=100)  # Show weather icon
            else:
                st.write("**Bot:** Sorry, I don't have data for that city.")

        # Handle 5-day forecast requests
        if "5-day forecast" in user_input or "forecast" in user_input:
            if normalized_city in cities:
                forecast_report = get_weather_data(normalized_city, forecast=True)
                st.write("**Bot:**", forecast_report)

        # Use chatbot model for general conversation
        else:
            response = chatbot(user_input, max_length=50, num_return_sequences=1)[0]['generated_text']
            st.write("**Bot:**", response)

    # Footer
    st.markdown("---")
    st.write("👋 Ask me about the weather or just chat with me!")

if __name__ == "__main__":
    main()
