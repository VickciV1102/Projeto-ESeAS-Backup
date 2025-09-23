from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from utils.backup_facade import BackupFacade

# Para abrir seletor de pastas no Windows
import tkinter as tk
from tkinter import filedialog

Builder.load_file('views/backup_view.kv')

class BackupScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backup_facade = BackupFacade()

    def open_source_dialog(self):
        root = tk.Tk()
        root.withdraw()  # Esconder janela principal do Tkinter
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.ids.source_path_input.text = folder_path

    def open_destination_dialog(self):
        root = tk.Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.ids.destination_path_input.text = folder_path

    def start_backup(self):
        backupconfig = {
            'origem_caminho': self.ids.source_path_input.text,
            'destino_caminho': self.ids.destination_path_input.text
        }
        self.backup_facade.executefullbackup(1, backupconfig)
