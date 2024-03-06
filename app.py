import datetime
from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
import requests
import logging
import json

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

def get_coordinates(location):
    geolocator = Nominatim(user_agent="michaelWeather")
    location = geolocator.geocode(location)
    if location:
        return (location.latitude, location.longitude)
    else:
        return None, None

def get_gridpoint(lat, lon):
    url = f"https://api.weather.gov/points/{lat},{lon}"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        properties = data.get('properties', {})
        gridId = properties.get('gridId', 'Not found')
        gridX = properties.get('gridX', 'Not found')
        gridY = properties.get('gridY', 'Not found')
        return gridId, gridX, gridY
    else:
        return 'Error', 'Error', 'Error' 

@app.route('/')
def home():
    user_name="Michael"
    return render_template('index.html', utc_dt=datetime.datetime.now(datetime.UTC), default_location="San Francisco", user_name=user_name)

@app.route('/weather', methods=['POST'])
def weather():
    location = request.form['location']
    forecast = get_weather_forcast(location)

    logging.debug("In weather(): location='{}'",location)
    return render_template('weather.html', location=location, forecast=forecast["detailedForecast"], highTemp=forecast["highTemp"], lowTemp=forecast["lowTemp"], wIcon=forecast["wIcon"], shortForecast=forecast["shortForecast"])

def get_weather_forcast(location):
    #geolocator = Nominatim(user_agent="mhill-weather")
    #gloc = geolocator.geocode(location)
    lat, lon = get_coordinates(location)
    if lat is not None and lon is not None:
        gridId, gridX, gridY = get_gridpoint(lat, lon)
        logging.debug("Gridpoint for " + location +" : "+ gridId +'/'+ str(gridX) +'/'+ str(gridY))
        url = f"https://api.weather.gov/gridpoints/{gridId}/{gridX},{gridY}/forecast"
        response = requests.get(url)
        data = response.json()
        # Simplified extraction of forecast data

        logging.debug(json.dumps(data, indent=4))
        detailedForecast = data['properties']['periods'][0]['detailedForecast']
        shortForecast = data['properties']['periods'][0]['shortForecast']
        highTemp = data['properties']['periods'][0]['temperature']
        wIcon = data['properties']['periods'][0]['icon']
        lowTemp = data['properties']['periods'][1]['temperature']
        forecast = {
            'detailedForecast':detailedForecast,
            'shortForecast':shortForecast,
            'highTemp':highTemp,
            'wIcon':wIcon,
            'lowTemp':lowTemp
            }
        return forecast
    else:
        logging.ERROR("Location not found.")
        return "Location not found."

if __name__ == "__main__":
    app.run()
