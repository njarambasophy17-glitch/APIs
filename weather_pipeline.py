#the requests library handles all HTTPS calls. trns a URL + params into a real network request
import requests

#for converting our list of results into a clean table and saving to CSV
import pandas as pd

#we'll use time.sleep() to pause between requests and respect rate limits
import time

#os.getenv() reads environment variables - values loaded from our env file
import os

#load_dotenv() reads the .env file and puts its values into our environment
from dotenv import load_dotenv


load_dotenv()
# reads the .env file and makes its values available

API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    raise ValueError("API key not found. Check your .env file.")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

CITIES = ["Nairobi", "Lagos", "Accra", "Kampala", "Dar es Salaam", "Addis Ababa", "Cairo", "Johannesburg", "Casablanca", "Dakar", "Tokyo", "Seoul", "Beijing", "Bangkok", "Mumbai", "Sydney", "Los Angeles", "New York", "London", "Paris"]

def fetch_weather(city_name):
    params = {"q": city_name, "appid": API_KEY, "units": "metric"}

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return {
                "city":          data["name"],
                "country":       data["sys"]["country"],
                "temperature_c": data["main"]["temp"],
                "feels_like_c":  data["main"]["feels_like"],
                "humidity_pct":  data["main"]["humidity"],
                "description":   data["weather"][0]["description"],
                "wind_speed_ms": data["wind"]["speed"]
            }
        elif response.status_code == 401:
            print(f"[AUTH ERROR] Check your API key. Got 401 for {city_name}")
        elif response.status_code == 404:
            print(f"[NOT FOUND] City not recognised: {city_name}")
        elif response.status_code == 429:
            print(f"[RATE LIMIT] Waiting 60 seconds...")
            time.sleep(60)
        else:
            print(f"[ERROR] Status {response.status_code} for {city_name}")
        return None

    except requests.exceptions.Timeout:
        print(f"[TIMEOUT] Request timed out for {city_name}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"[CONNECTION ERROR] Check your internet connection.")
        return None


def run_pipeline():
    all_results = []
    print("Starting weather pipeline...\n")

    for city in CITIES:
        print(f"Fetching: {city}")
        result = fetch_weather(city)

        if result is not None:
            all_results.append(result)
            print(f"  Done: {result['city']} — {result['temperature_c']}C, {result['description']}")
        else:
            print(f"  Skipped {city}")

        time.sleep(1)

    if all_results:
        df = pd.DataFrame(all_results)
        df["fetched_at"] = pd.Timestamp.now()
        df.to_csv("weather_data.csv", index=False)
        print(f"\nDone. {len(df)} cities saved to weather_data.csv")
        print(df[["city", "temperature_c", "humidity_pct", "description"]])
    else:
        print("No data collected. Check errors above.")


if __name__ == "__main__":
    run_pipeline()




