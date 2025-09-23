import time

from typing import Dict, List
from .log_manager import get_log_manager
from .backup_observer import BackupSubject

class BackupFacade(BackupSubject):
    
    def __init__(self):
        super().__init__()
        self.log_manager = get_log_manager()
        self.backup_progress = 0
        self.current_operation = ""
        self.is_backup_running = False
    
    def execute_full_backup(self, user_id: int, backup_config: Dict) -> bool:
        try:
            self.is_backup_running = True
            self.backup_progress = 0
            start_time = time.time()
            
            self._notify_observers("backup_started", {"progress": 0, "message": "Iniciando backup..."})
            
            # Etapa 1: Validar configurações
            if not self._validate_backup_config(backup_config):
                raise ValueError("Configurações de backup inválidas")
            self._update_progress(20, "Configurações validadas")
            
            # Etapa 2: Preparar diretórios
            self._prepare_backup_directories(backup_config)
            self._update_progress(40, "Diretórios preparados")
            
            # Etapa 3: Backup de arquivos do usuário
            self._backup_user_files(backup_config.get('source_paths', []), backup_config.get('destination_path'))
            self._update_progress(60, "Arquivos de usuário copiados")
            
            # Etapa 4: Finalizar
            self._finalize_backup(backup_config.get('destination_path'))
            self._update_progress(80, "Backup realizado com sucesso!")
            
            # Etapa 5: Registrar backup no banco de dados
            self._register_backup_in_database(user_id, "Full Backup", duration)
            self._update_progress(100, "Backup registrado no banco de dados com sucesso!")

            duration = time.time() - start_time
            self.log_manager.log_backup_complete(user_id, "Full Backup", duration)

            self._notify_observers("backup_completed", {
                "progress": 100, 
                "message": "Backup concluído com sucesso!",
                "duration": duration
            })

            return True
            
        except Exception as e:
            self._notify_observers("backup_error", {
                "progress": self.backup_progress,
                "message": f"Erro durante o backup: {str(e)}",
                "error": str(e)
            })

            return False
        finally:
            self.is_backup_running = False
    
    def execute_quick_backup(self, user_id: int, source_paths: List[str], destination_path: str) -> bool:
        try:
            self.is_backup_running = True
            start_time = time.time()
            
            self._notify_observers("backup_started", {"progress": 0, "message": "Iniciando backup rápido..."})
            
            self._backup_user_files(source_paths, destination_path)
            self._update_progress(100, "Backup rápido concluído!")
            
            duration = time.time() - start_time
            self.log_manager.log_backup_complete(user_id, "Quick Backup", duration)
            self._notify_observers("backup_completed", {
                "progress": 100,
                "message": "Backup rápido concluído!",
                "duration": duration
            })
            
            return True
            
        except Exception as e:
            self.log_manager.log_backup_error(user_id, "Quick Backup", str(e))
            self._notify_observers("backup_error", {
                "progress": self.backup_progress,
                "message": f"Erro durante o backup: {str(e)}",
                "error": str(e)
            })
            return False
        finally:
            self.is_backup_running = False
    
    def _validate_backup_config(self, config: Dict) -> bool:
        pass
    
    def _prepare_backup_directories(self, config: Dict):
        pass
    
    def _backup_user_files(self, source_paths: List[str], destination_path: str):
        pass

    def _register_backup_in_database(self, user_id: int, backup_type: str, duration: float):
        pass
    
    def _finalize_backup(self, destination_path: str):
        pass
    
    def _update_progress(self, progress: int, message: str):
        self.backup_progress = progress
        self.current_operation = message
        self._notify_observers("progress_updated", {
            "progress": progress,
            "message": message
        })

    def get_backup_status(self) -> Dict:
        return {
            "is_running": self.is_backup_running,
            "progress": self.backup_progress,
            "current_operation": self.current_operation
        }