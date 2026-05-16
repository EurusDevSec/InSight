-- src/api-gateway/src/main/resources/db/migration/V1__create_tables.sql

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    medication JSONB DEFAULT '[]',
    insulin_settings JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Food Database
CREATE TABLE food (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_vi VARCHAR(255) NOT NULL,
    name_en VARCHAR(255),
    carb_per_100g FLOAT NOT NULL,
    gi_index FLOAT NOT NULL,
    category VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Density Factors (cho món nước: Phở, Bún, Cháo...)
CREATE TABLE density_factor (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    food_id UUID REFERENCES food(id) ON DELETE CASCADE,
    variant VARCHAR(100) DEFAULT 'standard',
    solid_ratio FLOAT NOT NULL,  -- Tỷ lệ phần đặc (0.0 - 1.0)
    density FLOAT NOT NULL,      -- g/ml
    created_at TIMESTAMP DEFAULT NOW()
);

-- Meal Logs
CREATE TABLE meal_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    logged_at TIMESTAMP DEFAULT NOW(),
    total_carbs FLOAT,
    total_gl FLOAT,
    insulin_suggestion TEXT,
    disclaimer_shown BOOLEAN DEFAULT TRUE,
    image_url TEXT,
    confidence_score FLOAT
);

-- Meal Items (từng món trong bữa)
CREATE TABLE meal_item (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meal_log_id UUID REFERENCES meal_log(id) ON DELETE CASCADE,
    food_id UUID REFERENCES food(id),
    volume_ml FLOAT,
    weight_g FLOAT,
    carbs_g FLOAT,
    confidence_score FLOAT
);

-- Glucose Readings
CREATE TABLE glucose_reading (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    value_mgdl FLOAT NOT NULL,
    measured_at TIMESTAMP DEFAULT NOW(),
    source VARCHAR(50) DEFAULT 'manual'  -- 'manual', 'cgm_freestyle', 'cgm_dexcom'
);

-- Favorite Restaurants (Quán quen)
CREATE TABLE favorite_restaurant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    custom_density_factors JSONB DEFAULT '{}'
);

-- Indexes
CREATE INDEX idx_meal_log_user ON meal_log(user_id);
CREATE INDEX idx_meal_item_log ON meal_item(meal_log_id);
CREATE INDEX idx_glucose_user ON glucose_reading(user_id);
CREATE INDEX idx_food_category ON food(category);