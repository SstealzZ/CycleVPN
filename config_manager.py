import json
import os
from pathlib import Path
from loguru import logger


class ConfigManager:
    """
    Manages configuration loading and validation for CycleVPN.
    
    This class handles reading configuration from JSON files and provides
    validated access to configuration parameters.
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        self.config_data = {}
        self.load_configuration()
    
    def load_configuration(self):
        """
        Load configuration from the JSON file.
        
        Raises:
            FileNotFoundError: If configuration file doesn't exist
            json.JSONDecodeError: If configuration file is malformed
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config_data = json.load(file)
            self.validate_configuration()
            logger.info(f"Configuration loaded from {self.config_path}")
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            self.create_default_configuration()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            raise
    
    def create_default_configuration(self):
        """
        Create a default configuration file if none exists.
        """
        default_config = {
            "network": {
                "connection_timeout": 10,
                "vpn_establish_wait": 5,
                "ip_check_retries": 3,
                "ip_check_timeout": 5
            },
            "session": {
                "cooldown_seconds": 20,
                "max_connection_failures": 3,
                "kill_switch_enabled": True
            },
            "services": {
                "transmission_service": "transmission",
                "openvpn_service": "openvpn"
            },
            "paths": {
                "ovpn_directory": "./openvpn",
                "log_file": "cyclevpn.log",
                "temp_directory": "/tmp"
            },
            "logging": {
                "level": "INFO",
                "rotation": "10 MB",
                "retention": "7 days",
                "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
            },
            "security": {
                "clear_credentials_on_exit": True,
                "secure_temp_files": True,
                "verify_ip_change": True
            }
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as file:
            json.dump(default_config, file, indent=2)
        
        self.config_data = default_config
        logger.info(f"Default configuration created at {self.config_path}")
    
    def validate_configuration(self):
        """
        Validate that all required configuration sections exist.
        
        Raises:
            ValueError: If required configuration sections are missing
        """
        required_sections = ['network', 'session', 'services', 'paths', 'logging', 'security']
        
        for section in required_sections:
            if section not in self.config_data:
                raise ValueError(f"Missing required configuration section: {section}")
        
        self.ensure_directories_exist()
    
    def ensure_directories_exist(self):
        """
        Create necessary directories if they don't exist.
        """
        ovpn_dir = Path(self.config_data['paths']['ovpn_directory'])
        temp_dir = Path(self.config_data['paths']['temp_directory'])
        
        ovpn_dir.mkdir(parents=True, exist_ok=True)
        temp_dir.mkdir(parents=True, exist_ok=True)
    
    def get_network_config(self) -> dict:
        """
        Get network configuration parameters.
        
        Returns:
            Dictionary containing network configuration
        """
        return self.config_data['network']
    
    def get_session_config(self) -> dict:
        """
        Get session configuration parameters.
        
        Returns:
            Dictionary containing session configuration
        """
        return self.config_data['session']
    
    def get_services_config(self) -> dict:
        """
        Get services configuration parameters.
        
        Returns:
            Dictionary containing services configuration
        """
        return self.config_data['services']
    
    def get_paths_config(self) -> dict:
        """
        Get paths configuration parameters.
        
        Returns:
            Dictionary containing paths configuration
        """
        return self.config_data['paths']
    
    def get_logging_config(self) -> dict:
        """
        Get logging configuration parameters.
        
        Returns:
            Dictionary containing logging configuration
        """
        return self.config_data['logging']
    
    def get_security_config(self) -> dict:
        """
        Get security configuration parameters.
        
        Returns:
            Dictionary containing security configuration
        """
        return self.config_data['security']
    
    def get_cooldown_seconds(self) -> int:
        """
        Get the cooldown duration in seconds.
        
        Returns:
            Cooldown duration in seconds
        """
        return self.config_data['session']['cooldown_seconds']
    
    def is_kill_switch_enabled(self) -> bool:
        """
        Check if the kill switch is enabled.
        
        Returns:
            True if kill switch is enabled, False otherwise
        """
        return self.config_data['session']['kill_switch_enabled'] 