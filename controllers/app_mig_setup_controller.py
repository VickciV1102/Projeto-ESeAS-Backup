from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.core.window import Window

from models.users_model import UserModel

Builder.load_file('views/app_mig_setup_view.kv')

class AppMigSetupScreenController(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)