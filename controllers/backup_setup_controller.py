from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.core.window import Window

from models.users_model import UserModel

Builder.load_file('views/backup_setup_view.kv')

class BackupSetupScreenController(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)