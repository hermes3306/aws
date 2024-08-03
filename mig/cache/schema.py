import psycopg2
from psycopg2 import sql
import configparser
import os
import random
import string

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the configuration file
config.read(os.path.join(current_dir, 'db.ini'))

# Get the database configuration
db_config = config['postgresql']

# SQL commands
sql_commands = [
    # Drop existing tables
    "DROP TABLE IF EXISTS order_items CASCADE;",
    "DROP TABLE IF EXISTS orders CASCADE;",
    "DROP TABLE IF EXISTS products CASCADE;",
    "DROP TABLE IF EXISTS users CASCADE;",

    # Create users table
    """
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(100) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,

    # Create products table
    """
    CREATE TABLE products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        price DECIMAL(10, 2) NOT NULL,
        inventory INTEGER NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,

    # Create orders table
    """
    CREATE TABLE orders (
        id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(id),
        status VARCHAR(20) NOT NULL,
        total_amount DECIMAL(10, 2) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,

    # Create order_items table
    """
    CREATE TABLE order_items (
        id SERIAL PRIMARY KEY,
        order_id INTEGER REFERENCES orders(id),
        product_id INTEGER REFERENCES products(id),
        quantity INTEGER NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """
]

# Additional SQL commands for populating the database
populate_commands = [
    # Insert users
    """
    INSERT INTO users (username, email, password_hash)
    VALUES (%s, %s, %s)
    """,
    
    # Insert products
    """
    INSERT INTO products (name, description, price, inventory)
    VALUES (%s, %s, %s, %s)
    """,
    
    # Insert orders
    """
    INSERT INTO orders (user_id, status, total_amount)
    VALUES (%s, %s, %s)
    """,
    
    # Insert order items
    """
    INSERT INTO order_items (order_id, product_id, quantity, price)
    VALUES (%s, %s, %s, %s)
    """
]

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_sample_data():
    users = []
    products = []
    orders = []
    order_items = []

    # Generate 10 users
    for i in range(10):
        username = f"user{i+1}"
        email = f"user{i+1}@example.com"
        password_hash = generate_random_string(20)  # In real scenario, use proper hashing
        users.append((username, email, password_hash))

    # Generate 20 products
    for i in range(20):
        name = f"Product {i+1}"
        description = f"Description for Product {i+1}"
        price = round(random.uniform(10.0, 100.0), 2)
        inventory = random.randint(10, 100)
        products.append((name, description, price, inventory))

    # Generate 100 orders
    for _ in range(100):
        user_id = random.randint(1, 10)
        status = random.choice(["pending", "completed", "cancelled"])
        total_amount = 0
        
        order_items_for_order = []
        for _ in range(random.randint(1, 5)):  # 1 to 5 items per order
            product_id = random.randint(1, 20)
            quantity = random.randint(1, 5)
            price = products[product_id-1][2]  # Price from the product
            total_amount += price * quantity
            order_items_for_order.append((None, product_id, quantity, price))  # order_id is None for now
        
        orders.append((user_id, status, total_amount))
        order_items.extend(order_items_for_order)

    return users, products, orders, order_items

def execute_sql_commands():
    conn = None
    cur = None
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password'],
            sslmode='require'
        )

        # Create a cursor
        cur = conn.cursor()

        # Execute each SQL command to create tables
        for command in sql_commands:
            cur.execute(command)
            print(f"Executed: {command[:50]}...")  # Print first 50 characters of each command

        # Generate and insert sample data
        users, products, orders, order_items = generate_sample_data()
        
        print(f"Inserting {len(users)} users...")
        cur.executemany(populate_commands[0], users)
        
        print(f"Inserting {len(products)} products...")
        cur.executemany(populate_commands[1], products)
        
        print(f"Inserting {len(orders)} orders...")
        cur.executemany(populate_commands[2], orders)
        
        # Get the inserted order IDs
        cur.execute("SELECT id FROM orders ORDER BY id")
        order_ids = [row[0] for row in cur.fetchall()]
        print(f"Retrieved {len(order_ids)} order IDs.")
        
        # Update order_items with actual order_ids
        for i, item in enumerate(order_items):
            order_items[i] = (order_ids[i // 5],) + item[1:]  # Assume max 5 items per order
        
        print(f"Inserting {len(order_items)} order items...")
        cur.executemany(populate_commands[3], order_items)

        # Commit the changes
        conn.commit()

        print("All SQL commands executed successfully and sample data inserted.")

        # Verify data insertion
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM products")
        product_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM orders")
        order_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM order_items")
        order_item_count = cur.fetchone()[0]

        print(f"Verification: {user_count} users, {product_count} products, {order_count} orders, {order_item_count} order items.")

    except (Exception, psycopg2.Error) as error:
        print(f"Error: {error}")
        if conn:
            conn.rollback()

    finally:
        # Close communication with the database
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("Database connection closed.")
                        
if __name__ == "__main__":
    execute_sql_commands()