import threading
import logging
import os

from datetime import datetime
from typing import Optional

class LogManager:
    _instance: Optional['LogManager'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'LogManager':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._setup_logger()

    def _setup_logger(self):
        log_dir = "C:/BlueMacaw/logs/"

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        self.logger = logging.getLogger('BlueMacawBackup')
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        log_filename = f"{log_dir}/backup_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def log_info(self, message: str):
        formatted_message = f"[User: {user_id}] {message}" if user_id else message
        self.logger.info(formatted_message)

    def log_error(self, message: str, exception: Optional[Exception] = None):
        formatted_message = message
        if exception:
            formatted_message += f" - Exception: {str(exception)}"
        self.logger.error(formatted_message)

    def log_warning(self, message: str):
        formatted_message = f"[User: {user_id}] {message}" if user_id else message
        self.logger.warning(formatted_message)

    def log_backup_start(self, backup_type: str):
        self.log_info(f"Backup iniciado - Tipo: {backup_type}", user_id)

    def log_backup_complete(self, backup_type: str, duration: float):
        self.log_info(f"Backup concluído - Tipo: {backup_type} - Duração: {duration:.2f}s", user_id)

    def log_backup_error(self, backup_type: str, error: str):
        self.log_error(f"Erro no backup - Tipo: {backup_type} - Erro: {error}", user_id)

def get_log_manager() -> LogManager:
    return LogManager()