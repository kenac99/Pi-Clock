#!/usr/bin/env python3
# Fetches data from Ambient Weather API.
# Requires config.env with AMBIENT_API_KEY, AMBIENT_APP_KEY, STATION_MAC.
# Run via cron every 5 minutes:
#   */5 * * * * /usr/bin/python3 /home/pi/pi-clock/scrape-weather.py

import json, os, sys, urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT        = os.path.join(SCRIPT_DIR, "weather.json")

# Load credentials from config.env
env = {}
env_path = os.path.join(SCRIPT_DIR, "config.env")
if os.path.exists(env_path):
    for line in open(env_path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()

API_KEY = env.get("AMBIENT_API_KEY") or os.environ.get("AMBIENT_API_KEY", "")
APP_KEY = env.get("AMBIENT_APP_KEY") or os.environ.get("AMBIENT_APP_KEY", "")
MAC     = env.get("STATION_MAC")     or os.environ.get("STATION_MAC", "")

if not all([API_KEY, APP_KEY, MAC]):
    print("Error: missing credentials in config.env", file=sys.stderr)
    sys.exit(1)

URL = (
    f"https://rt.ambientweather.net/v1/devices/{MAC}"
    f"?applicationKey={APP_KEY}&apiKey={API_KEY}&limit=1"
)


def derive_condition(solar_wm2, humidity):
    if solar_wm2 > 600: return "Sunny"
    if solar_wm2 > 300: return "Mostly Sunny"
    if solar_wm2 > 100: return "Partly Cloudy"
    if solar_wm2 > 20:  return "Cloudy"
    if humidity > 80:   return "Overcast"
    return "Clear"


try:
    with urllib.request.urlopen(URL, timeout=10) as r:
        data = json.loads(r.read())[0]

    temp_f   = round(data["tempf"])
    solar    = float(data.get("solarradiation", 0))
    humidity = int(data.get("humidity", 50))

    condition = derive_condition(solar, humidity)
    weather   = f"{condition} - {temp_f}°F"
    print(weather)

    existing = {}
    if os.path.exists(OUT):
        with open(OUT) as f:
            existing = json.load(f)

    existing["weather"]   = weather
    existing["solar_wm2"] = solar
    existing["humidity"]  = humidity

    ckpool = existing.get("ckpool", "")
    existing["display"] = f"{weather} - {ckpool}" if ckpool else weather

    with open(OUT, "w") as f:
        json.dump(existing, f)

except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
