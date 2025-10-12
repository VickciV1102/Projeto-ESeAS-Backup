import time
import os
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from utils.backup_facade import BackupFacade
from utils.backup_observer import BackupObserver
from abc import ABC

# Para abrir seletor de pastas no Windows
import tkinter as tk
from tkinter import filedialog

Builder.load_file('views/backup_view.kv')

class BackupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backup_facade = BackupFacade()
        self.backup_facade.attach(self)
        self.start_time = None
    
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
            # Habilita o botão Next quando o backup é concluído
            self.ids.next_button.disabled = False
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

    def open_source_dialog(self):
        root = tk.Tk()
        root.withdraw()  # Esconder janela principal do Tkinter
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.ids.source_path_input.text = folder_path
            self.ids.source_path_status.text = f"Pasta de origem: {folder_path}"
            self.ids.source_path_status.color = (0.11, 0.55, 0.27, 1)

    def open_destination_dialog(self):
        root = tk.Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.ids.destination_path_input.text = folder_path
            self.ids.dest_path_status.text = f"Pasta de destino: {folder_path}"
            self.ids.dest_path_status.color = (0.11, 0.55, 0.27, 1)

    def start_backup(self):
        # Reset status labels (mantendo os caminhos selecionados)
        self.reset_status()
        self.start_time = time.time()
        
        # Get paths and validate
        source_path = self.ids.source_path_input.text
        dest_path = self.ids.destination_path_input.text
        
        if not source_path or not dest_path:
            self.show_error("Erro: Selecione as pastas de origem e destino.")
            return
            
        # Configure and start backup
        backup_config = {
            'source_path': source_path,
            'destination_path': dest_path
        }
        
        try:
            # Start backup in facade
            self.backup_facade.execute_full_backup(1, backup_config)
        except Exception as e:
            self.show_error(f"Erro: {str(e)}")

    def show_error(self, message):
        """Mostra uma mensagem de erro"""
        # Escapar caracteres especiais e garantir que a mensagem seja uma string
        message = str(message).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        self.ids.error_status.text = message
        self.ids.error_status.color = (1, 0.2, 0.2, 1)  # Vermelho

    def update_status(self, label_id, message, success=True):
        """Atualiza o status de um label específico"""
        if label_id in self.ids:
            label = self.ids[label_id]
            label.text = message
            label.color = (0.11, 0.55, 0.27, 1) if success else (1, 0.2, 0.2, 1)



    def go_to_software_selection(self):
        """Navega para a tela de seleção de software"""
        self.manager.current = 'transfer_software_screen'

    def reset_status(self):
        """Reseta todos os status para o estado inicial"""
        # Desabilita o botão Next ao reiniciar
        self.ids.next_button.disabled = True
        # Preservar os caminhos selecionados
        source_path = self.ids.source_path_input.text
        dest_path = self.ids.destination_path_input.text
        
        status_updates = {
            'init_status': ('Aguardando início do backup...', (.6, .6, .6, 1)),
            'connectivity_status': ('Verificando conectividade...', (.6, .6, .6, 1)),
            'env_ready_status': ('Ambiente não verificado', (.6, .6, .6, 1)),
            'files_count_status': ('Total de arquivos: Calculando...', (.6, .6, .6, 1)),
            'copy_status': ('Aguardando início da cópia...', (.6, .6, .6, 1)),
            'progress_status': ('Progresso: 0%', (.6, .6, .6, 1)),
            'validation_status': ('Validação pendente', (.6, .6, .6, 1)),
            'finish_status': ('', (.6, .6, .6, 1)),
            'error_status': ('', (1, .2, .2, 1))
        }
        
        # Atualizar status mantendo os caminhos selecionados
        for id_name, (text, color) in status_updates.items():
            if id_name in self.ids:
                label = self.ids[id_name]
                label.text = text
                label.color = color
                
        # Restaurar os caminhos selecionados com cor verde
        if source_path:
            self.ids.source_path_status.text = f"Pasta de origem: {source_path}"
            self.ids.source_path_status.color = (0.11, 0.55, 0.27, 1)
        
        if dest_path:
            self.ids.dest_path_status.text = f"Pasta de destino: {dest_path}"
            self.ids.dest_path_status.color = (0.11, 0.55, 0.27, 1)
