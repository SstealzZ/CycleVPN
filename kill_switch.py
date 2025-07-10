import subprocess
import sys
import time
import psutil
import requests
from typing import Optional, List
from colorama import Fore


class KillSwitch:
    """
    Advanced kill switch implementation for CycleVPN.
    
    This class provides comprehensive network protection by monitoring
    VPN connection status and blocking network traffic when VPN fails.
    """
    
    def __init__(self, config_manager, logger_manager):
        """
        Initialize the kill switch.
        
        Args:
            config_manager: Instance of ConfigManager
            logger_manager: Instance of LoggerManager
        """
        self.config_manager = config_manager
        self.logger = logger_manager
        self.network_config = config_manager.get_network_config()
        self.security_config = config_manager.get_security_config()
        self.initial_ip = None
        self.vpn_process = None
        self.blocked_services = []
        
    def get_current_ip_address(self) -> Optional[str]:
        """
        Get the current public IP address with retry mechanism.
        
        Returns:
            Current public IP address or None if failed
        """
        ip_services = [
            "https://ifconfig.io/ip",
            "https://ipinfo.io/ip",
            "https://httpbin.org/ip",
            "https://api.ipify.org"
        ]
        
        for attempt in range(self.network_config['ip_check_retries']):
            for service in ip_services:
                try:
                    response = requests.get(
                        service,
                        timeout=self.network_config['ip_check_timeout']
                    )
                    if response.status_code == 200:
                        ip = response.text.strip()
                        if service == "https://httpbin.org/ip":
                            import json
                            ip = json.loads(ip)['origin']
                        self.logger.debug(f"IP obtained from {service}: {ip}")
                        return ip
                except requests.RequestException as e:
                    self.logger.debug(f"Failed to get IP from {service}: {e}")
                    continue
            
            if attempt < self.network_config['ip_check_retries'] - 1:
                self.logger.warning(f"IP check attempt {attempt + 1} failed, retrying...")
                time.sleep(2)
        
        self.logger.error("Failed to obtain IP address from all services")
        return None
    
    def store_initial_ip(self):
        """
        Store the initial IP address before VPN connection.
        """
        self.initial_ip = self.get_current_ip_address()
        if self.initial_ip:
            self.logger.info(f"Initial IP address stored: {self.initial_ip}")
        else:
            self.logger.error("Failed to store initial IP address")
    
    def verify_vpn_connection(self, expected_different_ip: bool = True) -> bool:
        """
        Verify if VPN connection is working properly.
        
        Args:
            expected_different_ip: Whether IP should be different from initial
            
        Returns:
            True if VPN is working correctly, False otherwise
        """
        if not self.security_config['verify_ip_change']:
            return True
        
        current_ip = self.get_current_ip_address()
        if not current_ip:
            self.logger.error("Cannot verify VPN connection - unable to get current IP")
            return False
        
        if expected_different_ip:
            is_connected = current_ip != self.initial_ip
            if is_connected:
                self.logger.success(f"VPN connection verified - IP changed to: {current_ip}")
            else:
                self.logger.error(f"VPN connection failed - IP unchanged: {current_ip}")
            return is_connected
        else:
            self.logger.info(f"Current IP: {current_ip}")
            return True
    
    def block_network_services(self, services: List[str]):
        """
        Block specified network services to prevent data leakage.
        
        Args:
            services: List of service names to block
        """
        if not self.config_manager.is_kill_switch_enabled():
            self.logger.info("Kill switch is disabled, skipping service blocking")
            return
        
        for service in services:
            try:
                self.stop_system_service(service)
                self.blocked_services.append(service)
                self.logger.warning(f"Blocked service: {service}")
            except Exception as e:
                self.logger.error(f"Failed to block service {service}: {e}")
    
    def unblock_network_services(self):
        """
        Unblock previously blocked network services.
        """
        for service in self.blocked_services:
            try:
                self.logger.info(f"Unblocking service: {service}")
            except Exception as e:
                self.logger.error(f"Failed to unblock service {service}: {e}")
        
        self.blocked_services.clear()
    
    def stop_system_service(self, service_name: str):
        """
        Stop a system service.
        
        Args:
            service_name: Name of the service to stop
        """
        try:
            result = subprocess.run(
                ["service", service_name, "stop"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.logger.success(f"Successfully stopped service: {service_name}")
            else:
                self.logger.error(f"Failed to stop service {service_name}: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout stopping service: {service_name}")
        except Exception as e:
            self.logger.error(f"Error stopping service {service_name}: {e}")
    
    def start_system_service(self, service_name: str):
        """
        Start a system service.
        
        Args:
            service_name: Name of the service to start
        """
        try:
            result = subprocess.run(
                ["service", service_name, "start"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.logger.success(f"Successfully started service: {service_name}")
            else:
                self.logger.error(f"Failed to start service {service_name}: {result.stderr}")
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout starting service: {service_name}")
        except Exception as e:
            self.logger.error(f"Error starting service {service_name}: {e}")
    
    def kill_vpn_processes(self):
        """
        Terminate all OpenVPN processes.
        """
        killed_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'openvpn':
                    proc.terminate()
                    killed_processes.append(proc.info['pid'])
                    self.logger.warning(f"Terminated OpenVPN process: {proc.info['pid']}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        if killed_processes:
            time.sleep(2)
            for pid in killed_processes:
                try:
                    proc = psutil.Process(pid)
                    if proc.is_running():
                        proc.kill()
                        self.logger.error(f"Force killed OpenVPN process: {pid}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
    
    def activate_kill_switch(self, services_to_block: List[str] = None):
        """
        Activate the kill switch to protect against data leakage.
        
        Args:
            services_to_block: List of services to block (default: ['transmission'])
        """
        if not self.config_manager.is_kill_switch_enabled():
            self.logger.info("Kill switch is disabled in configuration")
            return
        
        if services_to_block is None:
            services_to_block = ['transmission']
        
        self.logger.error("KILL SWITCH ACTIVATED - VPN connection failed!", Fore.RED)
        self.logger.error("Blocking network services to prevent data leakage...", Fore.RED)
        
        self.kill_vpn_processes()
        self.block_network_services(services_to_block)
        
        self.logger.error("All network services have been blocked for security", Fore.RED)
        self.logger.error("Fix VPN connection before continuing", Fore.RED)
    
    def emergency_shutdown(self):
        """
        Emergency shutdown of the application with full network protection.
        """
        self.logger.error("EMERGENCY SHUTDOWN INITIATED", Fore.RED)
        self.activate_kill_switch(['transmission', 'openvpn'])
        self.logger.error("Application terminated for security reasons", Fore.RED)
        sys.exit(1) 