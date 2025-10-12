import kivy
from kivy.app import App
from kivy.core.window import Window
import sys
import ctypes
from kivy.uix.screenmanager import ScreenManager
from kivy.config import Config

from controllers.app_mig_setup_controller import AppMigSetupScreenController
from controllers.backup_setup_controller import BackupSetupScreenController
from controllers.finish_migration_controller import FinishMigrationScreenController
from controllers.login_controller import (LoginScreenController, AdminUserInit)
from controllers.backup_controller import BackupScreen
from controllers.transfer_software_controller import TransferSoftwareScreen

from db import db_conn

from models.users_model import UserModel

kivy.require('2.3.0')
Config.set('graphics', 'resizable', True)

class MainApp(App):
    def build(self):
        # Project main details configuration
        self.title = 'Blue Macaw Backup System'
        Window.size = (1280, 768)
        # Try to center the window on the primary monitor (Windows only).
        try:
            if sys.platform == 'win32':
                user32 = ctypes.windll.user32
                screen_w = user32.GetSystemMetrics(0)
                screen_h = user32.GetSystemMetrics(1)
                Window.left = int((screen_w - Window.width) / 2)
                # On Windows, top is measured from the top of the screen
                Window.top = int((screen_h - Window.height) / 2)
        except Exception:
            # Non-fatal: if anything goes wrong, just leave default positioning
            pass

        db_conn.init_db()

        AdminUserInit.init_admin_user()

        sm = ScreenManager()
        sm.add_widget(LoginScreenController(name='login'))
        #sm.add_widget(BackupSetupScreenController(name='backup_setup'))
        sm.add_widget(BackupScreen(name='backup_start_screen'))
        sm.add_widget(TransferSoftwareScreen(name='transfer_software_screen'))
        sm.add_widget(FinishMigrationScreenController(name='finish_migration'))
        sm.add_widget(AppMigSetupScreenController(name='app_mig_setup'))
        return sm

if __name__ == '__main__':
    MainApp().run()
