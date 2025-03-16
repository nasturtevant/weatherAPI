from weatherApp.app import WeatherAPI
from utilities import Utilities
from graphene import InputObjectType, ObjectType, String, Schema, Float, Int, List, Field, JSONString
import json
from flask import Flask
from flask_graphql import GraphQLView
import logging
from time import strftime, localtime


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class GeoInput(InputObjectType):
    lat = Float(required=True)
    lon = Float(required=True)
    @property
    def latlon(self):
        return (self.lat, self.lon)

class CoordType(ObjectType):
    lat = Float()
    lon = Float()


class City(ObjectType):
    id = Int()
    name = String()
    coord = Field(CoordType)
    country = String()
    population = Int()
    timezone = Int()
    sunrise = Int()
    sunset = Int()

class MainDataType(ObjectType):
    temp = Float()
    feels_like = Float()
    temp_min = Float()
    temp_max = Float()
    pressure = Int()
    sea_level = Int()
    grnd_level = Int()
    humidity = Int()
    temp_kf = Float()

class WeatherDataType(ObjectType):
    id = Int()
    main = String()
    description = String()
    icon = String()

class CloudsDataType(ObjectType):
    all = Int()

class WindDataType(ObjectType):
    speed = Float()
    deg = Int()
    gust = Float()

class SysDataType(ObjectType):
    pod = String()

class ForecastItemType(ObjectType):
    datetime = String()
    main = Field(MainDataType)
    weather = List(WeatherDataType)
    clouds = Field(CloudsDataType)
    wind = Field(WindDataType)
    visibility = Int()
    pop = Int()
    sys = Field(SysDataType)
    dt_txt = String()

class WeatherForecastType(ObjectType):
    cod = String()
    message = Int()
    cnt = Int()
    list = List(ForecastItemType)
    city = Field(City)

# Example usage (if you have your data as a dictionary 'data'):

def resolve_weather_schema(root, info, data):
    return WeatherForecastType(
        cod=data.get("cod"),
        message=data.get("message"),
        cnt=data.get("cnt"),
        list=[
            ForecastItemType(
                datetime=Utilities.convert_time(item.get("dt")),
                main=MainDataType(
                    temp=item.get("main", {}).get("temp"),
                    feels_like=item.get("main", {}).get("feels_like"),
                    temp_min=item.get("main", {}).get("temp_min"),
                    temp_max=item.get("main", {}).get("temp_max"),
                    pressure=item.get("main", {}).get("pressure"),
                    sea_level=item.get("main", {}).get("sea_level"),
                    grnd_level=item.get("main", {}).get("grnd_level"),
                    humidity=item.get("main", {}).get("humidity"),
                    temp_kf=item.get("main", {}).get("temp_kf"),
                ),
                weather=[
                    WeatherDataType(
                        id=weather.get("id"),
                        main=weather.get("main"),
                        description=weather.get("description"),
                        icon=weather.get("icon"),
                    )
                    for weather in item.get("weather", [])
                ],
                clouds=CloudsDataType(all=item.get("clouds", {}).get("all")),
                wind=WindDataType(
                    speed=item.get("wind", {}).get("speed"),
                    deg=item.get("wind", {}).get("deg"),
                    gust=item.get("wind", {}).get("gust"),
                ),
                visibility=item.get("visibility"),
                pop=item.get("pop"),
                sys=SysDataType(pod=item.get("sys", {}).get("pod")),
                dt_txt=item.get("dt_txt"),
            )
            for item in data.get("list", [])
        ],
        city=City(
            id=data.get("city", {}).get("id"),
            name=data.get("city", {}).get("name"),
            coord=CoordType(lat=data.get("city", {}).get("coord", {}).get("lat"), lon=data.get("city", {}).get("coord", {}).get("lon")),
            country=data.get("city", {}).get("country"),
            population=data.get("city", {}).get("population"),
            timezone=data.get("city", {}).get("timezone"),
            sunrise=data.get("city", {}).get("sunrise"),
            sunset=data.get("city", {}).get("sunset"),
        ),
    )

class Query(ObjectType):
    weather = Field(WeatherForecastType, geo=GeoInput(required=True))

    def resolve_weather(root, info, geo):
        logger.info(f"Resolving weather for {geo.latlon}")
        lat, lon = geo.latlon
        w = WeatherAPI(lat, lon)
        data = w.get_weather()
        return resolve_weather_schema(root, info, data)


schema = Schema(query=Query)

app = Flask(__name__)

app.add_url_rule('/graphql', view_func=GraphQLView.as_view(
    'graphql',
    schema=schema,
    graphiql=True,
))

def getSchema():
    return schema

    
if __name__ == "__main__":
    print_schema(schema)
    logger.info("Starting server...")
    # app.run(debug=True, host='0.0.0.0')
    
