import os
from typing import Dict
from .log_manager import LogManager
from utils.observer import BackupSubject

class BackupManager(BackupSubject):
    def __init__(self):
        super().__init__()
        self.log_manager = LogManager()
        self.backup_progress = 0
        self.current_operation = ""
        
    def _check_connectivity(self, backup_config: Dict) -> bool:
        # Verifica conectividade e permissões dos diretórios
        self._notify_observers("checking_connectivity", {})
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
                # Notificar ambiente pronto
                self._notify_observers("environment_ready", {})
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
        
        self._notify_observers("counting_files", {
            "total_files": total_files,
            "total_size": total_size / (1024 * 1024 * 1024)  # Converter para GB
        })
        
        for root, _, files in os.walk(path):
            total_files += len(files)
            for name in files:
                try:
                    total_size += os.path.getsize(os.path.join(root, name))
                except OSError:
                    continue
                
        self._notify_observers("counting_files", {
            "total_files": total_files,
            "total_size": total_size / (1024 * 1024 * 1024)  # Converter para GB
        })
                
        return total_files, total_size
    
    def _copy_files(self, source_path: str, dest_path: str, total_files) -> None:
        self._notify_observers("copying_files", {})
        files_copied = 0
        
        for root, _, files in os.walk(source_path):
            for file in files:
                source_file = os.path.join(root, file)
                rel_path = os.path.relpath(source_file, source_path)
                dest_file = os.path.join(dest_path, rel_path)
                
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
    
    def _validate_backup(self, source_path: str, dest_path: str):
        """Valida se todos os arquivos foram copiados corretamente"""
        self._notify_observers("validating", {})
        
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
        
        if errors:
            self._notify_observers("error", {
                "error_type": "validation_failed",
                "message": f"Erros na validação: {', '.join(validation_errors)}"
            })
            
            raise Exception("Backup validation failed with errors: " + ", ".join(errors))
    