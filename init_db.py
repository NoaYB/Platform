import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_db():
    # Connect to default 'postgres' db to create new db
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="password",  # Try default, might fail
            host="localhost",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if db exists
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'fiverr'")
        exists = cur.fetchone()
        
        if not exists:
            print("Creating database 'fiverr'...")
            cur.execute("CREATE DATABASE fiverr")
            print("Database 'fiverr' created successfully!")
        else:
            print("Database 'fiverr' already exists.")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error checking/creating database: {e}")
        print("Tip: If password failed, update it in the script or connection string.")

if __name__ == "__main__":
    init_db()
