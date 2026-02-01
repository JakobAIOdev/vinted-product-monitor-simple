# Vinted Monitor

A fast, proxy-rotating Vinted monitor that sends Discord notifications for new listings. Built with Python and designed to bypass anti-bot measures using rotating proxies (IPv4 & IPv6 supported).

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

- **Hybrid Proxy Support** - Works with IPv4 (Residential/Datacenter) and IPv6 proxies automatically.
- **Auto-Format** - Automatically detects and formats IPv6 addresses (`[::1]`) correctly.
- **Fast Polling** - Configurable polling interval (default: 15s).
- **Discord Webhooks** - Rich embeds with item image, price, size & condition.
- **Persistence** - Remembers seen items across restarts (no duplicate alerts).
- **Anti-Detection** - Uses `curl_cffi` to impersonate a real Chrome browser.
- **Lightweight** - No Selenium/Puppeteer overhead.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/vinted-monitor.git
cd vinted-monitor

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
# Vinted Search URL (Filter for newest first!)
VINTED_URL=https://www.vinted.de/catalog?search_text=ralph+lauren&order=newest_first

# Discord Webhook (optional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx/xxx

# Polling Interval in Seconds
POLL_SECONDS=15
```

## Proxies (`proxies.txt`)
Create a file named `proxies.txt` in the root directory. Add your proxies line by line.
Format: `HOST:PORT:USER:PASS` (standard export format from IPRoyal, Webshare, Proxy6, etc.).

Example `proxies.txt`:

```text
# IPv4 Example (Datacenter/Residential)
1.2.3.4:8000:user123:pass456

# IPv6 Example (The monitor automatically adds brackets [])
2a00:1234:5678:9abc::1:12345:user123:pass456
2a00:1234:5678:9abc::2:12345:user123:pass456
````

### Customizing Search

Modify `VINTED_URL` to filter by:
- **Brand**: `search_text=nike`
- **Category**: `catalog[]=5` (Clothing)
- **Price Range**: `price_from=10&price_to=50`
- **Size**: `size_id[]=208` (M)
- **Order**: `order=newest_first`

Example for Nike shoes under 50€:
```
https://www.vinted.de/catalog?search_text=nike&catalog[]=1231&price_to=50&order=newest_first
```

## Usage

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the monitor
python main.py
```

### First Run
On the first run, the monitor performs an initial scan to populate the database with existing items. After that, only **new listings** trigger Discord notifications.

### Output Example
```
Monitor started. Known items: 0
[INIT] Syncing current listings...
[OK] Synced 96 items (96 new). Monitor ready.
[14:05:22] No new drops (Scanned: 96 items)
[NEW] 1 DROP(S) FOUND!
   > Ralph Lauren | 25,00 € | M
```

<img width="499" height="648" alt="image" src="https://github.com/user-attachments/assets/550ce82f-00ca-44eb-b51c-6efb22dbf6d4" />

## Project Structure

```
vinted-monitor/
├── main.py           # Main monitor script
├── proxy_manager.py  # Handles proxy loading & IPv6 formatting
├── .env              # Environment variables
├── proxies.txt       # List of proxies (ignored by git)
├── seen_items.json   # Persisted seen item IDs
├── requirements.txt  # Python dependencies
└── README.md
```

## Requirements

- Python 3.10+
- Proxies
    - IPv6 Datacenter (Cheapest option for monitoring, e.g. IPRoyal, Proxy6)
    - IPv4 Datacenter/Residential (Works too)
- Discord Webhook URL (optional)

## Dependencies

```
curl-cffi>=0.5.0
beautifulsoup4>=4.12.0
python-dotenv>=1.0.0
```

## Disclaimer

This tool is for **educational purposes only**. Use responsibly and in accordance with Vinted's Terms of Service. The authors are not responsible for any misuse or account bans.

## License

MIT License - feel free to use and modify!

