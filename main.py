import sys
import signal
from pathlib import Path
from colorama import init, Fore

from config_manager import ConfigManager
from logger_manager import LoggerManager
from kill_switch import KillSwitch
from vpn_manager import VPNManager


class CycleVPNApplication:
    """
    Main application class for CycleVPN.
    
    This class coordinates all components of the CycleVPN application,
    providing a unified interface for VPN rotation and management.
    """
    
    def __init__(self):
        """
        Initialize the CycleVPN application.
        """
        init(autoreset=True)
        
        try:
            self.config_manager = ConfigManager()
            self.logger_manager = LoggerManager(self.config_manager)
            self.kill_switch = KillSwitch(self.config_manager, self.logger_manager)
            self.vpn_manager = VPNManager(
                self.config_manager, 
                self.logger_manager, 
                self.kill_switch
            )
            
            self.setup_signal_handlers()
            self.logger_manager.success("CycleVPN application initialized successfully")
            
        except Exception as e:
            print(f"{Fore.RED}Failed to initialize CycleVPN: {e}")
            sys.exit(1)
    
    def setup_signal_handlers(self):
        """
        Setup signal handlers for graceful shutdown.
        """
        def signal_handler(signum, frame):
            self.logger_manager.warning("Received interrupt signal, shutting down...")
            self.shutdown()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def display_welcome_message(self):
        """
        Display welcome message and application information.
        """
        welcome_message = """
        ╔══════════════════════════════════════════════════════════════╗
        ║                        CycleVPN v2.0                         ║
        ║                  Advanced VPN Rotation Tool                  ║
        ╠══════════════════════════════════════════════════════════════╣
        ║  • Automated VPN server rotation                             ║
        ║  • Advanced kill switch protection                           ║
        ║  • Secure credential management                              ║
        ║  • Comprehensive logging with loguru                        ║
        ║  • Configurable parameters                                   ║
        ║  • Service integration (Transmission)                       ║
        ╚══════════════════════════════════════════════════════════════╝
        """
        
        print(Fore.CYAN + welcome_message)
        self.logger_manager.info("CycleVPN v2.0 - Advanced VPN Rotation Tool")
    
    def display_configuration_summary(self):
        """
        Display current configuration summary.
        """
        session_config = self.config_manager.get_session_config()
        network_config = self.config_manager.get_network_config()
        
        self.logger_manager.info("Configuration Summary:")
        self.logger_manager.info(f"  • Cooldown: {session_config['cooldown_seconds']} seconds")
        self.logger_manager.info(f"  • Kill Switch: {'Enabled' if session_config['kill_switch_enabled'] else 'Disabled'}")
        self.logger_manager.info(f"  • Max Failures: {session_config['max_connection_failures']}")
        self.logger_manager.info(f"  • VPN Timeout: {network_config['vpn_establish_wait']} seconds")
    
    def verify_prerequisites(self) -> bool:
        """
        Verify that all prerequisites are met before starting.
        
        Returns:
            True if all prerequisites are met, False otherwise
        """
        self.logger_manager.info("Verifying prerequisites...")
        
        ovpn_files = self.vpn_manager.discover_ovpn_files()
        if not ovpn_files:
            self.logger_manager.error("No OpenVPN configuration files found")
            return False
        
        self.logger_manager.info(f"Found {len(ovpn_files)} OpenVPN configuration files")
        
        try:
            initial_ip = self.kill_switch.get_current_ip_address()
            if not initial_ip:
                self.logger_manager.error("Unable to determine current IP address")
                return False
            
            self.logger_manager.info(f"Current IP address: {initial_ip}")
            
        except Exception as e:
            self.logger_manager.error(f"Network connectivity check failed: {e}")
            return False
        
        self.logger_manager.success("All prerequisites verified successfully")
        return True
    
    def run_application(self):
        """
        Run the main application loop.
        """
        try:
            self.display_welcome_message()
            self.display_configuration_summary()
            
            if not self.verify_prerequisites():
                self.logger_manager.error("Prerequisites verification failed")
                return False
            
            self.logger_manager.info("Starting VPN rotation...")
            
            username, password = self.vpn_manager.get_user_credentials()
            
            self.logger_manager.info("Initiating continuous VPN rotation")
            self.vpn_manager.run_continuous_vpn_rotation(username, password)
            
        except KeyboardInterrupt:
            self.logger_manager.info("Application stopped by user")
        except Exception as e:
            self.logger_manager.error(f"Application error: {e}")
            return False
        
        return True
    
    def shutdown(self):
        """
        Perform graceful shutdown of the application.
        """
        self.logger_manager.info("Shutting down CycleVPN...")
        
        try:
            self.vpn_manager.disconnect_vpn()
            self.vpn_manager.cleanup_temporary_credentials()
            
            if self.config_manager.get_security_config()['clear_credentials_on_exit']:
                self.logger_manager.info("Clearing credentials for security")
            
            self.logger_manager.success("CycleVPN shutdown completed")
            
        except Exception as e:
            self.logger_manager.error(f"Error during shutdown: {e}")
        
        finally:
            sys.exit(0)


def main():
    """
    Main entry point of the CycleVPN application.
    """
    try:
        app = CycleVPNApplication()
        success = app.run_application()
        
        if not success:
            sys.exit(1)
            
    except Exception as e:
        print(f"{Fore.RED}Critical error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
