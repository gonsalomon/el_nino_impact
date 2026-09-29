# 🌊 El Niño Impact — Climate Data Pipeline

Open-source project that analyzes the historical impact of El Niño and La Niña on South American cities, and uses AI to generate plain-language narratives about the 2026 Super El Niño.

## What does this project do?

- Downloads historical climate data (1981–2024) from NASA and the ENSO index from NOAA
- Transforms the data with dbt, linking temperature and precipitation to each climate phase
- Validates data quality with Soda
- Generates plain-language narratives per city using an LLM (Groq), contextualized in the Super El Niño event forming in 2026

## Context

NOAA estimates a greater than 90% probability [link](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/ensodisc.shtml) that the 2026 Super El Niño will reach historic intensity between October and December, comparable to the 1997–1998 event. This project hopes to turn that data into something anyone can understand. It's still in baby steps... what about people who never touched a line of code? Many things are coming...

## Stack

| Layer | Technology |
|---|---|
| Ingestion | Python + requests |
| Storage | PostgreSQL (Supabase) |
| Transformation | dbt Core |
| Quality | Soda Core |
| AI narratives | Groq API (openai/gpt-oss-20b) |

## Data sources

- **NASA POWER API** — Monthly mean temperature and precipitation by coordinate (1981–2024), free
- **NOAA ONI Index** — Official El Niño / La Niña / Neutral classification index, free

## Cities analyzed

| City | Country |
|---|---|
| Buenos Aires | Argentina |
| Rosario | Argentina |
| Tandil | Argentina |
| Santiago | Chile |
| Puerto Montt | Chile |
| Lima | Peru |
| Bogotá | Colombia |
| São Paulo | Brazil |
| Manaus | Brazil |

## Architecture

```
NASA POWER API ──┐
                 ├──► Python ingestion ──► PostgreSQL (raw)
NOAA ONI CSV ────┘                            │
                                              ▼
                                        dbt models
                                   stg_nasa_power (view)
                                   stg_oni (view)
                                   mart_climate_by_enso (table)
                                              │
                                              ▼
                                        Soda checks
                                      (11/11 passing)
                                              │
                                              ▼
                                   Groq API (narratives)
                                              │
                                              ▼
                                   public.city_narratives
```

## Repo structure

```
el_nino_impact/
├── ingesta/
│   ├── cities.py          # City coordinates
│   ├── fetch_nasa.py      # Downloads NASA POWER data
│   ├── fetch_oni.py       # Downloads NOAA ONI index
│   └── load_postgres.py   # Loads CSVs into PostgreSQL
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/
│       │   ├── stg_nasa_power.sql
│       │   └── stg_oni.sql
│       └── marts/
│           └── mart_climate_by_enso.sql
├── soda/
│   ├── configuration.yml
│   └── checks/
│       └── mart_climate_by_enso.yml
├── narrativas/
│   └── generate.py        # Generates and persists narratives with Groq
├── .env.example
└── requirements.txt
```

## Setup

### 1. Clone and set up the environment

```bash
git clone https://github.com/gonsalomon/el_nino_impact.git
cd el_nino_impact
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Fill in `.env`:

```
DB_HOST=your-host.supabase.com
DB_PORT=6543
DB_NAME=postgres
DB_USER=postgres.your-project
DB_PASSWORD=your-password
GROQ_API_KEY=gsk_...
```

### 3. Ingest data

```bash
cd ingesta
python fetch_oni.py
python fetch_nasa.py
python load_postgres.py
```

### 4. Run dbt transformations

```bash
cd ../dbt
dbt run
```

### 5. Validate quality with Soda

```powershell
cd ../soda
# Load environment variables first (PowerShell):
Get-Content ..\.env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.+)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), 'Process')
    }
}
soda scan -d el_nino -c configuration.yml checks/mart_climate_by_enso.yml
```

### 6. Generate narratives

```bash
cd ../narrativas
python generate.py
```

## Technical notes

- NASA POWER returns a record with `month=13` (annual average) — filtered out in staging with `WHERE month BETWEEN 1 AND 12`
- NASA precipitation comes in mm/day (monthly average) — converted to mm/month by multiplying by the days in the month
- The ONI index is quarterly; each month is mapped to its corresponding quarter to join with the temperature data
- Groq's `openai/gpt-oss-20b` is a reasoning model — it requires `max_tokens >= 2048` to produce output in Spanish, which is what this repo was originally aimed at

## Roadmap

- [ ] Interactive visualization: map of South America with per-city narratives
- [ ] Add more cities
- [ ] Historical comparison: 1997–1998 vs 2015–2016 vs 2026
- [ ] Public dashboard with automatic updates

## License

MIT
