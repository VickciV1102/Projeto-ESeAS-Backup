from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.modalview import ModalView

from .manager.backup_session_manager import BackupSessionManager

Builder.load_file('views/options_view.kv')
Builder.load_file('views/ticket_modal.kv')

class OptionsScreenController(Screen):

    def __init__(self, **kwargs):
        super(OptionsScreenController, self).__init__(**kwargs)

    def on_enter(self):
        if hasattr(self.ids, 'ticket_input'):
            self.ids.ticket_input.foreground_color = (0.1, 0.1, 0.1, 1)

    def view_backup_history(self):
        """Navega para a tela de histórico de backups"""
        self.manager.current = 'backup_history_screen'

    def start_backup(self):
        """Abre modal para solicitar número do chamado"""
        modal = TicketNumberModal(callback=self.navigate_to_backup)
        modal.open()

    def navigate_to_backup(self):
        self.manager.current = 'backup_start_screen'
        
class TicketNumberModal(ModalView):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.backup_session = BackupSessionManager()

    def confirm_ticket(self):
        ticket_number = self.ids.ticket_input.text.strip()

        self.ids.error_label.text = ''

        if not ticket_number:
            self.ids.error_label.text = 'O número do chamado é obrigatório'
            return

        if len(ticket_number) != 6:
            self.ids.error_label.text = 'Deve ter exatamente 6 dígitos'
            return

        if not ticket_number.isdigit():
            self.ids.error_label.text = 'Deve conter apenas números'
            return

        self.backup_session.set_ticket_number(ticket_number)

        print("=" * 50)
        print(f"✓ Número do chamado validado: {ticket_number}")
        print("=" * 50)

        self.dismiss()
        self.callback()