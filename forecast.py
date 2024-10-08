# Name:forecast

# Author: Stig Dahl <stig@charlottendal.net>
# Created: 2024-10-02

'''
Using data from YR.NO (MET Norway) to lookup the weather forecast.

TODO:
- Add location
- Read .env file
- Cache data locally
- Create directory structure at initial startup
- Error handling
- Add credits
- Follow Expires header, If-Modified-Since
- Save an example to disk, use that for data processing and tests
'''

# Import modules
import requests
from pathlib import Path
import json

EXAMPLE_URI='https://api.met.no/weatherapi/locationforecast/2.0/compact'
EXAMPLE_PAYLOAD = {"lat": 60.10, "lon": 9.58}
USER_AGENT = "Forecast/0.1.0 github.com/sdaaish/forecast"
headers = {"User-Agent": USER_AGENT}

# Define main function
def main():
    r = requests.get(EXAMPLE_URI, params=EXAMPLE_PAYLOAD,headers=headers)
#    r = requests.get('https://api.met.no/weatherapi/locationforecast/2.0/status',headers=headers)
    print(r.url)
    print(r.status_code)
    json= r.json()
    meta= json["properties"]["meta"]
    coordinates = json["geometry"]["coordinates"]
    instant = json["properties"]["timeseries"][0]
    print(meta,coordinates)
    print(f'{instant["time"]}, {instant["data"]["instant"]["details"]}')

if __name__ == "__main__":
    main()
