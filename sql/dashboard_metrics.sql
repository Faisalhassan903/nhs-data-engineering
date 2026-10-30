-- Read-only metrics used for the static dashboard, April–September 2026.
-- Filter is explicit so future months do not change this snapshot's scope.
WITH source AS (
 SELECT * FROM staging.ae_attendances
 WHERE period IN ('MSitAE-APRIL-2026', 'MSitAE-MAY-2026',
 'MSitAE-JUNE-2026', 'MSitAE-JULY-2026', 'MSitAE-AUGUST-2026',
 'MSitAE-SEPTEMBER-2026')
), totals AS (
 SELECT count(*) AS records,
 sum(ae_attendances_type_1) AS type_1,
 sum(ae_attendances_type_1 + ae_attendances_type_2 + ae_attendances_other_department) AS attendances,
 sum(attendances_over_4hrs_type_1 + attendances_over_4hrs_type_2 + attendances_over_4hrs_other_department) AS over_4_hours,
 sum(emergency_admissions_type_1 + emergency_admissions_type_2 + emergency_admissions_other_department + other_emergency_admissions) AS emergency_admissions
 FROM source
)
SELECT *, round(100.0 * (attendances - over_4_hours) / NULLIF(attendances, 0), 2) AS within_4_hours_percent FROM totals;
