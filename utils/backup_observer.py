from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .log_manager import get_log_manager

class BackupObserver(ABC):
    """Interface abstrata para observadores de backup"""
    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]):
        pass

class BackupSubject:
    """Classe base para objetos que podem ser observados"""
    def __init__(self):
        self._observers: List[object] = []
    
    def attach(self, observer: object):
        """Anexa um observador que implementa o método update"""
        if observer not in self._observers and hasattr(observer, 'update'):
            self._observers.append(observer)
    
    def detach(self, observer: object):
        if observer in self._observers:
            self._observers.remove(observer)
    
    def _notify_observers(self, event_type: str, data: Dict[str, Any]):
        for observer in self._observers:
            try:
                observer.update(event_type, data)
            except Exception as e:
                print(f"Erro ao notificar observador: {e}")


class LogBackupObserver(BackupObserver):
    def __init__(self):
        self.log_manager = get_log_manager()
    
    def update(self, event_type: str, data: Dict[str, Any]):
        if event_type == "backup_started":
            self.log_manager.log_info("Iniciando backup...")
        elif event_type == "checking_connectivity":
            self.log_manager.log_info("Verificando conectividade e permissões...")
        elif event_type == "environment_ready":
            self.log_manager.log_info("Ambiente pronto — iniciando backup.")
        elif event_type == "counting_files":
            total_files = data.get('total_files', 0)
            total_size = data.get('total_size', 0)
            self.log_manager.log_info(f"Total de arquivos: {total_files} arquivos / {total_size:.2f} GB")
        elif event_type == "copying_files":
            self.log_manager.log_info("Copiando arquivos...")
        elif event_type == "progress_update":
            progress = data.get('progress', 0)
            files_copied = data.get('files_copied', 0)
            total_files = data.get('total_files', 0)
            self.log_manager.log_info(f"Progresso: {progress}% concluído — {files_copied} de {total_files} arquivos copiados.")
        elif event_type == "validating":
            self.log_manager.log_info("Verificando integridade dos arquivos...")
        elif event_type == "backup_registered":
            self.log_manager.log_info("Backup registrado no histórico.")
        elif event_type == "backup_completed":
            duration = data.get('duration', 0)
            hours, remainder = divmod(int(duration), 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.log_manager.log_info(f"Backup finalizado — duração: {duration_str}")
        elif event_type == "error":
            error_type = data.get('error_type', '')
            message = ""
            if error_type == 'auth_error':
                message = 'Erro: Falha na autenticação.'
            elif error_type == 'connection_lost':
                message = 'Erro: Conexão perdida.'
            elif error_type == 'insufficient_space':
                message = 'Erro: Espaço insuficiente.'
            elif error_type == 'inaccessible_file':
                message = 'Erro: Arquivo inacessível.'
            else:
                message = f'Erro: {data.get("message", "Erro desconhecido")}'
            self.log_manager.log_error(message)