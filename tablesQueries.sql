CREATE TABLE Shipments (
    id INT PRIMARY KEY IDENTITY(1,1),
    shipment_date DATETIME,
    supplier_id INT,
    total_weight DECIMAL(10,2),
    refrigerated BIT,
    received BIT DEFAULT 0,
    received_date DATETIME,
    approved BIT DEFAULT 0
);


CREATE TABLE products (
    product_id varchar(10) PRIMARY KEY,
    name NVARCHAR(255)
);
CREATE TABLE suppliers (
    supplier_id varchar(10) PRIMARY KEY,
    supplier_name NVARCHAR(255)
);
CREATE TABLE Location (
    LocationID INTEGER PRIMARY KEY,
    LocationName VARCHAR(100),
    LocationAddress VARCHAR(200)
);
CREATE TABLE categories (
    category_id varchar(10) PRIMARY KEY,
    name NVARCHAR(255),
	supplier_id varchar(10),
	location_id int,
	

);
CREATE TABLE orders (
    order_id varchar(10) PRIMARY KEY,
    supplier_id varchar(10),
    order_date Date,
    expected_delivery Date,
    
);

CREATE TABLE orderLineItems (
    orderline_id varchar PRIMARY KEY,
    order_id varchar(10),
    product_id varchar(10),
    quantity int,
    unit_price DECIMAL(18, 2),
   
);

CREATE TABLE transactions (
    transaction_id varchar PRIMARY KEY,
    product_id varchar(10),
    quantity int,
    transaction_date DATE,
    
);

CREATE TABLE Shippers (
    shipper_id INT PRIMARY KEY,
    shipper_name VARCHAR(100) NOT NULL,
    contact_info VARCHAR(255),
    delivery_preferences VARCHAR(255)
);

CREATE TABLE users (
    user_id INT PRIMARY KEY IDENTITY(1,1),
    username NVARCHAR(255) NOT NULL,
    email NVARCHAR(255) UNIQUE NOT NULL,
    password NVARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);
CREATE TABLE cart (
    cart_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    product_id varchar(10) NOT NULL,
    quantity INT NOT NULL,
    timestamp DATETIME DEFAULT GETDATE(),
   
);




CREATE TABLE Inventory (
    InventoryID INTEGER PRIMARY KEY,
    product_id varchar(10),
    LocationID INTEGER,
    QuantityAvailable INTEGER,
    MinimumStockLevel INTEGER,
    MaximumStockLevel INTEGER,
    ReorderPoint INTEGER,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (LocationID) REFERENCES Warehouse(WarehouseID)
);



CREATE TABLE supplier_S2 (
    name NVARCHAR(255) PRIMARY KEY,
    contact_info NVARCHAR(255),
	category_id varchar(10),
	FOREIGN KEY (category_id) REFERENCES categories(category_id)
);
CREATE TABLE products_P02 (
    name VARCHAR(100) PRIMARY KEY,
    description VARCHAR(200),
    price DECIMAL(10, 2),
    quantity INTEGER,
    category_id VARCHAR(10),
    min_threshold INTEGER,
    cost_price DECIMAL(10, 2),
    packed_weight DECIMAL(10, 2),
    packed_height DECIMAL(10, 2),
    packed_width DECIMAL(10, 2),
    packed_depth DECIMAL(10, 2),
	
    refrigerated BIT,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
	
);
