import os
import random
import tempfile
import subprocess
import signal
import time

def get_list_of_ovpn_files(path):
    ovpn_files = []
    for file in os.listdir(path):
        if file.endswith(".ovpn"):
            ovpn_files.append(file)
            print("Found ovpn file: " + file)
    return ovpn_files

def connect_to_ovpn(profile_path, username, password):
    # Create a temporary file to store username and password
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(f"{username}\n{password}".encode())
    temp_file.close()

    # Run OpenVPN with the temporary file
    command = ["openvpn", "--config", profile_path, "--auth-user-pass", temp_file.name]
    process = subprocess.Popen(command)

    # Wait for the process to finish (or be interrupted)
    try:
        process.wait(timeout=30)  # Adjust timeout as needed
    except subprocess.TimeoutExpired:
        # If timeout expires, kill the process
        process.terminate()
        try:
            process.wait(timeout=10)  # Wait for the process to terminate gracefully
        except subprocess.TimeoutExpired:
            # If it still doesn't terminate, force kill it
            process.kill()

    # Remove the temporary file after OpenVPN exits
    os.unlink(temp_file.name)

def disconnect_from_ovpn():
    os.system("pkill openvpn")

def main():
    ovpn_files = get_list_of_ovpn_files("./openvpn")
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    while True:
        random.shuffle(ovpn_files)
        for ovpn_file in ovpn_files:
            connect_to_ovpn(f"./openvpn/{ovpn_file}", username, password)
            time.sleep(10)  # Adjust sleep time as needed
            disconnect_from_ovpn()
            time.sleep(5)   # Adjust sleep time as needed

if __name__ == "__main__":
    main()
