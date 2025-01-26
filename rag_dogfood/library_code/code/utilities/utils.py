import logging
import os
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def log_message(class_name, module_name, description):
    frame = logging.currentframe().f_back  # Get the caller's frame
    filename = os.path.basename(frame.f_code.co_filename)  # Extract actual filename
    lineno = frame.f_lineno  # Get line number

    logging.info(f"class: {class_name}, module: {module_name}, file: {filename}, log: {description}, line: {lineno}")
