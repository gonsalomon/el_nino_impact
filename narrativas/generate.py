import time
import os
import requests
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_KEY = os.getenv("GROQ_API_KEY")

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require",
    )

def create_table(conn):
    sql = """
        CREATE TABLE IF NOT EXISTS public.city_narratives (
            id           SERIAL PRIMARY KEY,
            city         TEXT NOT NULL,
            country      TEXT NOT NULL,
            narrative    TEXT NOT NULL,
            model        TEXT NOT NULL,
            generated_at TIMESTAMPTZ DEFAULT now()
        )
    """
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()

def save_narrative(conn, city: str, country: str, narrative: str):
    sql = """
        INSERT INTO public.city_narratives (city, country, narrative, model)
        VALUES (%s, %s, %s, %s)
    """
    with conn.cursor() as cur:
        cur.execute(sql, (city, country, narrative, "openai/gpt-oss-20b"))
    conn.commit()

def fetch_summary() -> pd.DataFrame:
    sql = """
        select
            city,
            country,
            enso_phase,
            round(avg(temp_c)::numeric, 2)     as avg_temp_c,
            round(avg(precip_mm)::numeric, 2)  as avg_precip_mm
        from public_marts.mart_climate_by_enso
        where enso_phase is not null
        group by city, country, enso_phase
        order by city, enso_phase
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return pd.DataFrame(rows, columns=cols)

def build_prompt(city: str, country: str, stats: dict) -> str:
    nino    = stats.get("el_nino",  {})
    nina    = stats.get("la_nina",  {})
    neutral = stats.get("neutral",  {})

    return (
        f"Ciudad: {city}, {country}\n"
        f"Años normales:  {neutral.get('avg_temp_c')}°C, {neutral.get('avg_precip_mm')} mm/mes\n"
        f"Años El Niño:   {nino.get('avg_temp_c')}°C, {nino.get('avg_precip_mm')} mm/mes\n"
        f"Años La Niña:   {nina.get('avg_temp_c')}°C, {nina.get('avg_precip_mm')} mm/mes\n\n"
        f"Contexto actual: la NOAA estima 81% de probabilidad de un Súper El Niño "
        f"de intensidad histórica hacia octubre-diciembre 2026, comparable al evento de 1997-1998. "
        f"Basándote en los datos históricos de esta ciudad, explicá en 3 oraciones "
        f"qué puede esperar concretamente la gente que vive ahí."
    )

def call_gemini(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "openai/gpt-oss-20b",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2048,
    }
    r = requests.post(GROQ_URL, headers=headers, json=body, timeout=30)
    if r.status_code != 200:
        r.raise_for_status()
    content = r.json()["choices"][0]["message"]["content"]
    return content

def generate_all():
    df = fetch_summary()
    conn = get_conn()
    create_table(conn)
    cities = df.groupby(["city", "country"])

    for (city, country), group in cities:
        stats = {
            row["enso_phase"]: {
                "avg_temp_c":    row["avg_temp_c"],
                "avg_precip_mm": row["avg_precip_mm"],
            }
            for _, row in group.iterrows()
        }

        prompt    = build_prompt(city, country, stats)
        narrative = call_gemini(prompt)

        print(f"\n{'='*50}")
        print(f"{city}, {country}")
        print(f"{'='*50}")
        print(narrative)
        save_narrative(conn, city, country, narrative)
    conn.close()
    time.sleep(3)

if __name__ == "__main__":
    generate_all()