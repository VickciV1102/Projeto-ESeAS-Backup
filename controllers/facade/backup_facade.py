from ..manager.backup_manager import BackupManager
import time

class BackupFacade:
    def __init__(self):
        self.manager = BackupManager()

    def attach_observer(self, observer):
        self.manager.attach(observer)

    def execute_full_backup(self, backup_config: dict) -> bool:
        try:
            self.manager._notify_observers("backup_started", {"progress": 0})
            
            start_time = time.time()
            
            # Etapa 1: Checando conectividade e acesso as pastas
            if not self.manager._check_connectivity(backup_config):
                    raise ValueError("Erro de conectividade ou permissões")
                
            source_path = backup_config.get('source_path')
            destination_path = backup_config.get('destination_path')
            
            # Etapa 2: Contagem de arquivos e tamanho total
            total_files, total_size = self.manager._count_files(source_path)
            
            # Etapa 3: Iniciar cópia
            self.manager._copy_files(source_path, destination_path, total_files)
            
            # Etapa 4: Validar os arquivos copiados
            self.manager._validate_backup(source_path, destination_path)

            # Etapa 5: Finalizar e registrar no histórico
            duration = time.time() - start_time
                
            self.manager._notify_observers("backup_completed", {
                "duration": duration,
                "total_files": total_files,
                "total_size": total_size
            })
            
            return True
        except Exception as e:
            error_type = "unknown"
            if "conectividade" in str(e):
                error_type = "connection_lost"
            elif "permissões" in str(e):
                error_type = "auth_error"
            elif "espaço" in str(e):
                error_type = "insufficient_space"
            
            self.manager._notify_observers("error", {
                "error_type": error_type,
                "message": str(e)
            })
            
            return False