CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.dim_date (
    date_key INT PRIMARY KEY,               -- e.g. 20260902
    full_date DATE NOT NULL UNIQUE,         -- e.g. 2026-09-02
    day INT NOT NULL,
    day_of_week VARCHAR(10) NOT NULL,
    day_of_week_num INT NOT NULL,
    week INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(15) NOT NULL,
    quarter VARCHAR(2) NOT NULL,
    year INT NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_dim_date_full_date ON analytics.dim_date(full_date);
