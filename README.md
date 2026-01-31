# Vinted Monitor

A fast, proxy-rotating Vinted monitor that sends Discord notifications for new listings. Built with Python and designed to bypass anti-bot measures using rotating residential proxies.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)

## Features

- **Rotating Proxy Support** - Automatic session rotation to avoid blocks
- **Fast Polling** - Configurable polling interval (default: 15s)
- **Discord Webhooks** - Rich embeds with item image, price, size & condition
- **Persistence** - Remembers seen items across restarts
- **Anti-Detection** - Uses `curl_cffi` to impersonate real Chrome browser
- **Lightweight** - No Selenium/Puppeteer overhead

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
# Proxy Configuration (Mars Proxies or similar)
PROXY_HOST=ultra.marsproxies.com
PROXY_PORT=44443
PROXY_USER=your_username
PROXY_PASS_BASE=your_password_country-de

# Vinted Search URL
VINTED_URL=https://www.vinted.de/catalog?search_text=ralph+lauren&order=newest_first

# Discord Webhook (optional)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx/xxx

# Polling Interval in Seconds
POLL_SECONDS=15
```

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
Performing INITIAL SCAN (filling database)...
Initial Scan complete. Saved 96 items. Starting Monitor now!
No new drops. (Scan: 96)
1 NEW DROP items found!
-> Webhook: Ralph Lauren (25,00 €)
```

## Project Structure

```
vinted-monitor/
├── main.py           # Main monitor script
├── .env              # Environment variables (create this)
├── .env.example      # Example configuration
├── seen_items.json   # Persisted seen item IDs (auto-generated)
├── requirements.txt  # Python dependencies
└── README.md
```

## Requirements

- Python 3.10+
- Rotating Residential Proxies (recommended: [Mars Proxies](https://marsproxies.com))
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

