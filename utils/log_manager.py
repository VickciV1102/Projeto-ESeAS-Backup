import threading
import logging
import os

from datetime import datetime
from typing import Optional
from models.backup_logs_model import BackupLog

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
        """Log de informação"""
        self.logger.info(message)
        print(f"[INFO] {message}")

    def log_error(self, message: str, exception: Optional[Exception] = None):
        """Log de erro"""
        formatted_message = message
        if exception:
            formatted_message += f" - Exception: {str(exception)}"
        self.logger.error(formatted_message)
        print(f"[ERROR] {formatted_message}")

    def log_warning(self, message: str):
        """Log de aviso"""
        self.logger.warning(message)
        print(f"[WARNING] {message}")

    def log_backup_start(self, backup_type: str):
        """Registra o início de um backup"""
        self.log_info(f"Backup iniciado - Tipo: {backup_type}")

    def log_backup_complete(self, user_id, backup_type, duration, **kwargs):
        """Registra um backup completo com todos os detalhes"""
        try:
            BackupLog.create(
                user_id=user_id,
                backup_type=backup_type,
                ticket_number=kwargs.get('ticket_number', None),
                duration=duration,
                end_time=datetime.now(),
                source_path=kwargs.get('source_path', ''),
                destination_path=kwargs.get('destination_path', ''),
                total_size=kwargs.get('total_size', 0),
                total_files=kwargs.get('total_files', 0),
                copied_files=kwargs.get('copied_files', 0),
                status=kwargs.get('status', 'Concluído')
            )
            self.log_info(f"Backup registrado: {backup_type}")
        except Exception as e:
            self.log_error(f"Erro ao registrar backup: {str(e)}", e)
    
    def log_backup_error(self, user_id, backup_type, error_message):
        """Registra um erro de backup"""
        try:
            BackupLog.create(
                user_id=user_id,
                backup_type=backup_type,
                status=f'Erro: {error_message}',
                end_time=datetime.now()
            )
            self.log_error(f"Erro no backup {backup_type}: {error_message}")
        except Exception as e:
            self.log_error(f"Erro ao registrar erro de backup: {str(e)}", e)

def get_log_manager() -> LogManager:
    return LogManager()