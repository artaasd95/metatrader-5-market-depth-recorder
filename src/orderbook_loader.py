import os
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo
import MetaTrader5 as mt5
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, WriteOptions

def _env(k, d=None):
    v = os.getenv(k)
    return v if v is not None and v != "" else d

def _side(t):
    return "bid" if t == 1 else "ask" if t == 2 else "unk"

def _digest(items):
    return hash(tuple((it.type, it.price, it.volume) for it in items)) if items else None

def _lines(symbol, tzname, items, ts_ns):
    tz_tag = tzname.replace(" ", "_")
    lines = []
    for idx, it in enumerate(items):
        side = _side(it.type)
        tag = f"orderbook,symbol={symbol},side={side},timezone={tz_tag}"
        fields = []
        fields.append(f"level={idx}i")
        fields.append(f"type={it.type}i")
        fields.append(f"price={format(it.price, 'f')}")
        fields.append(f"volume={it.volume}i")
        fields.append(f"volume_dbl={format(it.volume_dbl, 'f')}")
        line = tag + " " + ",".join(fields) + f" {ts_ns}"
        lines.append(line)
    return lines

def main():
    load_dotenv()
    symbol = _env("SYMBOL", "EURUSD")
    tzname = _env("TIMEZONE", "Asia/Nicosia")
    tz = ZoneInfo(tzname)
    url = _env("INFLUX_URL", "http://localhost:8086")
    token = _env("INFLUX_TOKEN")
    org = _env("INFLUX_ORG")
    bucket = _env("INFLUX_BUCKET")
    poll_ms = int(_env("POLL_INTERVAL_MS", "50"))
    batch_size = int(_env("WRITE_BATCH_SIZE", "500"))
    flush_ms = int(_env("WRITE_FLUSH_INTERVAL_MS", "250"))
    mt5_path = _env("MT5_TERMINAL_PATH")
    login = _env("MT5_LOGIN")
    password = _env("MT5_PASSWORD")
    server = _env("MT5_SERVER")

    if not token or not org:
        print("Missing INFLUX_TOKEN or INFLUX_ORG")
        sys.exit(1)
    if not bucket:
        bucket = f"orderbook_{symbol}"

    # Initialize MT5 - use path if provided, otherwise use default initialization
    if mt5_path:
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

    client = InfluxDBClient(url=url, token=token, org=org)
    write_api = client.write_api(write_options=WriteOptions(batch_size=batch_size, flush_interval=flush_ms, jitter_interval=0, retry_interval=2000))

    prev = None
    try:
        while True:
            items = mt5.market_book_get(symbol)
            if not items:
                time.sleep(poll_ms / 1000.0)
                continue
            now = datetime.now(tz)
            ts_ns = int(now.timestamp() * 1e9)
            dg = _digest(items)
            if dg != prev:
                lines = _lines(symbol, tzname, items, ts_ns)
                write_api.write(bucket=bucket, org=org, record=lines)
                prev = dg
            time.sleep(poll_ms / 1000.0)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            mt5.market_book_release(symbol)
        except Exception:
            pass
        mt5.shutdown()
        try:
            write_api.flush()
        except Exception:
            pass
        try:
            client.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
