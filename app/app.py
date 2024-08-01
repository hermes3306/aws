from flask import Flask, jsonify
import psycopg2
from psycopg2 import sql
import configparser
from flask_cors import CORS
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)
CORS(app)

def get_db_connection():
    config = configparser.ConfigParser()
    config.read('db.ini')
    print(config)
    
    conn = psycopg2.connect(
        host=config['postgresql']['host'],
        port=config['postgresql']['port'],
        database=config['postgresql']['database'],
        user=config['postgresql']['user'],
        password=config['postgresql']['password']
    )
    return conn

@app.route('/')
def index():
    return send_from_directory('.', 'index.htm')

@app.route('/table')
def get_tables():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = [table[0] for table in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(tables)

@app.route('/table/<table_name>')
def get_table_info(table_name):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Check if the table exists
    cur.execute("SELECT to_regclass(%s)", (table_name,))
    if cur.fetchone()[0] is None:
        cur.close()
        conn.close()
        return jsonify({"error": f"Table '{table_name}' does not exist"}), 404

    # Get table schema
    cur.execute(sql.SQL("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s"), (table_name,))
    schema = [{"column_name": col[0], "data_type": col[1]} for col in cur.fetchall()]
    
    # Get table content
    try:
        cur.execute(sql.SQL("SELECT * FROM {} LIMIT 10").format(sql.Identifier(table_name)))
        content = [list(row) for row in cur.fetchall()]
    except psycopg2.Error as e:
        cur.close()
        conn.close()
        return jsonify({"error": f"Error querying table: {str(e)}"}), 500
    
    cur.close()
    conn.close()
    
    return jsonify({
        "table_name": table_name,
        "schema": schema,
        "content": content
    })

@app.route('/schema')
def get_all_schemas():
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get all table names
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [table[0] for table in cur.fetchall()]
        
        schemas = {}
        for table in tables:
            # Get schema for each table
            cur.execute(sql.SQL("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s"), (table,))
            schema = [{"column_name": col[0], "data_type": col[1]} for col in cur.fetchall()]
            schemas[table] = schema
        
        cur.close()
        conn.close()
        
        return jsonify(schemas)
    except psycopg2.Error as e:
        cur.close()
        conn.close()
        return jsonify({"error": f"Error fetching schemas: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
