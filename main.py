import os
import random
import subprocess
import tempfile
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

def cooldown(seconds, ip_local, ip_vpn):
    log_and_print(f"Cooldown for {seconds} seconds...", color=Fore.GREEN)
    if ip_local != ip_vpn:
        log_and_print("VPN connection established.", color=Fore.GREEN)
    else:
        log_and_print("VPN connection failed.", color=Fore.RED)
        manage_service("transmission", "stop")
        run_command(["pkill", "openvpn"])
    time.sleep(seconds)

def core(ovpn_file, username, password):
    log_and_print(f"Connecting to VPN server using {ovpn_file}...", color=Fore.GREEN)
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        temp_file.write(f"{username}\n{password}".encode())
        temp_file.close()

        try:
            command = ["openvpn", "--config", f"./openvpn/{ovpn_file}", "--auth-user-pass", temp_file.name, "--mute-replay-warnings"]
            run_command(command)
            log_and_print("VPN connection closed.", color=Fore.YELLOW)
        except Exception as e:
            log_and_print(f"Error: {e}", level="error", color=Fore.RED)
        finally:
            os.remove(temp_file.name)

def main():
    ovpn_files = get_list_of_ovpn_files("./openvpn")
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    try:
        while True:
            random.shuffle(ovpn_files)
            for ovpn_file in ovpn_files:
                manage_service("transmission", "stop")
                ip_local = get_ip()
                if ip_local:
                    core(ovpn_file, username, password)
                    ip_vpn = get_ip()
                    if ip_vpn:
                        cooldown(20, ip_local, ip_vpn)
                        run_command(["pkill", "openvpn"])
    except KeyboardInterrupt:
        log_and_print("Script interrupted by user.", color=Fore.YELLOW)

if __name__ == "__main__":
    main()
