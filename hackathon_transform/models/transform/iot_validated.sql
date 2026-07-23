{{ config(materialized='table', schema='CLEAN') }}

SELECT 
    device_id,
    latitude,
    longitude,
    CAST(timestamp AS TIMESTAMP) AS event_timestamp,
    -- Severity tagging logic based on sensor data
    CASE 
        WHEN latitude IS NULL OR longitude IS NULL THEN 'INVALID'
        ELSE 'VALID'
    END AS validation_status,
    CURRENT_TIMESTAMP() as processed_at
FROM {{ source('HACKATHON_IOT', 'RAW_IOT_EVENTS') }}
WHERE device_id IS NOT NULL