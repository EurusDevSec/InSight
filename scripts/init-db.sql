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

-- FOOD TABLE
CREATE TABLE foods(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name_vi VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),

    --Dinh duong (per 100g)
    car_per_100g DECIMAL(6,2) NOT NULL,
    protein_per_100g DECIMAL(6,2),
    fat_per_100g DECIMAL(6,2),
    fiber_per_100g DECIMAL(6,2),

    -- Glycemic Index

    gi_value INT, --0-100
    gi_category VARCHAR(10), --'low', 'medium', 'high'

    -- Phan loai
    category VARCHAR(50), --' rice', 'noodle', 'bread', 'drink', etc.
    is_liquid BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)

-- DENSITY FACTORS (Hệ số mật độ cho món nước)
-- =============================================
CREATE TABLE density_factors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    food_id UUID REFERENCES foods(id),

    variant VARCHAR(50), -- 'default', 'ít bánh', 'nhiều bánh'
    solid_ratio DECIMAL(4,2), -- 0.30 = 30% đặc, 70% nước
    density DECIMAL(4,2) DEFAULT 1.0, -- g/ml

    -- Cho calibrate quán quen
    restaurant_name VARCHAR(100),
    user_id UUID REFERENCES users(id),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- MEAL LOGS (Lịch sử ăn uống)
-- =============================================
CREATE TABLE meal_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),

    -- Thời gian
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    meal_type VARCHAR(20), -- 'breakfast', 'lunch', 'dinner', 'snack'

    -- Ảnh
    image_url TEXT,

    -- Kết quả
    total_volume_ml DECIMAL(8,2),
    total_weight_g DECIMAL(8,2),
    total_carbs_g DECIMAL(8,2),
    total_gl DECIMAL(8,2),

    -- AI Response
    insulin_suggestion DECIMAL(5,2),
    confidence_score DECIMAL(4,2),
    rag_response TEXT,

    -- Tracking
    is_panic_mode BOOLEAN DEFAULT FALSE,
    disclaimer_shown BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- MEAL ITEMS (Chi tiết từng món trong bữa)
-- =============================================
CREATE TABLE meal_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    meal_log_id UUID REFERENCES meal_logs(id),
    food_id UUID REFERENCES foods(id),

    -- Kết quả tính toán
    volume_ml DECIMAL(8,2),
    weight_g DECIMAL(8,2),
    carbs_g DECIMAL(8,2),

    -- Thông tin bổ sung từ form
    portion_size VARCHAR(20), -- 'full', 'half', 'quarter'
    sweetness_level VARCHAR(20), -- 'full', 'less', 'none'
    sauce_amount VARCHAR(20), -- 'none', 'little', 'normal', 'extra'

    confidence_score DECIMAL(4,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- GLUCOSE READINGS (Đọc đường huyết từ CGM)
-- =============================================
CREATE TABLE glucose_readings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),

    value_mgdl INT NOT NULL,
    measured_at TIMESTAMP NOT NULL,
    source VARCHAR(20), -- 'cgm', 'manual'

    -- Liên kết với bữa ăn (nếu có)
    meal_log_id UUID REFERENCES meal_logs(id),
    reading_type VARCHAR(20), -- 'before_meal', 'after_meal_1h', 'after_meal_2h'

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- FAVORITE RESTAURANTS (Quán quen)
-- =============================================
CREATE TABLE favorite_restaurants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),

    name VARCHAR(100) NOT NULL,
    address TEXT,

    -- Custom density factors sẽ lưu trong bảng density_factors
    -- với restaurant_name và user_id

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- INDEXES
-- =============================================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_foods_category ON foods(category);
CREATE INDEX idx_foods_name_vi ON foods(name_vi);
CREATE INDEX idx_meal_logs_user ON meal_logs(user_id, logged_at DESC);
CREATE INDEX idx_glucose_user ON glucose_readings(user_id, measured_at DESC);
CREATE INDEX idx_density_food ON density_factors(food_id);
CREATE INDEX idx_density_restaurant ON density_factors(restaurant_name, user_id);

-- =============================================
-- SEED DATA: Một số món ăn cơ bản
-- =============================================
INSERT INTO foods (name_vi, name_en, carb_per_100g, gi_value, gi_category, category, is_liquid) VALUES
-- Cơm, xôi
('Cơm trắng', 'White Rice', 28.0, 73, 'high', 'rice', FALSE),
('Xôi', 'Sticky Rice', 30.0, 87, 'high', 'rice', FALSE),
('Cơm chiên', 'Fried Rice', 25.0, 65, 'medium', 'rice', FALSE),

-- Phở, Bún
('Phở bò', 'Beef Pho', 12.0, 55, 'low', 'noodle', TRUE),
('Phở gà', 'Chicken Pho', 11.0, 55, 'low', 'noodle', TRUE),
('Bún bò Huế', 'Hue Beef Noodle', 13.0, 58, 'medium', 'noodle', TRUE),
('Bún chả', 'Grilled Pork Noodle', 15.0, 50, 'low', 'noodle', FALSE),

-- Bánh mì
('Bánh mì thịt', 'Vietnamese Sandwich', 35.0, 75, 'high', 'bread', FALSE),
('Bánh mì trứng', 'Egg Sandwich', 32.0, 70, 'high', 'bread', FALSE),

-- Đồ uống
('Trà sữa trân châu (M)', 'Bubble Tea (M)', 45.0, 65, 'medium', 'drink', TRUE),
('Trà sữa trân châu (L)', 'Bubble Tea (L)', 45.0, 65, 'medium', 'drink', TRUE),
('Cà phê sữa đá', 'Vietnamese Iced Coffee', 25.0, 60, 'medium', 'drink', TRUE),
('Nước ngọt (lon)', 'Soft Drink (can)', 11.0, 63, 'medium', 'drink', TRUE);

-- =============================================
-- SEED DATA: Density Factors mặc định
-- =============================================
INSERT INTO density_factors (food_id, variant, solid_ratio, density)
SELECT id, 'default', 0.30, 1.05 FROM foods WHERE name_vi = 'Phở bò'
UNION ALL
SELECT id, 'ít bánh', 0.20, 1.03 FROM foods WHERE name_vi = 'Phở bò'
UNION ALL
SELECT id, 'nhiều bánh', 0.45, 1.08 FROM foods WHERE name_vi = 'Phở bò'
UNION ALL
SELECT id, 'default', 0.35, 1.05 FROM foods WHERE name_vi = 'Bún bò Huế'
UNION ALL
SELECT id, 'default', 1.0, 1.05 FROM foods WHERE name_vi = 'Trà sữa trân châu (M)'
UNION ALL
SELECT id, 'default', 1.0, 1.05 FROM foods WHERE name_vi = 'Trà sữa trân châu (L)';

-- Done!
SELECT 'Database initialized successfully!' as status;