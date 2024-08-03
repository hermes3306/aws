import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QComboBox, QLabel, QInputDialog, QMessageBox, QTableWidget, QTableWidgetItem, QListWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import configparser
from dbman_my import PostgreSQLManager, Neo4jManager, MongoDBManager, MySQLManager, RedisManager

class DatabaseManagerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.loadDatabases()
        self.current_manager = None

    def initUI(self):
        self.setWindowTitle('Database Manager')
        self.setGeometry(100, 100, 1200, 800)

        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Database selection
        db_layout = QHBoxLayout()
        self.db_combo = QComboBox()
        self.db_combo.currentIndexChanged.connect(self.onDatabaseChanged)
        db_layout.addWidget(QLabel('Select Database:'))
        db_layout.addWidget(self.db_combo)
        left_layout.addLayout(db_layout)

        # List box for tables/collections
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.onItemSelected)
        left_layout.addWidget(self.list_widget)

        # Buttons
        button_layout = QVBoxLayout()
        buttons = [
            ('Create Table', self.createTable),
            ('Upload CSV', self.uploadCSV),
            ('Download CSV', self.downloadCSV),
            ('Delete All', self.deleteAll),
            ('Display Structure', self.displayStructure),
            ('Custom Query', self.customQuery),
        ]
        for text, func in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            button_layout.addWidget(btn)
        left_layout.addLayout(button_layout)

        # Output area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        right_layout.addWidget(self.output)

        # Table for displaying contents
        self.table = QTableWidget()
        right_layout.addWidget(self.table)

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        self.setLayout(main_layout)

    def loadDatabases(self):
        config = configparser.ConfigParser()
        config.read('db2.ini')
        for section in config.sections():
            self.db_combo.addItem(section)

    def onDatabaseChanged(self, index):
        db_label = self.db_combo.currentText()
        config = configparser.ConfigParser()
        config.read('db2.ini')
        db_config = dict(config[db_label])
        db_type = db_config.pop('dbtype')

        if db_type == 'postgresql':
            self.current_manager = PostgreSQLManager(db_config)
        elif db_type == 'neo4j':
            self.current_manager = Neo4jManager(db_config)
        elif db_type == 'mongodb':
            self.current_manager = MongoDBManager(db_config)
        elif db_type == 'mysql':
            self.current_manager = MySQLManager(db_config)
        elif db_type == 'redis':
            self.current_manager = RedisManager(db_config)
        else:
            self.output.setText(f"Unsupported database type: {db_type}")
            return

        self.updateListWidget()

    def updateListWidget(self):
        self.list_widget.clear()
        try:
            if isinstance(self.current_manager, (PostgreSQLManager, MySQLManager)):
                items = self.current_manager.list_tables()
            elif isinstance(self.current_manager, Neo4jManager):
                items = self.current_manager.get_node_labels()
            elif isinstance(self.current_manager, MongoDBManager):
                items = self.current_manager.list_collections()
            elif isinstance(self.current_manager, RedisManager):
                items = self.current_manager.list_keys()
            else:
                items = []

            self.list_widget.addItems(items)
        except Exception as e:
            self.output.setText(f"An error occurred: {str(e)}")

    def onItemSelected(self, item):
        selected_item = item.text()
        try:
            if isinstance(self.current_manager, (PostgreSQLManager, MySQLManager)):
                columns = self.current_manager.get_table_columns(selected_item)
                data = self.current_manager.execute_query(f"SELECT * FROM {selected_item}", fetch=True)
            elif isinstance(self.current_manager, Neo4jManager):
                query = f"MATCH (n:{selected_item}) RETURN n"
                result = self.current_manager.execute_query(query)
                columns = list(result[0]['n'].keys()) if result else []
                data = [[node['n'][col] for col in columns] for node in result]
            elif isinstance(self.current_manager, MongoDBManager):
                documents = self.current_manager.find_documents(selected_item, {})
                columns = list(documents[0].keys()) if documents else []
                data = [[doc.get(col, '') for col in columns] for doc in documents]
            elif isinstance(self.current_manager, RedisManager):
                value = self.current_manager.get_value(selected_item)
                columns = ['Key', 'Value']
                data = [[selected_item, value]]
            else:
                columns = []
                data = []

            self.displayTableContents(columns, data)
        except Exception as e:
            self.output.setText(f"An error occurred: {str(e)}")

    def createTable(self):
        if not self.current_manager:
            self.output.setText("Please select a database first.")
            return

        try:
            if isinstance(self.current_manager, (PostgreSQLManager, MySQLManager)):
                table_name, ok = QInputDialog.getText(self, "Create Table", "Enter the new table name:")
                if ok:
                    columns, ok = QInputDialog.getText(self, "Create Table", "Enter column names (comma-separated):")
                    if ok:
                        self.current_manager.create_table(table_name, columns)
                        self.output.setText(f"Table '{table_name}' created.")
                        self.updateListWidget()
            elif isinstance(self.current_manager, Neo4jManager):
                label, ok = QInputDialog.getText(self, "Create Node", "Enter the node label:")
                if ok:
                    properties = {}
                    while True:
                        key, ok = QInputDialog.getText(self, "Add Property", "Enter property name (or cancel to finish):")
                        if not ok or not key:
                            break
                        value, ok = QInputDialog.getText(self, "Add Property", f"Enter value for {key}:")
                        if ok:
                            properties[key] = value
                    self.current_manager.create_node(label, properties)
                    self.output.setText(f"Node with label '{label}' created.")
                    self.updateListWidget()
            elif isinstance(self.current_manager, MongoDBManager):
                collection_name, ok = QInputDialog.getText(self, "Create Collection", "Enter the new collection name:")
                if ok:
                    self.current_manager.create_collection(collection_name)
                    self.output.setText(f"Collection '{collection_name}' created.")
                    self.updateListWidget()
            elif isinstance(self.current_manager, RedisManager):
                key, ok = QInputDialog.getText(self, "Set Key", "Enter the key:")
                if ok:
                    value, ok = QInputDialog.getText(self, "Set Key", "Enter the value:")
                    if ok:
                        self.current_manager.set_value(key, value)
                        self.output.setText(f"Key '{key}' set.")
                        self.updateListWidget()
        except Exception as e:
            self.output.setText(f"An error occurred: {str(e)}")

    def uploadCSV(self):
        if not self.current_manager:
            self.output.setText("Please select a database first.")
            return

        try:
            csv_file, ok = QInputDialog.getText(self, "Upload CSV", "Enter the CSV file name:")
            if ok:
                if isinstance(self.current_manager, (PostgreSQLManager, MySQLManager)):
                    self.current_manager.upload_csv_to_table(csv_file)
                    self.output.setText(f"CSV '{csv_file}' uploaded.")
                    self.updateListWidget()
                elif isinstance(self.current_manager, Neo4jManager):
                    self.current_manager.upload_csv_to_nodes(csv_file)
                    self.output.setText(f"CSV '{csv_file}' uploaded as nodes.")
                    self.updateListWidget()
                else:
                    self.output.setText("CSV upload not implemented for this database type.")
        except Exception as e:
            self.output.setText(f"An error occurred: {str(e)}")

    def downloadCSV(self):
        if not self.current_manager:
            self.output.setText("Please select a database first.")
            return

        try:
            selected_items = self.list_widget.selectedItems()
            if not selected_items:
                self.output.setText("Please select an item to download.")
                return

            selected_item = selected_items[0].text()

            if isinstance(self.current_manager, (PostgreSQLManager, MySQLManager)):
                self.current_manager.download_table_as_csv(selected_item)
                self.output.setText(f"Table '{selected_item}' downloaded as CSV.")
            elif isinstance(self.current_manager, Neo4jManager):
                self.current_manager.download_nodes_as_csv(selected_item)
                self.output.setText(f"Nodes with label '{selected_item}' downloaded as CSV.")
            else:
                self.output.setText("CSV download not implemented for this database type.")
        except Exception as e:
            self.output.setText(f"An error occurred: {str(e)}")

    def deleteAll(self):
        if not self.current_manager:
            self.output.setText("Please select a database first.")
            return

        reply = QMessageBox.question(self, 'Delete All', 'Are you sure you want to delete all data?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                if isinstance(self.current_manager, (PostgreSQLManager, MySQLManager)):
                    self.current_manager.delete_all_tables()
                elif isinstance(self.current_manager, Neo4jManager):
                    self.current_manager.delete_all_nodes()
                elif isinstance(self.current_manager, MongoDBManager):
                    for collection in self.current_manager.list_collections():
                        self.current_manager.drop_collection(collection)
                elif isinstance(self.current_manager, RedisManager):
                    self.current_manager.flush_all()
                self.output.setText("All data has been deleted.")
                self.updateListWidget()
            except Exception as e:
                self.output.setText(f"An error occurred: {str(e)}")

    def displayStructure(self):
        if not self.current_manager:
            self.output.setText("Please select a database first.")
            return

        try:
            selected_items = self.list_widget.selectedItems()
            if not selected_items:
                self.output.setText("Please select an item to display its structure.")
                return

            selected_item = selected_items[0].text()

            if isinstance(self.current_manager, (PostgreSQLManager, MySQLManager)):
                structure = self.current_manager.display_table_structure(selected_item)
                self.output.setText(structure)
            elif isinstance(self.current_manager, Neo4jManager):
                structure = self.current_manager.display_node_structure(selected_item)
                self.output.setText(structure)
            elif isinstance(self.current_manager, MongoDBManager):
                documents = self.current_manager.find_documents(selected_item, {})
                if documents:
                    structure = f"Structure of collection '{selected_item}':\n"
                    structure += "\n".join(documents[0].keys())
                    self.output.setText(structure)
                else:
                    self.output.setText(f"No documents found in collection '{selected_item}'")
            elif isinstance(self.current_manager, RedisManager):
                self.output.setText("Structure display not applicable for Redis")
        except Exception as e:
            self.output.setText(f"An error occurred: {str(e)}")

    def customQuery(self):
        if not self.current_manager:
            self.output.setText("Please select a database first.")
            return

        query, ok = QInputDialog.getText(self, "Custom Query", "Enter your query:")
        if ok:
            try:
                if isinstance(self.current_manager, (PostgreSQLManager, MySQLManager, Neo4jManager)):
                    result = self.current_manager.execute_custom_query(query)
                    self.output.setText(str(result))
                elif isinstance(self.current_manager, RedisManager):
                    value = self.current_manager.get_value(query)
                    if value:
                        self.output.setText(f"Value for key '{query}': {value}")
                    else:
                        self.output.setText(f"No value found for key '{query}'")
                else:
                    self.output.setText("Custom queries not implemented for this database type")
            except Exception as e:
                self.output.setText(f"An error occurred: {str(e)}")

    def displayTableContents(self, columns, data):
        self.table.clear()
        self.table.setColumnCount(len(columns))
        self.table.setRowCount(len(data))
        self.table.setHorizontalHeaderLabels(columns)

        for row, record in enumerate(data):
            for col, value in enumerate(record):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DatabaseManagerGUI()
    ex.show()
    sys.exit(app.exec_())