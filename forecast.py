# Name:forecast

# Author: Stig Dahl <stig@charlottendal.net>
# Created: 2024-10-02

"""
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
"""

# Import modules
import json
import sys
from pathlib import Path

import requests

COMPACT_URI = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
LOCATION = {"lat": 60.10, "lon": 9.58}
USER_AGENT = "Forecast/0.1.0 github.com/sdaaish/forecast"
headers = {"User-Agent": USER_AGENT}


def get_forecast(uri, params):
    try:
        response = requests.get(COMPACT_URI, params=LOCATION, headers=headers)
    except ConnectionError():
        print(repr(sys.exception()))
    # or response.raise_for_status() # ensure we notice bad responses
    return response


def save_to_file(file, resp):
    p = Path(file).resolve()
    with open(p, encoding="utf-8", mode="w") as f:
        json.dump(resp, f, indent=2)


# Define main function
def main():
    r = get_forecast(COMPACT_URI, LOCATION)

    print(r.url)
    print(r.status_code)
    data = r.json()
    save_to_file("response.json", data)

    meta = data["properties"]["meta"]
    coordinates = data["geometry"]["coordinates"]
    instant = data["properties"]["timeseries"][0]
    print(f"Meta: {meta['units']}")
    print(meta["units"], coordinates)
    print(f'{instant["time"]}, {instant["data"]["instant"]["details"]}')

    print("#" * 10)
    for k, v in instant["data"].items():
        print(f"Key: {k}:")

        for y in v:
            print(f"Value:  {y}: {v[y]}")

    print("#" * 10)
    for k, v in instant["data"].items():
        if k == "instant":
            print(f"Air pressure:\t{v['details']['air_pressure_at_sea_level']}")
            print(f"Air temperature:\t{v['details']['air_temperature']}")
            print(f"Cloudiness:\t{v['details']['cloud_area_fraction']}")
            print(f"Humidity:\t{v['details']['relative_humidity']}")
            print(f"Wind direction:\t{v['details']['wind_from_direction']}")
            print(f"Wind speed:\t{v['details']['wind_speed']}")
        else:
            print(f"Summary:\t{v['summary']}")


if __name__ == "__main__":
    main()
