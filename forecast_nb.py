# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.20.1",
#     "pydantic==2.12.5",
#     "pydantic-ai==1.63.0",
#     "requests==2.32.5",
# ]
# ///

import marimo

__generated_with = "0.20.2"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import json
    import os
    import sys
    from pathlib import Path
    from datetime import datetime, timedelta
    import requests

    return datetime, mo, requests


@app.cell
def _():
    COMPACT_URI = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
    NOMINATIM_URI = "https://nominatim.openstreetmap.org/search"
    USER_AGENT = "Forecast/0.1.0 github.com/sdaaish/forecast"
    HEADERS = {"User-Agent": USER_AGENT}

    SYMBOLS = {
        "partlycloudy_day": "⛅ Partly Cloudy",
        "partlycloudy_night": "🌙 Partly Cloudy",
        "fair_night": "🌌 Fair",
        "fair_day": "☀️ Fair",
        "clearsky_day": "☀️ Clear Sky",
        "clearsky_night": "🌙 Clear Sky",
        "cloudy": "☁️ Cloudy",
        "lightrain": "🌧️ Light Rain",
        "rain": "🌧️ Rain",
        "heavyrain": "⛈️ Heavy Rain",
        "snow": "❄️ Snow",
        "sleet": "🌨️ Sleet",
        "fog": "🌫️ Fog",
    }
    return COMPACT_URI, HEADERS, NOMINATIM_URI, SYMBOLS


@app.cell
def _(mo):
    # Initialize state for latitude and longitude
    get_lat, set_lat = mo.state(60.10)
    get_lon, set_lon = mo.state(9.58)
    return get_lat, get_lon, set_lat, set_lon


@app.cell
def _(mo):
    search_input = mo.ui.text(placeholder="Search for a city or place...", label="Location Search")
    search_form = search_input.form(label="Search")
    return (search_form,)


@app.cell
def _(HEADERS, NOMINATIM_URI, mo, requests, search_form, set_lat, set_lon):
    current_search = search_form.value

    search_results = None
    if current_search:
        params = {
            "q": current_search,
            "format": "json",
            "limit": 1
        }
        try:
            resp = requests.get(NOMINATIM_URI, params=params, headers=HEADERS, timeout=5)
            resp.raise_for_status()
            results = resp.json()
            if results:
                res = results[0]
                lat, lon = float(res["lat"]), float(res["lon"])
                set_lat(lat)
                set_lon(lon)
                search_results = mo.md(
                    f"✅ Found: **{res['display_name']}**\n\n"
                    f"📍 **Coordinates:** {lat}°N, {lon}°E"
                )
            else:
                search_results = mo.md("⚠️ No locations found.")
        except Exception as e:
            search_results = mo.md(f"❌ Error searching: {e}")

    mo.vstack([
        mo.md("### 🔍 Find a Place"),
        search_form,
        search_results if search_results else mo.md("")
    ])
    return


@app.cell
def _(HEADERS, requests):
    def get_forecast(uri, location):
        """Get the forecast for the location."""
        try:
            response = requests.get(uri, params=location, headers=HEADERS, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    return (get_forecast,)


@app.cell
def _(COMPACT_URI, get_forecast, get_lat, get_lon):
    data = get_forecast(COMPACT_URI, {"lat": get_lat(), "lon": get_lon()})
    return (data,)


@app.cell
def _(SYMBOLS, data, datetime, mo):
    mo.stop("error" in data, mo.md(f"⚠️ **Error fetching forecast:** {data.get('error')}"))

    meta = data["properties"]["meta"]
    update_time = meta["updated_at"]
    coords = data["geometry"]["coordinates"]
    timeseries = data["properties"]["timeseries"]
    instant = timeseries[0]

    # Current Conditions
    details = instant["data"]["instant"]["details"]
    summary = instant["data"].get("next_1_hours", {}).get("summary", {})
    symbol_code = summary.get("symbol_code", "unknown")
    symbol_text = SYMBOLS.get(symbol_code, symbol_code)

    # Multi-day forecast (Next 3 days)
    daily_data = {}
    for entry in timeseries:
        time = datetime.fromisoformat(entry["time"].replace("Z", "+00:00"))
        day_str = time.strftime("%Y-%m-%d")
        if day_str not in daily_data:
            daily_data[day_str] = {"temps": [], "symbols": []}

        # Collect temperatures
        if "air_temperature" in entry["data"]["instant"]["details"]:
            daily_data[day_str]["temps"].append(entry["data"]["instant"]["details"]["air_temperature"])

        # Collect symbols from 6-hour windows if available
        if "next_6_hours" in entry["data"]:
            daily_data[day_str]["symbols"].append(entry["data"]["next_6_hours"]["summary"]["symbol_code"])

    # Build 3-day cards
    forecast_cards = []
    today = datetime.now().strftime("%Y-%m-%d")
    count = 0
    for day, info in daily_data.items():
        if day == today: continue # Skip today for the multi-day list
        if count >= 3: break

        max_t = max(info["temps"]) if info["temps"] else "N/A"
        min_t = min(info["temps"]) if info["temps"] else "N/A"

        # Pick most frequent symbol or just the first one
        main_symbol = info["symbols"][0] if info["symbols"] else "unknown"
        symbol_display = SYMBOLS.get(main_symbol, main_symbol)

        date_obj = datetime.strptime(day, "%Y-%m-%d")
        day_name = date_obj.strftime("%A, %b %d")

        forecast_cards.append(
            mo.md(f"""
            **{day_name}**
            # {symbol_display.split()[0]}
            **{max_t}° / {min_t}°**
            { " ".join(symbol_display.split()[1:]) }
            """).style({"text-align": "center", "padding": "10px", "border": "1px solid #ddd", "border-radius": "8px"})
        )
        count += 1

    current_ui = mo.vstack([
        mo.md(f"## Weather Forecast"),
        mo.md(f"**Updated at:** {update_time}"),
        mo.md(f"**Coordinates:** {coords[1]}°N, {coords[0]}°E"),
        mo.md(f"### Current Conditions: {symbol_text}"),
        mo.hstack([
            mo.stat(label="Temperature", value=f"{details['air_temperature']}°C"),
            mo.stat(label="Wind Speed", value=f"{details['wind_speed']} m/s"),
            mo.stat(label="Humidity", value=f"{details['relative_humidity']}%"),
            mo.stat(label="Pressure", value=f"{details['air_pressure_at_sea_level']} hPa"),
        ], justify="start")
    ])

    multi_day_ui = mo.vstack([
        mo.md("### 📅 Next 3 Days"),
        mo.hstack(forecast_cards, justify="start")
    ])

    mo.vstack([current_ui, multi_day_ui])
    return


if __name__ == "__main__":
    app.run()
