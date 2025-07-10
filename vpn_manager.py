import os
import random
import subprocess
import tempfile
import time
from pathlib import Path
from typing import List, Optional, Tuple
import getpass
from colorama import Fore


class VPNManager:
    """
    Manages OpenVPN connections and related network operations.
    
    This class handles VPN connection establishment, credential management,
    and service coordination for secure network operations.
    """
    
    def __init__(self, config_manager, logger_manager, kill_switch):
        """
        Initialize the VPN manager.
        
        Args:
            config_manager: Instance of ConfigManager
            logger_manager: Instance of LoggerManager
            kill_switch: Instance of KillSwitch
        """
        self.config_manager = config_manager
        self.logger = logger_manager
        self.kill_switch = kill_switch
        self.paths_config = config_manager.get_paths_config()
        self.services_config = config_manager.get_services_config()
        self.network_config = config_manager.get_network_config()
        self.session_config = config_manager.get_session_config()
        
        self.vpn_process = None
        self.current_ovpn_file = None
        self.temp_credentials_file = None
    
    def discover_ovpn_files(self) -> List[str]:
        """
        Discover all OpenVPN configuration files in the configured directory.
        
        Returns:
            List of OpenVPN configuration file names
        """
        ovpn_directory = Path(self.paths_config['ovpn_directory'])
        
        if not ovpn_directory.exists():
            self.logger.error(f"OpenVPN directory not found: {ovpn_directory}")
            return []
        
        ovpn_files = [
            file.name for file in ovpn_directory.glob("*.ovpn")
            if file.is_file()
        ]
        
        if not ovpn_files:
            self.logger.error("No OpenVPN configuration files found")
            return []
        
        self.logger.info(f"Found {len(ovpn_files)} OpenVPN configuration files")
        
        for file in ovpn_files:
            self.logger.debug(f"Discovered OpenVPN file: {file}")
        
        return ovpn_files
    
    def get_user_credentials(self) -> Tuple[str, str]:
        """
        Get VPN credentials from user input.
        
        Returns:
            Tuple of (username, password)
        """
        self.logger.info("Please enter your VPN credentials:")
        username = input("Username: ")
        password = getpass.getpass("Password: ")
        
        if not username or not password:
            self.logger.error("Username and password are required")
            raise ValueError("Invalid credentials provided")
        
        self.logger.info("Credentials obtained successfully")
        return username, password
    
    def create_secure_temporary_credentials_file(self, username: str, password: str) -> str:
        """
        Create a secure temporary file with VPN credentials.
        
        Args:
            username: VPN username
            password: VPN password
            
        Returns:
            Path to temporary credentials file
        """
        temp_dir = self.paths_config['temp_directory']
        
        fd, temp_file_path = tempfile.mkstemp(
            dir=temp_dir,
            prefix='cyclevpn_',
            suffix='.auth'
        )
        
        try:
            os.fchmod(fd, 0o600)
            
            with os.fdopen(fd, 'w') as temp_file:
                temp_file.write(f"{username}\n{password}")
            
            self.temp_credentials_file = temp_file_path
            self.logger.debug("Secure temporary credentials file created")
            return temp_file_path
            
        except Exception as e:
            os.close(fd)
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            raise e
    
    def secure_cleanup_credentials(self):
        """
        Securely remove temporary credentials file with overwrite.
        """
        if self.temp_credentials_file and os.path.exists(self.temp_credentials_file):
            try:
                file_size = os.path.getsize(self.temp_credentials_file)
                
                with open(self.temp_credentials_file, 'r+b') as f:
                    f.write(os.urandom(file_size))
                    f.flush()
                    os.fsync(f.fileno())
                
                os.remove(self.temp_credentials_file)
                self.logger.debug("Temporary credentials file securely removed")
                self.temp_credentials_file = None
                
            except OSError as e:
                self.logger.error(f"Failed to securely remove credentials file: {e}")
    
    def manage_system_service(self, service_name: str, action: str):
        """
        Manage system services (start/stop/restart).
        
        Args:
            service_name: Name of the service
            action: Action to perform (start, stop, restart)
        """
        self.logger.info(f"Managing service: {service_name} - {action}")
        
        try:
            result = subprocess.run(
                ["service", service_name, action],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.success(f"Service {service_name} {action}ed successfully")
            else:
                stderr_msg = result.stderr.strip()
                if action == "stop" and ("not running" in stderr_msg.lower() or "inactive" in stderr_msg.lower()):
                    self.logger.info(f"Service {service_name} was already stopped")
                elif action == "start" and ("already running" in stderr_msg.lower() or "active" in stderr_msg.lower()):
                    self.logger.info(f"Service {service_name} was already running")
                else:
                    self.logger.error(f"Failed to {action} service {service_name}: {stderr_msg}")
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout while trying to {action} service {service_name}")
        except Exception as e:
            self.logger.error(f"Error managing service {service_name}: {e}")
    
    def connect_to_vpn(self, ovpn_file: str, username: str, password: str) -> bool:
        """
        Establish VPN connection using OpenVPN with secure credential handling.
        
        Args:
            ovpn_file: Name of the OpenVPN configuration file
            username: VPN username
            password: VPN password
            
        Returns:
            True if connection was established successfully, False otherwise
        """
        ovpn_file_path = Path(self.paths_config['ovpn_directory']) / ovpn_file
        
        if not ovpn_file_path.exists():
            self.logger.error(f"OpenVPN configuration file not found: {ovpn_file_path}")
            return False
        
        self.current_ovpn_file = ovpn_file
        self.logger.info(f"Connecting to VPN server using: {ovpn_file}")
        
        credentials_file = None
        try:
            credentials_file = self.create_secure_temporary_credentials_file(username, password)
            
            command = [
                "openvpn",
                "--config", str(ovpn_file_path),
                "--auth-user-pass", credentials_file,
                "--mute-replay-warnings",
                "--daemon"
            ]
            
            self.vpn_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.logger.info("OpenVPN process started, waiting for connection...")
            time.sleep(self.network_config['vpn_establish_wait'])
            
            if self.kill_switch.verify_vpn_connection():
                self.logger.success(f"VPN connection established successfully using {ovpn_file}")
                return True
            else:
                self.logger.error("VPN connection verification failed")
                self.disconnect_vpn()
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to establish VPN connection: {e}")
            if credentials_file:
                self.secure_cleanup_credentials()
            return False
    
    def disconnect_vpn(self):
        """
        Disconnect from VPN and cleanup processes.
        """
        if self.vpn_process:
            try:
                self.vpn_process.terminate()
                self.vpn_process.wait(timeout=10)
                self.logger.info("VPN connection terminated")
            except subprocess.TimeoutExpired:
                self.vpn_process.kill()
                self.logger.warning("VPN process force killed")
            except Exception as e:
                self.logger.error(f"Error disconnecting VPN: {e}")
            
            self.vpn_process = None
        
        self.kill_switch.kill_vpn_processes()
        self.secure_cleanup_credentials()
        self.current_ovpn_file = None
    
    def run_vpn_session(self, ovpn_file: str, username: str, password: str) -> bool:
        """
        Run a complete VPN session with transmission service.
        
        Args:
            ovpn_file: OpenVPN configuration file name
            username: VPN username
            password: VPN password
            
        Returns:
            True if session completed successfully, False otherwise
        """
        session_successful = False
        
        try:
            self.kill_switch.store_initial_ip()
            
            self.manage_system_service(
                self.services_config['transmission_service'],
                "stop"
            )
            
            if self.connect_to_vpn(ovpn_file, username, password):
                self.manage_system_service(
                    self.services_config['transmission_service'],
                    "start"
                )
                
                cooldown_seconds = self.config_manager.get_cooldown_seconds()
                self.logger.info(f"VPN session active for {cooldown_seconds} seconds...")
                time.sleep(cooldown_seconds)
                
                self.manage_system_service(
                    self.services_config['transmission_service'],
                    "stop"
                )
                
                session_successful = True
            else:
                self.logger.error("Failed to establish VPN connection")
                if self.config_manager.is_kill_switch_enabled():
                    self.kill_switch.activate_kill_switch()
        
        except Exception as e:
            self.logger.error(f"Error during VPN session: {e}")
        
        finally:
            self.disconnect_vpn()
        
        return session_successful
    
    def run_continuous_vpn_rotation(self, username: str, password: str):
        """
        Run continuous VPN server rotation.
        
        Args:
            username: VPN username
            password: VPN password
        """
        ovpn_files = self.discover_ovpn_files()
        
        if not ovpn_files:
            self.logger.error("No OpenVPN files available for rotation")
            return
        
        failure_count = 0
        max_failures = self.session_config['max_connection_failures']
        
        try:
            while True:
                random.shuffle(ovpn_files)
                
                for ovpn_file in ovpn_files:
                    try:
                        if self.run_vpn_session(ovpn_file, username, password):
                            failure_count = 0
                            self.logger.success(f"Completed session with {ovpn_file}")
                        else:
                            failure_count += 1
                            self.logger.error(f"Session failed with {ovpn_file} (failure {failure_count})")
                            
                            if failure_count >= max_failures:
                                self.logger.error("Maximum failures reached, activating kill switch")
                                self.kill_switch.emergency_shutdown()
                    
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        failure_count += 1
                        self.logger.error(f"Unexpected error with {ovpn_file}: {e}")
                        
                        if failure_count >= max_failures:
                            self.kill_switch.emergency_shutdown()
        
        except KeyboardInterrupt:
            self.logger.info("VPN rotation stopped by user")
        
        finally:
            self.disconnect_vpn() 