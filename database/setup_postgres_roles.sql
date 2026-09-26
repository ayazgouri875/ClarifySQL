-- ==============================================================================
-- QueryMind Security Setup: Read-Only Database User
-- This script creates the unprivileged user 'text2sql_readonly' restricted to SELECT
-- ==============================================================================

-- 1. Create readonly role/user with secure password (change in production)
DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = 'text2sql_readonly'
   ) THEN
      CREATE ROLE text2sql_readonly WITH LOGIN PASSWORD 'Readonly_SafePass2026!';
   END IF;
END
$do$;

-- 2. Revoke default public schema create permissions
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- 3. Grant schema usage and SELECT-only on all current tables
GRANT USAGE ON SCHEMA public TO text2sql_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO text2sql_readonly;

-- 4. Ensure future tables created also have SELECT only for this user
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO text2sql_readonly;

-- 5. Revoke hazardous function execution permissions if needed
REVOKE EXECUTE ON ALL FUNCTIONS IN SCHEMA public FROM text2sql_readonly;
