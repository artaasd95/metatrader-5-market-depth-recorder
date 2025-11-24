import psycopg2
from dotenv import load_dotenv
import os

def _env(k, d=None):
    v = os.getenv(k)
    return v if v is not None and v != "" else d

def create_orderbook_table():
    """Create the orderbook_data table and TimescaleDB hypertable"""
    load_dotenv()
    
    # PostgreSQL/TimescaleDB connection settings
    db_host = _env("DB_HOST", "localhost")
    db_port = _env("DB_PORT", "5432")
    db_name = _env("DB_NAME", "mt5_orderbook")
    db_user = _env("DB_USER", "mt5_user")
    db_password = _env("DB_PASSWORD", "mt5_password")
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        conn.autocommit = False
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        
        # Create table if it doesn't exist (without primary key for TimescaleDB compatibility)
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS orderbook_data (
            id SERIAL,
            symbol VARCHAR(10) NOT NULL,
            side VARCHAR(4) NOT NULL,
            level INTEGER NOT NULL,
            order_type INTEGER NOT NULL,
            price DOUBLE PRECISION NOT NULL,
            volume INTEGER NOT NULL,
            volume_dbl DOUBLE PRECISION NOT NULL,
            timestamp TIMESTAMPTZ NOT NULL,
            timezone VARCHAR(50) NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        
        cursor.execute(create_table_sql)
        print("✅ orderbook_data table created")
        
        # Create hypertable
        cursor.execute("SELECT create_hypertable('orderbook_data', 'timestamp', if_not_exists => TRUE)")
        conn.commit()
        print("✅ TimescaleDB hypertable created")
        
        # Verify table creation
        cursor.execute("SELECT to_regclass('public.orderbook_data')")
        result = cursor.fetchone()
        print(f"✅ Table verification: {result[0] is not None}")
        
        cursor.close()
        conn.close()
        print("✅ Database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        raise

if __name__ == "__main__":
    create_orderbook_table()