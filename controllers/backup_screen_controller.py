import time
import os
import tkinter as tk

from tkinter import filedialog

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

from abc import ABC
from datetime import datetime

from controllers.manager.user_session_manager import UserSessionManager
from controllers.manager.backup_session_manager import BackupSessionManager
from controllers.facade.backup_facade import BackupFacade
from utils.observer import BackupLogObserver
# Para abrir seletor de pastas no Windows

Builder.load_file('views/backup_view.kv')

class BackupScreenController(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backup_facade = BackupFacade()
        self.backup_facade.attach_observer(BackupLogObserver(self))
        self.backup_session = BackupSessionManager()
        self.user_session = UserSessionManager()
        self.start_time = None

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
                    
        # Configure and start backup
        backup_config = {
            'source_path': source_path,
            'destination_path': dest_path
        }
        
        backup_ok = self.backup_facade.execute_full_backup(backup_config)
        
        if backup_ok:
            self.ids.next_button.disabled = False

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
