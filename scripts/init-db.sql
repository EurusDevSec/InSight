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
    diabetes_type VARCHAR(20), -- 'TYPE1',' TYPE2'
    insulin_type VARCHAR(50), --'rapid', 'long-acting', 'mixed'
    insulin_ratio DECIMAL(5,2), -- Units per 10g Carb
    target_glucose_min INT DEFAULT 80,
    target_glucose_max INT DEFAULT 140,

    -- CGM Integration
    cgm_provider VARCHAR(50), --'freestyle_libre', 'dexcom', null
    cgm_access_token TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

