import pyodbc
import random
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
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
        self.log_frame = ttk.Frame(self.master)
        self.log_frame.pack(fill='x', padx=10, pady=5)
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=5)
        self.log_text.pack(fill='x')

        # Create status bar
        self.status_bar = ttk.Frame(self.master)
        self.status_bar.pack(fill='x', side='bottom')
        self.status_label = ttk.Label(self.status_bar, text="Not connected")
        self.status_label.pack(side='left')
        self.status_icon = ttk.Label(self.status_bar, text="🔴")
        self.status_icon.pack(side='right')

        self.update_status_bar()

    def create_orders_tab(self):
        # (Keep the existing code for the Orders tab here)
        # Generate Schema button
        self.generate_btn = ttk.Button(self.orders_tab, text="Generate Schema", command=self.generate_schema)
        self.generate_btn.pack(pady=10)

        # Update Table selection dropdown
        self.table_var = tk.StringVar()
        self.table_dropdown = ttk.Combobox(self.orders_tab, textvariable=self.table_var, state="readonly", width=50)
        self.table_dropdown.pack(pady=10)
        self.table_dropdown.bind("<<ComboboxSelected>>", self.load_table_data)

        # Create a frame to hold the treeview and scrollbars
        self.tree_frame = ttk.Frame(self.orders_tab)
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
        
        # Configure the overall style
        style = ttk.Style(self.master)
        style.theme_use("clam")
        style.configure("Treeview", background="#F0F0F0", fieldbackground="#F0F0F0", foreground="black")
        style.map('Treeview', background=[('selected', '#4A6984')])

        # Pack the treeview
        self.tree.pack(expand=True, fill='both')

        # Populate table dropdown
        self.update_table_list()

    def create_database_tab(self):
        # SQL edit box
        self.sql_frame = ttk.Frame(self.database_tab)
        self.sql_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.sql_text = scrolledtext.ScrolledText(self.sql_frame, height=10)
        self.sql_text.pack(fill='both', expand=True)
        self.sql_text.insert(tk.END, "select * from SYSTEM_.SYS_TABLES_")

        # Execute button
        self.execute_btn = ttk.Button(self.database_tab, text="Execute", command=self.execute_query)
        self.execute_btn.pack(pady=10)

        # Result display area
        self.result_frame = ttk.Frame(self.database_tab)
        self.result_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.result_tree = ttk.Treeview(self.result_frame)
        self.result_tree.pack(fill='both', expand=True)

        # Add scrollbars to the result tree
        vsb = ttk.Scrollbar(self.result_frame, orient="vertical", command=self.result_tree.yview)
        hsb = ttk.Scrollbar(self.result_frame, orient="horizontal", command=self.result_tree.xview)
        self.result_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side='right', fill='y')
        hsb.pack(side='bottom', fill='x')
            
    def execute_query(self):
        query = self.sql_text.get("1.0", tk.END).strip()
        if not query:
            self.log_message("No query to execute", "warning")
            return

        cursor = self.conn.cursor()
        try:
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            self.display_query_results(columns, rows)
            self.log_message("Query executed successfully", "info")
        except pyodbc.Error as ex:
            self.log_message(f"Error executing query: {ex}", "error")
        finally:
            cursor.close()

    def display_query_results(self, columns, rows):
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
        


    def display_ddl_results(self, message):
        self.result_tree.delete(*self.result_tree.get_children())
        self.result_tree['columns'] = ['Result']
        self.result_tree.heading('Result', text='Result')
        self.result_tree.column('Result', width=400)
        self.result_tree.insert("", "end", values=(message,))

    def log_message(self, message, level):
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

            self.tree.delete(*self.tree.get_children())
            self.tree['columns'] = columns
            self.tree.heading("#0", text="Index")
            self.tree.column("#0", width=50, stretch=tk.NO)

            # Style configuration for alternating row colors
            self.tree.tag_configure('oddrow', background='#E8E8E8')
            self.tree.tag_configure('evenrow', background='#F5F5F5')

            # Configure headings style
            style = ttk.Style()
            style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))

            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=100, stretch=tk.NO)

            for i, row in enumerate(rows, start=1):
                formatted_row = []
                for item in row:
                    if isinstance(item, datetime):
                        formatted_row.append(item.strftime('%Y-%m-%d %H:%M:%S'))
                    else:
                        formatted_row.append(str(item))
                
                # Apply alternating row colors
                tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                self.tree.insert("", "end", text=str(i), values=formatted_row, tags=(tag,))

            # Adjust column widths based on content
            for col in columns:
                max_width = max(self.font.measure(str(row[columns.index(col)])) for row in rows)
                header_width = self.font.measure(col)
                self.tree.column(col, width=max(max_width, header_width) + 20)

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