# OVH Cloud Region Availability Checker

A Python-based tool to monitor OVH VPS availability across different datacenters and receive Telegram notifications when instances become available.

## Features

- 🌍 Monitor multiple OVH datacenters simultaneously
- 🔄 Real-time availability checks
- 💻 Support for Linux, Windows, or overall VPS availability monitoring
- 📱 Instant Telegram notifications when VPS becomes available
- ⚙️ Interactive configuration setup
- 🚀 Easy to set up and use

## Prerequisites

- Python 3.6+
- A Telegram bot token (get it from [@BotFather](https://t.me/botfather))
- Your Telegram chat ID

## Installation

1. Clone the repository:
```bash
git clone https://github.com/art-hack/OVH-Cloud-Region-Availability-Checker.git
cd OVH-Cloud-Region-Availability-Checker
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

4. Update the `.env` file with your Telegram credentials:
```plaintext
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
API_URL=api_url_for_the_status_api

# Optional - For Monitoring
CRONITOR_API_KEY=your_monitoring_key
```

## Configuration

Run the interactive configuration to select datacenters and OS type:

```bash
python vps_availability_checker.py --configure
```

This will:
1. Display available datacenters with their current status
2. Let you select which datacenters to monitor
3. Let you choose the OS type to monitor (Overall/Linux/Windows)

## Usage

### Running the Checker

After configuration, simply run:

```bash
python vps_availability_checker.py
```

### Telegram Notifications

When a VPS becomes available in your selected datacenters, you'll receive a Telegram notification with:
- Datacenter name and code
- Availability status based on your selected OS type
- Direct link to OVH VPS configurator

## Sample Notification

```
🎉 ALERT: VPS instances are now available in the following locations:

• Singapore (SIN1)
  - Linux Status: available

🔗 Configure your VPS here:
https://www.ovhcloud.com/en-in/vps/configurator/
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | Yes |
| `TELEGRAM_CHAT_ID` | Your Telegram chat ID | Yes |
| `API_URL` | URL to OVH Status based on the type of VPS you want | Yes |
| `CRONITOR_API_KEY` | Api Key to monitor script executions | Optional |
| `TARGET_DATACENTERS` | Comma-separated list of datacenter names (auto-configured) | Auto-set |
| `OS_TYPE` | Type of VPS to monitor (auto-configured) | Auto-set |

Note: You can get the `API_URL` by opening the page for the VPS and looking for XHR requests in the Inspect Tab. It is of a format like `https://ca.api.ovh.com/1.0/vps/order/rule/datacenter?<QUERY_PARAMS>`.

## Directory Structure

```
.
├── README.md
├── requirements.txt
├── .env.example
└── vps_availability_checker.py
```

## Requirements

```plaintext
requests==2.31.0
python-telegram-bot==13.7
python-dotenv==1.0.0
tabulate==0.9.0
cronitor
```

## Contributing

Feel free to open issues or submit pull requests for any improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

[art-hack](https://github.com/art-hack)
