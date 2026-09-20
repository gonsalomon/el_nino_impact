# 🌊 El Niño Impact — Pipeline de Datos Climáticos

Proyecto open-source que analiza el impacto histórico de El Niño y La Niña en ciudades sudamericanas, y genera narrativas en lenguaje simple sobre el **Súper El Niño 2026** usando IA.

---

## ¿Qué hace este proyecto?

1. **Descarga** datos climáticos históricos (1981–2024) de la NASA y el índice ENSO de la NOAA
2. **Transforma** los datos con dbt, vinculando temperatura y precipitación a cada fase climática
3. **Valida** la calidad del dato con Soda
4. **Genera** narrativas en lenguaje simple por ciudad usando un LLM (Groq), contextualizadas en el evento de Súper El Niño que se está formando en 2026

---

## Contexto

La NOAA estima un **81% de probabilidad** de que el Súper El Niño 2026 alcance intensidad histórica entre octubre y diciembre, comparable al evento de 1997–1998. Este proyecto traduce esos datos en algo que cualquier persona pueda entender.

---

## Stack

| Capa | Tecnología |
|------|-----------|
| Ingesta | Python + requests |
| Almacenamiento | PostgreSQL (Supabase) |
| Transformación | dbt Core |
| Calidad | Soda Core |
| Narrativas IA | Groq API (openai/gpt-oss-20b) |

---

## Fuentes de datos

- **[NASA POWER API](https://power.larc.nasa.gov/)** — Temperatura media y precipitación mensual por coordenada (1981–2024), gratis
- **[NOAA ONI Index](https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt)** — Índice oficial de clasificación El Niño / La Niña / Neutro, gratis

---

## Ciudades analizadas

| Ciudad | País |
|--------|------|
| Buenos Aires | Argentina |
| Rosario | Argentina |
| Tandil | Argentina |
| Santiago | Chile |
| Puerto Montt | Chile |
| Lima | Perú |
| Bogotá | Colombia |
| São Paulo | Brasil |
| Manaus | Brasil |

---

## Arquitectura

```
NASA POWER API ──┐
                 ├──► Python ingesta ──► PostgreSQL (raw)
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
                                   Groq API (narrativas)
                                              │
                                              ▼
                                   public.city_narratives
```

---

## Estructura del repo

```
el_nino_impact/
├── ingesta/
│   ├── cities.py          # Coordenadas de ciudades
│   ├── fetch_nasa.py      # Descarga datos NASA POWER
│   ├── fetch_oni.py       # Descarga índice ONI de NOAA
│   └── load_postgres.py   # Carga CSVs a PostgreSQL
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
│   └── generate.py        # Genera y persiste narrativas con Groq
├── .env.example
└── requirements.txt
```

---

## Setup

### 1. Clonar y configurar entorno

```bash
git clone https://github.com/tu-usuario/el_nino_impact.git
cd el_nino_impact
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Completar `.env`:

```
DB_HOST=tu-host.supabase.com
DB_PORT=6543
DB_NAME=postgres
DB_USER=postgres.tu-proyecto
DB_PASSWORD=tu-password
GROQ_API_KEY=gsk_...
```

### 3. Ingestar datos

```bash
cd ingesta
python fetch_oni.py
python fetch_nasa.py
python load_postgres.py
```

### 4. Correr transformaciones dbt

```bash
cd ../dbt
dbt run
```

### 5. Validar calidad con Soda

```bash
cd ../soda
# Cargar variables de entorno primero (PowerShell):
Get-Content ..\.env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]+)=(.+)$') {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim(), 'Process')
    }
}
soda scan -d el_nino -c configuration.yml checks/mart_climate_by_enso.yml
```

### 6. Generar narrativas

```bash
cd ../narrativas
python generate.py
```

---

## Notas técnicas

- NASA POWER devuelve un registro con `month=13` (promedio anual) — filtrado en staging con `WHERE month BETWEEN 1 AND 12`
- La precipitación de NASA viene en **mm/día** (promedio mensual) — convertida a mm/mes multiplicando por días del mes
- El índice ONI es trimestral; cada mes se mapea a su trimestre correspondiente para el join con datos de temperatura
- El modelo `openai/gpt-oss-20b` de Groq es de razonamiento — requiere `max_tokens >= 2048` para producir output en español

---

## Roadmap

- [ ] Visualización interactiva: mapa de Sudamérica con narrativas por ciudad
- [ ] Agregar más ciudades
- [ ] Comparativa histórica: 1997–1998 vs 2015–2016 vs 2026
- [ ] Dashboard público con actualización automática

---

## Licencia

MIT