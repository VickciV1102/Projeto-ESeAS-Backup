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
from controllers.options_controller import OptionsScreenController
from controllers.transfer_software_controller import TransferSoftwareScreen
from controllers.backup_history_controller import BackupHistoryScreen

from db import db_conn

from models.users_model import UserModel

kivy.require('2.3.0')
Config.set('graphics', 'resizable', True)

class MainApp(App):
    def build(self):
        # Project main details configuration
        self.title = 'Blue Macaw Backup System'
        Window.size = (1024, 600)  # Tamanho reduzido para melhor visualização

        db_conn.init_db()

        AdminUserInit.init_admin_user()

        sm = ScreenManager()
        sm.add_widget(LoginScreenController(name='login'))
        #sm.add_widget(BackupSetupScreenController(name='backup_setup'))
        sm.add_widget(BackupScreen(name='backup_start_screen'))
        sm.add_widget(TransferSoftwareScreen(name='transfer_software_screen'))
        sm.add_widget(FinishMigrationScreenController(name='finish_migration'))
        sm.add_widget(AppMigSetupScreenController(name='app_mig_setup'))
        sm.add_widget(BackupHistoryScreen(name='backup_history_screen'))
        sm.add_widget(OptionsScreenController(name='options'))
        return sm
    
    def on_start(self):
        """Chamado após a janela ser criada - centraliza a janela"""
        from kivy.clock import Clock
        # Agendar centralização após a janela estar completamente renderizada
        Clock.schedule_once(self._center_window, 0.1)
    
    def _center_window(self, dt):
        """Centraliza a janela na tela"""
        try:
            if sys.platform == 'win32':
                user32 = ctypes.windll.user32
                screen_w = user32.GetSystemMetrics(0)
                screen_h = user32.GetSystemMetrics(1)
                
                # Calcula posição central
                win_w = Window.width
                win_h = Window.height
                
                Window.left = int((screen_w - win_w) / 2)
                Window.top = int((screen_h - win_h) / 2)
                
                print(f"Janela centralizada: {win_w}x{win_h} em tela {screen_w}x{screen_h}")
                print(f"Posição: left={Window.left}, top={Window.top}")
        except Exception as e:
            # Non-fatal: if anything goes wrong, just leave default positioning
            print(f"Não foi possível centralizar a janela: {e}")

if __name__ == '__main__':
    MainApp().run()
