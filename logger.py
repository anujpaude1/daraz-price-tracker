from prisma import Prisma
import logging
import os

def setup_logger(name: str, log_file: str = 'app.log') -> logging.Logger:
    """Set up and return a logger with the specified name and log file."""
    # Clear the log file
    if os.path.exists(log_file):
        os.remove(log_file)

    # Create a custom logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create handlers
    c_handler = logging.StreamHandler()
    f_handler = logging.FileHandler(log_file)

    # Create formatters and add them to handlers
    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    c_handler.setFormatter(c_format)
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)

    return logger

# Set up logging
def main():
    logger = setup_logger(__name__)


# Example usage
if __name__ == "__main__":
    main()
