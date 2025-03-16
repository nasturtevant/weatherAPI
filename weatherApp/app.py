import requests
import json
import pytz
import time
import boto3
import logging
import os

from datetime import datetime
from datetime import timedelta
from pytz import timezone
from configparser import ConfigParser

logger = logging.getLogger(__name__)

class WeatherAPI:
    
    def __init__(self, lat, lon):
        logger.setLevel(logging.DEBUG)
        logger.info(f"Initializing WeatherAPI with lat: {lat} and lon: {lon}")
        self.lat = lat
        self.lon = lon
        self.api_key = api_key
        self.units = 'imperial'
        # self.wind_speed = wind_speed
        # self.low_temp = low_temp
        # self.high_temp = high_temp
        # self.sns_topic_arn = sns_topic_arn

    def get_weather(self):
        # with open('test.json') as f:
        #     data = json.load(f)
        # return data
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={self.lat}&lon={self.lon}&appid={self.api_key}&units={self.units}"
        
        try:
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception(f"Failed to retrieve weather data: {resonse.status_code}")
        except Exception as e:
            logger.error("Error getting weather data: {}".format(e))
            return "Error getting weather data: {}".format(e)
        logger.info("Successfully retrieved weather data")
        data = json.loads(response.text)

        return data

        temperatureDataDict,windDataDict = load_weather_data(data)

        # triggerData = find_weather_data(temperatureDataDict,windDataDict, props.get('wind_speed'), props.get('low_temp'), props.get('high_temp'))

        # jdata = json.dumps(triggerData, indent=4)
        # print(jdata)

        # for item in triggerData:
        #     print(triggerData[item])


    def load_weather_data(self, data):
        temperatureDataDict = {}
        windDataDict = {}

        try:
            for d in data["list"]:
                dt = datetime.fromtimestamp(d["dt"], pytz.timezone('EST'))
                temperature = d["main"]["temp"]
                wind = d["wind"]["gust"]
                stringTime = dt.strftime("%A %m-%d-%Y %H:%M %Z")
                temperatureDataDict[stringTime] = temperature
                windDataDict[stringTime] = wind
        except Exception as e:
            logger.error("Error loading weather data: {}".format(e))
        return temperatureDataDict,windDataDict

    def find_weather_data(temperatureDataDict,windDataDict,wind_speed,min,max):
        weatherData = {}

        for time, temp in temperatureDataDict.items():
            if temp < int(min):
                if time in weatherData:
                    if "Temp" in weatherData[time]:
                        if weatherData[time]["Temp"] < temp:
                            weatherData[time].update({"Temp": temp})
                    else:
                        weatherData[time].update({"Temp": temp})
                else:
                    weatherData[time] = {"Temp": temp}
                logger.info(f"Temperature {temp} is below minimum {min} at {time}")
            if temp > int(max):
                if time in weatherData:
                    if "Temp" in weatherData[time]:
                        if weatherData[time]["Temp"] > temp:
                            weatherData[time].update({"Temp": temp})
                    else:
                        weatherData[time].update({"Temp": temp})
                else:
                    weatherData[time] = {"Temp": temp}

        for time, wind in windDataDict.items():
            if wind > int(wind_speed):
                if time in weatherData:
                    if "Wind" in weatherData[time]:
                        if weatherData[time]["Wind"] > wind:
                            weatherData[time].update({"Wind": wind})
                    else:
                        weatherData[time].update({"Wind": wind})
                else:
                    weatherData[time] = {"Wind": wind}

        return weatherData