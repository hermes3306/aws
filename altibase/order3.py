import pyodbc
import random
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import tkinter.font as tkFont


# Connection string
# conn_str = (
#     "DRIVER={Altibase};"
#     "SERVER=localhost;"
#     "PORT=20300;"
#     "UID=sys;"
#     "PWD=manager;"
#     "DATABASE=mydb;"
# )

conn_str = (
    "DSN=Altibase;"
    "UID=sys;"
    "PWD=manager;"
    "DATABASE=mydb;"
)

# conn_str = (
#     "DRIVER={ALTIBASE_HDB_ODBC_64bit};"
#     "SERVER=localhost;"
#     "PORT=20300;"
#     "UID=sys;"
#     "PWD=manager;"
#     "DATABASE=mydb;"
# )

def create_connection():
    try:
        conn = pyodbc.connect(conn_str)
        print("Connection successful")
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[1]
        print(f"Error connecting to database:")
        print(f"SQL State: {sqlstate}")
        print(f"Error message: {ex}")
        messagebox.showerror("Connection Error", f"Failed to connect to database: {ex}")
        return None

def drop_tables(cursor):
    tables = ["OrderItems", "Orders", "Products", "Users"]
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE {table}")
        except pyodbc.Error:
            pass  # Ignore errors if table doesn't exist

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
    
    for table_sql in tables:
        cursor.execute(table_sql)

def insert_sample_data(cursor, num_records):
    # Insert Users
    for i in range(1, num_records + 1):
        cursor.execute("INSERT INTO Users (user_id, username, email) VALUES (?, ?, ?)",
                       (i, f"user{i}", f"user{i}@example.com"))

    # Insert Products
    products = [
        (1, "Laptop", 999.99),
        (2, "Smartphone", 599.99),
        (3, "Headphones", 99.99),
        (4, "Tablet", 299.99),
        (5, "Smartwatch", 199.99)
    ]
    cursor.executemany("INSERT INTO Products (product_id, product_name, price) VALUES (?, ?, ?)", products)

    # Insert Orders and OrderItems
    order_item_id = 1
    for order_id in range(1, num_records + 1):
        user_id = random.randint(1, num_records)
        order_date = datetime.now() - timedelta(days=random.randint(0, 365))
        cursor.execute("INSERT INTO Orders (order_id, user_id, order_date) VALUES (?, ?, ?)",
                       (order_id, user_id, order_date))

        for _ in range(random.randint(1, 3)):  # 1 to 3 items per order
            product_id = random.randint(1, 5)
            quantity = random.randint(1, 5)
            cursor.execute("INSERT INTO OrderItems (order_item_id, order_id, product_id, quantity) VALUES (?, ?, ?, ?)",
                           (order_item_id, order_id, product_id, quantity))
            order_item_id += 1

def get_tables(cursor):
    try:
        # First, try to get just the table names
        cursor.execute("""
        SELECT TABLE_NAME
        FROM SYSTEM_.SYS_TABLES_
        WHERE TABLE_TYPE = 'T'
        ORDER BY TABLE_NAME
        """)
        tables = cursor.fetchall()
        
        # Now, let's try to get the owner for each table
        result = []
        for table in tables:
            try:
                cursor.execute(f"SELECT USER_ID FROM SYSTEM_.SYS_TABLES_ WHERE TABLE_NAME = '{table[0]}'")
                user_id = cursor.fetchone()[0]
                cursor.execute(f"SELECT USER_NAME FROM SYSTEM_.SYS_USERS_ WHERE USER_ID = {user_id}")
                user_name = cursor.fetchone()[0]
                result.append((user_name, table[0]))
            except pyodbc.Error:
                # If we can't get the owner, just use 'UNKNOWN'
                result.append(('UNKNOWN', table[0]))
        
        return result
    except pyodbc.Error as ex:
        print(f"Error in get_tables: {ex}")
        # If all else fails, return an empty list
        return []

def display_table(cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    return columns, rows

class AltibaseGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Altibase Database Manager")
        self.master.geometry("800x600")
        
        self.font = tkFont.Font()

        self.conn = create_connection()
        if not self.conn:
            self.master.quit()
            return
        
        self.create_widgets()



    def create_widgets(self):
        # Generate Schema button
        self.generate_btn = ttk.Button(self.master, text="Generate Schema", command=self.generate_schema)
        self.generate_btn.pack(pady=10)

        # Update Table selection dropdown
        self.table_var = tk.StringVar()
        self.table_dropdown = ttk.Combobox(self.master, textvariable=self.table_var, state="readonly", width=50)
        self.table_dropdown.pack(pady=10)
        self.table_dropdown.bind("<<ComboboxSelected>>", self.load_table_data)

        # Create a frame to hold the treeview and scrollbars
        self.tree_frame = ttk.Frame(self.master)
        self.tree_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Create the treeview
        self.tree = ttk.Treeview(self.tree_frame)

        # Create vertical scrollbar
        self.vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.vsb.pack(side='right', fill='y')

        # Create horizontal scrollbar
        self.hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.hsb.pack(side='bottom', fill='x')

        # Configure the treeview to use scrollbars
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        # Pack the treeview
        self.tree.pack(expand=True, fill='both')

        # Populate table dropdown
        self.update_table_list()

        # Create font for measurements
        self.font = tkFont.Font()
        

    def generate_schema(self):
        num_records = simpledialog.askinteger("Input", "Enter number of records to generate:", 
                                              minvalue=1, maxvalue=1000)
        if num_records is None:
            return

        cursor = self.conn.cursor()
        try:
            drop_tables(cursor)
            create_tables(cursor)
            insert_sample_data(cursor, num_records)
            self.conn.commit()
            messagebox.showinfo("Success", f"Schema generated with {num_records} records.")
            self.update_table_list()
        except pyodbc.Error as ex:
            messagebox.showerror("Error", f"Failed to generate schema: {ex}")
        finally:
            cursor.close()

    
    def update_table_list(self):
        cursor = self.conn.cursor()
        try:
            tables = get_tables(cursor)
            if tables:
                self.table_dropdown['values'] = [f"{user}.{table}" for user, table in tables]
                self.table_dropdown.set(f"{tables[0][0]}.{tables[0][1]}")
                self.load_table_data(None)
            else:
                messagebox.showwarning("No Tables", "No tables found in the database.")
                self.table_dropdown['values'] = []
        except pyodbc.Error as ex:
            messagebox.showerror("Error", f"Failed to retrieve table list: {ex}")
        finally:
            cursor.close()
        

    def load_table_data(self, event):
        table_full_name = self.table_var.get()
        if not table_full_name:
            return

        user, table_name = table_full_name.split('.')

        cursor = self.conn.cursor()
        try:
            columns, rows = display_table(cursor, f"{user}.{table_name}")

            self.tree.delete(*self.tree.get_children())
            self.tree['columns'] = columns
            self.tree.heading("#0", text="Index")
            self.tree.column("#0", width=50, stretch=tk.NO)

            for col in columns:
                self.tree.heading(col, text=col)
                # Set a minimum width for each column
                self.tree.column(col, width=100, stretch=tk.NO)

            for i, row in enumerate(rows, start=1):
                formatted_row = []
                for item in row:
                    if isinstance(item, datetime):
                        formatted_row.append(item.strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        formatted_row.append(str(item))
                self.tree.insert("", "end", text=str(i), values=formatted_row)

            # Adjust column widths based on content
            for col in columns:
                max_width = max(self.font.measure(str(row[columns.index(col)])) for row in rows)
                header_width = self.font.measure(col)
                self.tree.column(col, width=max(max_width, header_width) + 10)

        except pyodbc.Error as ex:
            messagebox.showerror("Error", f"Failed to load table data: {ex}")
        finally:
            cursor.close()


def main():
    root = tk.Tk()
    AltibaseGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()