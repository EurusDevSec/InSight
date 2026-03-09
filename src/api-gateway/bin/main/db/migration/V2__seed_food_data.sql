-- src/api-gateway/src/main/resources/db/migration/V2__seed_food_data.sql

-- 10 món Việt Nam phổ biến
INSERT INTO food (name_vi, name_en, carb_per_100g, gi_index, category) VALUES
('Cơm trắng',       'White rice',              28.0, 73, 'rice'),
('Phở bò',          'Beef pho',                15.0, 46, 'noodle_soup'),
('Bún bò Huế',      'Hue beef noodle',         18.0, 52, 'noodle_soup'),
('Bánh mì',         'Vietnamese sandwich',      49.0, 65, 'bread'),
('Cơm tấm',         'Broken rice plate',        28.0, 73, 'rice'),
('Bún thịt nướng',  'Grilled pork noodle',     20.0, 50, 'noodle'),
('Mì xào',          'Stir-fried noodle',        25.0, 55, 'noodle'),
('Cháo',            'Rice porridge',            12.0, 78, 'porridge'),
('Xôi',             'Sticky rice',              37.0, 87, 'rice'),
('Trà sữa',         'Milk tea (L, 100%)',       20.0, 55, 'beverage');

-- Density Factors cho món nước
INSERT INTO density_factor (food_id, variant, solid_ratio, density) VALUES
((SELECT id FROM food WHERE name_vi='Phở bò'),      'standard', 0.30, 1.02),
((SELECT id FROM food WHERE name_vi='Phở bò'),      'nhiều bánh', 0.45, 1.03),
((SELECT id FROM food WHERE name_vi='Bún bò Huế'),  'standard', 0.35, 1.03),
((SELECT id FROM food WHERE name_vi='Cháo'),         'standard', 0.20, 1.01),
((SELECT id FROM food WHERE name_vi='Cháo'),         'đặc',      0.35, 1.02);