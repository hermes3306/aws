import psycopg2
from psycopg2 import sql
from datetime import datetime

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

def insert_sample_data(conn):
    with conn.cursor() as cur:
        # Insert users
        cur.execute("INSERT INTO users (username, email) VALUES (%s, %s) RETURNING id", 
                    ("john_doe", "john@example.com"))
        user_id = cur.fetchone()[0]

        # Insert products
        cur.execute("INSERT INTO products (name, price) VALUES (%s, %s) RETURNING id", 
                    ("Widget", 19.99))
        product_id = cur.fetchone()[0]

        # Create an order
        cur.execute("INSERT INTO orders (user_id) VALUES (%s) RETURNING id", (user_id,))
        order_id = cur.fetchone()[0]

        # Add item to the order
        cur.execute("INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                    (order_id, product_id, 2))

    conn.commit()

def query_data(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT u.username, p.name, oi.quantity, o.order_date
            FROM users u
            JOIN orders o ON u.id = o.user_id
            JOIN order_items oi ON o.id = oi.order_id
            JOIN products p ON oi.product_id = p.id
        """)
        results = cur.fetchall()
        for row in results:
            print(f"User: {row[0]}, Product: {row[1]}, Quantity: {row[2]}, Order Date: {row[3]}")

def main():
    try:
        with psycopg2.connect(**conn_params) as conn:
            create_tables(conn)
            insert_sample_data(conn)
            query_data(conn)
    except psycopg2.Error as e:
        print(f"Database error: {e}")

if __name__ == "__main__":
    main()