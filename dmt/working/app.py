from flask import Flask, render_template_string
import psycopg2
import configparser

app = Flask(__name__)

def get_db_connection():
    config = configparser.ConfigParser()
    config.read('db.ini')
    
    conn = psycopg2.connect(
        host=config['postgresql']['host'],
        port=config['postgresql']['port'],
        database=config['postgresql']['database'],
        user=config['postgresql']['user'],
        password=config['postgresql']['password']
    )
    return conn

@app.route('/')
def home():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cur.fetchall()
    cur.close()
    conn.close()
    
    html = """
    <h1>Database Tables</h1>
    <ul>
    {% for table in tables %}
        <li><a href="{{ url_for('table_content', table_name=table[0]) }}">{{ table[0] }}</a></li>
    {% endfor %}
    </ul>
    """
    return render_template_string(html, tables=tables)

@app.route('/table/<table_name>')
def table_content(table_name):
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get table schema
    cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}'")
    schema = cur.fetchall()
    
    # Get table content
    cur.execute(f"SELECT * FROM {table_name} LIMIT 10")
    content = cur.fetchall()
    
    cur.close()
    conn.close()
    
    html = """
    <h1>Table: {{ table_name }}</h1>
    <h2>Schema:</h2>
    <table border="1">
        <tr><th>Column Name</th><th>Data Type</th></tr>
        {% for column in schema %}
            <tr><td>{{ column[0] }}</td><td>{{ column[1] }}</td></tr>
        {% endfor %}
    </table>
    <h2>Content (First 10 rows):</h2>
    <table border="1">
        <tr>
        {% for column in schema %}
            <th>{{ column[0] }}</th>
        {% endfor %}
        </tr>
        {% for row in content %}
            <tr>
            {% for cell in row %}
                <td>{{ cell }}</td>
            {% endfor %}
            </tr>
        {% endfor %}
    </table>
    <p><a href="{{ url_for('home') }}">Back to table list</a></p>
    """
    return render_template_string(html, table_name=table_name, schema=schema, content=content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
