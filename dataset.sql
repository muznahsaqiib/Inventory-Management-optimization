INSERT INTO Location (LocationID, LocationName, LocationAddress) VALUES
(1, 'Electronics Section', 'A1'),
(2, 'Toys Section', 'B2'),
(3, 'Automotive Parts Section', 'C3'),
(4, 'Books Section', 'D4'),
(5, 'Groceries Section', 'E5'),
(6, 'Office Supplies Section', 'F6');



-- Insert values into suppliers table
INSERT INTO suppliers (supplier_id, supplier_name) VALUES
('S001', 'ElectroMart'),
('S002', 'ToyTime'),
('S003', 'AutoZone'),
('S004', 'BookBarn'),
('S005', 'GroceryGalore'),
('S006', 'OfficeSuppliesCo');

-- Insert values into supplier_S2 table
INSERT INTO supplier_S2 (name, contact_info, category_id) VALUES
('ElectroMart', 'contact@electromart.com', 'C001'),
('ToyTime', 'contact@toytime.com', 'C002'),
('AutoZone', 'contact@autotech.com', 'C003'),
('BookBarn', 'contact@bookbarn.com', 'C004'),
('GroceryGalore', 'contact@grocerygalaxy.com', 'C005'),
('OfficeSuppliesCo', 'contact@officesuppliesco.com', 'C006');

INSERT INTO categories (category_id, name, supplier_id, location_id) VALUES 
('C001', 'Electronics', 'S001', 1),
('C002', 'Toys', 'S002', 2),
('C003', 'Automative Parts', 'S003', 3),
('C004', 'Books', 'S004', 4),
('C005', 'Groceries', 'S005', 5),
('C006', 'Office Supplies', 'S006', 6);

INSERT INTO Shippers (shipper_id, shipper_name, contact_info, delivery_preferences) 
VALUES 
    (1, 'Express Logistics', '123-456-7890', 'Fast delivery within 24 hours'),
    (2, 'Speedy Shipments', '555-555-5555', 'Guaranteed delivery within 48 hours'),
    (3, 'Reliable Couriers', '888-888-8888', 'Flexible delivery options, including same-day delivery'),
    (4, 'Swift Transport', '999-999-9999', 'Specializes in handling fragile items and sensitive shipments');
INSERT INTO Inventory(InventoryID, product_id, LocationID, QuantityAvailable, MinimumStockLevel, ReorderPoint) VALUES
(1, 'P001', 5, 500, 20, 10),   -- Organic Whole Milk in Groceries Section
(2, 'P002', 5, 500, 30, 15),   -- Whole Wheat Bread in Groceries Section
(3, 'P003', 5, 500, 40, 20),   -- Apples in Groceries Section
(4, 'P004', 4, 500, 5, 2),     -- To Kill a Mockingbird in Books Section
(5, 'P005', 4, 500, 5, 2),     -- Sapiens: A Brief History of Humankind in Books Section
(6, 'P006', 1, 500, 5, 2),     -- Star Wars Millennium Falcon in Electronics Section
(7, 'P007', 3, 500, 10, 5),    -- Michelin Pilot Sport in Automotive Parts Section
(8, 'P008', 3, 500, 15, 7),    -- Mobil 1 Synthetic in Automotive Parts Section
(9, 'P009', 6, 500, 50, 25),   -- Pilot G2 in Office Supplies Section
(10, 'P010', 1, 500, 3, 1),    -- iPhone in Electronics Section
(11, 'P011', 5, 500, 20, 10),  -- Almond Milk in Groceries Section
(12, 'P012', 5, 500, 20, 10),  -- Sourdough Bread in Groceries Section
(13, 'P013', 5, 500, 60, 30),  -- Bananas in Groceries Section
(14, 'P014', 4, 500, 5, 2),    -- Harry Potter and the Sorcerer Stone in Books Section
(15, 'P015', 4, 500, 5, 2),    -- Educated in Books Section
(16, 'P016', 2, 500, 5, 2),    -- Settlers of Catan in Toys Section
(17, 'P017', 3, 500, 10, 5),   -- Bridgestone Blizzak in Automotive Parts Section
(18, 'P018', 3, 500, 15, 7),   -- Castrol EDGE in Automotive Parts Section
(19, 'P019', 6, 500, 50, 25),  -- Sharpie in Office Supplies Section
(20, 'P020', 1, 500, 3, 1),    -- Samsung Galaxy in Electronics Section
(21, 'P021', 5, 500, 40, 20),  -- Spinach in Groceries Section
(22, 'P022', 4, 500, 5, 2),    -- To Kill a Mockingbird in Books Section
(23, 'P023', 4, 500, 5, 2),    -- Sapiens: A Brief History of Humankind in Books Section
(24, 'P024', 2, 500, 5, 2),    -- Ticket to Ride in Toys Section
(25, 'P025', 3, 500, 10, 5),   -- Brembo in Automotive Parts Section
(26, 'P026', 3, 500, 10, 5),   -- Wagner ThermoQuiet in Automotive Parts Section
(27, 'P027', 6, 500, 20, 10),  -- Moleskine in Office Supplies Section
(28, 'P028', 1, 500, 3, 1),    -- MacBook Pro in Electronics Section
(29, 'P029', 1, 500, 5, 2),    -- Sony Bravia in Electronics Section
(30, 'P030', 1, 500, 3, 1);    -- LG OLED in Electronics Section



INSERT INTO products (product_id, name) VALUES
('P001', 'Organic Whole Milk'),
('P002', 'Whole Wheat Bread'),
('P003', 'Apples'),
('P004', 'To Kill a Mockingbird'),
('P005', 'Sapiens: A Brief History of Humankind'),
('P006', 'Star Wars Millennium Falcon'),
('P007', 'Michelin Pilot Sport'),
('P008', 'Mobil 1 Synthetic'),
('P009', 'Pilot G2'),
('P010', 'iPhone'),
('P011', 'Almond Milk'),
('P012', 'Sourdough Bread'),
('P013', 'Bananas'),
('P014', 'Harry Potter and the Sorcerer Stone'),
('P015', 'Educated'),
('P016', 'Settlers of Catan'),
('P017', 'Bridgestone Blizzak'),
('P018', 'Castrol EDGE'),
('P019', 'Sharpie'),
('P020', 'Samsung Galaxy'),
('P021', 'Spinach'),
('P022', 'To Kill a Mockingbird'),
('P023', 'Sapiens: A Brief History of Humankind'),
('P024', 'Ticket to Ride'),
('P025', 'Brembo'),
('P026', 'Wagner ThermoQuiet'),
('P027', 'Moleskine'),
('P028', 'MacBook Pro'),
('P029', 'Sony Bravia'),
('P030', 'LG OLED');
INSERT INTO products_P02 (name, description, price, quantity, category_id, cost_price, packed_weight, packed_height, packed_width, packed_depth, refrigerated) VALUES
('Organic Whole Milk', 'Organic Whole Milk', 299, 500, 'C005', 2.50, 2.0, 10.0, 4.0, 6.0, 1),
('Whole Wheat Bread', 'Whole Wheat Bread', 349, 500, 'C005', 2.80, 2.0, 8.0, 4.0, 6.0, 0),
('Apples', 'Fresh Apples', 199, 500, 'C005', 1.50, 3.0, 6.0, 4.0, 6.0, 1),
('To Kill a Mockingbird', 'Fiction Book', 1299, 500, 'C004', 8.50, 1.0, 8.0, 5.0, 8.0, 0),
('Sapiens: A Brief History of Humankind', 'Non-fiction Book', 1599, 500, 'C004', 12.50, 2.0, 9.0, 6.0, 9.0, 0),
('Star Wars Millennium Falcon', 'LEGO Set', 5999, 500, 'C002', 45.00, 10.0, 15.0, 12.0, 15.0, 0),
('Michelin Pilot Sport', 'Car Tire', 19999, 500, 'C003', 150.00, 20.0, 20.0, 18.0, 20.0, 0),
('Mobil 1 Synthetic', 'Engine Oil', 49.99, 500, 'C003', 35.00, 5.0, 10.0, 5.0, 10.0, 0),
('Pilot G2', 'Gel Pen', 249, 500, 'C006', 1.80, 0.5, 6.0, 1.0, 5.0, 0),
('iPhone', 'Smartphone', 6999, 500, 'C001', 600.00, 0.5, 6.0, 3.0, 6.0, 0),
('Sourdough Bread', 'Sourdough Bread', 399, 500, 'C005', 3.20, 2.0, 8.0, 4.0, 6.0, 0),
('Bananas', 'Fresh Bananas', 79, 500, 'C005', 0.50, 2.0, 6.0, 3.0, 6.0, 0),
('Harry Potter and the Sorcerer''s Stone', 'Fiction Book', 1499, 500, 'C004', 10.00, 1.0, 8.0, 5.0, 8.0, 0),
('Educated', 'Non-fiction Book', 1899, 500, 'C004', 15.00, 2.0, 9.0, 6.0, 9.0, 0),
('Settlers of Catan', 'Board Game', 2999, 500, 'C002', 22.50, 5.0, 10.0, 8.0, 10.0, 0),
('Bridgestone Blizzak', 'Winter Tire', 14999, 500, 'C003', 120.00, 18.0, 18.0, 16.0, 18.0, 0),
('Castrol EDGE', 'Engine Oil', 3999, 500, 'C003', 30.00, 4.0, 8.0, 4.0, 8.0, 0),
('Sharpie', 'Permanent Marker', 199, 500, 'C006', 1.20, 0.3, 5.0, 0.8, 4.0, 0),
('Samsung Galaxy', 'Smartphone', 8999, 500, 'C001', 750.00, 0.6, 7.0, 3.5, 7.0, 0),
('Spinach', 'Fresh Spinach', 199, 500, 'C005', 1.50, 3.0, 6.0, 4.0, 6.0, 1),
('To Kill a Mockingbird', 'Fiction Book', 1299, 500, 'C004', 8.50, 1.0, 8.0, 5.0, 8.0, 0),
('Sapiens: A Brief History of Humankind', 'Non-fiction Book', 15.99, 40, 'C004', 12.50, 2.0, 9.0, 6.0, 9.0, 0),
('Ticket to Ride', 'Board Game', 2999, 500, 'C002', 20.00, 5.0, 12.0, 8.0, 12.0, 0),
('Brembo', 'Brake Pads', 9999, 500, 'C003', 75.00, 8.0, 8.0, 6.0, 8.0, 0),
('Wagner ThermoQuiet', 'Brake Pads', 7999, 500, 'C003', 60.00, 8.0, 8.0, 6.0, 8.0, 0),
('Moleskine', 'Notebook', 999, 500, 'C006', 7.50, 1.0, 9.0, 7.0, 9.0, 0),
('MacBook Pro', 'Laptop', 12999, 500, 'C001', 1100.00, 5.0, 12.0, 8.0, 12.0, 0),
('Sony Bravia', 'Television', 9999, 500, 'C001', 850.00, 20.0, 30.0, 15.0, 30.0, 0),
('Almond Milk', 'dairy product', 1299, 500, 'C005', 850, 1.0, 8.0, 5.0, 8.0, 1),
('LG OLED', 'Television', 14999, 500, 'C001', 1200.00, 25.0, 35.0, 20.0, 35.0, 0);
