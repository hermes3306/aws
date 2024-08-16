import psycopg2
from psycopg2 import sql
from datetime import datetime, timedelta
import random
import string

# Connection parameters - adjust these as needed
conn_params = {
    'dbname': 'defaultdb',
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'port': '26257'
}

def create_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10, 2) NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id INT NOT NULL REFERENCES users(id),
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INT NOT NULL REFERENCES orders(id),
                product_id INT NOT NULL REFERENCES products(id),
                quantity INT NOT NULL
            )
        """)
    conn.commit()

def generate_random_data():
    users = []
    products = []
    orders = []
    order_items = []

    # Generate users
    for i in range(100):
        username = f"user_{i}"
        email = f"user_{i}@example.com"
        users.append((username, email))

    # Generate products
    for i in range(50):
        name = f"Product {i}"
        price = round(random.uniform(1, 1000), 2)
        products.append((name, price))

    # Generate orders and order items
    for _ in range(200):
        user_id = random.randint(1, 100)
        order_date = datetime.now() - timedelta(days=random.randint(0, 365))
        orders.append((user_id, order_date))

        num_items = random.randint(1, 5)
        for _ in range(num_items):
            order_id = len(orders)
            product_id = random.randint(1, 50)
            quantity = random.randint(1, 10)
            order_items.append((order_id, product_id, quantity))

    return users, products, orders, order_items

def insert_random_data(conn):
    users, products, orders, order_items = generate_random_data()

    with conn.cursor() as cur:
        cur.executemany("INSERT INTO users (username, email) VALUES (%s, %s)", users)
        cur.executemany("INSERT INTO products (name, price) VALUES (%s, %s)", products)
        cur.executemany("INSERT INTO orders (user_id, order_date) VALUES (%s, %s)", orders)
        cur.executemany("INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)", order_items)

    conn.commit()

def show_table_contents(conn, table_name):
    with conn.cursor() as cur:
        cur.execute(f"SELECT * FROM {table_name} LIMIT 10")
        rows = cur.fetchall()
        
        if not rows:
            print(f"No data in {table_name}")
            return

        # Get column names
        col_names = [desc[0] for desc in cur.description]
        
        # Print column names
        print("\t".join(col_names))
        print("-" * (len(col_names) * 10))  # Separator line
        
        # Print rows
        for row in rows:
            print("\t".join(str(item) for item in row))
        
        print(f"\nShowing first 10 rows of {table_name}")

def menu(conn):
    while True:
        print("\n--- Menu ---")
        print("1. List tables")
        print("2. Show table contents")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            with conn.cursor() as cur:
                cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                tables = cur.fetchall()
                print("\nTables in the database:")
                for table in tables:
                    print(table[0])
        elif choice == '2':
            table_name = input("Enter table name: ")
            show_table_contents(conn, table_name)
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    try:
        with psycopg2.connect(**conn_params) as conn:
            create_tables(conn)
            
            # Check if tables are empty
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM users")
                if cur.fetchone()[0] == 0:
                    print("Populating database with random data...")
                    insert_random_data(conn)
                    print("Database populated successfully.")
                else:
                    print("Database already contains data. Skipping population step.")
            
            menu(conn)
    except psycopg2.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    main()