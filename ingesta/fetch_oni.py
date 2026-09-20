import requests
import pandas as pd
from io import StringIO

ONI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"

def fetch_oni() -> pd.DataFrame:
    r = requests.get(ONI_URL, timeout=30)
    r.raise_for_status()

    df = pd.read_csv(StringIO(r.text), sep=r"\s+")
    df.columns = df.columns.str.lower()

    # ANOM = anomalía SST en región Niño 3.4
    # Clasificación estándar NOAA: ±0.5°C por al menos 5 trimestres
    df["enso_phase"] = "neutral"
    df.loc[df["anom"] >=  0.5, "enso_phase"] = "el_nino"
    df.loc[df["anom"] <= -0.5, "enso_phase"] = "la_nina"

    df.to_csv("raw_oni.csv", index=False)
    print(f"{len(df)} trimestres guardados en raw_oni.csv")
    return df

if __name__ == "__main__":
    fetch_oni()