{{ config(materialized='table', tags=['mart','dashboard']) }}

SELECT
    neighbourhood AS neighbourhood_group,
    room_type,
    price_bracket,
    COUNT(*)                             AS total_listings,
    ROUND(AVG(price_usd), 2)             AS avg_price_usd,
    ROUND(MIN(price_usd), 2)             AS min_price_usd,
    ROUND(MAX(price_usd), 2)             AS max_price_usd,
    ROUND(AVG(number_of_reviews), 1)     AS avg_reviews,
    ROUND(AVG(availability_365), 0)      AS avg_availability_days,
    COUNT(DISTINCT host_id)              AS unique_hosts
FROM {{ ref('stg_listings') }}
WHERE neighbourhood IS NOT NULL
GROUP BY 1, 2, 3
ORDER BY neighbourhood, room_type