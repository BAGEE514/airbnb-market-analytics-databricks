{{ config(materialized='table', tags=['mart','dashboard']) }}

WITH monthly AS (
    SELECT
        review_month_start,
        review_year,
        review_month,
        listing_id,
        COUNT(*) AS review_count
    FROM {{ ref('stg_reviews') }}
    GROUP BY 1, 2, 3, 4
)
SELECT
    m.review_month_start,
    m.review_year,
    m.review_month,
    l.neighbourhood_group,
    l.room_type,
    SUM(m.review_count)          AS total_reviews,
    COUNT(DISTINCT m.listing_id) AS active_listings,
    ROUND(AVG(l.price_usd), 2)   AS avg_price_usd
FROM monthly m
JOIN {{ ref('stg_listings') }} l ON m.listing_id = l.listing_id
WHERE m.review_year BETWEEN 2018 AND YEAR(CURRENT_DATE())
GROUP BY 1, 2, 3, 4, 5
ORDER BY review_month_start, neighbourhood_group
