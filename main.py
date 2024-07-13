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

def log_and_print(message, level="info", color=Fore.RESET):
    """Log a message and print it with a specific color."""
    print(color + message + Style.RESET_ALL)
    if level == "info":
        logging.info(message)
    elif level == "error":
        logging.error(message)

def get_list_of_ovpn_files(path):
    ovpn_files = []
    for file in os.listdir(path):
        if file.endswith(".ovpn"):
            ovpn_files.append(file)
            log_and_print(f"Found ovpn file: {file}", color=Fore.CYAN)
    return ovpn_files

def connect_to_ovpn(profile_path, username, password, timeout):
    log_and_print(f"Connecting to {profile_path}...", color=Fore.GREEN)
    # Create a temporary file to store username and password
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(f"{username}\n{password}".encode())
    temp_file.close()

    # Run OpenVPN with the temporary file
    command = ["openvpn", "--config", profile_path, "--auth-user-pass", temp_file.name, "--mute-replay-warnings"]
    process = subprocess.Popen(command)

    # Wait for the process to finish (or be interrupted)
    try:
        process.wait(timeout=timeout)  # Adjust timeout as needed
        log_and_print("Connection successful.", color=Fore.GREEN)
    except subprocess.TimeoutExpired:
        # If timeout expires, kill the process
        process.terminate()
        log_and_print("Connection timed out.", level="error", color=Fore.RED)

        ## Process to kill the OpenVPN process (if needed)
        try:
            process.wait(timeout=10)  # Wait for the process to terminate gracefully
        except subprocess.TimeoutExpired:
            # If it still doesn't terminate, force kill it
            process.kill()

    # Remove the temporary file after OpenVPN exits
    os.unlink(temp_file.name)

    return process.returncode == 0

def gestion_transmission(status):
    # Manage the Transmission service
    log_and_print(f"Transmission service {status}...", color=Fore.YELLOW)
    command = ["service", "transmission", status]
    try:
        subprocess.run(command, check=True)
        log_and_print(f"Transmission service {status}ed successfully.", color=Fore.YELLOW)
    except subprocess.CalledProcessError as e:
        log_and_print(f"Failed to {status} Transmission service: {str(e)}", level="error", color=Fore.RED)

def main():
    ovpn_files = get_list_of_ovpn_files("./openvpn")
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    try:
        while True:
            random.shuffle(ovpn_files)
            for ovpn_file in ovpn_files:
                if connect_to_ovpn(f"./openvpn/{ovpn_file}", username, password, 3600):
                    gestion_transmission("start")
                    time.sleep(3600)  # Adjust sleep time to match VPN connection duration
                    gestion_transmission("stop")
                else:
                    log_and_print("Failed to establish VPN connection. Retrying with the next profile.", level="error", color=Fore.RED)
                time.sleep(5)  # Adjust sleep time as needed
    except KeyboardInterrupt:
        log_and_print("Script interrupted by user.", color=Fore.YELLOW)

if __name__ == "__main__":
    main()
