# MetaTrader 5 Market Depth Recorder

A high-performance Python data loader that streams MetaTrader 5 market depth (order book) data to InfluxDB in real-time. Built for Windows with Docker containerization support.

## Features

- 🚀 **Real-time Market Depth Streaming**: Captures MT5 order book data with nanosecond precision
- ⚡ **High Performance**: Optimized polling (50ms default) with change detection to minimize writes
- 🕐 **Timezone Support**: Configurable timezone (default: Asia/Nicosia) for accurate timestamps
- 📊 **InfluxDB Integration**: Batched writes with configurable batch sizes and flush intervals
- 🐳 **Docker + Native Hybrid**: InfluxDB in Docker, MT5 loader runs natively on Windows
- 🔧 **Fully Configurable**: Environment-driven configuration for all parameters

## Prerequisites

- **Windows OS** (required for MetaTrader 5 integration)
- **Docker Desktop** (for running InfluxDB)
- **MetaTrader 5** installed (default: `C:\Program Files\MetaTrader 5\terminal64.exe`)
- **Python 3.12+** (for running the MT5 loader on Windows host)
- **Git** (for cloning and version control)

## Quick Start

### 1. Configure Environment

Edit `.env` file with your settings:

```bash
# Required: InfluxDB connection
INFLUX_TOKEN=your-influxdb-token
INFLUX_ORG=your-organization

# Optional: Override defaults
SYMBOL=EURUSD
TIMEZONE=Asia/Nicosia
INFLUX_URL=http://localhost:8086
INFLUX_BUCKET=orderbook_EURUSD

# MT5 Configuration (required for MT5 access)
MT5_TERMINAL_PATH=C:\Program Files\MetaTrader 5\terminal64.exe
MT5_LOGIN=your_login
MT5_PASSWORD=your_password
MT5_SERVER=your_broker_server
```

### 2. Start InfluxDB with Docker

```bash
# Start only InfluxDB in Docker
docker compose up influxdb -d

# Check InfluxDB status
docker compose logs influxdb

# Access InfluxDB UI at: http://localhost:8086
```

### 3. Run MT5 Loader on Windows Host

Since MetaTrader 5 requires direct access to the Windows host, run the loader natively:

```powershell
# Option 1: Use the setup script (recommended)
.\setup-windows.ps1

# Option 2: Manual setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src/orderbook_loader.py

# Option 3: Use the run script after setup
.\run-windows.ps1
```

### 4. Stop Services

```bash
# Stop InfluxDB
docker compose down

# Stop MT5 Loader: Press Ctrl+C in the terminal
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SYMBOL` | Trading symbol to monitor | `EURUSD` |
| `TIMEZONE` | Timezone for timestamps | `Asia/Nicosia` |
| `INFLUX_URL` | InfluxDB server URL | `http://localhost:8086` |
| `INFLUX_TOKEN` | InfluxDB authentication token | *Required* |
| `INFLUX_ORG` | InfluxDB organization | *Required* |
| `INFLUX_BUCKET` | InfluxDB bucket name | `orderbook_<SYMBOL>` |
| `POLL_INTERVAL_MS` | Polling interval in milliseconds | `50` |
| `WRITE_BATCH_SIZE` | Batch size for InfluxDB writes | `500` |
| `WRITE_FLUSH_INTERVAL_MS` | Flush interval for batches | `250` |
| `MT5_TERMINAL_PATH` | Path to MT5 terminal executable | `C:\Program Files\MetaTrader 5\terminal64.exe` |
| `MT5_LOGIN` | MT5 account login | *Optional* |
| `MT5_PASSWORD` | MT5 account password | *Optional* |
| `MT5_SERVER` | MT5 broker server | *Optional* |

### Performance Tuning

- **`POLL_INTERVAL_MS`**: Lower values (10-100ms) for higher frequency data capture
- **`WRITE_BATCH_SIZE`**: Increase (1000+) for better throughput on high-volume symbols
- **`WRITE_FLUSH_INTERVAL_MS`**: Adjust based on your network latency and InfluxDB capacity

## Data Schema

### InfluxDB Measurement: `orderbook`

**Tags:**
- `symbol`: Trading symbol (e.g., EURUSD)
- `side`: Order side (`bid` or `ask`)
- `timezone`: Timezone used for timestamps

**Fields:**
- `level`: Order book level (integer)
- `type`: Order type (1 = bid, 2 = ask)
- `price`: Price level (float)
- `volume`: Volume (integer)
- `volume_dbl`: Volume as double (float)

**Timestamp:** Nanosecond precision in configured timezone

### Example Data Point

```
orderbook,symbol=EURUSD,side=bid,timezone=Asia_Nicosia level=0i,type=1i,price=1.12345,volume=100i,volume_dbl=100.0 1732204800000000000
```

## Architecture

```
MetaTrader 5 → Python Loader → InfluxDB
    │               │            │
    │ Market Depth  │ Change     │ Time-Series
    │ Subscription  │ Detection  │ Database
    │               │            │
    └───────────────┴────────────┴────────────┘
```

### Key Components

1. **MT5 Integration** (`src/orderbook_loader.py:59-68`)
   - Initializes MT5 connection
   - Subscribes to market depth updates
   - Handles authentication if provided

2. **Change Detection** (`src/orderbook_loader.py:17-18,82-83`)
   - Hash-based comparison of order book snapshots
   - Writes only when market depth changes
   - Reduces redundant database writes

3. **InfluxDB Writer** (`src/orderbook_loader.py:70-71,85`)
   - Batched writes with configurable parameters
   - Line protocol formatting
   - Error handling and cleanup

4. **Timezone Handling** (`src/orderbook_loader.py:39-40,80-81`)
   - Proper timezone conversion using `zoneinfo`
   - Nanosecond precision timestamps

## Development

### Project Structure

```
metatrader-5-market-depth-recorder/
├── src/
│   └── orderbook_loader.py  # Main loader application
├── .env                     # Environment configuration
├── Dockerfile               # Windows container definition
├── docker-compose.yml       # Docker orchestration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Building from Source

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests (add your test suite here)
python -m pytest tests/
```

## Troubleshooting

### Common Issues

1. **MT5 Connection Failed**
   - Verify MT5 is installed at the specified path
   - Check if MT5 terminal is running

2. **InfluxDB Connection Issues**
   - Verify InfluxDB is running and accessible
   - Check token and organization permissions

3. **Timezone Errors**
   - Ensure the specified timezone is valid
   - Use IANA timezone format (e.g., `Asia/Nicosia`)

### Logs and Monitoring

```bash
# View Docker logs
docker compose logs -f loader

# Monitor InfluxDB writes
docker exec -it influxdb influx query 'from(bucket: "orderbook_EURUSD") |> range(start: -1m)'
```

## Performance Considerations

- **Memory Usage**: Batched writes reduce memory pressure
- **Network Latency**: Adjust flush intervals for your network
- **MT5 Performance**: High polling rates may impact MT5 terminal performance
- **Disk I/O**: InfluxDB should be on fast storage for high write volumes

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Ensure all prerequisites are met

---

Built with ❤️ for high-frequency trading data collection