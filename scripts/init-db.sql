-- Insigh Database Schema
-- version: 1.0.0


-- Enable UUID extension

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- USERS TABLE

CREATE TABLE user(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,


    -- Thong tin y te
    diabetes_type

)