import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivy.config import Config

from controllers.app_mig_setup_controller import AppMigSetupScreenController
from controllers.backup_setup_controller import BackupSetupScreenController
from controllers.finish_migration_controller import FinishMigrationScreenController
from controllers.login_controller import (LoginScreenController, AdminUserInit)

from db import db_conn

from models.users_model import UserModel

kivy.require('2.3.0')
Config.set('graphics', 'resizable', True)

class MainApp(App):
    def build(self):
        # Project main details configuration
        self.title = 'Blue Macaw Backup System'
        Window.size = (1280, 768)

        db_conn.init_db()

        AdminUserInit.init_admin_user()

        sm = ScreenManager()
        sm.add_widget(LoginScreenController(name='login'))
        sm.add_widget(BackupSetupScreenController(name='backup_setup'))
        sm.add_widget(FinishMigrationScreenController(name='finish_migration'))
        sm.add_widget(AppMigSetupScreenController(name='app_mig_setup'))
        return sm

if __name__ == '__main__':
    MainApp().run()
