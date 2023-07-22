import requests


def get_weather_data(city_name, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city_name}&appid={api_key}"

    response = requests.get(complete_url)
    data = response.json()

    if data["cod"] == "404":
        print("City not found")
        return None
    else:
        weather_info = {
            "City": data["name"],
            "Temperature (Celsius)": round(data["main"]["temp"] - 273.15, 2),
            "Weather": data["weather"][0]["description"],
            "Wind Speed (m/s)": data["wind"]["speed"],
            "Humidity (%)": data["main"]["humidity"]
        }
        return weather_info


def main():
    city_name = "Brest"  # Замените на название города, для которого хотите получить данные о погоде
    api_key = "YOUR_API_KEY"  # Замените на ваш собственный API-ключ

    weather_data = get_weather_data(city_name, api_key)
    if weather_data:
        for key, value in weather_data.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
