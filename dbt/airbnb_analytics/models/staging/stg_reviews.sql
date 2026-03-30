{{ config(materialized='view', tags=['staging']) }}

SELECT
    listing_id, review_id, review_date,
    reviewer_id, reviewer_name,
    review_year, review_month, review_quarter,
    month_start AS review_month_start
FROM {{ source('silver', 'reviews') }}
WHERE review_date IS NOT NULL AND review_year >= 2015