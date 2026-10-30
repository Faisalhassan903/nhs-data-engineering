-- Read-only checks of the existing local database.
SELECT 'staging' AS layer, count(*) AS records FROM staging.ae_attendances
UNION ALL
SELECT 'warehouse', count(*) FROM warehouse.fact_ae_monthly;
