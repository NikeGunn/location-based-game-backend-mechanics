-- SQL script to set up the game database
-- Run this in pgAdmin Query Tool

-- Create the database (run this first)
CREATE DATABASE gamedb;

-- Connect to gamedb and run the following:
-- (In pgAdmin, right-click gamedb and select "Query Tool")

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create a dedicated user (optional)
-- CREATE USER gameuser WITH PASSWORD 'gamepass123';
-- GRANT ALL PRIVILEGES ON DATABASE gamedb TO gameuser;
