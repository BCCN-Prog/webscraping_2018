from pony.orm import *


db = Database()


class DailyPrediction(db.Entity):
    id = PrimaryKey(int, auto=True)
    website = Required(str)
    city = Required(str)
    date_of_aquisition = Required(str)
    date_for_which_weather_is_predicted = Required(str)
    temperature_max = Required(float)
    temperature_min = Required(float)
    wind_speed = Optional(float, nullable=True)
    humidity = Optional(float, nullable=True)
    precipation_per = Optional(float, nullable=True)
    precipation_l = Optional(float, nullable=True)
    wind_direction = Optional(str, 3, nullable=True)
    condition = Optional(str, nullable=True)
    snow = Optional(float, nullable=True)
    UVI = Optional(int, unsigned=True)


class HourlyPrediction(db.Entity):
    id = PrimaryKey(int, auto=True)
    website = Required(str)
    city = Required(str)
    date_of_acquisition = Required(str)
    date_for_which_weather_is_predicted = Required(str)
    temperature = Required(float)
    wind_speed = Optional(float)
    humidity = Optional(float)
    precipitation_per = Optional(float)
    precipitation_l = Optional(float)
    wind_direction = Optional(str, 3)
    condition = Optional(str)
    snow = Optional(float)
    UVI = Optional(int, unsigned=True)


class DailyPeriodPrediction(db.Entity):
    id = PrimaryKey(int, auto=True)
    website = Required(str)
    city = Required(str)
    date_of_acquisition = Required(str)
    date_for_which_weather_is_predicted = Required(str)
    temperature = Required(float)
    wind_speed = Optional(float)
    precipitation_per = Optional(float)
    precipitation_l = Optional(float)
    wind_direction = Optional(str, 3)
    condition = Optional(str)



db.generate_mapping()