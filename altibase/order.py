import pyodbc
import random
from datetime import datetime, timedelta

# Connection string
conn_str = (
    "DRIVER={Altibase};"
    "SERVER=localhost;"
    "PORT=20300;"
    "UID=sys;"
    "PWD=manager;"
    "DATABASE=mydb;"
)

def drop_tables(cursor):
    tables = ["OrderItems", "Orders", "Products", "Users"]
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE {table}")
            print(f"Table {table} dropped successfully")
        except pyodbc.Error as ex:
            print(f"Error dropping table {table}: {ex}")

def create_tables(cursor):
    tables = [
        """
        CREATE TABLE Users (
            user_id INTEGER PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            email VARCHAR(100) NOT NULL
        )
        """,
        """
        CREATE TABLE Products (
            product_id INTEGER PRIMARY KEY,
            product_name VARCHAR(100) NOT NULL,
            price DECIMAL(10, 2) NOT NULL
        )
        """,
        """
        CREATE TABLE Orders (
            order_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            order_date DATE,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
        """,
        """
        CREATE TABLE OrderItems (
            order_item_id INTEGER PRIMARY KEY,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES Orders(order_id),
            FOREIGN KEY (product_id) REFERENCES Products(product_id)
        )
        """
    ]
    
    for i, table_sql in enumerate(tables, 1):
        try:
            cursor.execute(table_sql)
            print(f"Table {i} created successfully")
        except pyodbc.Error as ex:
            print(f"Error creating table {i}: {ex}")

def insert_sample_data(cursor):
    try:
        # Insert Users
        for i in range(1, 21):
            cursor.execute("INSERT INTO Users (user_id, username, email) VALUES (?, ?, ?)",
                           (i, f"user{i}", f"user{i}@example.com"))
        print("Users inserted successfully")

        # Insert Products
        products = [
            (1, "Laptop", 999.99),
            (2, "Smartphone", 599.99),
            (3, "Headphones", 99.99),
            (4, "Tablet", 299.99),
            (5, "Smartwatch", 199.99)
        ]
        cursor.executemany("INSERT INTO Products (product_id, product_name, price) VALUES (?, ?, ?)", products)
        print("Products inserted successfully")

        # Insert Orders and OrderItems
        order_item_id = 1  # Initialize order_item_id
        for order_id in range(1, 101):
            user_id = random.randint(1, 20)
            order_date = datetime.now() - timedelta(days=random.randint(0, 365))
            cursor.execute("INSERT INTO Orders (order_id, user_id, order_date) VALUES (?, ?, ?)",
                           (order_id, user_id, order_date))

            for _ in range(random.randint(1, 3)):  # 1 to 3 items per order
                product_id = random.randint(1, 5)
                quantity = random.randint(1, 5)
                cursor.execute("INSERT INTO OrderItems (order_item_id, order_id, product_id, quantity) VALUES (?, ?, ?, ?)",
                               (order_item_id, order_id, product_id, quantity))
                order_item_id += 1  # Increment order_item_id for the next item
        print("Orders and OrderItems inserted successfully")

    except pyodbc.Error as ex:
        print(f"Error inserting sample data: {ex}")
        print(f"Error args: {ex.args}")
        if len(ex.args) > 1:
            print(f"SQL State: {ex.args[0]}")
            print(f"Error message: {ex.args[1]}")

def display_table(cursor, table_name):
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        if not rows:
            print(f"No data in {table_name}")
            return
        
        columns = [column[0] for column in cursor.description]
        print("\n" + "-" * 50)
        print(f"{table_name} Contents:")
        print("-" * 50)
        print(" | ".join(columns))
        print("-" * 50)
        for row in rows:
            print(" | ".join(str(item) for item in row))
    except pyodbc.Error as ex:
        print(f"Error displaying table {table_name}: {ex}")

def main_menu(cursor):
    while True:
        print("\n--- Main Menu ---")
        print("1. List Users")
        print("2. List Products")
        print("3. List Orders")
        print("4. List OrderItems")
        print("5. Exit")
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            display_table(cursor, "Users")
        elif choice == '2':
            display_table(cursor, "Products")
        elif choice == '3':
            display_table(cursor, "Orders")
        elif choice == '4':
            display_table(cursor, "OrderItems")
        elif choice == '5':
            print("Exiting program...")
            break
        else:
            print("Invalid choice. Please try again.")

def main():
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        print("Dropping existing tables...")
        drop_tables(cursor)
        
        print("Creating tables...")
        create_tables(cursor)
        
        print("Inserting sample data...")
        insert_sample_data(cursor)
        
        conn.commit()
        print("Database setup complete.")
        
        main_menu(cursor)
        
    except pyodbc.Error as ex:
        sqlstate = ex.args[1]
        print(f"Error connecting to the database: {sqlstate}")
        print(f"Error details: {ex}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
