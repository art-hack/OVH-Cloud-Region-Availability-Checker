import requests
import os
import argparse
from telegram import Bot
from dotenv import load_dotenv, set_key
from tabulate import tabulate
import cronitor

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CRONITOR_API_KEY = os.getenv('CRONITOR_API_KEY')

# API URL to monitor
API_URL = os.getenv('API_URL')

# Setup Monitoring
cronitor.api_key = CRONITOR_API_KEY
monitor = cronitor.Monitor('vps-availability-checker')

def setup_telegram_bot():
    """Initialize Telegram bot"""
    return Bot(token=TELEGRAM_BOT_TOKEN)

def send_telegram_notification(bot, available_datacenters, os_type):
    """Send notification via Telegram"""
    try:
        message = "🎉 ALERT: VPS instances are now available in the following locations:\n\n"
        for dc in available_datacenters:
            message += f"• {dc['datacenter']} ({dc['code']})\n"
            if os_type == 'overall':
                message += f"  - Status: {dc['status']}\n"
            elif os_type == 'linux':
                message += f"  - Linux Status: {dc['linuxStatus']}\n"
            elif os_type == 'windows':
                message += f"  - Windows Status: {dc['windowsStatus']}\n"
            message += "\n"
        
        message += "🔗 Configure your VPS here:\n"
        message += "https://www.ovhcloud.com/en-in/vps/configurator/"
        
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("Notification sent successfully!")
    except Exception as e:
        print(f"Failed to send notification: {str(e)}")

def get_all_datacenters():
    """Get all available datacenters and their status"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        return response.json().get('datacenters', [])
        
    except Exception as e:
        print(f"Error fetching datacenters: {str(e)}")

        if CRONITOR_API_KEY:
            monitor.ping(state='fail')

        return []

def select_os_type():
    """Let user select the OS type to monitor"""
    print("\nSelect OS type to monitor:")
    print("1. Overall availability")
    print("2. Linux only")
    print("3. Windows only")
    
    while True:
        try:
            selection = input("\nEnter your choice (1-3): ").strip()
            if selection == '1':
                return 'overall'
            elif selection == '2':
                return 'linux'
            elif selection == '3':
                return 'windows'
            else:
                print("Invalid selection. Please enter 1, 2, or 3.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def display_datacenter_table():
    """Display all datacenters in a table format and get user selection"""
    datacenters = get_all_datacenters()
    
    # Prepare table data
    headers = ["#", "Datacenter", "Region", "Overall Status", "Linux Status", "Windows Status"]
    table_data = []
    
    for idx, dc in enumerate(datacenters, 1):
        region = dc['code'].split('-')[0].upper()
        table_data.append([
            idx,
            f"{dc['datacenter']} ({dc['code']})",
            region,
            dc['status'],
            dc['linuxStatus'],
            dc['windowsStatus']
        ])
    
    # Print table
    print("\nAvailable Datacenters:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    # Get user selection
    while True:
        try:
            print("\nEnter the numbers of datacenters to monitor (comma-separated, e.g., 1,3,5)")
            selection = input("Selection: ").strip()
            
            if not selection:
                print("Please select at least one datacenter.")
                continue
            
            selected_nums = [int(num.strip()) for num in selection.split(',')]
            if all(1 <= num <= len(datacenters) for num in selected_nums):
                selected_dcs = [datacenters[num-1]['datacenter'] for num in selected_nums]
                
                # Get OS type selection
                os_type = select_os_type()
                
                # Update .env file
                set_key('.env', 'TARGET_DATACENTERS', ','.join(selected_dcs))
                set_key('.env', 'OS_TYPE', os_type)
                
                print(f"\nConfiguration updated:")
                print(f"Selected datacenters: {', '.join(selected_dcs)}")
                print(f"OS type: {os_type}")
                return
            else:
                print("Invalid selection. Please enter valid numbers.")
        except ValueError:
            print("Invalid input. Please enter numbers separated by commas.")

def check_vps_availability():
    """Check VPS availability in target datacenters"""
    try:
        target_dcs = os.getenv('TARGET_DATACENTERS')
        os_type = os.getenv('OS_TYPE')
        
        if not target_dcs or not os_type:
            print("Configuration missing. Please run with --configure first.")
            return []
            
        target_dcs = target_dcs.split(',')
        all_datacenters = get_all_datacenters()
        available_datacenters = []
        
        for datacenter in all_datacenters:
            if datacenter['datacenter'] in target_dcs:
                if (
                    (os_type == 'overall' and datacenter['status'] == 'available') or
                    (os_type == 'linux' and datacenter['linuxStatus'] == 'available') or
                    (os_type == 'windows' and datacenter['windowsStatus'] == 'available')
                ):
                    available_datacenters.append(datacenter)
        
        return available_datacenters
        
    except Exception as e:
        print(f"Error checking availability: {str(e)}")

        if CRONITOR_API_KEY:
            monitor.ping(state='fail')

        return []

def main():

    if CRONITOR_API_KEY:
        monitor.ping(state='run')

    parser = argparse.ArgumentParser(description='OVH VPS Availability Checker')
    parser.add_argument('--configure', action='store_true', 
                       help='Configure target datacenters and OS type interactively')
    args = parser.parse_args()

    if args.configure:
        display_datacenter_table()
        return

    target_dcs = os.getenv('TARGET_DATACENTERS')
    os_type = os.getenv('OS_TYPE')
    
    if not target_dcs or not os_type:
        print("Configuration missing. Running setup...")
        display_datacenter_table()
        return

    print(f"Checking VPS availability in datacenters: {target_dcs}")
    print(f"Monitoring {os_type} availability")
    
    try:
        available_datacenters = check_vps_availability()
        if available_datacenters:
            print("VPS is available!")
            bot = setup_telegram_bot()
            send_telegram_notification(bot, available_datacenters, os_type)
            print("Notification sent on Telegram")
        else:
            print("No VPS availability in target datacenters at the moment.")
        
        if CRONITOR_API_KEY:
            monitor.ping(state='complete')
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
        if CRONITOR_API_KEY:
            monitor.ping(state='fail')

if __name__ == "__main__":
    main()