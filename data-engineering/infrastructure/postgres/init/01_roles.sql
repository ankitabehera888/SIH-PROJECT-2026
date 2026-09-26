-- PostgreSQL Least-Privilege Role Provisioning Script
-- Run as superuser (postgres) during database initialization

-- 1. Create Application Role (Operational Transactions)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
        CREATE ROLE app_user WITH LOGIN PASSWORD 'app_secure_pass';
    END IF;
END
$$;

-- 2. Create ETL Pipeline Role (Staging & Analytics Pipeline)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'etl_user') THEN
        CREATE ROLE etl_user WITH LOGIN PASSWORD 'etl_secure_pass';
    END IF;
END
$$;

-- 3. Create Analytics Read-Only Role (Analytics APIs & Dashboards)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'analytics_user') THEN
        CREATE ROLE analytics_user WITH LOGIN PASSWORD 'analytics_secure_pass';
    END IF;
END
$$;

-- 4. Create Read-Only Audit Role
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'readonly_user') THEN
        CREATE ROLE readonly_user WITH LOGIN PASSWORD 'readonly_secure_pass';
    END IF;
END
$$;

-- Grant Schema Access
GRANT USAGE ON SCHEMA public TO app_user, etl_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;

GRANT USAGE, CREATE ON SCHEMA analytics TO etl_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA analytics TO etl_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA analytics TO etl_user;

GRANT USAGE ON SCHEMA analytics TO analytics_user, readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO analytics_user, readonly_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT SELECT ON TABLES TO analytics_user, readonly_user;
