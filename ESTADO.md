# El Niño Impact — Estado del proyecto

## Stack
- Python 3.14, dbt 1.12.5, PostgreSQL via Supabase
- Supabase: aws-0-us-east-1.pooler.supabase.com:6543
- Groq API: openai/gpt-oss-20b (max_tokens: 1024)

## Completado
- Ingesta NASA POWER (1981-2024) → raw.nasa_power (5148 filas)
- Ingesta NOAA ONI → raw.oni (919 filas)
- dbt staging: stg_nasa_power, stg_oni
- dbt mart: mart_climate_by_enso (14256 filas)
- Soda: 11/11 quality checks en mart_climate_by_enso
- Narrativas generadas y persistidas en public.city_narratives (8/9 ciudades)
- Puerto Montt falla: modelo de razonamiento agota tokens pensando en español

## Prompt actual (Groq)
System:
  "Eres un meteorólogo experto pero que le habla a niños o personas sin
  conocimiento técnico. Tu objetivo es explicar el impacto del fenómeno
  'Súper El Niño' en Sudamérica usando analogías cotidianas (piscinas,
  esponjas, sartenes). Sé breve, empático y directo."

User (build_prompt):
  - Datos históricos por ciudad (normal / El Niño / La Niña)
  - Contexto: NOAA estima 81% de prob. de Súper El Niño histórico
    hacia oct-dic 2026, comparable a 1997-1998
  - Pedido: 3 oraciones concretas para la gente que vive ahí

## Fixes aplicados
- month BETWEEN 1 AND 12 (NASA devuelve mes 13 como promedio anual)
- extract(day from ...) en vez de day() — PostgreSQL no tiene day()
- dbt en PATH: C:\Users\Gonza\AppData\Roaming\Python\Python314\Scripts\
- Soda: cargar .env manualmente con PowerShell antes del scan
- Soda config: "data_source el_nino:" (singular, no "data_sources:")
- Gemini descartado: keys AQ. no funcionan con REST API directo
- Groq: llama-3.1-8b-instant y llama-3.3-70b-versatile deprecated en free tier
- Groq: max_tokens=300 insuficiente (modelo de razonamiento usa tokens en pensar)

## Pendiente
1. Resolver Puerto Montt (narrativa manual o max_tokens=2048)
2. Visualización: mapa interactivo Sudamérica + narrativas por ciudad

## Estructura
el_nino_impact/
├── ingesta/
│   ├── cities.py
│   ├── fetch_nasa.py
│   ├── fetch_oni.py
│   └── load_postgres.py
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/stg_nasa_power.sql
│       ├── staging/stg_oni.sql
│       └── marts/mart_climate_by_enso.sql
├── soda/
│   ├── configuration.yml
│   └── checks/mart_climate_by_enso.yml
└── narrativas/
    └── generate.py

## Ciudades incluidas
Tandil AR, Buenos Aires AR, Rosario AR, Santiago CL,
Lima PE, Bogota CO, Sao Paulo BR, Manaus BR, Puerto Montt CL

## Fuentes de datos
- NASA POWER API: temperatura (T2M) y precipitación (PRECTOTCORR), 1981-2024
- NOAA ONI: índice oficial El Niño/La Niña por trimestre