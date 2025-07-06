-- Step 1: Create Database
CREATE OR REPLACE DATABASE ECOMMERCE_DATA;

-- Step 2: Create RAW Schema to store unstructured Kafka data
CREATE OR REPLACE SCHEMA ECOMMERCE_DATA.RAW;

-- Step 3: Create Table to hold raw JSON payloads from Kafka
CREATE OR REPLACE TABLE ECOMMERCE_DATA.RAW.KAFKA_EVENTS (
    RAW_DATA VARIANT
);

-- Step 4: Create TRANSFORMED Schema to store structured table
CREATE OR REPLACE SCHEMA ECOMMERCE_DATA.TRANSFORMED;

-- Step 5: Create Structured Table from Nested JSON
CREATE OR REPLACE TABLE ECOMMERCE_DATA.TRANSFORMED.EVENTS AS
SELECT
    RAW_DATA:event_id::STRING AS id,
    RAW_DATA:user.user_id::STRING AS user_id,
    RAW_DATA:user.location.country::STRING AS country,
    RAW_DATA:order.total_amount::FLOAT AS amount,
    RAW_DATA:event_timestamp::STRING AS timestamp
FROM ECOMMERCE_DATA.RAW.KAFKA_EVENTS;
