-- ============================================================
-- Customer Churn Analysis & Prediction - MySQL Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS churn_analytics;
USE churn_analytics;

CREATE TABLE IF NOT EXISTS customers (
    CustomerID          VARCHAR(20) PRIMARY KEY,
    Gender              VARCHAR(10),
    SeniorCitizen       INT,
    Partner             VARCHAR(5),
    Dependents          VARCHAR(5),
    Tenure              INT,
    PhoneService        VARCHAR(5),
    MultipleLines       VARCHAR(20),
    InternetService     VARCHAR(20),
    OnlineSecurity      VARCHAR(25),
    OnlineBackup        VARCHAR(25),
    DeviceProtection    VARCHAR(25),
    TechSupport         VARCHAR(25),
    StreamingTV         VARCHAR(25),
    StreamingMovies     VARCHAR(25),
    Contract            VARCHAR(20),
    PaperlessBilling    VARCHAR(5),
    PaymentMethod       VARCHAR(40),
    MonthlyCharges      DECIMAL(10,2),
    TotalCharges        DECIMAL(12,2),
    Churn               VARCHAR(5)
);

-- Import: data/customer_churn.csv → customers table
