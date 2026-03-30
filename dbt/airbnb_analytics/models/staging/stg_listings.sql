
  
  
  create or replace view `workspace`.`gold`.`stg_listings`
  
  as (
    SELECT
    listing_id, name AS listing_name,
    host_id, host_name, host_type,
    neighbourhood_group, neighbourhood,
    latitude, longitude, room_type,
    price_usd, price_bracket,
    minimum_nights, number_of_reviews,
    last_review, reviews_per_month,
    calculated_host_listings_count AS host_listing_count,
    availability_365,
    CASE WHEN availability_365 >= 180 THEN true ELSE false END AS is_high_availability
FROM `workspace`.`airbnb_silver`.`listings`
WHERE price_usd IS NOT NULL AND price_usd > 0 AND price_usd < 10000
  )
