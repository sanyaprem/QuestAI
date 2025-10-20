# frontend/logging_config.py
"""
Centralized logging configuration for frontend.
This ensures logs work properly with Streamlit.
"""

import logging
import pathlib
import sys

def setup_frontend_logging():
    """
    Setup logging that works with Streamlit.
    Returns the configured logger.
    """
    # Create logs directory in project root
    log_dir = pathlib.Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "frontend.log"
    
    # Get root logger
    root_logger = logging.getLogger()
    
    # Remove all existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set level
    root_logger.setLevel(logging.DEBUG)
    
    # Create formatters
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with immediate flushing
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Force immediate write (no buffering)
    class FlushingFileHandler(logging.FileHandler):
        def emit(self, record):
            super().emit(record)
            self.flush()
    
    flushing_handler = FlushingFileHandler(log_file, mode='a', encoding='utf-8')
    flushing_handler.setLevel(logging.DEBUG)
    flushing_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Add handlers to root logger
    root_logger.addHandler(flushing_handler)
    root_logger.addHandler(console_handler)
    
    # Also configure Streamlit's logger
    streamlit_logger = logging.getLogger('streamlit')
    streamlit_logger.addHandler(flushing_handler)
    
    # Test logging
    logger = logging.getLogger(__name__)
    logger.info("=" * 70)
    logger.info("Frontend logging initialized")
    logger.info(f"Log file: {log_file.absolute()}")
    logger.info("=" * 70)
    
    return logger