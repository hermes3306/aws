import pyodbc
import random
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import tkinter.font as tkFont
import tkinter as tk
from tkinter import ttk, scrolledtext


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
        print(f"Error connecting to database: {ex}")
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
        self.master.geometry("1000x800")
        
        self.font = tkFont.Font()

        # Initialize attributes
        self.conn = None
        self.notebook = None
        self.orders_tab = None
        self.database_tab = None
        self.table_var = None
        self.table_dropdown = None
        self.orders_tree = None  # Separate tree for Orders tab
        self.query_text = None
        self.history_notebook = None
        self.database_tree = None  # Separate tree for Database tab
        self.log_text = None
        self.status_label = None
        self.status_icon = None

        self.conn = create_connection()
        self.create_widgets()
        
        if not self.conn:
            messagebox.showerror("Connection Error", "Failed to connect to the database. The application will have limited functionality.")

    def create_widgets(self):
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill='both')

        # Create Orders tab
        self.orders_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_tab, text="Orders")

        # Create Database tab
        self.database_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.database_tab, text="Database")

        # Create widgets for Orders tab
        self.create_orders_tab()

        # Create widgets for Database tab
        self.create_database_tab()

        # Create log message box
        log_frame = ttk.Frame(self.master)
        log_frame.pack(fill='x', padx=10, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=5)
        self.log_text.pack(fill='x')

        # Create status bar
        status_bar = ttk.Frame(self.master)
        status_bar.pack(fill='x', side='bottom')
        self.status_label = ttk.Label(status_bar, text="Not connected")
        self.status_label.pack(side='left')
        self.status_icon = ttk.Label(status_bar, text="🔴")
        self.status_icon.pack(side='right')

        self.update_status_bar()

    def display_query_results(self, columns, rows):
        if self.result_tree is None:
            self.log_message("Error: Result tree not initialized", "error")
            return

        self.result_tree.delete(*self.result_tree.get_children())
        self.result_tree['columns'] = columns
        self.result_tree.heading("#0", text="Index")
        self.result_tree.column("#0", width=50, stretch=tk.NO)

        for col in columns:
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=100, stretch=tk.NO)

        for i, row in enumerate(rows, start=1):
            formatted_row = [str(item) for item in row]
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.result_tree.insert("", "end", text=str(i), values=formatted_row, tags=(tag,))

        # Adjust column widths based on content
        for col in columns:
            max_width = max(self.font.measure(str(row[columns.index(col)])) for row in rows)
            header_width = self.font.measure(col)
            self.result_tree.column(col, width=max(max_width, header_width) + 20)

    def log_message(self, message, level):
        if self.log_text is None:
            print(f"Log not initialized. Message: {level.upper()} - {message}")
            return

        if level == "error":
            tag = "error"
            color = "red"
        elif level == "warning":
            tag = "warning"
            color = "orange"
        else:
            tag = "info"
            color = "black"

        self.log_text.tag_config(tag, foreground=color)
        self.log_text.insert(tk.END, f"{message}\n", tag)
        self.log_text.see(tk.END)


    def create_orders_tab(self):
        # Generate Schema button
        generate_btn = ttk.Button(self.orders_tab, text="Generate Schema", command=self.generate_schema)
        generate_btn.pack(pady=10)

        # Update Table selection dropdown
        self.table_var = tk.StringVar()
        self.table_dropdown = ttk.Combobox(self.orders_tab, textvariable=self.table_var, state="readonly", width=50)
        self.table_dropdown.pack(pady=10)
        self.table_dropdown.bind("<<ComboboxSelected>>", self.load_table_data)

        # Create a frame to hold the treeview and scrollbars
        tree_frame = ttk.Frame(self.orders_tab)
        tree_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Create the treeview
        self.tree = ttk.Treeview(tree_frame)
        self.tree.pack(expand=True, fill='both')

        # Create the treeview for Orders tab
        tree_frame = ttk.Frame(self.orders_tab)
        tree_frame.pack(expand=True, fill='both', padx=10, pady=10)
        self.orders_tree = ttk.Treeview(tree_frame)
        self.orders_tree.pack(expand=True, fill='both')

        # Create scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.orders_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.orders_tree.xview)
        self.orders_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')

        # Populate table dropdown
        self.update_table_list()

    def create_database_tab(self):
        # Query text area
        self.query_text = scrolledtext.ScrolledText(self.database_tab, height=10)
        self.query_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Default query
        default_query = "select * from SYSTEM_.SYS_TABLES_"
        self.query_text.insert(tk.END, default_query)
        
            # Button frame
        button_frame = ttk.Frame(self.database_tab)
        button_frame.pack(fill='x', padx=10, pady=5)

        # Execute button
        execute_btn = ttk.Button(button_frame, text="Execute", command=self.execute_query)
        execute_btn.pack(side='left', padx=5)

        # Clear button
        clear_btn = ttk.Button(button_frame, text="Clear", command=self.clear_current_query)
        clear_btn.pack(side='left', padx=5)

        # Query history tabs
        self.history_notebook = ttk.Notebook(self.database_tab)
        self.history_notebook.pack(fill='x', padx=10, pady=5)

        # Result display area
        result_frame = ttk.Frame(self.database_tab)
        result_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.database_tree = ttk.Treeview(result_frame)
        self.database_tree.pack(fill='both', expand=True)

        # Add scrollbars to the result tree
        vsb = ttk.Scrollbar(result_frame, orient="vertical", command=self.database_tree.yview)
        hsb = ttk.Scrollbar(result_frame, orient="horizontal", command=self.database_tree.xview)
        self.database_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')


    def clear_current_query(self):
        """Clear the current query in the query text area."""
        self.query_text.delete("1.0", tk.END)


    def create_result_tree(self, parent):
        # Create the result treeview
        result_frame = ttk.Frame(parent)
        result_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        tree = ttk.Treeview(result_frame)
        tree.pack(fill='both', expand=True)

        # Add scrollbars to the result tree
        vsb = ttk.Scrollbar(result_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(result_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')

        # Configure the treeview style
        style = ttk.Style()
        style.configure("Treeview", font=self.font)
        style.configure("Treeview.Heading", font=self.font)

        # Configure tag styles for alternating row colors
        tree.tag_configure('oddrow', background='#E8E8E8')
        tree.tag_configure('evenrow', background='#FFFFFF')

        return tree
            
    def add_query_tab(self, query):
        tab = ttk.Frame(self.history_notebook)
        self.history_notebook.add(tab, text=f"Query {self.history_notebook.index('end') + 1}")
        text = scrolledtext.ScrolledText(tab, height=10)
        text.pack(fill='both', expand=True)
        text.insert(tk.END, query)
        text.config(state='disabled')  # Make it read-only
        self.history_notebook.select(tab)


    def display_query_results(self, columns, rows, tree):
        if tree is None:
            self.log_message(f"Error: Result tree not initialized for {self.notebook.select()}", "error")
            return

        tree.delete(*tree.get_children())
        tree['columns'] = columns
        tree.heading("#0", text="Index")
        tree.column("#0", width=50, stretch=tk.NO)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, stretch=tk.NO)

        for i, row in enumerate(rows, start=1):
            formatted_row = [str(item) for item in row]
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert("", "end", text=str(i), values=formatted_row, tags=(tag,))

        # Adjust column widths based on content
        for col in columns:
            max_width = max(self.font.measure(str(row[columns.index(col)])) for row in rows)
            header_width = self.font.measure(col)
            tree.column(col, width=max(max_width, header_width) + 20)

    def update_status_bar(self):
        if self.conn:
            self.status_label.config(text="Connected")
            self.status_icon.config(text="🟢", foreground="green")
        else:
            self.status_label.config(text="Not connected")
            self.status_icon.config(text="🔴", foreground="red")

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
            self.display_query_results(columns, rows, self.orders_tree)
        except pyodbc.Error as ex:
            messagebox.showerror("Error", f"Failed to load table data: {ex}")
        finally:
            cursor.close()

    def execute_query(self):
        query = self.query_text.get("1.0", tk.END).strip()

        if not query:
            self.log_message("No query to execute", "warning")
            return

        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            self.display_query_results(columns, rows, self.database_tree)
            self.log_message("Query executed successfully", "info")
            
            # Add new tab with this query
            self.add_query_tab(query)
        except pyodbc.Error as ex:
            self.log_message(f"Error executing query: {ex}", "error")
        finally:
            cursor.close()


def main():
    root = tk.Tk()
    AltibaseGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()