import os
import random
import tempfile
import subprocess
import time
import logging
from colorama import init, Fore, Style
import getpass

# Initialize colorama to support ANSI escape character sequences for colored output
init(autoreset=True)

# Configure logging with time
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_ip():
    try:
        ip = subprocess.check_output(["curl", "ifconfig.io"])
        return ip.decode().strip()
    except subprocess.CalledProcessError as e:
        log_and_print(f"Failed to get IP: {e}", level="error", color=Fore.RED)
        return None

def log_and_print(message, level="info", color=Fore.RESET):
    """Log a message and print it with a specific color."""
    print(color + message + Style.RESET_ALL)
    if level == "info":
        logging.info(message)
    elif level == "error":
        logging.error(message)

def get_list_of_ovpn_files(path):
    ovpn_files = [file for file in os.listdir(path) if file.endswith(".ovpn")]
    for file in ovpn_files:
        log_and_print(f"Found ovpn file: {file}", color=Fore.CYAN)
    return ovpn_files

def manage_service(service, action):
    log_and_print(f"{service.capitalize()} service is {action}.", color=Fore.GREEN)
    command = ["service", service, action]
    run_command(command)

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break
        if output:
            log_and_print(output.decode().strip(), color=Fore.GREEN)
        time.sleep(0.1)

def core(ovpn_file, username, password, cooldown_seconds):
    log_and_print(f"Current IP: {get_ip()}", color=Fore.CYAN)
    log_and_print(f"Connecting to VPN server using {ovpn_file}...", color=Fore.GREEN)
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write(f"{username}\n{password}")

    try:
        command = ["openvpn", "--config", f"./openvpn/{ovpn_file}", "--auth-user-pass", temp_file.name, "--mute-replay-warnings"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)  # Wait for the VPN connection to establish
        log_and_print(f"VPN IP: {get_ip()}", color=Fore.CYAN)
        manage_service("transmission", "start")
        log_and_print("Transmission service started.", color=Fore.GREEN)
        
        log_and_print(f"Cooldown for {cooldown_seconds} seconds...", color=Fore.GREEN)
        time.sleep(cooldown_seconds)  # Cooldown period
        
        manage_service("transmission", "stop")
        log_and_print("Transmission service stopped.", color=Fore.YELLOW)
        process.terminate()
        process.wait()  # Ensure the process has terminated
        log_and_print("VPN connection closed.", color=Fore.YELLOW)
    except Exception as e:
        log_and_print(f"Error: {e}", level="error", color=Fore.RED)
    finally:
        os.remove(temp_file.name)

def main():
    ovpn_files = get_list_of_ovpn_files("./openvpn")
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")
    cooldown_seconds = 20

    try:
        while True:
            random.shuffle(ovpn_files)
            for ovpn_file in ovpn_files:
                manage_service("transmission", "stop")
                core(ovpn_file, username, password, cooldown_seconds)

    except KeyboardInterrupt:
        log_and_print("Script interrupted by user.", color=Fore.YELLOW)

if __name__ == "__main__":
    main()
