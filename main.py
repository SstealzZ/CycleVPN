import os

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
    if not ovpn_files:
        print("No OpenVPN profiles found.")
        return
    
    print("Available OpenVPN profiles:")
    for idx, file in enumerate(ovpn_files):
        print(f"{idx+1}. {file}")

    choice = input("Enter the profile number to connect (0 to quit): ")
    if choice == '0':
        return
    elif not choice.isdigit() or int(choice) < 1 or int(choice) > len(ovpn_files):
        print("Invalid choice. Please enter a valid profile number.")
        return

    selected_profile = ovpn_files[int(choice) - 1]
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    connect_to_ovpn(f"./openvpn/{selected_profile}", username, password)

if __name__ == "__main__":
    main()
