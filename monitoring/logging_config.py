import logging
import json
from datetime import datetime
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """Custom formatter to output logs as JSON."""

    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(log_dir='logs', log_level=logging.INFO):
    """
    Setup application logging configuration.

    Args:
        log_dir: Directory for log files
        log_level: Logging level
    """
    Path(log_dir).mkdir(exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    file_handler = logging.FileHandler(f'{log_dir}/app.log')
    file_handler.setLevel(log_level)
    file_formatter = JSONFormatter()
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    return root_logger
