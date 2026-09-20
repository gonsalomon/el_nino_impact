
  create view "postgres"."public_staging"."stg_oni__dbt_tmp"
    
    
  as (
    select
    seas,
    yr   as year,
    anom as sst_anomaly,
    enso_phase
from raw.oni
  );