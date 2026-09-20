
  create view "postgres"."public_staging"."stg_nasa_power__dbt_tmp"
    
    
  as (
    select
    city,
    country,
    lat,
    lon,
    year,
    month,
    t2m                                           as temp_c,
    -- NASA devuelve mm/día, convertimos a mm/mes
        precip * extract(day from (make_date(year::int, month::int, 1) + interval '1 month - 1 day'))
                                                  as precip_mm
from raw.nasa_power
where t2m is not null
  and precip is not null
  and month between 1 and 12
  );