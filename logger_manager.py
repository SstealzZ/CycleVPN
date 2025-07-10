import sys
from pathlib import Path
from loguru import logger
from colorama import Fore, Style


class LoggerManager:
    """
    Manages logging configuration and colored output for CycleVPN.
    
    This class configures loguru for both file and console logging
    with color support and proper formatting.
    """
    
    def __init__(self, config_manager):
        """
        Initialize the logger manager.
        
        Args:
            config_manager: Instance of ConfigManager for logging configuration
        """
        self.config_manager = config_manager
        self.setup_logging()
    
    def setup_logging(self):
        """
        Configure loguru logger with file and console handlers.
        """
        logging_config = self.config_manager.get_logging_config()
        paths_config = self.config_manager.get_paths_config()
        
        logger.remove()
        
        log_file_path = Path(paths_config['log_file'])
        
        logger.add(
            log_file_path,
            level=logging_config['level'],
            format=logging_config['format'],
            rotation=logging_config['rotation'],
            retention=logging_config['retention'],
            enqueue=True
        )
        
        logger.add(
            sys.stdout,
            level=logging_config['level'],
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{message}</cyan>",
            colorize=True
        )
        
        logger.info("Logger initialized successfully")
    
    def log_and_print(self, message: str, level: str = "info", color: str = Fore.RESET):
        """
        Log a message and print it with specified color.
        
        Args:
            message: The message to log and print
            level: Log level (info, warning, error, debug)
            color: Color code for console output
        """
        print(color + message + Style.RESET_ALL)
        
        level_map = {
            "info": logger.info,
            "warning": logger.warning,
            "error": logger.error,
            "debug": logger.debug,
            "success": logger.success
        }
        
        log_function = level_map.get(level.lower(), logger.info)
        log_function(message)
    
    def info(self, message: str, color: str = Fore.CYAN):
        """
        Log and print an info message.
        
        Args:
            message: The message to log
            color: Color for console output
        """
        self.log_and_print(message, "info", color)
    
    def success(self, message: str, color: str = Fore.GREEN):
        """
        Log and print a success message.
        
        Args:
            message: The message to log
            color: Color for console output
        """
        self.log_and_print(message, "success", color)
    
    def warning(self, message: str, color: str = Fore.YELLOW):
        """
        Log and print a warning message.
        
        Args:
            message: The message to log
            color: Color for console output
        """
        self.log_and_print(message, "warning", color)
    
    def error(self, message: str, color: str = Fore.RED):
        """
        Log and print an error message.
        
        Args:
            message: The message to log
            color: Color for console output
        """
        self.log_and_print(message, "error", color)
    
    def debug(self, message: str, color: str = Fore.MAGENTA):
        """
        Log and print a debug message.
        
        Args:
            message: The message to log
            color: Color for console output
        """
        self.log_and_print(message, "debug", color) 