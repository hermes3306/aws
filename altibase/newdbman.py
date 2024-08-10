import sys
import os
import pyodbc
import random
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QTabWidget, QAction, QMenu, QMenuBar, QTreeWidget, QTreeWidgetItem, QComboBox, QLabel, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Connection string
conn_str = (
    "DSN=Altibase;"
    "UID=sys;"
    "PWD=manager;"
    "DATABASE=mydb;"
)

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
        order_date = datetime.now()
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
        cursor.execute("""
        SELECT USER_NAME, TABLE_NAME
        FROM SYSTEM_.SYS_TABLES_ t
        JOIN SYSTEM_.SYS_USERS_ u ON t.USER_ID = u.USER_ID
        WHERE t.TABLE_TYPE = 'T'
        ORDER BY USER_NAME, TABLE_NAME
        """)
        return cursor.fetchall()
    except pyodbc.Error as ex:
        print(f"Error in get_tables: {ex}")
        return []

def display_table(cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    return columns, rows

class AltibaseGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Altibase Database Manager")
        self.setGeometry(100, 100, 1000, 800)
        
        self.font = QFont()

        self.conn = None
        self.connections = {'Altibase': [], 'SQLite': []}
        self.query_history = []
        self.max_history = 10
        self.create_widgets()
        self.load_query_history()

    def create_widgets(self):
        # Create menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        # Create 'New' submenu
        new_menu = QMenu('New', self)
        file_menu.addMenu(new_menu)

        # Add connection options to 'New' submenu
        altibase_action = QAction('Connection Altibase', self)
        altibase_action.triggered.connect(lambda: self.new_connection('Altibase'))
        new_menu.addAction(altibase_action)

        sqlite_action = QAction('Connection SQLite', self)
        sqlite_action.triggered.connect(lambda: self.new_connection('SQLite'))
        new_menu.addAction(sqlite_action)

        # Add Exit option
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create and add tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create log message box
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        main_layout.addWidget(self.log_text)

        # Create status bar
        self.statusBar().showMessage("Not connected")

    def new_connection(self, db_type):
        conn_count = len(self.connections[db_type]) + 1
        conn_name = f"{db_type} {conn_count}"
        
        if db_type == 'Altibase':
            conn = create_connection()  # You may need to modify this to accept connection parameters
        else:  # SQLite
            conn = None  # Implement SQLite connection here
        
        if conn:
            self.connections[db_type].append(conn)
            self.create_connection_tab(conn_name, conn)
            self.statusBar().showMessage(f"Connected to {conn_name}")
        else:
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to {conn_name}")

    def create_connection_tab(self, conn_name, conn):
        new_tab = QWidget()
        self.tab_widget.addTab(new_tab, conn_name)
        
        layout = QVBoxLayout(new_tab)

        # Add widgets specific to this connection
        # Table selection dropdown
        table_dropdown = QComboBox()
        table_dropdown.currentIndexChanged.connect(lambda: self.load_table_data(conn, table_dropdown))
        layout.addWidget(table_dropdown)

        # Tree widget for displaying data
        tree_widget = QTreeWidget()
        layout.addWidget(tree_widget)

        # Query text area
        query_text = QTextEdit()
        layout.addWidget(query_text)

        # Execute and Clear buttons
        button_layout = QHBoxLayout()
        execute_btn = QPushButton("Execute")
        execute_btn.clicked.connect(lambda: self.execute_query(conn, query_text, tree_widget))
        button_layout.addWidget(execute_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(query_text.clear)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)

        # Query history area
        history_label = QLabel("Query History:")
        layout.addWidget(history_label)
        history_text = QTextEdit()
        history_text.setReadOnly(True)
        layout.addWidget(history_text)

        # Populate table dropdown
        self.update_table_list(conn, table_dropdown)

    def update_table_list(self, conn, dropdown):
        cursor = conn.cursor()
        try:
            tables = get_tables(cursor)
            if tables:
                dropdown.clear()
                for user, table in tables:
                    dropdown.addItem(f"{user}.{table}")
            else:
                QMessageBox.warning(self, "No Tables", "No tables found in the database.")
        except pyodbc.Error as ex:
            QMessageBox.critical(self, "Error", f"Failed to retrieve table list: {ex}")
        finally:
            cursor.close()

    def load_table_data(self, conn, dropdown):
        table_full_name = dropdown.currentText()
        if not table_full_name:
            return

        cursor = conn.cursor()
        try:
            columns, rows = display_table(cursor, table_full_name)
            tree_widget = self.tab_widget.currentWidget().findChild(QTreeWidget)
            self.display_query_results(columns, rows, tree_widget)
        except pyodbc.Error as ex:
            QMessageBox.critical(self, "Error", f"Failed to load table data: {ex}")
        finally:
            cursor.close()

    def execute_query(self, conn, query_text, tree_widget):
        query = query_text.toPlainText().strip()

        if not query:
            self.log_message("No query to execute", "warning")
            return

        cursor = conn.cursor()
        try:
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            rows = cursor.fetchall()
            self.display_query_results(columns, rows, tree_widget)
            self.log_message("Query executed successfully", "info")
            
            self.add_query_to_history(query)
        except pyodbc.Error as ex:
            self.log_message(f"Error executing query: {ex}", "error")
        finally:
            cursor.close()

    def display_query_results(self, columns, rows, tree):
        tree.clear()
        tree.setColumnCount(len(columns))
        tree.setHeaderLabels(columns)

        for row in rows:
            item = QTreeWidgetItem(tree)
            for i, value in enumerate(row):
                item.setText(i, str(value))

        for i in range(len(columns)):
            tree.resizeColumnToContents(i)

    def log_message(self, message, level):
        color = {"error": "red", "warning": "orange", "info": "black"}[level]
        self.log_text.append(f'<font color="{color}">{message}</font>')

    def add_query_to_history(self, query):
        self.query_history.append(query)
        self.query_history = self.query_history[-self.max_history:]
        self.update_history_text()
        self.save_query_history()

    def update_history_text(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            history_text = current_tab.findChild(QTextEdit, "history_text")
            if history_text:
                history_text.clear()
                for query in reversed(self.query_history):
                    history_text.append(query)

    def load_query_history(self):
        history_file = "query_history.txt"
        if os.path.exists(history_file):
            try:
                with open(history_file, "r") as file:
                    self.query_history = [query.strip() for query in file.readlines()]
                self.log_message(f"Query history loaded from {history_file}", "info")
            except IOError as ex:
                self.log_message(f"Error loading query history: {ex}", "error")
        else:
            self.query_history = []

    def save_query_history(self):
        history_file = "query_history.txt"
        try:
            with open(history_file, "w") as file:
                for query in self.query_history:
                    file.write(query + "\n")
            self.log_message(f"Query history saved to {history_file}", "info")
        except IOError as ex:
            self.log_message(f"Error saving query history: {ex}", "error")

def main():
    app = QApplication(sys.argv)
    gui = AltibaseGUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()