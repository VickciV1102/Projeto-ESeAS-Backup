from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.core.window import Window

from models.users_model import UserModel
from utils import backup_facade

Builder.load_file('views/backup_setup_view.kv')

class BackupSetupScreenController(Screen):
    def __init__(self, **kwargs):
        Screen.__init__(self, **kwargs)
        
        self.log_manager = get_log_manager()
        self.backup_facade = BackupFacade()
        
        self.backup_facade.attach(self) 
        self.backup_facade.attach(LogBackupObserver())
    
    def start_backup(self):
        if self.backup_facade.get_backup_status()["is_running"]:
            self.show_message("Backup já está em execução!")
            return
        
        backup_config = {
            'source_paths': self.get_selected_paths(),
            'destination_path': self.get_destination_path()
        }
        
        self.backup_facade.execute_full_backup(self, 1, backup_config)
    