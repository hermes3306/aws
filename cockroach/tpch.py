import psycopg2
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
from datetime import datetime, timedelta

# Connection parameters - adjust these as needed
postgres_params = {
    'dbname': 'tpch',  # Connect to default database first
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

cockroach_params = {
    'dbname': 'postgres',  # Connect to default database first
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'port': '26257'
}

# Database and table creation statements
create_db_stmt = "CREATE DATABASE IF NOT EXISTS tpch;"


create_table_stmts = [
    """
    CREATE TABLE IF NOT EXISTS lineitem (
        l_orderkey INTEGER NOT NULL,
        l_partkey INTEGER NOT NULL,
        l_suppkey INTEGER NOT NULL,
        l_linenumber INTEGER NOT NULL,
        l_quantity DECIMAL(15,2) NOT NULL,
        l_extendedprice DECIMAL(15,2) NOT NULL,
        l_discount DECIMAL(15,2) NOT NULL,
        l_tax DECIMAL(15,2) NOT NULL,
        l_returnflag CHAR(1) NOT NULL,
        l_linestatus CHAR(1) NOT NULL,
        l_shipdate DATE NOT NULL,
        l_commitdate DATE NOT NULL,
        l_receiptdate DATE NOT NULL,
        l_shipinstruct CHAR(25) NOT NULL,
        l_shipmode CHAR(10) NOT NULL,
        l_comment VARCHAR(44) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS orders (
        o_orderkey INTEGER NOT NULL,
        o_custkey INTEGER NOT NULL,
        o_orderstatus CHAR(1) NOT NULL,
        o_totalprice DECIMAL(15,2) NOT NULL,
        o_orderdate DATE NOT NULL,
        o_orderpriority CHAR(15) NOT NULL,
        o_clerk CHAR(15) NOT NULL,
        o_shippriority INTEGER NOT NULL,
        o_comment VARCHAR(79) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS customer (
        c_custkey INTEGER NOT NULL,
        c_name VARCHAR(25) NOT NULL,
        c_address VARCHAR(40) NOT NULL,
        c_nationkey INTEGER NOT NULL,
        c_phone CHAR(15) NOT NULL,
        c_acctbal DECIMAL(15,2) NOT NULL,
        c_mktsegment CHAR(10) NOT NULL,
        c_comment VARCHAR(117) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS part (
        p_partkey INTEGER NOT NULL,
        p_name VARCHAR(55) NOT NULL,
        p_mfgr CHAR(25) NOT NULL,
        p_brand CHAR(10) NOT NULL,
        p_type VARCHAR(25) NOT NULL,
        p_size INTEGER NOT NULL,
        p_container CHAR(10) NOT NULL,
        p_retailprice DECIMAL(15,2) NOT NULL,
        p_comment VARCHAR(23) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS supplier (
        s_suppkey INTEGER NOT NULL,
        s_name CHAR(25) NOT NULL,
        s_address VARCHAR(40) NOT NULL,
        s_nationkey INTEGER NOT NULL,
        s_phone CHAR(15) NOT NULL,
        s_acctbal DECIMAL(15,2) NOT NULL,
        s_comment VARCHAR(101) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS partsupp (
        ps_partkey INTEGER NOT NULL,
        ps_suppkey INTEGER NOT NULL,
        ps_availqty INTEGER NOT NULL,
        ps_supplycost DECIMAL(15,2) NOT NULL,
        ps_comment VARCHAR(199) NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS nation (
        n_nationkey INTEGER NOT NULL,
        n_name CHAR(25) NOT NULL,
        n_regionkey INTEGER NOT NULL,
        n_comment VARCHAR(152)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS region (
        r_regionkey INTEGER NOT NULL,
        r_name CHAR(25) NOT NULL,
        r_comment VARCHAR(152)
    )
    """
]


# Simplified TPC-H-like queries
queries = [
    """
    SELECT l_returnflag, l_linestatus, 
           SUM(l_quantity) AS sum_qty,
           SUM(l_extendedprice) AS sum_base_price,
           SUM(l_extendedprice * (1 - l_discount)) AS sum_disc_price,
           SUM(l_extendedprice * (1 - l_discount) * (1 + l_tax)) AS sum_charge,
           AVG(l_quantity) AS avg_qty,
           AVG(l_extendedprice) AS avg_price,
           AVG(l_discount) AS avg_disc,
           COUNT(*) AS count_order
    FROM lineitem
    WHERE l_shipdate <= DATE '1998-12-01' - INTERVAL '90 day'
    GROUP BY l_returnflag, l_linestatus
    ORDER BY l_returnflag, l_linestatus
    """
    # Other queries remain the same as in the previous version
]

def populate_tables(conn):
    with conn.cursor() as cur:
        # Populate region
        regions = ['AFRICA', 'AMERICA', 'ASIA', 'EUROPE', 'MIDDLE EAST']
        for i, region in enumerate(regions):
            cur.execute("INSERT INTO region (r_regionkey, r_name, r_comment) VALUES (%s, %s, %s)", 
                        (i, region, 'Sample comment for ' + region))

        # Populate nation
        nations = [('ALGERIA', 0), ('ARGENTINA', 1), ('BRAZIL', 1), ('CANADA', 1), ('EGYPT', 0),
                   ('ETHIOPIA', 0), ('FRANCE', 3), ('GERMANY', 3), ('INDIA', 2), ('INDONESIA', 2)]
        for i, (nation, region_key) in enumerate(nations):
            cur.execute("INSERT INTO nation (n_nationkey, n_name, n_regionkey, n_comment) VALUES (%s, %s, %s, %s)", 
                        (i, nation, region_key, 'Sample comment for ' + nation))

        # Populate customer (10 sample customers)
        for i in range(10):
            cur.execute("INSERT INTO customer (c_custkey, c_name, c_address, c_nationkey, c_phone, c_acctbal, c_mktsegment, c_comment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                        (i, f'Customer{i}', f'Address{i}', random.randint(0, 9), '123-456-7890', random.uniform(0, 10000), 'SEGMENT', 'Sample comment'))

        # Populate supplier (5 sample suppliers)
        for i in range(5):
            cur.execute("INSERT INTO supplier (s_suppkey, s_name, s_address, s_nationkey, s_phone, s_acctbal, s_comment) VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                        (i, f'Supplier{i}', f'Address{i}', random.randint(0, 9), '987-654-3210', random.uniform(0, 10000), 'Sample comment'))

        # Populate part (20 sample parts)
        for i in range(20):
            cur.execute("INSERT INTO part (p_partkey, p_name, p_mfgr, p_brand, p_type, p_size, p_container, p_retailprice, p_comment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                        (i, f'Part{i}', 'Manufacturer', 'Brand', 'Type', random.randint(1, 50), 'Container', random.uniform(10, 1000), 'Sample comment'))

        # Populate partsupp
        for i in range(20):  # for each part
            for j in range(5):  # for each supplier
                cur.execute("INSERT INTO partsupp (ps_partkey, ps_suppkey, ps_availqty, ps_supplycost, ps_comment) VALUES (%s, %s, %s, %s, %s)", 
                            (i, j, random.randint(1, 1000), random.uniform(1, 1000), 'Sample comment'))

        # Populate orders (15 sample orders)
        for i in range(15):
            cur.execute("INSERT INTO orders (o_orderkey, o_custkey, o_orderstatus, o_totalprice, o_orderdate, o_orderpriority, o_clerk, o_shippriority, o_comment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                        (i, random.randint(0, 9), 'O', random.uniform(1000, 10000), datetime.now() - timedelta(days=random.randint(0, 365)), '1-URGENT', 'Clerk', 0, 'Sample comment'))

        # Populate lineitem (multiple items for each order)
        for i in range(15):  # for each order
            for j in range(random.randint(1, 5)):  # 1-5 items per order
                cur.execute("INSERT INTO lineitem (l_orderkey, l_partkey, l_suppkey, l_linenumber, l_quantity, l_extendedprice, l_discount, l_tax, l_returnflag, l_linestatus, l_shipdate, l_commitdate, l_receiptdate, l_shipinstruct, l_shipmode, l_comment) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", 
                            (i, random.randint(0, 19), random.randint(0, 4), j, random.randint(1, 50), random.uniform(100, 1000), random.uniform(0, 0.1), random.uniform(0, 0.1), 'N', 'O', datetime.now() + timedelta(days=random.randint(1, 30)), datetime.now() + timedelta(days=random.randint(31, 60)), datetime.now() + timedelta(days=random.randint(61, 90)), 'DELIVER IN PERSON', 'TRUCK', 'Sample comment'))

    conn.commit()

def create_database_and_tables(conn_params, db_name):
    try:
        # Connect to the default database
        with psycopg2.connect(**conn_params) as conn:
            conn.set_session(autocommit=True)
            with conn.cursor() as cur:
                if db_name == "PostgreSQL":
                    # For PostgreSQL, first check if the database exists
                    cur.execute("SELECT 1 FROM pg_database WHERE datname = 'tpch'")
                    exists = cur.fetchone()
                    if not exists:
                        cur.execute("CREATE DATABASE tpch")
                else:
                    # For CockroachDB, use the original statement
                    cur.execute(create_db_stmt)
        
        # Update connection parameters to connect to the tpch database
        conn_params['dbname'] = 'tpch'
        
        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor() as cur:
                for stmt in create_table_stmts:
                    cur.execute(stmt)
            conn.commit()
            
            # Populate tables with sample data
            populate_tables(conn)
        
        print(f"Database and tables created and populated successfully for {db_name}")
    except psycopg2.Error as e:
        print(f"Error creating database and tables for {db_name}: {e}")


def run_query(conn, query):
    start_time = time.time()
    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()
    end_time = time.time()
    return end_time - start_time
def benchmark_database(db_params, db_name):
    try:
        create_database_and_tables(db_params, db_name)
        
        # Update connection parameters to use the tpch database
        db_params['dbname'] = 'tpch'
        
        with psycopg2.connect(**db_params) as conn:
            conn.set_client_encoding('UTF8')  # Set client encoding to UTF-8
            print(f"Connected to {db_name}")
            results = []
            for i, query in enumerate(queries):
                try:
                    query_time = run_query(conn, query)
                    results.append((i+1, query_time))
                    print(f"{db_name} - Query {i+1} execution time: {query_time:.4f} seconds")
                except psycopg2.Error as e:
                    print(f"Error executing query {i+1} on {db_name}: {e}")
            return results
    except psycopg2.Error as e:
        print(f"Error connecting to {db_name}: {e}")
        return []

def run_benchmarks():
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_to_db = {
            executor.submit(benchmark_database, postgres_params, "PostgreSQL"): "PostgreSQL",
            executor.submit(benchmark_database, cockroach_params, "CockroachDB"): "CockroachDB"
        }

        results = {}
        for future in as_completed(future_to_db):
            db = future_to_db[future]
            try:
                results[db] = future.result()
            except Exception as e:
                print(f"{db} generated an exception: {e}")

    return results

def print_results(results):
    print("\nBenchmark Results:")
    print("------------------")
    for db, queries in results.items():
        print(f"\n{db}:")
        for query_num, time in queries:
            print(f"  Query {query_num}: {time:.4f} seconds")

if __name__ == "__main__":
    results = run_benchmarks()
    print_results(results)