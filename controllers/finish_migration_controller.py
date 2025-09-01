from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.core.window import Window

from models.users_model import UserModel

Builder.load_file('views/finish_migration_view.kv')

class FinishMigrationScreenController(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)