import os
import random

def get_list_of_ovpn_files(path):
    ovpn_files = []
    for file in os.listdir(path):
        if file.endswith(".ovpn"):
            ovpn_files.append(file)
            print("Found ovpn file: " + file)
    return ovpn_files

def connect_to_ovpn(profile_path, username, password):
    command = f"openvpn --config {profile_path} --auth-user-pass <(echo '{username}\n{password}')"
    os.system(command)

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
            os.system("sleep 30")
            disconnect_from_ovpn()
            os.system("sleep 10")


if __name__ == "__main__":
    main()
