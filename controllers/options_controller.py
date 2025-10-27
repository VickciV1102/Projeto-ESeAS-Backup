from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from utils.backup_session import get_backup_session

Builder.load_file('views/options_view.kv')

class OptionsScreenController(Screen):

    def __init__(self, **kwargs):
        super(OptionsScreenController, self).__init__(**kwargs)
    
    def on_enter(self):
        """Chamado quando a tela é exibida"""
        # Forçar a cor do texto do TextInput
        if hasattr(self.ids, 'ticket_input'):
            # Força a cor do texto para preto, ignorando o tema do sistema
            self.ids.ticket_input.foreground_color = (0.1, 0.1, 0.1, 1)
    
    def view_backup_history(self):
        """Navega para a tela de histórico de backups"""
        self.manager.current = 'backup_history_screen'
    
    def start_backup(self):      
        """Navega para a tela de início de backup"""
        # Validar número do chamado
        ticket_number = self.ids.ticket_input.text.strip()
        
        # Limpar mensagem de erro anterior
        self.ids.ticket_error.text = ''
        
        # Validar: deve ter exatamente 6 dígitos
        if not ticket_number:
            self.ids.ticket_error.text = 'O número do chamado é obrigatório'
            return
        
        if len(ticket_number) != 6:
            self.ids.ticket_error.text = 'O número do chamado deve ter exatamente 6 dígitos'
            return
        
        if not ticket_number.isdigit():
            self.ids.ticket_error.text = 'O número do chamado deve conter apenas números'
            return
        
        # Armazenar número do chamado na sessão
        backup_session = get_backup_session()
        backup_session.set_ticket_number(ticket_number)
        
        print("=" * 50)
        print(f"✓ Número do chamado validado: {ticket_number}")
        print("=" * 50)
        
        # Limpar campo para próximo uso
        self.ids.ticket_input.text = ''
        
        # Navegar para tela de backup
        self.manager.current = 'backup_start_screen'