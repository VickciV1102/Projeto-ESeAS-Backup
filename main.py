import kivy
import sys
import ctypes

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivy.config import Config
from kivy.clock import Clock

from controllers.login_screen_controller import (LoginScreenController, AdminUserInit)
from controllers.backup_screen_controller import BackupScreenController
from controllers.options_screen_controller import OptionsScreenController
from controllers.transfer_software__screen_controller import TransferSoftwareScreen
from controllers.backup_history_screen_controller import BackupHistoryScreenController

from db import db_conn

kivy.require('2.3.0')
Config.set('graphics', 'resizable', True)

class MainApp(App):
    def build(self):
        # Project main details configuration
        self.title = 'Blue Macaw Backup System'
        Window.size = (1366, 768)  # Tamanho reduzido para melhor visualização

        db_conn.init_db()

        AdminUserInit.init_admin_user()

        sm = ScreenManager()
        sm.add_widget(LoginScreenController(name='login'))
        sm.add_widget(OptionsScreenController(name='options_screen'))
        sm.add_widget(BackupScreenController(name='backup_start_screen'))
        sm.add_widget(TransferSoftwareScreen(name='transfer_software_screen'))
        sm.add_widget(BackupHistoryScreenController(name='backup_history_screen'))
        return sm
    
    def on_start(self):
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
