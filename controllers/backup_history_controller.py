from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle
from datetime import datetime
from models.backup_logs_model import BackupLog

Builder.load_file('views/backup_history_view.kv')

class BackupRecordItem(BoxLayout):
    def __init__(self, backup_id, ticket_number, user, date, start_time, end_time, duration, files, size, source, destination, status, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint = (None, None)
        self.width = 1800  # Mesma largura da tabela
        self.height = 50
        self.spacing = 5

        # Fundo branco
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_rect, size=self._update_rect)

        # ID
        self.add_widget(Label(
            text=str(backup_id),
            color=(0.3, 0.3, 0.3, 1),
            size_hint_x=None,
            width=80,
            font_size=12
        ))

        # Ticket Number
        self.add_widget(Label(
            text=ticket_number or 'N/A',
            color=(0.3, 0.3, 0.3, 1),
            size_hint_x=None,
            width=100,
            font_size=12
        ))

        # User
        self.add_widget(Label(
            text=user,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_x=None,
            width=120,
            font_size=12
        ))

        # Date
        self.add_widget(Label(
            text=date,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_x=None,
            width=140,
            font_size=12
        ))

        # Start Time
        self.add_widget(Label(
            text=start_time,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_x=None,
            width=100,
            font_size=12
        ))

        # End Time
        self.add_widget(Label(
            text=end_time,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_x=None,
            width=100,
            font_size=12
        ))

        # Duration
        self.add_widget(Label(
            text=duration,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_x=None,
            width=120,
            font_size=12
        ))

        # Files
        self.add_widget(Label(
            text=files,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_x=None,
            width=100,
            font_size=12
        ))

        # Size
        self.add_widget(Label(
            text=size,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_x=None,
            width=120,
            font_size=12
        ))

        # Source
        self.add_widget(Label(
            text=source,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_x=None,
            width=220,
            font_size=12
        ))

        # Destination
        self.add_widget(Label(
            text=destination,
            color=(0.3, 0.3, 0.3, 1),
            size_hint_x=None,
            width=220,
            font_size=12
        ))

        # Status
        status_color = (0.11, 0.55, 0.27, 1) if status == 'Concluído' else (1, 0.2, 0.2, 1)
        self.add_widget(Label(
            text=status,
            color=status_color,
            size_hint_x=None,
            width=120,
            font_size=13,
            bold=True
        ))

    def _update_rect(self, instance, value):
        if hasattr(self, 'rect'):
            self.rect.pos = instance.pos
            self.rect.size = instance.size

class BackupHistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_backup_data = None

    def on_enter(self):
        """Carrega os registros quando a tela é exibida"""
        self.load_backup_records()

    def set_backup_data(self, backup_data):
        """Armazena os dados do backup atual"""
        self.current_backup_data = backup_data
        print(f"Backup data recebido: {backup_data}")

    def format_duration(self, seconds):
        """Formata a duração em horas:minutos:segundos"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def format_size(self, size_bytes):
        """Formata o tamanho do arquivo"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"

    def load_backup_records(self):
        """Carrega os registros de backup do banco de dados"""
        # Limpa a lista atual
        self.ids.backup_records.clear_widgets()

        try:
            # Busca os últimos registros de backup
            backups = BackupLog.select().order_by(BackupLog.backup_id.desc()).limit(10)

            for backup in backups:
                # Formata data e hora
                start_time = backup.start_time
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(start_time)
                
                end_time = backup.end_time if backup.end_time else start_time
                if isinstance(end_time, str):
                    end_time = datetime.fromisoformat(end_time)
                
                date_str = start_time.strftime("%b %d - %Y")
                start_time_str = start_time.strftime("%I:%M %p")
                end_time_str = end_time.strftime("%I:%M %p")
                
                # Duração
                duration_str = self.format_duration(backup.duration) if backup.duration else "N/A"
                
                # Tamanho
                size_str = self.format_size(backup.total_size) if backup.total_size else "N/A"
                
                # Arquivos
                files_str = f"{backup.copied_files}/{backup.total_files}" if backup.total_files else "N/A"
                
                # Nome do usuário - busca do banco de dados
                try:
                    from models.users_model import UserModel
                    user = UserModel.get_by_id(backup.user_id)
                    user_str = user.name  # Apenas o nome, sem o ID
                except:
                    user_str = f"User-{backup.user_id}"

                # Source e Destination (sem encurtar, pois agora temos scroll horizontal)
                source_str = backup.source_path if backup.source_path else 'N/A'
                destination_str = backup.destination_path if backup.destination_path else 'N/A'

                # Cria o item da lista
                record_item = BackupRecordItem(
                    backup_id=backup.backup_id,
                    ticket_number=backup.ticket_number,
                    user=user_str,
                    date=date_str,
                    start_time=start_time_str,
                    end_time=end_time_str,
                    duration=duration_str,
                    files=files_str,
                    size=size_str,
                    source=source_str,
                    destination=destination_str,
                    status=backup.status or 'N/A'
                )
                self.ids.backup_records.add_widget(record_item)

            print(f"Carregados {backups.count()} registros de backup")

        except Exception as e:
            print(f"Erro ao carregar registros: {str(e)}")
            import traceback
            traceback.print_exc()

    def finish(self):
        """Finaliza e volta para a tela inicial"""
        # Importar e resetar a sessão de backup
        from utils.backup_session import get_backup_session
        backup_session = get_backup_session()
        backup_session.reset()
        
        print("=" * 50)
        print("✓ Sessão encerrada")
        print("=" * 50)
        
        # Limpar todos os campos das telas
        self._clear_all_screens()
        
        # Voltar para tela de login
        self.manager.current = 'login'
    
    def _clear_all_screens(self):
        """Limpa todos os campos de todas as telas"""
        try:
            # Limpar tela de login
            if self.manager.has_screen('login'):
                login_screen = self.manager.get_screen('login')
                if hasattr(login_screen.ids, 'login_input'):
                    login_screen.ids.login_input.text = ''
                if hasattr(login_screen.ids, 'password_input'):
                    login_screen.ids.password_input.text = ''
            
            # Limpar tela de opções
            if self.manager.has_screen('options_screen'):
                options_screen = self.manager.get_screen('options_screen')
                if hasattr(options_screen.ids, 'ticket_input'):
                    options_screen.ids.ticket_input.text = ''
                if hasattr(options_screen.ids, 'ticket_error'):
                    options_screen.ids.ticket_error.text = ''
            
            # Limpar tela de backup - restaurar textos padrão
            if self.manager.has_screen('backup_start_screen'):
                backup_screen = self.manager.get_screen('backup_start_screen')
                if hasattr(backup_screen.ids, 'source_path_input'):
                    backup_screen.ids.source_path_input.text = ''
                if hasattr(backup_screen.ids, 'destination_path_input'):
                    backup_screen.ids.destination_path_input.text = ''
                
                # Restaurar status labels com textos padrão em cinza
                default_statuses = {
                    'source_path_status': ('Pasta de origem: Não selecionada', (0.6, 0.6, 0.6, 1)),
                    'dest_path_status': ('Pasta de destino: Não selecionada', (0.6, 0.6, 0.6, 1)),
                    'init_status': ('Aguardando início do backup...', (0.6, 0.6, 0.6, 1)),
                    'connectivity_status': ('Verificando conectividade...', (0.6, 0.6, 0.6, 1)),
                    'env_ready_status': ('Ambiente não verificado', (0.6, 0.6, 0.6, 1)),
                    'files_count_status': ('Total de arquivos: Calculando...', (0.6, 0.6, 0.6, 1)),
                    'copy_status': ('Aguardando início da cópia...', (0.6, 0.6, 0.6, 1)),
                    'progress_status': ('Progresso: 0%', (0.6, 0.6, 0.6, 1)),
                    'validation_status': ('Validação pendente', (0.6, 0.6, 0.6, 1)),
                    'finish_status': ('', (0.6, 0.6, 0.6, 1)),
                    'error_status': ('', (1, 0.2, 0.2, 1))
                }
                
                for status_id, (text, color) in default_statuses.items():
                    if hasattr(backup_screen.ids, status_id):
                        label = getattr(backup_screen.ids, status_id)
                        label.text = text
                        label.color = color
            
            # Limpar tela de transfer software
            if self.manager.has_screen('transfer_software_screen'):
                transfer_screen = self.manager.get_screen('transfer_software_screen')
                if hasattr(transfer_screen, 'software_items'):
                    transfer_screen.software_items = []
                if hasattr(transfer_screen.ids, 'software_list'):
                    transfer_screen.ids.software_list.clear_widgets()
            
            print("✓ Todos os campos foram limpos")
            
        except Exception as e:
            print(f"Erro ao limpar campos: {str(e)}")