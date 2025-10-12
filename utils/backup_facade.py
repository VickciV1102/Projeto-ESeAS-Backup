import time
import os
from typing import Dict, List, Tuple
from .log_manager import get_log_manager
from .backup_observer import BackupSubject

class BackupFacade(BackupSubject):
    
    def __init__(self):
        super().__init__()
        self.log_manager = get_log_manager()
        self.backup_progress = 0
        self.current_operation = ""
        self.is_backup_running = False
        
    def _check_connectivity(self, backup_config: Dict) -> bool:
        """Verifica conectividade e permissões dos diretórios"""
        try:
            source_path = backup_config.get('source_path')
            dest_path = backup_config.get('destination_path')
            
            # Verificar se os caminhos existem
            if not os.path.exists(source_path):
                raise ValueError("Caminho de origem não existe")
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
                
            # Verificar permissões
            test_file = os.path.join(dest_path, '.test')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
            except Exception:
                raise ValueError("Sem permissão de escrita no destino")
                
            return True
        except Exception as e:
            self._notify_observers("error", {
                "error_type": "auth_error",
                "message": str(e)
            })
            return False

    def _count_files(self, path: str) -> tuple:
        """Conta arquivos e calcula tamanho total"""
        total_files = 0
        total_size = 0
        for root, _, files in os.walk(path):
            total_files += len(files)
            for name in files:
                try:
                    total_size += os.path.getsize(os.path.join(root, name))
                except OSError:
                    continue
        return total_files, total_size
    
    def execute_full_backup(self, user_id: int, backup_config: Dict) -> bool:
        try:
            self.is_backup_running = True
            self.backup_progress = 0
            start_time = time.time()
            
            # Notificar início do backup
            self._notify_observers("backup_started", {"progress": 0})
            
            # Etapa 1: Verificar conectividade e permissões
            self._notify_observers("checking_connectivity", {})
            if not self._check_connectivity(backup_config):
                raise ValueError("Erro de conectividade ou permissões")
                
            # Notificar ambiente pronto
            self._notify_observers("environment_ready", {})
            
            # Etapa 2: Contagem de arquivos e tamanho total
            source_path = backup_config.get('source_path')
            total_files, total_size = self._count_files(source_path)
            self._notify_observers("counting_files", {
                "total_files": total_files,
                "total_size": total_size / (1024 * 1024 * 1024)  # Converter para GB
            })
            
            # Etapa 3: Iniciar cópia
            self._notify_observers("copying_files", {})
            files_copied = 0
            
            for root, _, files in os.walk(source_path):
                for file in files:
                    source_file = os.path.join(root, file)
                    rel_path = os.path.relpath(source_file, source_path)
                    dest_file = os.path.join(backup_config['destination_path'], rel_path)
                    
                    # Criar diretório de destino se não existir
                    os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                    
                    # Copiar arquivo
                    try:
                        with open(source_file, 'rb') as src, open(dest_file, 'wb') as dst:
                            dst.write(src.read())
                    except Exception as e:
                        self._notify_observers("error", {
                            "error_type": "inaccessible_file",
                            "message": f"Erro ao copiar {source_file}: {str(e)}"
                        })
                        continue
                    
                    files_copied += 1
                    progress = int((files_copied / total_files) * 100)
                    
                    self._notify_observers("progress_update", {
                        "progress": progress,
                        "files_copied": files_copied,
                        "total_files": total_files
                    })
            
            # Etapa 4: Validar os arquivos copiados
            self._notify_observers("validating", {})
            validation_errors = self._validate_backup(source_path, backup_config['destination_path'])
            
            if validation_errors:
                self._notify_observers("error", {
                    "error_type": "validation_failed",
                    "message": f"Erros na validação: {', '.join(validation_errors)}"
                })
                return False

            # Etapa 5: Finalizar e registrar no histórico
            duration = time.time() - start_time
            self._notify_observers("backup_completed", {
                "duration": duration,
                "total_files": total_files,
                "total_size": total_size
            })
            
            # Log no banco de dados
            self.log_manager.log_backup_complete(user_id, "Full Backup", duration)
            
            return True
        except Exception as e:
            error_type = "unknown"
            if "conectividade" in str(e):
                error_type = "connection_lost"
            elif "permissões" in str(e):
                error_type = "auth_error"
            elif "espaço" in str(e):
                error_type = "insufficient_space"
            
            self._notify_observers("error", {
                "error_type": error_type,
                "message": str(e)
            })
            return False
        finally:
            self.is_backup_running = False

            duration = time.time() - start_time
            self.log_manager.log_backup_complete(user_id, "Full Backup", duration)

            self._notify_observers("backup_completed", {
                "progress": 100, 
                "message": "Backup concluído com sucesso!",
                "duration": duration
            })

            return True
    
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
            self._notify_observers("error", {
                "error_type": "unknown",
                "message": f"Erro durante o backup: {str(e)}"
            })
            return False
        finally:
            self.is_backup_running = False
    
    def _validate_backup(self, source_path: str, dest_path: str) -> List[str]:
        """Valida se todos os arquivos foram copiados corretamente"""
        errors = []
        
        # Percorre todos os arquivos na origem
        for root, _, files in os.walk(source_path):
            for file in files:
                source_file = os.path.join(root, file)
                # Calcula o caminho relativo e reconstrói no destino
                rel_path = os.path.relpath(source_file, source_path)
                dest_file = os.path.join(dest_path, rel_path)
                
                # Verifica se o arquivo existe no destino
                if not os.path.exists(dest_file):
                    errors.append(f"Arquivo não encontrado no destino: {rel_path}")
                    continue
                
                # Verifica o tamanho dos arquivos
                try:
                    source_size = os.path.getsize(source_file)
                    dest_size = os.path.getsize(dest_file)
                    
                    if source_size != dest_size:
                        errors.append(f"Tamanho diferente para o arquivo: {rel_path}")
                except OSError as e:
                    errors.append(f"Erro ao verificar arquivo {rel_path}: {str(e)}")
        
        return errors

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
    
    def executefullbackup(self, userid: int, backupconfig: dict):
        origem_nome = backupconfig.get('origem_nome')
        origem_caminho = backupconfig.get('origem_caminho')
        destino_nome = backupconfig.get('destino_nome')
        destino_caminho = backupconfig.get('destino_caminho')
        # Adicione as operações de backup usando esses dados...
