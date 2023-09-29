CREATE SCHEMA IF NOT EXISTS content;
CREATE SCHEMA IF NOT EXISTS auth;
ALTER ROLE app SET search_path TO content,auth,public;
