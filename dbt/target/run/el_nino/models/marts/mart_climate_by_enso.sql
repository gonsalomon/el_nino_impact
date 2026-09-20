
  
    

  create  table "postgres"."public_marts"."mart_climate_by_enso__dbt_tmp"
  
  
    as
  
  (
    with weather as (
    select * from "postgres"."public_staging"."stg_nasa_power"
),

oni as (
    select * from "postgres"."public_staging"."stg_oni"
),

-- ONI viene en trimestres (DJF, JFM...). Mapeamos cada mes a su trimestre.
month_to_seas as (
    select * from (values
        (12, 'DJF'), (1, 'DJF'), (2, 'DJF'),
        (1,  'JFM'), (2, 'JFM'), (3, 'JFM'),
        (2,  'FMA'), (3, 'FMA'), (4, 'FMA'),
        (3,  'MAM'), (4, 'MAM'), (5, 'MAM'),
        (4,  'AMJ'), (5, 'AMJ'), (6, 'AMJ'),
        (5,  'MJJ'), (6, 'MJJ'), (7, 'MJJ'),
        (6,  'JJA'), (7, 'JJA'), (8, 'JJA'),
        (7,  'JAS'), (8, 'JAS'), (9, 'JAS'),
        (8,  'ASO'), (9, 'ASO'), (10,'ASO'),
        (9,  'SON'), (10,'SON'), (11,'SON'),
        (10, 'OND'), (11,'OND'), (12,'OND'),
        (11, 'NDJ'), (12,'NDJ'), (1, 'NDJ')
    ) as t(month, seas)
),

joined as (
    select
        w.city,
        w.country,
        w.year,
        w.month,
        w.temp_c,
        w.precip_mm,
        o.sst_anomaly,
        o.enso_phase
    from weather w
    left join month_to_seas m on w.month = m.month
    left join oni o
        on m.seas = o.seas
        and w.year = o.year
)

select
    city,
    country,
    year,
    month,
    temp_c,
    precip_mm,
    sst_anomaly,
    enso_phase
from joined
  );
  