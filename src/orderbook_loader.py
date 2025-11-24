import os
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import MetaTrader5 as mt5
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_batch

def _env(k, d=None):
    v = os.getenv(k)
    return v if v is not None and v != "" else d

def _side(t):
    return "bid" if t == 1 else "ask" if t == 2 else "unk"

def _digest(items):
    return hash(tuple((it.type, it.price, it.volume) for it in items)) if items else None

def _prepare_orderbook_data(symbol, tzname, items, timestamp):
    """Prepare orderbook data for PostgreSQL insertion"""
    records = []
    for idx, it in enumerate(items):
        side = _side(it.type)
        record = (
            symbol,
            side,
            idx,
            it.type,
            float(it.price),
            int(it.volume),
            float(it.volume_dbl),
            timestamp,
            tzname
        )
        records.append(record)
    return records

def main():
    load_dotenv()
    symbol = _env("SYMBOL", "EURUSD")
    tzname = _env("TIMEZONE", "Asia/Nicosia")
    tz = ZoneInfo(tzname)
    # PostgreSQL/TimescaleDB connection settings
    db_host = _env("DB_HOST", "localhost")
    db_port = _env("DB_PORT", "5432")
    db_name = _env("DB_NAME", "mt5_orderbook")
    db_user = _env("DB_USER", "mt5_user")
    db_password = _env("DB_PASSWORD", "mt5_password")
    
    poll_ms = int(_env("POLL_INTERVAL_MS", "50"))
    batch_size = int(_env("WRITE_BATCH_SIZE", "500"))
    mt5_path = _env("MT5_TERMINAL_PATH")
    login = _env("MT5_LOGIN")
    password = _env("MT5_PASSWORD")
    server = _env("MT5_SERVER")

    # Initialize MT5 - use path if provided, otherwise use default initialization
    if mt5_path:
        # Remove quotes if present and handle path formatting
        mt5_path = mt5_path.strip('"')
        print(f"Initializing MT5 with terminal path: {mt5_path}")
        if not mt5.initialize(path=mt5_path):
            print(f"MetaTrader5 initialize with path failed: {mt5.last_error()}")
            sys.exit(1)
    else:
        print("Initializing MT5 with default path (no MT5_TERMINAL_PATH provided)")
        if not mt5.initialize():
            print(f"MetaTrader5 initialize failed: {mt5.last_error()}")
            sys.exit(1)
    
    # Only attempt login if all credentials are provided
    if login and password and server:
        print(f"Attempting login with credentials for server: {server}")
        if not mt5.login(int(login), password=password, server=server):
            print(f"MetaTrader5 login failed: {mt5.last_error()}")
            print("Continuing with default initialization (assuming MT5 is already logged in)")
    else:
        print("No MT5 credentials provided - using default initialization")
        print("Ensure MetaTrader 5 is already running and logged in")
    
    if not mt5.market_book_add(symbol):
        print(f"Market book add failed: {mt5.last_error()}")
        sys.exit(1)

    # Connect to PostgreSQL/TimescaleDB
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        conn.autocommit = False
        cursor = conn.cursor()
        
        # Verify the orderbook_data table exists (should be created by create_tables.py)
        cursor.execute("SELECT to_regclass('orderbook_data')")
        table_exists = cursor.fetchone()[0]
        if not table_exists:
            print("Error: orderbook_data table does not exist. Please run create_tables.py first.")
            sys.exit(1)
        
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        sys.exit(1)

    prev = None
    insert_sql = """
    INSERT INTO orderbook_data (symbol, side, level, order_type, price, volume, volume_dbl, timestamp, timezone)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        while True:
            items = mt5.market_book_get(symbol)
            if not items:
                time.sleep(poll_ms / 1000.0)
                continue
            now = datetime.now(tz)
            dg = _digest(items)
            if dg != prev:
                records = _prepare_orderbook_data(symbol, tzname, items, now)
                execute_batch(cursor, insert_sql, records, page_size=batch_size)
                conn.commit()
                print(f"Inserted {len(records)} orderbook records at {now}")
                prev = dg
            time.sleep(poll_ms / 1000.0)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            mt5.market_book_release(symbol)
        except Exception:
            pass
        mt5.shutdown()
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
