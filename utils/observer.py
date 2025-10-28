from abc import ABC, abstractmethod
from typing import List, Dict, Any
from controllers.manager.backup_session_manager import BackupSessionManager
from controllers.manager.log_manager import LogManager       
from datetime import datetime 

class Observer(ABC):
    @abstractmethod
    def update(self, event_type: str, data: Dict[str, Any]):
        pass
    
class BackupLogObserver(Observer):
    def __init__(self, screen):
        self.log_manager = LogManager()
        self.backup_session = BackupSessionManager()
        self.screen = screen

    def update(self, event_type: str, data: dict):
        """Implementação do método do BackupObserver"""
        if event_type == "backup_started":
            self.update_status('init_status', 'Iniciando backup...', True)
        elif event_type == "checking_connectivity":
            self.update_status('connectivity_status', 'Verificando conectividade e permissões...', True)
        elif event_type == "environment_ready":
            self.update_status('env_ready_status', 'Ambiente pronto — iniciando backup.', True)
        elif event_type == "counting_files":
            total_files = data.get('total_files', 0)
            total_size = data.get('total_size', 0)
            self.update_status('files_count_status', f'Total de arquivos: {total_files} arquivos / {total_size:.2f} GB', True)
        elif event_type == "copying_files":
            self.update_status('copy_status', 'Copiando arquivos...', True)
        elif event_type == "progress_update":
            progress = data.get('progress', 0)
            files_copied = data.get('files_copied', 0)
            total_files = data.get('total_files', 0)
            self.update_status('progress_status', f"Progresso: {progress}% concluído — {files_copied} de {total_files} arquivos copiados.", True)
        elif event_type == "validating":
            self.update_status('validation_status', 'Verificando integridade dos arquivos...', True)
        elif event_type == "backup_registered":
            self.update_status('validation_status', 'Backup registrado no histórico.', True)
        elif event_type == "backup_completed":
            duration = data.get('duration', 0)
            hours, remainder = divmod(int(duration), 3600)
            minutes, seconds = divmod(remainder, 60)
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.update_status('finish_status', f'Backup finalizado — duração: {duration_str}', True)
            
            # Armazena dados na sessão
            if not self.backup_session.start_time:
                self.backup_session.start_time = datetime.now()
            
            # O tamanho vem em bytes do backup_facade
            total_size_bytes = data.get('total_size', 0)
            total_size_gb = total_size_bytes / (1024 * 1024 * 1024)  # Converter para GB para exibição
            
            self.backup_session.set_file_backup_data(
                files=data.get('total_files', 0),
                size=total_size_bytes,
                source=self.screen.ids.source_path_input.text,
                destination=self.screen.ids.destination_path_input.text
            )
            
            print("=" * 50)
            print("BACKUP DE ARQUIVOS CONCLUÍDO!")
            print(f"Dados armazenados na sessão:")
            print(f"  - Arquivos de documentos: {data.get('total_files', 0)}")
            print(f"  - Tamanho total (GB): {total_size_gb:.2f}")
            print(f"  - Tamanho total (bytes): {total_size_bytes}")
            print(f"  - Origem: {self.screen.ids.source_path_input.text}")
            print(f"  - Destino: {self.screen.ids.destination_path_input.text}")
            print("=" * 50)
            
            # Habilita o botão Next quando o backup é concluído
            self.screen.ids.next_button.disabled = False
        elif event_type == "error":
            error_type = data.get('error_type', '')
            if error_type == 'auth_error':
                self.show_error('Erro: Falha na autenticação.')
            elif error_type == 'connection_lost':
                self.show_error('Erro: Conexão perdida.')
            elif error_type == 'insufficient_space':
                self.show_error('Erro: Espaço insuficiente.')
            elif error_type == 'inaccessible_file':
                self.show_error('Erro: Arquivo inacessível.')
            elif error_type == 'validation_failed':
                self.show_error(data.get("message", "Erro na validação do backup."))
            else:
                self.show_error(f'Erro: {data.get("message", "Erro desconhecido")}')
                
    def show_error(self, message):
        """Mostra uma mensagem de erro"""
        # Escapar caracteres especiais e garantir que a mensagem seja uma string
        message = str(message).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.log_manager.log_error(message)
        self.screen.ids.error_status.text = message
        self.screen.ids.error_status.color = (1, 0.2, 0.2, 1)  # Vermelho

    def update_status(self, label_id, message, success=True):
        """Atualiza o status de um label específico"""
        self.log_manager.log_info(message)
        if label_id in self.screen.ids:
            label = self.screen.ids[label_id]
            label.text = message
            label.color = (0.11, 0.55, 0.27, 1) if success else (1, 0.2, 0.2, 1)
            
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
                