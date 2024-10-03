import requests, pytz, re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from jdatetime import datetime as jdatetime
import pandas as pd
import os

# Converts gregorian dates to jalali
def ToJalali(date_time):
    jalali_date = jdatetime.fromgregorian(datetime=date_time)
    return jalali_date

# Export data to Excel
def export_data(data,filename,foldername):
    df = pd.DataFrame(data)
    if not os.path.exists(foldername):
        os.makedirs(foldername)
    file_path = os.path.join(foldername, f'{filename}.csv')
    if not os.path.exists(file_path):
        df.to_csv(file_path)
    else:
        existing_df = pd.read_csv(file_path)
        combined_df = existing_df._append(df, ignore_index=True)
        combined_df.to_csv(file_path, index=False)

# Generates a list of dates
def GetDates(start, end):
    dates = []
    if end is None:
        return [start]
    
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')
    current_date = start_date
    
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)

    return dates


# Gets the distance between the departure airport and arrival airport in kilometers
def GetFlightDistance(departure_airport, arrival_airport):
    
    url = f'https://www.airportdistancecalculator.com/flight-{departure_airport}-to-{arrival_airport}.html'
    
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        distance_element = soup.find('strong', string=re.compile(r'\d+ kilometers'))

        if distance_element:
            distance_text = distance_element.get_text()
            distance_in_km = re.search(r'(\d+) kilometers', distance_text).group(1)
            return distance_in_km
    else:
        raise ValueError("Couldn't get the distance")


# Converts local datetime to GMT datetime
def GetGMTDateTime(city_name, local_datetime):
    # Use geopy to get the timezone for the given city
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.geocode(city_name)
    timezone = pytz.timezone(location)
    print(timezone)
    # Convert the local datetime to the city's timezone
    local_datetime = timezone.localize(local_datetime)

    # Convert the localized datetime to GMT/UTC
    gmt_datetime = local_datetime.astimezone(pytz.utc)

    return gmt_datetime
    # try:
    #     geolocator = Nominatim(user_agent="city_timezone_lookup")
    #     try:
    #         location = geolocator.geocode(city_name, timeout=10)
    #     except GeocoderTimedOut:
    #         raise ValueError("Geocoding service timed out. try again")
        
    #     if location:
    #         tz_finder = TimezoneFinder()
    #         local_timezone_str = tz_finder.timezone_at(lng=location.longitude, lat=location.latitude)
    #         local_timezone = pytz.timezone(local_timezone_str)
    #         gmt_datetime = local_datetime.astimezone(pytz.utc)

    #         return gmt_datetime
    
    # except pytz.exceptions.UnknownTimeZoneError:
    #     return "Unknown time zone for the city"

# Extracting dollars price
def get_dollar():
    url = 'https://www.xe.com/currencyconverter/convert/?Amount=1&From=USD&To=IRR'
    response = requests.get(url)
    #sleep(1)
    soup = BeautifulSoup(response.text,'lxml')
    ratio = soup.find('div',class_='unit-rates___StyledDiv-sc-1dk593y-0 iGxfWX').find('p').text
    int = ratio.find('=') + 2
    change = float(ratio[int:ratio.find(' ', int)])
    return change
           