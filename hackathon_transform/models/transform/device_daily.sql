{{
    config(
        materialized='incremental',
        unique_key=['device_id', 'event_date']
    )
}}

SELECT 
    device_id,
    CAST(EVENT_TIMESTAMP AS DATE) AS event_date,
    COUNT(*) AS total_events,
    AVG(latitude) AS avg_latitude,
    AVG(longitude) AS avg_longitude
FROM {{ ref('iot_validated') }}

{% if is_incremental() %}
  WHERE CAST(EVENT_TIMESTAMP AS DATE) > (SELECT MAX(event_date) FROM {{ this }})
{% endif %}

GROUP BY 1, 2