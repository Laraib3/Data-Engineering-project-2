CREATE SCHEMA IF NOT EXISTS ECOMMERCE_DATA.TRANSFORMED;

CREATE OR REPLACE TABLE ECOMMERCE_DATA.TRANSFORMED.EVENTS AS
SELECT
    raw_data:id::STRING AS id,
    raw_data:user_id::INT AS user_id,
    raw_data:country::STRING AS country,
    raw_data:amount::FLOAT AS amount,
    raw_data:timestamp::STRING AS timestamp
FROM ECOMMERCE_DATA.RAW.KAFKA_EVENTS;
