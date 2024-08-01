from flask import Flask, jsonify, request
import psycopg2
from psycopg2 import sql  # Add this line
import pymongo
from neo4j import GraphDatabase
import configparser
import pandas as pd
import io
import traceback
import logging
import pymongo
from pymongo.errors import ConnectionFailure

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load database configurations
config = configparser.ConfigParser()
config.read('db.ini')

# Database connections
pg_conn = None
mongo_client = None
neo4j_driver = None

# Helper functions for database connections
def connect_postgresql():
    global pg_conn
    try:
        pg_conn = psycopg2.connect(
            host=config['postgresql']['host'],
            port=config['postgresql']['port'],
            database=config['postgresql']['database'],
            user=config['postgresql']['user'],
            password=config['postgresql']['password']
        )
        return True
    except Exception as e:
        logger.error(f"PostgreSQL connection error: {str(e)}")
        logger.debug(traceback.format_exc())
        return str(e)


def connect_mongodb():
    global mongo_client
    try:
        connection_string = f"mongodb+srv://{config['mongodb']['user']}:{config['mongodb']['password']}@{config['mongodb']['host']}/{config['mongodb']['database']}?retryWrites=true&w=majority"
        mongo_client = pymongo.MongoClient(connection_string)
        # Ping the server to check if the connection is successful
        mongo_client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        return True
    except ConnectionFailure as e:
        logger.error(f"MongoDB connection error: {str(e)}")
        logger.debug(traceback.format_exc())
        return str(e)
    

def connect_neo4j():
    global neo4j_driver
    try:
        neo4j_driver = GraphDatabase.driver(
            config['neo4j']['url'],
            auth=(config['neo4j']['user'], config['neo4j']['password'])
        )
        return True
    except Exception as e:
        logger.error(f"Neo4j connection error: {str(e)}")
        logger.debug(traceback.format_exc())
        return str(e)

# PostgreSQL Routes


def get_table_name_with_correct_case(cur, table_name):
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND lower(table_name) = lower(%s)
    """, (table_name,))
    result = cur.fetchone()
    return result[0] if result else None

@app.route('/PostgreSQL')
def postgresql_data():
    if not pg_conn:
        error = connect_postgresql()
        if error is not True:
            return jsonify({"error": f"Failed to connect to PostgreSQL: {error}"})

    try:
        with pg_conn.cursor() as cur:
            # Get table list
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = [table[0] for table in cur.fetchall()]

            # Get contents of the first table
            if tables:
                table_name = get_table_name_with_correct_case(cur, tables[0])
                if table_name:
                    query = sql.SQL("SELECT * FROM {} LIMIT 100").format(sql.Identifier(table_name))
                    cur.execute(query)
                    columns = [desc[0] for desc in cur.description]
                    rows = cur.fetchall()
                    first_table_data = [dict(zip(columns, row)) for row in rows]
                else:
                    first_table_data = []
            else:
                first_table_data = []

        return jsonify({
            "tables": tables,
            "first_table_data": first_table_data
        })
    except Exception as e:
        logger.error(f"Error in postgresql_data: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()})

@app.route('/PostgreSQL/<table_name>')
def postgresql_table_data(table_name):
    if not pg_conn:
        error = connect_postgresql()
        if error is not True:
            return jsonify({"error": f"Failed to connect to PostgreSQL: {error}"})

    try:
        with pg_conn.cursor() as cur:
            correct_table_name = get_table_name_with_correct_case(cur, table_name)
            if not correct_table_name:
                return jsonify({"error": f"Table '{table_name}' not found"})

            query = sql.SQL("SELECT * FROM {} LIMIT 100").format(sql.Identifier(correct_table_name))
            cur.execute(query)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
            table_data = [dict(zip(columns, row)) for row in rows]

        return jsonify({
            "table_name": correct_table_name,
            "table_data": table_data
        })
    except Exception as e:
        logger.error(f"Error in postgresql_table_data: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()})
    
    
@app.route('/PostgreSQL/upload', methods=['POST'])
def postgresql_upload():
    if not pg_conn:
        error = connect_postgresql()
        if error is not True:
            return jsonify({"error": f"Failed to connect to PostgreSQL: {error}"})

    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file:
        try:
            # Read CSV file
            df = pd.read_csv(file)
            table_name = file.filename.rsplit('.', 1)[0]

            # Create table
            with pg_conn.cursor() as cur:
                columns = [f"{col} TEXT" for col in df.columns]
                create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
                cur.execute(create_table_query)

                # Insert data
                for _, row in df.iterrows():
                    insert_query = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({', '.join(['%s']*len(df.columns))})"
                    cur.execute(insert_query, tuple(row))

            pg_conn.commit()
            return jsonify({"message": f"Table {table_name} created and data uploaded successfully"})
        except Exception as e:
            logger.error(f"Error in postgresql_upload: {str(e)}")
            logger.debug(traceback.format_exc())
            return jsonify({"error": str(e), "trace": traceback.format_exc()})

# MongoDB Routes

@app.route('/MongoDB')
def mongodb_data():
    if not mongo_client:
        error = connect_mongodb()
        if error is not True:
            return jsonify({"error": f"Failed to connect to MongoDB: {error}"})

    try:
        db = mongo_client[config['mongodb']['database']]
        collections = db.list_collection_names()

        first_collection_data = []
        if collections:
            first_collection = db[collections[0]]
            first_collection_data = list(first_collection.find({}).limit(100))
            # Convert ObjectId to string for JSON serialization
            for doc in first_collection_data:
                doc['_id'] = str(doc['_id'])

        return jsonify({
            "collections": collections,
            "first_collection_data": first_collection_data
        })
    except Exception as e:
        logger.error(f"Error in mongodb_data: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()})

@app.route('/MongoDB/<collection_name>')
def mongodb_collection_data(collection_name):
    if not mongo_client:
        error = connect_mongodb()
        if error is not True:
            return jsonify({"error": f"Failed to connect to MongoDB: {error}"})

    try:
        db = mongo_client[config['mongodb']['database']]
        collection = db[collection_name]
        collection_data = list(collection.find({}).limit(100))
        
        # Convert ObjectId to string for JSON serialization
        for doc in collection_data:
            doc['_id'] = str(doc['_id'])

        return jsonify({
            "collection_name": collection_name,
            "collection_data": collection_data
        })
    except Exception as e:
        logger.error(f"Error in mongodb_collection_data: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()})

@app.route('/MongoDB/upload', methods=['POST'])
def mongodb_upload():
    if not mongo_client:
        error = connect_mongodb()
        if error is not True:
            return jsonify({"error": f"Failed to connect to MongoDB: {error}"})

    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file:
        try:
            # Read CSV file
            df = pd.read_csv(file)
            collection_name = file.filename.rsplit('.', 1)[0]

            db = mongo_client[config['mongodb']['database']]
            collection = db[collection_name]

            # Insert data
            records = df.to_dict('records')
            collection.insert_many(records)

            return jsonify({"message": f"Collection {collection_name} created and data uploaded successfully"})
        except Exception as e:
            logger.error(f"Error in mongodb_upload: {str(e)}")
            logger.debug(traceback.format_exc())
            return jsonify({"error": str(e), "trace": traceback.format_exc()})

# Neo4j Routes

@app.route('/Neo4j')
def neo4j_data():
    if not neo4j_driver:
        error = connect_neo4j()
        if error is not True:
            return jsonify({"error": f"Failed to connect to Neo4j: {error}"})

    try:
        with neo4j_driver.session() as session:
            # Get labels
            result = session.run("CALL db.labels()")
            labels = [record["label"] for record in result]

            # Get nodes of the first label
            first_label_data = []
            if labels:
                result = session.run(f"MATCH (n:`{labels[0]}`) RETURN n LIMIT 100")
                first_label_data = [dict(record["n"].items()) for record in result]

        return jsonify({
            "labels": labels,
            "first_label_data": first_label_data
        })
    except Exception as e:
        logger.error(f"Error in neo4j_data: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()})

@app.route('/Neo4j/<label>')
def neo4j_label_data(label):
    if not neo4j_driver:
        error = connect_neo4j()
        if error is not True:
            return jsonify({"error": f"Failed to connect to Neo4j: {error}"})

    try:
        with neo4j_driver.session() as session:
            result = session.run(f"MATCH (n:`{label}`) RETURN n LIMIT 100")
            label_data = [dict(record["n"].items()) for record in result]

        return jsonify({
            "label": label,
            "label_data": label_data
        })
    except Exception as e:
        logger.error(f"Error in neo4j_label_data: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()})

@app.route('/Neo4j/upload', methods=['POST'])
def neo4j_upload():
    if not neo4j_driver:
        error = connect_neo4j()
        if error is not True:
            return jsonify({"error": f"Failed to connect to Neo4j: {error}"})

    if 'file' not in request.files:
        return jsonify({"error": "No file part"})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})

    if file:
        try:
            # Read CSV file
            df = pd.read_csv(file)
            label = file.filename.rsplit('.', 1)[0]

            with neo4j_driver.session() as session:
                for _, row in df.iterrows():
                    properties = ", ".join([f"{k}: ${k}" for k in row.index])
                    query = f"CREATE (n:`{label}` {{{properties}}})"
                    session.run(query, dict(row))

            return jsonify({"message": f"Nodes with label {label} created and data uploaded successfully"})
        except Exception as e:
            logger.error(f"Error in neo4j_upload: {str(e)}")
            logger.debug(traceback.format_exc())
            return jsonify({"error": str(e), "trace": traceback.format_exc()})

# Migrate Routes

@app.route('/Migrate/<src>/<src_table>/<tar>/<tar_table>')
def migrate_table(src, src_table, tar, tar_table):
    try:
        # Implement migration logic here
        # This is a placeholder implementation
        return jsonify({
            "message": f"Migration from {src}.{src_table} to {tar}.{tar_table} completed successfully",
            "source": f"{src}.{src_table}",
            "target": f"{tar}.{tar_table}",
            "rows_migrated": 0  # Replace with actual count
        })
    except Exception as e:
        logger.error(f"Error in migrate_table: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()})

@app.route('/Migrate/all/<src>/<tar>')
def migrate_all(src, tar):
    try:
        # Implement migration logic here for all tables/collections/labels
        # This is a placeholder implementation
        return jsonify({
            "message": f"Migration of all data from {src} to {tar} completed successfully",
            "source": src,
            "target": tar,
            "tables_migrated": []  # Replace with actual list of migrated tables
        })
    except Exception as e:
        logger.error(f"Error in migrate_all: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()})

@app.route('/Relate')
def relate():
    # Implement relation logic here
    try:
        # Placeholder implementation
        return jsonify({"message": "Relate functionality not implemented yet"})
    except Exception as e:
        logger.error(f"Error in relate: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()})

@app.route('/Join')
def join():
    # Implement join logic here
    try:
        # Placeholder implementation
        return jsonify({"message": "Join functionality not implemented yet"})
    except Exception as e:
        logger.error(f"Error in join: {str(e)}")
        logger.debug(traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()})

    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
