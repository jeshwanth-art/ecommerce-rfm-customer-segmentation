-- ============================================================
-- E-Commerce RFM Customer Segmentation
-- Week 1: Data Cleaning & Exploration Queries
-- Author: G. Jeshwanth
-- Dataset: UCI Online Retail II (1,067,371 rows)
-- ============================================================

-- STEP 1: Create database
CREATE DATABASE IF NOT EXISTS retail_rfm;
USE retail_rfm;

-- STEP 2: Create raw table
CREATE TABLE online_retail (
  Invoice      VARCHAR(20),
  StockCode    VARCHAR(20),
  Description  VARCHAR(255),
  Quantity     INT,
  InvoiceDate  DATETIME,
  Price        DECIMAL(10,2),
  CustomerID   VARCHAR(20),
  Country      VARCHAR(100)
);

-- STEP 3: Initial data exploration
-- Total row count
SELECT COUNT(*) AS total_rows FROM online_retail;

-- Date range
SELECT MIN(InvoiceDate) AS first_date,
       MAX(InvoiceDate) AS last_date
FROM online_retail;

-- Unique customers and countries
SELECT
  COUNT(DISTINCT CustomerID) AS unique_customers,
  COUNT(DISTINCT Country)    AS unique_countries
FROM online_retail;

-- Sample rows
SELECT * FROM online_retail LIMIT 10;

-- STEP 4: Data quality checks
-- Count nulls in key columns
SELECT
  SUM(CASE WHEN CustomerID  IS NULL THEN 1 ELSE 0 END) AS null_customers,
  SUM(CASE WHEN Description IS NULL THEN 1 ELSE 0 END) AS null_desc,
  SUM(CASE WHEN Price        IS NULL THEN 1 ELSE 0 END) AS null_price
FROM online_retail;

-- Cancelled orders (InvoiceNo starts with 'C')
SELECT COUNT(*) AS cancelled_orders
FROM online_retail
WHERE Invoice LIKE 'C%';

-- Negative or zero quantities
SELECT COUNT(*) AS bad_quantity
FROM online_retail
WHERE Quantity <= 0;

-- Zero or negative prices
SELECT COUNT(*) AS bad_price
FROM online_retail
WHERE Price <= 0;

-- Duplicate rows
SELECT Invoice, StockCode, CustomerID, COUNT(*) AS dupes
FROM online_retail
GROUP BY Invoice, StockCode, CustomerID
HAVING COUNT(*) > 1
LIMIT 10;

-- STEP 5: Create clean table (removes all bad data)
CREATE TABLE online_retail_clean AS
SELECT DISTINCT
  Invoice,
  StockCode,
  Description,
  Quantity,
  InvoiceDate,
  Price,
  `Customer ID` AS CustomerID,
  Country,
  (Quantity * Price) AS Revenue
FROM online_retail
WHERE
  `Customer ID`  IS NOT NULL
  AND Quantity   > 0
  AND Price      > 0
  AND Invoice    NOT LIKE 'C%';

-- Verify clean row count
SELECT COUNT(*) AS clean_rows FROM online_retail_clean;

-- STEP 6: Business insight queries

-- Total revenue
SELECT ROUND(SUM(Revenue), 2) AS total_revenue
FROM online_retail_clean;

-- Monthly revenue trend
SELECT
  DATE_FORMAT(InvoiceDate, '%Y-%m') AS month,
  ROUND(SUM(Revenue), 2)            AS monthly_revenue,
  COUNT(DISTINCT Invoice)           AS num_orders
FROM online_retail_clean
GROUP BY month
ORDER BY month;

-- Top 10 products by revenue
SELECT
  Description,
  ROUND(SUM(Revenue), 2) AS product_revenue,
  SUM(Quantity)           AS units_sold
FROM online_retail_clean
GROUP BY Description
ORDER BY product_revenue DESC
LIMIT 10;

-- Top 10 countries by revenue
SELECT
  Country,
  ROUND(SUM(Revenue), 2)       AS country_revenue,
  COUNT(DISTINCT CustomerID)   AS num_customers
FROM online_retail_clean
GROUP BY Country
ORDER BY country_revenue DESC
LIMIT 10;

-- Orders per customer (top spenders)
SELECT
  CustomerID,
  COUNT(DISTINCT Invoice) AS num_orders,
  ROUND(SUM(Revenue), 2)  AS total_spent
FROM online_retail_clean
GROUP BY CustomerID
ORDER BY total_spent DESC
LIMIT 10;
