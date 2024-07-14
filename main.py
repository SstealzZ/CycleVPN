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
    level=logging.DEBUG,  # Change to DEBUG to capture more detailed logs
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_and_print(message, level="info", color=Fore.RESET):
    """Log a message and print it with a specific color."""
    print(color + message + Style.RESET_ALL)
    if level == "debug":
        logging.debug(message)
    elif level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
    elif level == "critical":
        logging.critical(message)

def get_list_of_ovpn_files(path):
    log_and_print(f"Scanning directory for .ovpn files: {path}", level="debug", color=Fore.BLUE)
    ovpn_files = []
    if not os.path.isdir(path):
        log_and_print(f"Directory does not exist: {path}", level="error", color=Fore.RED)
        return ovpn_files
    for file in os.listdir(path):
        if file.endswith(".ovpn"):
            ovpn_files.append(file)
            log_and_print(f"Found ovpn file: {file}", color=Fore.CYAN, level="debug")
    if not ovpn_files:
        log_and_print("No .ovpn files found.", level="warning", color=Fore.YELLOW)
    return ovpn_files

def connect_to_ovpn(profile_path, username, password, timeout):
    log_and_print(f"Connecting to {profile_path}...", color=Fore.GREEN, level="info")
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        temp_file.write(f"{username}\n{password}".encode())
        temp_file.close()

        command = ["openvpn", "--config", profile_path, "--auth-user-pass", temp_file.name, "--mute-replay-warnings"]
        log_and_print(f"Running command: {' '.join(command)}", level="debug", color=Fore.BLUE)
        process = subprocess.Popen(command)

        try:
            process.wait(timeout=timeout)
            log_and_print("Connection successful.", color=Fore.GREEN, level="info")
        except subprocess.TimeoutExpired:
            process.terminate()
            log_and_print("Connection timed out.", level="error", color=Fore.RED)

            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()

        return process.returncode == 0
    except Exception as e:
        log_and_print(f"An error occurred: {str(e)}", level="error", color=Fore.RED)
        return False
    finally:
        os.unlink(temp_file.name)
        log_and_print(f"Temporary file {temp_file.name} deleted.", level="debug", color=Fore.BLUE)

def gestion_transmission(status):
    log_and_print(f"Transmission service {status}...", color=Fore.YELLOW, level="info")
    command = ["service", "transmission", status]
    try:
        subprocess.run(command, check=True)
        log_and_print(f"Transmission service {status}ed successfully.", color=Fore.YELLOW, level="info")
    except subprocess.CalledProcessError as e:
        log_and_print(f"Failed to {status} Transmission service: {str(e)}", level="error", color=Fore.RED)

def main():
    ovpn_files = get_list_of_ovpn_files("./openvpn")
    if not ovpn_files:
        log_and_print("No VPN profiles found. Exiting...", level="critical", color=Fore.RED)
        return

    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    try:
        while True:
            random.shuffle(ovpn_files)
            for ovpn_file in ovpn_files:
                log_and_print(f"Attempting to connect using profile: {ovpn_file}", level="info", color=Fore.BLUE)
                if connect_to_ovpn(f"./openvpn/{ovpn_file}", username, password, 3600):
                    gestion_transmission("start")
                    time.sleep(3600)
                    gestion_transmission("stop")
                else:
                    log_and_print("Failed to establish VPN connection. Retrying with the next profile.", level="error", color=Fore.RED)
                time.sleep(5)
    except KeyboardInterrupt:
        log_and_print("Script interrupted by user.", color=Fore.YELLOW, level="warning")

if __name__ == "__main__":
    main()
