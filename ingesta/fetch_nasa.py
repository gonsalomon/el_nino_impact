import requests
import pandas as pd
import time
from cities import CITIES

NASA_URL = "https://power.larc.nasa.gov/api/temporal/monthly/point"
START_YEAR = 1981
END_YEAR   = 2024

def fetch_city(city: dict) -> pd.DataFrame:
    params = {
        "parameters": "T2M,PRECTOTCORR",
        "community":  "RE",
        "longitude":  city["lon"],
        "latitude":   city["lat"],
        "start":      START_YEAR,
        "end":        END_YEAR,
        "format":     "JSON",
    }
    r = requests.get(NASA_URL, params=params, timeout=60)
    r.raise_for_status()

    data = r.json()["properties"]["parameter"]
    rows = []
    for yyyymm, temp in data["T2M"].items():
        rows.append({
            "city":    city["name"],
            "country": city["country"],
            "lat":     city["lat"],
            "lon":     city["lon"],
            "year":    int(yyyymm[:4]),
            "month":   int(yyyymm[4:]),
            "t2m":     temp,
            "precip":  data["PRECTOTCORR"].get(yyyymm),
        })
    return pd.DataFrame(rows)

def fetch_all() -> pd.DataFrame:
    dfs = []
    for city in CITIES:
        print(f"Fetching {city['name']}...")
        dfs.append(fetch_city(city))
        time.sleep(1)  # respetar rate limit de NASA
    return pd.concat(dfs, ignore_index=True)

if __name__ == "__main__":
    df = fetch_all()
    df.to_csv("raw_nasa_power.csv", index=False)
    print(f"{len(df)} filas guardadas en raw_nasa_power.csv")