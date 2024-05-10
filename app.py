
from datetime import datetime, timedelta
import datetime
import decimal
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import pyodbc


app = Flask(__name__)
app.secret_key = '1502'

def connect_to_database():
    try:
        conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-U9MLR5I\MSSQLSERVER06;'
                      'Database=Warehouse;'
                      'Trusted_Connection=yes;')
        print("Connection successful!")
        return conn
    except Exception as e:
        print("Error connecting to SQL Server:", e)
        return None
    
                                                        #MAIN MENU
                                                                                                                                                                                                                                                                     
@app.route('/')
def homepage():
    return render_template('homepage.html')
@app.route('/main_menu')
def main_menu():
    return render_template('main_menu.html')
@app.route('/Aboutus')
def about_us():
    return render_template('Aboutus.html')


                                                #receive new productss.
@app.route('/receive_shipment', methods=['GET', 'POST'])
def receive_shipment():
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        if request.method == 'POST':
            try:
                shipment_date = request.form['shipment_date']
                supplier_id = request.form['supplier_id']
                category_id = request.form['category_id']
                total_weight = request.form['total_weight']
                refrigerated = request.form.get('refrigerated', False)
                
                product_name = request.form['product_name']
                product_quantity = request.form['product_quantity']
                price_per_qty = request.form['price_per_qty']  
                
                # Retrieve the last inserted product_id and increment it
                cursor.execute("SELECT MAX(product_id) FROM products")
                last_product_id = cursor.fetchone()[0]
                if last_product_id is None:
                    next_product_id = 'P001'
                else:
                    # Split the product_id string and extract the numeric part
                    prefix, numeric_part = last_product_id.split('P')
                    numeric_part = int(numeric_part)
                    # Increment the numeric part
                    numeric_part += 1
                    # Format it back to the original format
                    next_product_id = 'P{:03d}'.format(numeric_part)

                cursor.execute("INSERT INTO Shipments (shipment_date, supplier_id, category_id, total_weight, refrigerated,received,received_date,approved,product_id,product_name,quantity, price_per_qty) VALUES (?, ?, ?, ?, ?,1,?,0,?,?,?,?)",
                               (shipment_date, supplier_id, category_id, total_weight, refrigerated,shipment_date,next_product_id,product_name,product_quantity, price_per_qty))
                
                conn.commit()
                
                session['message'] = 'Shipment details added. Awaiting admin approval.'
                conn.close()
                return redirect(url_for('main_menu'))
            except Exception as e:
                session['message'] = 'Error: {}'.format(e)
                conn.close()
                return redirect(url_for('receive_shipment'))

        cursor.execute("SELECT supplier_id, supplier_name FROM Suppliers")
        suppliers = cursor.fetchall()

        cursor.execute("SELECT category_id, name FROM Categories")
        categories = cursor.fetchall()
        
        return render_template('receive_shipment.html', suppliers=suppliers, categories=categories)

    return "Error: Unable to connect to the database"

    

                                        #REVIEW NEW SHIPMENT

@app.route('/received_shipments', methods=['GET'])
def received_shipments():
    try:
        print("Entered received_shipments route") 
        conn = connect_to_database()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Shipments WHERE received = 'true'") 
        shipments_data = cursor.fetchall()

        conn.close()

        shipments = []
        for shipment in shipments_data:

            received = shipment[5] == 'true' 
            shipment[5] = received
            shipments.append(shipment)
            print("successfull")
        return render_template('received_shipments.html', shipments=shipments)
    except Exception as e:
        return f"An error occurred: {e}"

                                                #APPROVE SHIPMENT
@app.route('/approve_shipment', methods=['GET', 'POST'])
def approve_shipment():
    if request.method == 'POST':
        try:
            id = request.form.get('id')
            cost_price = (request.form.get('cost_price'))
            location_name = request.form.get('location_name')
            location_address = request.form.get('location_address')
            description = request.form.get('description')

            conn = connect_to_database()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT * FROM Shipments WHERE id = ?", (id,))
                    shipment = cursor.fetchone()
                    if shipment:
                        product_name = shipment[9]
                        price_per_qty =(shipment[11])
                        packed_weight=shipment[3]
                        refrigerated = 1 if shipment[4] else 0
                        quantity =(shipment[11]) 
                        price = quantity * price_per_qty
                        category_id = shipment[10]
                        product_id=shipment[8]
                        print("Debug: Before products_P02 INSERT")
                        cursor.execute("""
                            INSERT INTO products (
                               product_id, name
                            ) VALUES (?, ?)
                        """, (
                           product_id, product_name
                        ))
                        cursor.execute("""
                            INSERT INTO products_P02 (
                                name, description, price, quantity, category_id, cost_price, refrigerated, packed_weight
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            product_name, description, price, quantity, category_id, cost_price, refrigerated, packed_weight
                        ))
                        conn.commit()
                        print("Debug: After products_P02 INSERT")
                        
                        cursor.execute("SELECT MAX(LocationID) FROM Location")
                        last_location_id = cursor.fetchone()[0]  
                        new_location_id = last_location_id + 1 if last_location_id is not None else 1  
                        print("Debug: Before Location INSERT")
                        cursor.execute("INSERT INTO Location (LocationID, LocationName, LocationAddress) VALUES (?, ?, ?)", (new_location_id, location_name, location_address))
                        conn.commit()
                        print("Debug: After Location INSERT")

                        cursor.execute("SELECT MAX(InventoryID) FROM Inventory")
                        last_inventory_id = cursor.fetchone()[0] 
                        new_inventory_id = last_inventory_id + 1 if last_inventory_id is not None else 1  # Increment the last ID or start from 1 if table is empty
                        print("Debug: Before Inventory INSERT")
                        cursor.execute("""
                            INSERT INTO Inventory (
                                InventoryID, product_id, LocationID, QuantityAvailable, MinimumStockLevel, ReorderPoint
                            ) VALUES (?, ?,?, ?, ?, ?)
                        """, (
                            new_inventory_id ,product_id, new_location_id, quantity, 0, 0
                        ))
                        conn.commit()
                        print("Debug: After Inventory INSERT")
                        cursor = conn.cursor()

                        cursor.execute("UPDATE shipments SET approved = 1")

                        conn.commit()
                    else:
                        print('Shipment with ID {} not found'.format(id))
                        return redirect(url_for('received_shipments'))
                except Exception as e:
                    print('Error: {}'.format(e))
                    return redirect(url_for('received_shipments'))
                finally:
                    conn.close()
            else:
                print('Error connecting to the database.')
                return redirect(url_for('received_shipments'))

        except Exception as e:
            print('Error: {}'.format(e))
            return redirect(url_for('received_shipments'))

    elif request.method == 'GET':
        id = request.args.get('id')
        return render_template('approve_shipment.html', id=id)

    return "Successfully added the product"
                                         #view products

def get_products():
    conn = connect_to_database()
    products = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.product_id, p.name, pp.description, pp.quantity, l.LocationAddress
            FROM products p 
            INNER JOIN products_P02 pp ON p.name = pp.name
            INNER JOIN categories c ON pp.category_id = c.category_id
            INNER JOIN Location l ON c.location_id = l.LocationID
        """)
        products = cursor.fetchall()
        conn.close()
    return products

                                            #add products

def add_product_to_inventory(product_id, quantity):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        try:
           
            query = """
                SELECT 
                    p.product_id, 
                    p.name,
                    i.QuantityAvailable, 
                    i.MaximumStockLevel, 
                    l.LocationAddress 
                FROM 
                    products AS p 
                INNER JOIN 
                    products_P02 AS pp ON p.name = pp.name 
                INNER JOIN 
                    Inventory AS i ON p.product_id = i.product_id 
                INNER JOIN 
                    categories AS c ON pp.category_id = c.category_id 
                INNER JOIN 
                    Location AS l ON c.location_id = l.LocationID 
                WHERE 
                    p.product_id = ?
            """
            print("Executing query:", query) 
            cursor.execute(query, (product_id,))
            product_info = cursor.fetchone()
            if product_info:
                product_id, product_name, current_quantity, max_stock_level, shelf_location = product_info
                new_quantity = current_quantity + int(quantity)
                if new_quantity > max_stock_level:
                    session['message'] = f"No space left on the shelf {shelf_location} for {product_name}."
                else:
                    
                    update_query_1 = """
                        UPDATE 
                            products_P02 
                        SET 
                            quantity = quantity + ? 
                        FROM 
                            products_P02 AS pp 
                        INNER JOIN 
                            products AS p ON pp.name = p.name 
                        WHERE 
                            p.product_id = ?
                    """
                    print("Executing query:", update_query_1) 
                    cursor.execute(update_query_1, (quantity, product_id))
                    
                    update_query_2 = """
                        UPDATE 
                            Inventory 
                        SET 
                            QuantityAvailable = QuantityAvailable + ? 
                        WHERE 
                            product_id = ?
                    """
                    print("Executing query:", update_query_2) 
                    cursor.execute(update_query_2, (quantity, product_id))
                    conn.commit()
                    session['message'] = 'Quantity added successfully.'
            else:
                session['message'] = 'Product not found.'
        except Exception as e:
            session['message'] = 'Error: {}'.format(e)
            print("Error executing query:", e)
            conn.rollback()
        finally:
            conn.close()


                                        # Function to delete a product from the database

def delete_product_from_inventory(product_id):
    conn = connect_to_database()
    if conn:
        cursor = conn.cursor()
        try:
           
            cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
            
          
            cursor.execute("""
                DELETE p2 FROM products_P02 p2
                INNER JOIN products p ON p2.name = p.name
                WHERE p.product_id = ?
            """, (product_id,))

            cursor.execute("DELETE FROM Inventory WHERE product_id = ?", (product_id,))
            
            conn.commit()
            session['message'] = 'Product deleted successfully.'
        except Exception as e:
            session['message'] = 'Error: {}'.format(e)
        finally:
            conn.close()


                                            # Function to display all products and handle add/delete actions

@app.route('/manage_inventory', methods=['GET', 'POST'])
def manage_inventory():
    products = get_products()

    if request.method == 'POST':
        if 'add' in request.form:
            product_id = request.form['product_id']
            return redirect(url_for('add_product', product_id=product_id))
        elif 'delete' in request.form:
            product_id = request.form['product_id']
            delete_product_from_inventory(product_id)
            return redirect(url_for('manage_inventory'))

    return render_template('manage_inventory.html', products=products)


# Function to add a product
@app.route('/add_product/<product_id>', methods=['GET', 'POST'])
def add_product(product_id):
    if request.method == 'POST':
        quantity = request.form['quantity']
        add_product_to_inventory(product_id, quantity)
        return redirect(url_for('manage_inventory'))
    
    return render_template('add_product.html', product_id=product_id)


                                              #search products by product_ID

@app.route('/search_product_by_id', methods=['GET', 'POST'])
def search_product_by_id():
    if request.method == 'POST':
        product_id = request.form['product_id']
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.product_id, p.name, pp.description, pp.price, pp.quantity, pp.category_id, pp.cost_price, i.LocationID, l.LocationName, l.LocationAddress
                FROM products p
                JOIN products_P02 pp ON p.name = pp.name
                JOIN Inventory i ON p.product_id = i.product_id
                JOIN Location l ON i.LocationID = l.LocationID
                WHERE p.product_id = ?
            """, (product_id,))
            rows = cursor.fetchall()
            if not rows:
                return render_template('error.html', error='Product does not exist in the table. Please provide a valid product ID for searching.')
            products = []
            for row in rows:
                product = {
                    'product_id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'price': row[3],
                    'quantity': row[4],
                    'category_id': row[5],
                    'cost_price': row[6],
                    'location_id': row[7],
                    'location_name': row[8],
                    'location_address': row[9]
                }
                products.append(product)
            conn.close()
            return render_template('product_search_results.html', products=products)
        except Exception as e:
            return render_template('error.html', error=f'Error searching products by ID: {e}')
    return render_template('search_product_by_id.html')

                                             #ADD SUPPLIER
def generate_new_id(max_id, prefix):
    # Function to generate a new ID by incrementing the maximum ID
    if max_id:
        new_id = int(max_id[1:]) + 1
    else:
        new_id = 1
    return prefix + str(new_id).zfill(3)

def allocate_inventory_location():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        
        # Check the current number of allocated locations
        cursor.execute("SELECT COUNT(*) FROM Location")
        current_locations = cursor.fetchone()[0]

        if current_locations >= 10:
            # If the maximum limit of locations is reached, return an error message
            return {'error': 'No more locations available in the inventory.'}
        
        # Get the next available location ID
        cursor.execute("SELECT MAX(LocationID) FROM Location")
        max_location_id = cursor.fetchone()[0]
        if max_location_id:
            next_location_id = max_location_id + 1
        else:
            next_location_id = 1

        # Insert the new location into the database
        cursor.execute("INSERT INTO Location (LocationID) VALUES (?)",
                       (next_location_id,))
        conn.commit()

        return next_location_id
    except Exception as e:
        return {'error': f'Error allocating inventory location: {e}'}
    finally:
        conn.close()

@app.route('/add_supplier', methods=['GET', 'POST'])
def add_supplier():
    if request.method == 'POST':
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            name = request.form['name']
            contact_info = request.form['contact_info']
            category_name = request.form['category_name']
            location_name = request.form['location_name']
            location_address = request.form['location_address']
            
            # Get the maximum supplier ID and increment it to generate a new ID
            cursor.execute("SELECT MAX(supplier_id) FROM suppliers")
            max_supplier_id = cursor.fetchone()[0]
            new_supplier_id = generate_new_id(max_supplier_id, 'S')

            # Insert the new supplier into the suppliers table
            cursor.execute("INSERT INTO suppliers (supplier_id, supplier_name) VALUES (?, ?)",
                           (new_supplier_id, name))
            conn.commit()
            
            # Get the maximum category ID and increment it to generate a new ID
            cursor.execute("SELECT MAX(category_id) FROM categories")
            max_category_id = cursor.fetchone()[0]
            new_category_id = generate_new_id(max_category_id, 'C')

            # Get the next available location ID
            new_location_id = allocate_inventory_location()

            # Insert the new location name and address into the Location table
            cursor.execute("UPDATE Location SET LocationName = ?, LocationAddress = ? WHERE LocationID = ?",
                           (location_name, location_address, new_location_id))
            conn.commit()

            # Insert the new category into the categories table
            cursor.execute("INSERT INTO categories (category_id, name, supplier_id, location_id) VALUES (?, ?, ?, ?)",
                           (new_category_id, category_name, new_supplier_id, new_location_id))
            conn.commit()

            # Insert the new supplier information into the supplier_S2 table
            cursor.execute("INSERT INTO supplier_S2 (name, contact_info, category_id) VALUES (?, ?, ?)",
                           (name, contact_info, new_category_id))
            conn.commit()

            return jsonify({'message': 'Supplier and category added successfully', 'new_supplier_id': new_supplier_id, 'new_category_id': new_category_id})
        except Exception as e:
            return jsonify({'error': f'Error adding supplier: {e}'})
        finally:
            conn.close()
    return render_template('add_supplier.html')






                                                        #DELETE SUPPLIER

@app.route('/delete_supplier', methods=['GET','POST'])
def delete_supplier():
    if request.method == 'POST':
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            supplier_id = request.form['supplier_id']
            cursor.execute("SELECT COUNT(*) FROM suppliers WHERE supplier_id = ?", (supplier_id,))
            supplier_exists = cursor.fetchone()[0]
            if supplier_exists == 0:
                return render_template('error.html', error='Supplier with this ID does not exist in the records.')
            cursor.execute("SELECT supplier_name FROM suppliers WHERE supplier_id = ?", (supplier_id,))
            supplier_name = cursor.fetchone()[0]
            cursor.execute("SELECT category_id FROM supplier_S2 WHERE name = ?", (supplier_name,))
            category_id = cursor.fetchone()[0]
            cursor.execute("SELECT location_id FROM categories WHERE category_id = ?", (category_id,))
            location_id = cursor.fetchone()[0]

            cursor.execute("DELETE FROM suppliers WHERE supplier_id = ?", (supplier_id,))
            cursor.execute("DELETE FROM supplier_S2 WHERE name = ?", (supplier_name,))
            cursor.execute("DELETE FROM categories WHERE category_id = ?", (category_id,))
            cursor.execute("DELETE FROM Location WHERE LocationID = ?", (location_id,))
            
            conn.commit()
            conn.close()
            return render_template('delete_supplier.html', message='Supplier, category, associated records, and location deleted successfully')
        except Exception as e:
            return render_template('error.html', error=f'Error deleting supplier, category, associated records, and location: {e}')
    return render_template('delete_supplier.html')


                                                #SEARCH SUPPLIER
@app.route('/search_suppliers', methods=['GET', 'POST'])
def search_suppliers():
    if request.method == 'POST':
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            supplier_id = request.form['supplier_id']
            cursor.execute("SELECT * FROM suppliers WHERE supplier_id = ?", (supplier_id,))
            supplier = cursor.fetchone()
            if supplier:
                cursor.execute("SELECT * FROM supplier_S2 WHERE name = ?", (supplier[1],))
                supplier_details = cursor.fetchone()
                if supplier_details:
                    supplier_data = {
                        'supplier_id': supplier[0],
                        'supplier_name': supplier[1],
                        'contact_info': supplier_details[1],
                        'category_id': supplier_details[2]
                    }
                    return render_template('supplier_details.html', supplier=supplier_data)
                else:
                    return render_template('error.html', error='Supplier details not found in supplier_S2 table')
            else:
                return render_template('error.html', error='Supplier does not exist')
        except Exception as e:
            return render_template('error.html', error=f'Error searching supplier: {e}')
        finally:
            conn.close()
    return render_template('search_suppliers.html')


                                                    #UPDATE SUPPLIER

@app.route('/update_supplier', methods=['GET', 'POST'])
def update_supplier():
    if request.method == 'POST':
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            supplier_id = request.form['supplier_id']
            name = request.form['name']
            contact_info = request.form['contact_info']
            category_name = request.form['category_name']
            cursor.execute("SELECT COUNT(*) FROM suppliers WHERE supplier_id = ?", (supplier_id,))
            supplier_exists = cursor.fetchone()[0]
            if supplier_exists == 0:
                return render_template('error.html', error='Supplier does not exist in the table. Please provide a valid supplier ID for updating.')
            cursor.execute("UPDATE suppliers SET supplier_name = ? WHERE supplier_id = ?", (name, supplier_id))
            cursor.execute("UPDATE supplier_S2 SET contact_info = ? WHERE name = ?", (contact_info, name))
            cursor.execute("UPDATE categories SET name = ? WHERE supplier_id = ?", (category_name, supplier_id))
            conn.commit()
            return jsonify({'message': 'Supplier updated successfully'})
        except Exception as e:
            return jsonify({'error': f'Error updating supplier: {e}'})
        finally:
            conn.close()
    return render_template('update_supplier.html')


                                        #ALL SUPPLIERS

@app.route('/view_all_suppliers')
def view_all_suppliers():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT s.supplier_id, s.supplier_name, s2.contact_info, s2.category_id FROM suppliers s LEFT JOIN supplier_S2 s2 ON s.supplier_name = s2.name")
        suppliers = cursor.fetchall()
        conn.close()
        return render_template('view_all_suppliers.html', suppliers=suppliers)
    except Exception as e:
        return f'Error retrieving all suppliers: {e}'
                                                    #all categories
@app.route('/view_all_categories')
def view_all_categories():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT c.category_id, c.name, l.LocationName,l.LocationAddress FROM categories c LEFT JOIN Location l ON c.location_id = l.LocationID")
        categories = cursor.fetchall()
        conn.close()
        return render_template('view_all_categories.html', categories=categories)
    except Exception as e:
        return f'Error retrieving all categories: {e}'
    


                                            #SHIPPERS
                                            #ADD SHIPPER

@app.route('/add_shipper', methods=['GET', 'POST'])
def add_shipper():
    if request.method == 'POST':
        try:
            shipper_name = request.form['shipper_name']
            contact_info = request.form['contact_info']
            delivery_preferences = request.form['delivery_preferences']
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(shipper_id) FROM Shippers")
            max_shipper_id = cursor.fetchone()[0]
            next_shipper_id = max_shipper_id + 1 if max_shipper_id else 1
            cursor.execute("INSERT INTO Shippers (shipper_id, shipper_name, contact_info, delivery_preferences) VALUES (?, ?, ?, ?)",
                           (next_shipper_id, shipper_name, contact_info, delivery_preferences))
            conn.commit()
            return render_template('add_shipper.html', success=True, message="Shipper added successfully")
        except Exception as e:
            return render_template('error.html', error=f'Error adding shipper: {str(e)}')
        finally:
            if conn:
                conn.close()
    else:
        return render_template('add_shipper.html')
    
                                            #DELETE SHIPPER

@app.route('/delete_shipper', methods=['GET', 'POST'])
def delete_shipper():
    if request.method == 'POST':
        try:
            shipper_id = request.form['shipper_id']
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Shippers WHERE shipper_id = ?", (shipper_id,))
            shipper_exists = cursor.fetchone()[0]
            if shipper_exists == 0:
                return jsonify({'success': False, 'error': 'Shipper does not exist.'})
            cursor.execute("DELETE FROM Shippers WHERE shipper_id = ?", (shipper_id,))
            conn.commit()
            return jsonify({'success': True, 'message': 'Shipper deleted successfully'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
        finally:
            if conn:
                conn.close()
    else:
        return render_template('delete_shipper.html')
    
                                            #UPDATE SHIPPER

@app.route('/update_shipper', methods=['GET', 'POST'])
def update_shipper():
    if request.method == 'POST':
        try:
            shipper_id = request.form['shipper_id']
            shipper_name = request.form['shipper_name']
            contact_info = request.form['contact_info']
            delivery_preferences = request.form['delivery_preferences']
            
            conn = connect_to_database()
            cursor = conn.cursor()
            
            # Check if the shipper exists
            cursor.execute("SELECT COUNT(*) FROM Shippers WHERE shipper_id = ?", (shipper_id,))
            shipper_exists = cursor.fetchone()[0]
            if shipper_exists == 0:
                return jsonify({'success': False, 'error': 'Shipper does not exist.'})
            
            # Update shipper details
            cursor.execute("UPDATE Shippers SET shipper_name=?, contact_info=?, delivery_preferences=? WHERE shipper_id=?",
                           (shipper_name, contact_info, delivery_preferences, shipper_id))
            conn.commit()
            
            return jsonify({'success': True, 'message': 'Shipper updated successfully'})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
        finally:
            if conn:
                conn.close()
    else:
        return render_template('update_shipper.html')
    
                                    #SEARCH SHIPPER

@app.route('/search_shipper', methods=['GET', 'POST'])
def search_shipper():
    if request.method == 'POST':
        try:
            shipper_name = request.form['shipper_name']
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Shippers WHERE shipper_name LIKE ?", ('%' + shipper_name + '%',))
            shippers = cursor.fetchall()
            return render_template('search_results.html', shippers=shippers)
        except Exception as e:
            return render_template('error.html', error=f'Error searching shipper: {str(e)}')
        finally:
            if conn:
                conn.close()
    else:
        return render_template('search_shipper.html')


                                        #VIEW ALL SHIPPERS
                                     
@app.route('/view_all_shippers')
def view_all_shippers():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Shippers")
        shippers = cursor.fetchall()
        return render_template('view_all_shippers.html', shippers=shippers)
    except Exception as e:
        return render_template('error.html', error=f'Error fetching shippers: {str(e)}')
    finally:
        if conn:
            conn.close()

            
                                                #SET MIN THRESHOLD FOR ALL PRODUCTS

@app.route('/set_min_threshold', methods=['GET', 'POST'])
def set_min_threshold():
    if request.method == 'POST':
        try:
            threshold = int(request.form['threshold'])
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("UPDATE Inventory SET MinimumStockLevel = ?", (threshold,))
            conn.commit()
            conn.close()
            return redirect(url_for('monitor_stock_levels', threshold=threshold))
        except Exception as e:
            return f'Error setting minimum threshold: {e}'
    return render_template('set_min_threshold.html')

                                                    #SET MAX THRESHOLD 

@app.route('/set_max_threshold', methods=['GET', 'POST'])
def set_max_threshold():
    if request.method == 'POST':
        try:
            threshold = int(request.form['threshold'])
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("UPDATE Inventory SET MaximumStockLevel = ?", (threshold,))
            conn.commit()
            conn.close()
            return redirect(url_for('monitor_max_stock_levels', threshold=threshold))
        except Exception as e:
            return f'Error setting maximum threshold: {e}'
    return render_template('set_max_threshold.html')

 

                                        #MONITOR STOCK LEVELS
@app.route('/monitor_stock_levels')
def monitor_stock_levels():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Inventory.product_id, products.name, Inventory.QuantityAvailable
            FROM Inventory
            INNER JOIN products ON Inventory.product_id = products.product_id
            WHERE Inventory.QuantityAvailable < Inventory.MinimumStockLevel
        """)
        low_stock_products = cursor.fetchall()
        print(low_stock_products)
        conn.close()
        return render_template('monitor_stock_levels.html', low_stock_products=low_stock_products)

    except Exception as e:
        return f'Error retrieving stock levels: {e}'


                                        #MONITOR max STOCK LEVELS
@app.route('/monitor_max_stock_levels')
def monitor_max_stock_levels():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT product_id, QuantityAvailable,MaximumStockLevel
            FROM Inventory
        """)
        max_stock_products = cursor.fetchall()
        print(max_stock_products)
        conn.close()
        return render_template('monitor_max_stock_levels.html', max_stock_products=max_stock_products)

    except Exception as e:
        return f'Error retrieving stock levels: {e}'


                                    
                                            #GENERATE INVENTORY REPORT FOR ADMIN

@app.route('/generate_inventory_report')
def generate_inventory_report():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        
        # Total Orders Placed
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders_placed = cursor.fetchone()[0]
        
        # Orders Delivered
        cursor.execute("SELECT COUNT(*) FROM orders WHERE approved = 'deliver' ")
        orders_delivered = cursor.fetchone()[0]
        
        # Orders Pending
        cursor.execute("SELECT COUNT(*) FROM orders WHERE approved = 'pending' ")
        orders_pending = cursor.fetchone()[0]
        
        # Amount of Transactions
        cursor.execute("SELECT SUM(total_amount) FROM Transactions")
        total_transactions_amount = cursor.fetchone()[0]
        
        # Total Stock Available
        cursor.execute("SELECT SUM(QuantityAvailable) FROM Inventory")
        total_stock_available = cursor.fetchone()[0]
        
        # Low Stock
        cursor.execute("SELECT COUNT(*) FROM Inventory WHERE QuantityAvailable < MinimumStockLevel")
        low_stock_count = cursor.fetchone()[0]
        
        # Profit Loss Report
        cursor.execute("SELECT SUM(total_amount) FROM Transactions WHERE order_id IS NOT NULL")
        total_revenue = cursor.fetchone()[0]
        # cursor.execute("SELECT SUM(total_cost) FROM Transactions WHERE order_id IS NOT NULL")
        # total_cost = cursor.fetchone()[0]
        # profit_loss = total_revenue - total_cost
        
        # Fetch product locations
        cursor.execute("""
            SELECT products.name, Location.LocationName
            FROM products
            INNER JOIN Inventory ON products.product_id = Inventory.product_id
            INNER JOIN Location ON Inventory.LocationID = Location.LocationID
        """)
        product_locations = cursor.fetchall()
        
        conn.close()

        return render_template('generate_inventory_report.html', 
                               total_orders_placed=total_orders_placed,
                               orders_delivered=orders_delivered,
                               orders_pending=orders_pending,
                               total_transactions_amount=total_transactions_amount,
                               total_stock_available=total_stock_available,
                               low_stock_count=low_stock_count,
                            #    profit_loss=profit_loss,
                               product_locations=product_locations)
    except Exception as e:
        return f'Error generating inventory report: {e}'


                                                        #SEARCH PRODUCT

@app.route('/search', methods=['GET', 'POST'])
def search():
    try:
        query = request.args.get('query')
        print("Search query:", query)  # Debug statement
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.product_id, p.name, pp.description, pp.price, pp.quantity, pp.category_id
            FROM products p
            JOIN products_P02 pp ON p.name = pp.name
            WHERE p.name LIKE ?
        """, ('%' + query + '%',))
        rows = cursor.fetchall()
        products = []
        for row in rows:
            product = dict(zip([column[0] for column in cursor.description], row))
            products.append(product)
        conn.close()
        print("Products:", products)  # Debug statement
        return jsonify({'products': products})
    except Exception as e:
        print("Error searching products:", e)
        return jsonify({'error': f'Error searching products: {e}'})




                                                #REGISTER USER


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            created_at = datetime.datetime.now()  
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                return redirect(url_for('login'))
            cursor.execute("INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)",
                           (username, email, password, created_at))
            conn.commit()
            return redirect(url_for('login'))
        except Exception as e:
            return f'Error registering user: {e}'
        finally:
            conn.close()
    return render_template('register.html')

                                                    # Login route

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            conn = connect_to_database()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            conn.close()
            if user:
                session['username'] = username  
                return redirect(url_for('homepage'))  
            else:
                return render_template('login.html', error='Invalid username or password')  
        except Exception as e:
            return f'Error during login: {e}'
    return render_template('login.html')

                                                    # Logout route

@app.route('/logout')
def logout():
    session.pop('username', None) 
    return redirect(url_for('homepage')) 

                                                    #ADD TO CART

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    conn = None
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'error': 'Please login first to add items to the cart'})
        username = session['username'] 
        data = request.get_json()
        product_id = data['product_id']
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        user_id = cursor.fetchone()[0]
        cursor.execute("SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
        existing_quantity = cursor.fetchone()
        if existing_quantity:
            new_quantity = existing_quantity[0] + 1
            cursor.execute("UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?", (new_quantity, user_id, product_id))
        else:
            cursor.execute("INSERT INTO cart (user_id, product_id, quantity, timestamp) VALUES (?, ?, 1, GETDATE())", (user_id, product_id))
        cursor.execute("""
            UPDATE pp
            SET pp.quantity = pp.quantity - 1
            FROM products_P02 pp
            JOIN products p ON pp.name = p.name
            WHERE p.product_id = ?
        """, (product_id,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        if conn:
            conn.close()


                                                        #REMOVE FROM CART

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    try:
        if 'username' not in session:
            return jsonify({'success': False, 'error': 'Please login first to remove items from the cart'})
        username = session['username'] 
        data = request.get_json()
        product_id = data['product_id']
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        user_id = cursor.fetchone()[0] 
        cursor.execute("SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
        existing_quantity = cursor.fetchone()
        if existing_quantity:
            current_quantity = existing_quantity[0]
            if current_quantity == 1:
                cursor.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
            else:
                new_quantity = current_quantity - 1
                cursor.execute("UPDATE cart SET quantity = ? WHERE user_id = ? AND product_id = ?", (new_quantity, user_id, product_id))
        else:
            return jsonify({'success': False, 'error': 'Item not found in the cart'})
        cursor.execute("""
            UPDATE pp
            SET pp.quantity = pp.quantity + 1
            FROM products_P02 pp
            JOIN products p ON pp.name = p.name
            WHERE p.product_id = ?
        """, (product_id,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    finally:
        if conn:
            conn.close()

                                                #VIEW CART


@app.route('/view_cart/<username>')
def view_cart(username):
    if 'username' not in session:
        return render_template('error.html', error='Please login first to see the cart')
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.user_id, p.product_id, p.name, pp.price, c.quantity
            FROM cart c
            JOIN users u ON c.user_id = u.user_id
            JOIN products p ON c.product_id = p.product_id
            JOIN products_P02 pp ON p.name = pp.name
            WHERE u.username = ?
        """, (username,))
        cart_items = cursor.fetchall()
        conn.close()
        total_price = sum(item[3] * item[4] for item in cart_items)
        return render_template('view_cart.html', cart_items=cart_items, total_price=total_price)
    except Exception as e:
        return f'Error retrieving cart items: {e}'


 
                                        # Route to display the list of shippers
@app.route('/select_shipper', methods=['GET'])
def select_shipper():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT shipper_id, shipper_name FROM Shippers")
        shippers = cursor.fetchall()
        conn.close()
        return render_template('select_shipper.html', shippers=shippers)
    except Exception as e:
        return f'Error retrieving shippers: {e}'

                                        #order placements
@app.route('/place_order', methods=['POST'])
def place_order():
    try:
        if 'username' not in session:
            return render_template('error.html', error='Please login first to place an order')

        username = session['username']
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM Users WHERE username = ?", (username,))
        user_id = cursor.fetchone()[0]

        shipper_id = request.form['shipper_id']
        cursor.execute("SELECT MAX(CAST(SUBSTRING(order_id, 2, LEN(order_id)) AS INT)) FROM orders")
        max_order_id = cursor.fetchone()[0]
        if max_order_id is None:
            max_order_id = 0
        new_order_id = 'O' + str(max_order_id + 1).zfill(3)
        order_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        expected_delivery = (datetime.datetime.now() + datetime.timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("INSERT INTO orders (order_id, shipper_id, order_date, expected_delivery, user_id,approved) VALUES (?, ?, ?, ?, ?,'pending')",
                       (new_order_id, shipper_id, order_date, expected_delivery, user_id))
        
        cursor.execute("SELECT product_id, quantity FROM cart WHERE user_id = ?", (user_id,))
        cart_items = cursor.fetchall()
        
        cursor.execute("SELECT MAX(CAST(SUBSTRING(orderline_id, 2, LEN(orderline_id)) AS INT)) FROM orderlineitems")
        max_orderline_id = cursor.fetchone()[0]
        if max_orderline_id is None:
            max_orderline_id = 0

        orderline_counter = max_orderline_id + 1

        for product_id, quantity in cart_items:
            orderline_id = 'i' + str(orderline_counter).zfill(3)
            cursor.execute("""
    SELECT p.price 
    FROM products_P02 p
    INNER JOIN products pr ON p.name = pr.name
    WHERE pr.product_id = ?
""", (product_id,))
            unit_price = cursor.fetchone()[0]
            
            cursor.execute("INSERT INTO orderlineitems (orderline_id, order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?, ?)",
                           (orderline_id, new_order_id, product_id, quantity, unit_price))
            orderline_counter += 1
        
        cursor.execute("INSERT INTO pending_orders (order_id, user_id) VALUES (?, ?)",
               (new_order_id, user_id))

        cursor.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
        
        conn.commit()
        conn.close()
        return render_template('pending_approval.html', order_id=new_order_id)
    except Exception as e:
        return f'Error placing order: {e}'




@app.route('/admin/pending_orders', methods=['GET', 'POST'])
def pending_orders():


    try:
        if request.method == 'POST':
            action = request.form.get('action')
            order_id = request.form.get('order_id')
            if action == 'approve':
                conn = connect_to_database()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM pending_orders WHERE order_id = ?", (order_id,))
                cursor.execute("UPDATE orders SET approved = 'approved' WHERE order_id = ?", (order_id,))
                conn.commit()
                conn.close()
                return redirect(url_for('pending_orders'))
            elif action == 'cancel':
                conn = connect_to_database()
                cursor = conn.cursor()
                cursor.execute("UPDATE orders SET approved = 'cancelled' WHERE order_id = ?", (order_id,))
                cursor.execute("DELETE FROM pending_orders WHERE order_id = ?", (order_id,))
                conn.commit()
                conn.close()
                return redirect(url_for('pending_orders'))

        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT order_id, user_id FROM pending_orders")
        pending_orders = cursor.fetchall()
        conn.close()

        return render_template('pending_orders.html', pending_orders=pending_orders)
    except Exception as e:
        return f'Error processing pending orders: {e}'


def get_user_orders(username):
    try:
        conn = connect_to_database()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.order_id, o.order_date, o.expected_delivery,o.approved, u.username,
                oli.product_id, oli.quantity, oli.unit_price,
                p.name AS product_name
                FROM orders o
                INNER JOIN orderLineItems oli ON o.order_id = oli.order_id
                INNER JOIN products p ON oli.product_id = p.product_id
                INNER JOIN users u ON o.user_id = u.user_id
                WHERE u.username = ?

            """, (username,))
            orders = cursor.fetchall()
            return orders
        else:
            print("Failed to connect to the database.")
            return None
    except Exception as e:
        print("Error fetching user orders:", e)
        return None
    finally:
        if conn:
            conn.close()

@app.route('/orders', methods=['GET'])
def display_orders():
    username = session.get('username')
    if username:
        orders = get_user_orders(username)
        if orders:
            return render_template('orders.html', orders=orders)
        else:
            return "No orders found for this user."
    else:
        return redirect(url_for('login')) 
    

                                        #TRANSACTION SLIPP



@app.route('/generate_slip', methods=['GET'])
def generate_slip():
    try:
        order_id = request.args.get('order_id')
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, shipper_id FROM orders WHERE order_id = ?", (order_id,))
        user_id, shipper_id = cursor.fetchone()
        cursor.execute("SELECT username FROM Users WHERE user_id = ?", (user_id,))
        user_name = cursor.fetchone()[0]
        cursor.execute("SELECT product_id, quantity, unit_price FROM orderlineitems WHERE order_id = ?", (order_id,))
        order_line_items = cursor.fetchall()
        total_amount = sum(quantity * unit_price for product_id, quantity, unit_price in order_line_items)
        product_descriptions = ', '.join(f"{quantity} x {product_id}" for product_id, quantity, _ in order_line_items)
        cursor.execute("SELECT pp.category_id FROM products p JOIN products_P02 pp ON p.name = pp.name WHERE p.product_id = ?", (order_line_items[0][0],))
        category_id = cursor.fetchone()[0]
        cursor.execute("SELECT supplier_id FROM categories WHERE category_id = ?", (category_id,))
        supplier_id = cursor.fetchone()[0]
        transaction_date = datetime.datetime.now()
        cursor.execute("""
            INSERT INTO Transactions (order_id, user_id, user_name, shipper_id, supplier_id, transaction_date, total_amount, product_description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_id, user_id, user_name, shipper_id, supplier_id, transaction_date, total_amount, product_descriptions)) 
        
        cursor.execute("UPDATE orders SET approved = 'deliver' WHERE order_id = ?", (order_id,))
        
        conn.commit()
        conn.close()   
        transaction_details = [order_id, product_descriptions, shipper_id, total_amount, str(transaction_date), user_name]     
        return render_template('transaction_slip.html', transaction_details=transaction_details)
    except Exception as e:
        return f'Error generating transaction slip: {e}'


                                        #order status (for user)
def update_order_status(order_id, new_status):
    try:
        conn = connect_to_database()  
        cursor = conn.cursor()
        
        cursor.execute("UPDATE orders SET approved = ? WHERE order_id = ?", (new_status, order_id))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e 
                                                #cancel order
@app.route('/cancel_order', methods=['GET'])
def cancel_order():
    try:
        order_id = request.args.get('order_id')
        
        conn = connect_to_database()  
        cursor = conn.cursor()
        cursor.execute("SELECT approved FROM orders WHERE order_id = ?", (order_id,))
        status = cursor.fetchone()
        
        if status is None:
            return render_template('error.html', error_message='Error: Order ID not found.')
        
        status = status[0]
        if status == 'pending':
            update_order_status(order_id, 'cancelled')
            return redirect('/user_orders')  
        elif status == 'deliver':
         
            return render_template('error.html', error_message='Error: This order has already been delivered and cannot be canceled.')
        else:
           
            return render_template('error.html', error_message='Error: This order cannot be canceled.')
        
    except Exception as e:
        return render_template('error.html', error_message=f'Error canceling order: {e}')
    













                                                #search products by category

@app.route('/search_product_by_category/<category>', methods=['GET'])
def search_product_by_category(category):
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.product_id, p.name, pp.description, pp.price, pp.quantity, pp.cost_price
            FROM products p
            JOIN products_P02 pp ON p.name = pp.name
            WHERE pp.category_id = ?
        """, (category,))
        rows = cursor.fetchall()
        products = []
        for row in rows:
            product = {
                'product_id': row[0],
                'name': row[1],
                'description': row[2],
                'price': row[3],
                'quantity': row[4],
                'cost_price': row[5]
            }
            products.append(product)
        conn.close()
        return render_template('product_search_results.html', products=products)
    except Exception as e:
        return render_template('error.html', error=f'Error searching products by category: {e}')
    



                                                #discounted Items
@app.route('/discounted_items')
def discounted_items():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        current_date = datetime.datetime.now()
        seven_days_ago = current_date - timedelta(days=1)
        cursor.execute("""
            SELECT p.product_id, p.product_name, pp.cost_price
            FROM products p
            LEFT JOIN orderlineitems oli ON p.product_id = oli.product_id
            LEFT JOIN products_P02 pp ON p.product_name = pp.name
            WHERE oli.order_id IS NULL OR oli.order_date < ?
            GROUP BY p.product_id, p.product_name, pp.cost_price
        """, (seven_days_ago,))
        products_to_discount = cursor.fetchall()

        total_loss = 0
        for product_id, product_name, original_cost_price in products_to_discount:
            discounted_cost_price = original_cost_price * 0.85  # 15% discount
            loss_per_product = original_cost_price - discounted_cost_price
            total_loss += loss_per_product

            cursor.execute("""
                UPDATE products_P02 
                SET cost_price = ?
                WHERE name = ?
            """, (discounted_cost_price, product_name))
        conn.commit()

        conn.close()

        return render_template('discounted_items.html', discounted_products=products_to_discount, total_loss=total_loss)
    except Exception as e:
        print(f"Error updating discounted items: {e}")
        return render_template('error.html', error_message=f"Error updating discounted items: {e}")





                                                   










                                                #orders chart

@app.route('/orders_status_chart', methods=['GET'])
def orders_status_chart():
    try:
        conn = connect_to_database()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orders WHERE approved = 'deliver'")
        delivered_orders = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM orders WHERE approved = 'cancelled'")
        cancelled_orders = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM orders WHERE approved = 'pending'")
        pending_orders = cursor.fetchone()[0]

        conn.close()

        data = {
            'delivered_orders': delivered_orders,
            'cancelled_orders': cancelled_orders,
            'pending_orders': pending_orders
        }
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)})


                                    #profit chart
@app.route('/daily_profit_chart')
def daily_profit_chart():
    try:
        current_date = datetime.datetime.now()
        start_of_day = datetime.datetime.combine(current_date, datetime.datetime.min.time())
        end_of_day = datetime.datetime.combine(current_date, datetime.datetime.max.time())
        
        conn = connect_to_database() 
        cursor = conn.cursor()
 
        cursor.execute("""
            SELECT SUM(total_amount)
            FROM Transactions
            WHERE transaction_date BETWEEN ? AND ?
        """, (start_of_day, end_of_day))
        total_revenue = cursor.fetchone()[0]
        cursor.execute("""
            SELECT SUM(pp.cost_price * oli.quantity)
            FROM orderlineitems oli
            INNER JOIN products p ON oli.product_id = p.product_id
            INNER JOIN products_P02 pp ON p.name = pp.name
            INNER JOIN orders o ON oli.order_id = o.order_id
            WHERE o.order_date BETWEEN ? AND ? AND o.approved = 'deliver'
        """, (start_of_day, end_of_day))
        total_cost_price = cursor.fetchone()[0]
        
        daily_profit = total_revenue - total_cost_price
        
        conn.close()
        
        return jsonify(daily_profit=daily_profit, total_cost=total_cost_price)
    except Exception as e:
        return jsonify(error_message=f"Error calculating daily profit: {e}")


                                        #total users and products
def get_total_users():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) AS total_users_count FROM users')
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else 0

@app.route('/total_users')
def total_users():
    total_users_count = get_total_users()
    return jsonify(totalUsers=total_users_count)

def get_total_products():
    conn = connect_to_database()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) AS total_products_count FROM products')
            result = cursor.fetchone()
            total_products_count = result[0] if result else 0
            cursor.close()
            conn.close()
            return total_products_count
        except Exception as e:
            print("Error executing SQL query:", e)
            return 0
    else:
        return 0

@app.route('/total_products')
def total_products():
    total_products_count = get_total_products()
    return jsonify(totalProducts=total_products_count)


def get_total_suppliers_count():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) AS total_suppliers_count FROM suppliers')
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else 0

def get_total_shippers_count():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) AS total_shippers_count FROM shippers')
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else 0

def get_total_categories_count():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) AS total_categories_count FROM categories')
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else 0

@app.route('/total_suppliers')
def total_suppliers():
    total_suppliers_count = get_total_suppliers_count()
    return jsonify(totalSuppliers=total_suppliers_count)

@app.route('/total_shippers')
def total_shippers():
    total_shippers_count = get_total_shippers_count()
    return jsonify(totalShippers=total_shippers_count)

@app.route('/total_categories')
def total_categories():
    total_categories_count = get_total_categories_count()
    return jsonify(totalCategories=total_categories_count)

















if __name__ == "__main__":
    app.run(debug=True)
