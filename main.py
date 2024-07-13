import subprocess
import time
import logging
from pathlib import Path
import random
import getpass

# Configurer les logs
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Chemin vers le répertoire contenant les fichiers de configuration .ovpn
CONFIG_DIRECTORY = Path('./openvpn')

# Liste des fichiers de configuration .ovpn
VPN_SERVERS = [str(file) for file in CONFIG_DIRECTORY.glob('*.ovpn')]

# Demander les identifiants à l'utilisateur
username = input("Enter your VPN username: ")
password = getpass.getpass("Enter your VPN password: ")

def start_vpn(config_file, username, password):
    """Connect to the VPN using a specific configuration file."""
    cmd = ['sudo', 'openvpn', '--config', config_file, '--auth-user-pass']
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.stdin.write(f'{username}\n{password}\n'.encode())
    process.stdin.flush()
    return process

def stop_vpn(process):
    """Disconnect from the VPN."""
    process.terminate()

def check_vpn_connection():
    """Check the current public IP address."""
    try:
        current_ip = subprocess.check_output(['curl', 'ifconfig.me']).decode().strip()
        logging.info(f'Current IP: {current_ip}')
        return current_ip
    except subprocess.CalledProcessError as e:
        logging.error('Error checking VPN connection: ' + str(e))
        return None

def switch_vpn(current_process, username, password):
    """Switch to a random VPN server."""
    if current_process:
        manage_transmission('stop')  # Stop Transmission service before disconnecting VPN
        stop_vpn(current_process)
        logging.info('VPN disconnected.')
        time.sleep(60)  # Wait for 1 minute before reconnecting

    new_server = random.choice(VPN_SERVERS)
    logging.info(f'Connecting to VPN server: {new_server}')
    vpn_process = start_vpn(new_server, username, password)
    time.sleep(15)  # Wait for VPN to establish connection
    manage_transmission('start')  # Start Transmission service after connecting VPN
    return vpn_process

def manage_transmission(action):
    """Manage Transmission service."""
    if action not in ['start', 'stop', 'restart', 'status']:
        logging.error(f'Invalid action for Transmission service: {action}')
        return
    cmd = ['sudo', 'service', 'transmission-daemon', action]
    try:
        subprocess.run(cmd, check=True)
        logging.info(f'Transmission service {action}ed successfully.')
    except subprocess.CalledProcessError as e:
        logging.error(f'Failed to {action} Transmission service: ' + str(e))

def main():
    vpn_process = None
    try:
        vpn_process = switch_vpn(vpn_process, username, password)
        while True:
            time.sleep(3600)  # Wait for 1 hour before changing VPN
            vpn_process = switch_vpn(vpn_process, username, password)
    except KeyboardInterrupt:
        logging.info('Script interrupted by user.')
    finally:
        if vpn_process:
            manage_transmission('stop')  # Ensure Transmission is stopped before disconnecting VPN
            stop_vpn(vpn_process)
            logging.info('VPN disconnected.')

if __name__ == '__main__':
    main()
