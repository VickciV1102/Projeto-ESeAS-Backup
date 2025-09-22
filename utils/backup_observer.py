from abc import ABC, abstractmethod
from typing import List, Dict, Any
from log_manager import get_log_manager

class BackupObserver(ABC):
    
    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]):
        pass

class BackupSubject:
    
    def __init__(self):
        self._observers: List[BackupObserver] = []
    
    def attach(self, observer: BackupObserver):
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: BackupObserver):
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
        message = data.get('message', '')
        
        if event_type == "backup_started":
            self.log_manager.log_info(f"Observer: {message}")
        elif event_type == "progress_updated":
            progress = data.get('progress', 0)
            self.log_manager.log_info(f"Observer: Progresso {progress}% - {message}")
        elif event_type == "backup_completed":
            duration = data.get('duration', 0)
            self.log_manager.log_info(f"Observer: {message} - Duração: {duration:.2f}s")
        elif event_type == "backup_error":
            error = data.get('error', '')
            self.log_manager.log_error(f"Observer: {message} - Erro: {error}")