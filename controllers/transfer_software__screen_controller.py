import os
import shutil
import time
import tkinter as tk

from dotenv import load_dotenv

from datetime import datetime

from tkinter import filedialog
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, InstructionGroup

from controllers.manager.user_session_manager import UserSessionManager

from .manager.log_manager import LogManager
from .manager.backup_session_manager import BackupSessionManager

Builder.load_file('views/transfer_software_view.kv')

load_dotenv()

class TransferSoftwareScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backup_session = BackupSessionManager()
        self.user_session = UserSessionManager()
        self.log_manager = LogManager()
        self.software_items = []
        self.backup_start_time = None
        self.backup_data = {}

    def on_enter(self):
        """Carrega a lista de softwares quando a tela é exibida"""
        self.load_software_list()
    
    def on_leave(self):
        """Reset da direção da transição ao sair da tela"""
        self.manager.transition.direction = 'left'

    def load_software_list(self):
        """Carrega a lista de softwares do diretório"""
        # Limpa a lista atual
        self.ids.software_list.clear_widgets()
        self.software_items = []
        
        # Diretório onde estão os executáveis
        software_dir = os.environ.get('SOFTWARE_INSTALLERS_PATH', '')
        
        # Verifica se o diretório existe
        if not os.path.exists(software_dir):
            print(f"Diretório não encontrado: {software_dir}")
            return

        # Lista todos os executáveis no diretório
        for file in os.listdir(software_dir):
            if file.endswith(('.exe', '.msi')):
                file_path = os.path.join(software_dir, file)
                size = self.get_file_size(file_path)
                software_item = SoftwareItem(name=file, size=size, file_path=file_path)
                self.software_items.append(software_item)
                self.ids.software_list.add_widget(software_item)

    def get_file_size(self, file_path):
        """Converte o tamanho do arquivo para uma string legível"""
        size = os.path.getsize(file_path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def select_all_software(self, value):
        """Seleciona ou deseleciona todos os softwares"""
        for item in self.software_items:
            item.checkbox.active = value

    def get_selected_software(self):
        """Retorna uma lista com os softwares selecionados"""
        return [item for item in self.software_items if item.checkbox.active]

    def go_back(self):
        """Volta para a tela anterior"""
        self.manager.transition.direction = 'right'
        self.manager.current = 'backup_start_screen'

    def proceed_next(self):
        """Avança para a próxima etapa - com ou sem softwares selecionados"""
        selected_software = self.get_selected_software()
        
        if not selected_software:
            # Nenhum software selecionado - pular para finalização
            print("=" * 50)
            print("Nenhum software selecionado - pulando etapa de software")
            print("=" * 50)
            
            # Registrar backup apenas com arquivos (sem software)
            self._finalize_without_software()
            return
        
        # Softwares selecionados - solicitar destino
        print(f"{len(selected_software)} software(s) selecionado(s)")
        
        # Abre diálogo para selecionar pasta de destino
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        destination_path = filedialog.askdirectory(title="Selecione o destino para copiar os softwares")
        root.destroy()
        
        if not destination_path:
            print("Nenhum destino selecionado - cancelando cópia de software")
            return
        
        # Inicia a cópia dos softwares
        self.copy_software(selected_software, destination_path)
    
    def _finalize_without_software(self):
        """Finaliza o backup sem copiar softwares"""
        
        # Define o fim do backup se ainda não foi definido
        if not self.backup_session.end_time:
            self.backup_session.end_time = datetime.now()
        
        # Calcula duração total
        if self.backup_session.start_time:
            duration = (self.backup_session.end_time - self.backup_session.start_time).total_seconds()
        else:
            duration = 0
        
        # Obtém resumo da sessão (apenas arquivos, sem software)
        summary = self.backup_session.get_summary()
        user = self.user_session.get_user()
        
        print("=" * 50)
        print("FINALIZAÇÃO DO BACKUP (APENAS ARQUIVOS):")
        print(f"  - Usuário: {user.get("user_name")} (ID: {user.get("user_id")})")
        print(f"  - Total de arquivos: {summary['file_backup_files']}")
        print(f"  - Tamanho total (bytes): {summary['file_backup_size']}")
        print(f"  - Tamanho total (MB): {summary['file_backup_size'] / (1024*1024):.2f}")
        print(f"  - Origem: {summary['source_path']}")
        print(f"  - Destino: {summary['destination_path']}")
        print("=" * 50)
        
        # Registrar backup apenas com arquivos no banco de dados
        self.log_manager.log_backup_complete(
            user_id=user.get("user_id"),
            backup_type='files_only',  # apenas arquivos
            ticket_number=summary['ticket_number'],
            duration=duration,
            source_path=summary['source_path'],
            destination_path=summary['destination_path'],
            total_size=summary['file_backup_size'],
            total_files=summary['file_backup_files'],
            copied_files=summary['file_backup_files'],
            status='Concluído'
        )
        
        print("✓ Backup registrado no banco de dados")
        print("=" * 50)
        
        # Limpar sessão para próximo backup
        self.backup_session.reset()
        
        # Navega para a tela de histórico
        if self.manager.has_screen('backup_history_screen'):
            self.manager.current = 'backup_history_screen'
        else:
            print("Tela 'backup_history_screen' não encontrada!")

    def copy_software(self, selected_software, destination_path):
        """Copia os softwares selecionados para o destino"""
        total_files = len(selected_software)
        total_size = 0
        copied_files = 0
        
        print(f"Iniciando cópia de {total_files} arquivos para {destination_path}")
        
        # Calcula o tamanho total
        for item in selected_software:
            total_size += os.path.getsize(item.file_path)
        
        # Copia cada arquivo
        for item in selected_software:
            try:
                source_file = item.file_path
                dest_file = os.path.join(destination_path, os.path.basename(source_file))
                
                print(f"Copiando: {os.path.basename(source_file)}...")
                shutil.copy2(source_file, dest_file)
                copied_files += 1
                
                print(f"✓ Copiado: {os.path.basename(source_file)} ({copied_files}/{total_files})")
                
            except Exception as e:
                print(f"✗ Erro ao copiar {item.file_path}: {str(e)}")
        
        # Define o fim do backup se ainda não foi definido
        if not self.backup_session.end_time:
            self.backup_session.end_time = datetime.now()
        
        # Armazena dados do software na sessão
        source_path = os.path.dirname(selected_software[0].file_path) if selected_software else ''
        self.backup_session.set_software_backup_data(
            files=copied_files,
            size=total_size,
            destination=destination_path
        )
        
        print("=" * 50)
        print("TRANSFERÊNCIA DE SOFTWARES CONCLUÍDA!")
        print(f"Softwares selecionados: {copied_files}")
        print(f"Tamanho total dos softwares: {total_size / (1024*1024):.2f} MB")
        print(f"Destino: {destination_path}")
        print("=" * 50)
        
        # Calcula duração total
        if self.backup_session.start_time:
            duration = (self.backup_session.end_time - self.backup_session.start_time).total_seconds()
        else:
            duration = 0
        
        # Obtém resumo completo da sessão
        summary = self.backup_session.get_summary()
        user = self.user_session.get_user()
        
        print("=" * 50)
        print("CONSOLIDAÇÃO FINAL DO BACKUP:")
        print(f"  - Usuário: {user.get("user_name")} (ID: {user.get("user_id")})")
        print(f"  - Total de arquivos (documentos + softwares): {summary['total_files']}")
        print(f"  - Arquivos de documentos: {summary['file_backup_files']}")
        print(f"  - Softwares copiados: {summary['software_backup_files']}")
        print(f"  - Tamanho total (bytes): {summary['total_size']}")
        print(f"  - Tamanho total (MB): {summary['total_size'] / (1024*1024):.2f}")
        print(f"  - Origem: {summary['source_path']}")
        print(f"  - Destino arquivos: {summary['destination_path']}")
        print(f"  - Destino softwares: {destination_path}")
        print("=" * 50)
        
        # Registrar backup consolidado no banco de dados
        self.log_manager.log_backup_complete(
            user_id=user.get("user_id"),
            backup_type='full',  # full = documentos + softwares
            ticket_number=summary['ticket_number'],
            duration=duration,
            source_path=summary['source_path'],
            destination_path=summary['destination_path'],
            total_size=summary['total_size'],
            total_files=summary['total_files'],
            copied_files=summary['total_files'],
            status='Concluído'
        )
        
        print("✓ Backup consolidado registrado no banco de dados")
        print("=" * 50)
        
        # Limpar sessão para próximo backup
        self.backup_session.reset()
        
        # Navega para a tela de histórico
        if self.manager.has_screen('backup_history_screen'):
            self.manager.current = 'backup_history_screen'
        else:
            print("Tela 'backup_history_screen' não encontrada!")
            
class SoftwareItem(BoxLayout):
    def __init__(self, name, size, file_path, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 50  # Altura mínima, pode crescer
        self.spacing = 5
        self.padding = [15, 5, 15, 5]
        self.file_path = file_path
        self.file_name = name

        # Fundo branco para cada item
        self.bg = InstructionGroup()
        self.bg.add(Color(1, 1, 1, 1))  # Branco
        self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bg.add(self.rect)
        self.canvas.before.add(self.bg)
        self.bind(pos=self._update_rect, size=self._update_rect)

        # Checkbox
        self.checkbox = CheckBox(
            size_hint_x=None,
            width=30,
            size_hint_y=None,
            height=30
        )
        self.add_widget(self.checkbox)

        # Software name - com wrap de texto
        self.name_label = Label(
            text=name,
            color=(0.2, 0.2, 0.2, 1),
            halign='left',
            valign='middle',
            size_hint_x=0.7,
            font_size=13,
            markup=True,
            shorten=False,  # Não encurtar o texto
            text_size=(400, None)  # Largura inicial estimada
        )
        self.name_label.bind(width=self._update_text_size)
        self.add_widget(self.name_label)

        # Size
        self.size_label = Label(
            text=size,
            color=(0.5, 0.5, 0.5, 1),
            halign='right',
            valign='middle',
            size_hint_x=0.22,
            font_size=13
        )
        self.add_widget(self.size_label)
    
    def _update_text_size(self, instance, value):
        """Atualiza o text_size para permitir wrap"""
        instance.text_size = (instance.width - 10, None)
        # Ajusta altura do item baseado no texto apenas se necessário
        instance.texture_update()
        if instance.texture_size[1] > 40:
            self.height = max(50, instance.texture_size[1] + 20)
        else:
            self.height = 50

    def _update_rect(self, instance, value):
        """Atualiza a posição e tamanho do retângulo de fundo"""
        if hasattr(self, 'rect'):
            self.rect.pos = instance.pos
            self.rect.size = instance.size