import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os

load_dotenv()

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode="require",
    )

DDL = """
CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.nasa_power (
    city        TEXT,
    country     TEXT,
    lat         FLOAT,
    lon         FLOAT,
    year        INT,
    month       INT,
    t2m         FLOAT,
    precip      FLOAT
);

CREATE TABLE IF NOT EXISTS raw.oni (
    seas        TEXT,
    yr          INT,
    total       FLOAT,
    anom        FLOAT,
    enso_phase  TEXT
);
"""

def load_csv(conn, table: str, df: pd.DataFrame):
    cols = list(df.columns)
    rows = [tuple(r) for r in df.itertuples(index=False)]
    sql = f"INSERT INTO {table} ({', '.join(cols)}) VALUES %s"
    with conn.cursor() as cur:
        execute_values(cur, sql, rows)
    conn.commit()
    print(f"{len(rows)} filas cargadas en {table}")

if __name__ == "__main__":
    conn = get_conn()

    with conn.cursor() as cur:
        cur.execute(DDL)
    conn.commit()

    load_csv(conn, "raw.nasa_power", pd.read_csv("raw_nasa_power.csv"))
    load_csv(conn, "raw.oni",        pd.read_csv("raw_oni.csv"))

    conn.close()