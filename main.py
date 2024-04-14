import os
import random
import tempfile
import subprocess
import signal
import time
import logging
from colorama import init, Fore, Style

# Initialize colorama to support ANSI escape character sequences for colored output
init(autoreset=True)

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='[%(levelname)s] %(message)s')

def get_list_of_ovpn_files(path):
    ovpn_files = []
    for file in os.listdir(path):
        if file.endswith(".ovpn"):
            ovpn_files.append(file)
            logging.info(f"Found ovpn file: {file}")  # Log the found ovpn file
    return ovpn_files

def connect_to_ovpn(profile_path, username, password, timeout):
    logging.info(f"Connecting to {profile_path}...")  # Log the connection attempt
    print(Fore.GREEN + f"[INFO] Connecting to {profile_path}..." + Style.RESET_ALL)  # Print info message in console
    # Create a temporary file to store username and password
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(f"{username}\n{password}".encode())
    temp_file.close()

    # Run OpenVPN with the temporary file
    command = ["openvpn", "--config", profile_path, "--auth-user-pass", temp_file.name]
    process = subprocess.Popen(command)

    # Wait for the process to finish (or be interrupted)
    try:
        process.wait(timeout=timeout)  # Adjust timeout as needed
        logging.info("Connection successful.")  # Log successful connection
        print(Fore.GREEN + "[INFO] Connection successful." + Style.RESET_ALL)  # Print success message in console
    except subprocess.TimeoutExpired:
        # If timeout expires, kill the process
        process.terminate()
        logging.error("Connection timed out.")  # Log connection timeout
        print(Fore.RED + "[ERROR] Connection timed out." + Style.RESET_ALL)  # Print error message in console

        ## Process to kill the OpenVPN process (if needed)
        try:
            process.wait(timeout=10)  # Wait for the process to terminate gracefully
        except subprocess.TimeoutExpired:
            # If it still doesn't terminate, force kill it
            process.kill()

    # Remove the temporary file after OpenVPN exits
    os.unlink(temp_file.name)

def gestion_transmission(status):
    # Restart the Transmission service
    if status == "start":
        time.sleep(10)  # Wait for the VPN connection to be established
    command = ["service", "transmission", status]
    subprocess.run(command)

def main():
    ovpn_files = get_list_of_ovpn_files("./openvpn")
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    while True:
        random.shuffle(ovpn_files)
        for ovpn_file in ovpn_files:
            gestion_transmission("start")
            connect_to_ovpn(f"./openvpn/{ovpn_file}", username, password, 30)
            gestion_transmission("stop")
            time.sleep(5)   # Adjust sleep time as needed

if __name__ == "__main__":
    main()
