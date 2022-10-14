# -*- coding: utf-8 -*-
"""
Created on Sat Oct 16 17:23:43 2021

@author: nedwards1
"""
import datetime
from datetime import datetime, timedelta
import geopy
import geocoder
from geopy.geocoders import Nominatim
import requests
import json
import smtplib
import ssl
import pytz

# project variables defined here (unconcerned about security on sending email)
city = "Tacoma"
state = "WA"
sender_email = "cefishingreport@gmail.com"
password = ""
receiver_email = "cefishingreport@gmail.com"
nl = '\n'


def send_email(sender_email, receiver_email, message, password):
    port = 465
    context = ssl.create_default_context()
    # log in to gmail and send message
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


def get_weather(city, state, time_stamp):
    """gets weather forecast for city and state"""
    ts = time_stamp

    # get lat/long for city, state
    app = Nominatim(user_agent="fishing report")
    city_state = f"{city}, {state}"
    location = app.geocode(city_state).raw
    latitude = location["lat"]
    longitude = location["lon"]

    # call OpenWeather API
    api_key = "71aea448c0fafed68f17c867506c0e25"
    url = (
        f"https://api.openweathermap.org/data/2.5/onecall?"
        f"lat={latitude}&lon={longitude}&exclude=hourly,minutely"
        f"&appid={api_key}&units=imperial"
    )
    response = requests.get(url)
    # convert json format data into python format
    x = response.json()
    # extract daily forecasts as a list of dictionaries
    daily = x["daily"]
    return(daily)
    # find the forecast for the relevant day
    for daily_weather in daily:
        forecast_day = daily_weather['dt']
        if forecast_day == ts:
            sunrise_ts = daily_weather['sunrise']
            sunrise = datetime.fromtimestamp(sunrise_ts).strftime('%H:%M')
            temp = daily_weather['temp']
            morning_temp = int(temp['morn'])
            day_temp = int(temp['day'])
            wind_speed = daily_weather['wind_speed']
            w = daily_weather['weather']
            weather = w[0]['main']
            detail = w[0]['description']
            forecast = (f"Overall weather: {weather} with {detail}."
                        f"{nl}Morning: Temp {morning_temp}F, sunrise"
                        f" at {sunrise}."
                        f"{nl}Daytime: Temp {day_temp}F, wind speed"
                        f" {wind_speed}mph.")
            return forecast


def get_ts(ddate):
    """returns integer timestamp for midnight of given date"""
    newdate = datetime(ddate.year, ddate.month, ddate.day,
                       12, 00, tzinfo=pytz.timezone(
                           'America/Los_Angeles'))
    newdate_ts = datetime.timestamp(newdate)
    ts = int(newdate_ts)
    return ts


# find relevant dates and timestamps
# "this" sat/sun refers to current or first upcoming
# "next" sat/sun refers to following "this" sat/sun
today = datetime.now()
today_date = today.strftime("%m/%d/%Y")
next_mon = today + timedelta(days=-today.weekday(), weeks=1)
this_sun = next_mon - timedelta(days=1)
this_sat = next_mon - timedelta(days=2)
next_sat = next_mon + timedelta(days=5)
next_sun = next_mon + timedelta(days=6)
todayts = get_ts(today)
thissatts = get_ts(this_sat)
thissunts = get_ts(this_sun)
nextsatts = get_ts(next_sat)
nextsunts = get_ts(next_sun)

# get weather forecasts for each of the weekend days
sat_weather = get_weather(city, state, thissatts)
sun_weather = get_weather(city, state, thissunts)
nextsat_weather = get_weather(city, state, nextsatts)
nextsun_weather = get_weather(city, state, nextsunts)

nextwknd_msg = (f"Next weekend's forecast:{nl}{nl}"
                f"Next Saturday{nl}{nextsat_weather}{nl}{nl}"
                f"Next Sunday{nl}{nextsun_weather}{nl}")

if today.isoweekday() == 6:
    text = (f"Today's forecast:{nl}{sat_weather}{nl}{nl}"
            f"Tomorrow's forecast:{nl}{sun_weather}{nl}{nl}"
            f"{nextwknd_msg}")
elif today.isoweekday() == 7:
    text = (f"Today's forecast:{nl}{sun_weather}{nl}{nl}"
            f"{nextwknd_msg}")
else:
    text = nextwknd_msg
subject = f"Daily Fishing Report {today_date}"
message = f"Subject: {subject}{nl}{nl}{text}"
# (sender_email, receiver_email, message, password)

# print(get_weather('Tacoma', 'WA', nextsatts))
print(thissunts)
