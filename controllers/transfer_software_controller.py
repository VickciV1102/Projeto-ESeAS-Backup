import os
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, InstructionGroup

Builder.load_file('views/transfer_software_view.kv')

class SoftwareItem(BoxLayout):
    def __init__(self, name, size, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 50
        self.spacing = 0
        self.padding = [20, 0, 20, 0]

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
            width=30
        )
        self.add_widget(self.checkbox)

        # Software name
        name_label = Label(
            text=name,
            color=(0.2, 0.2, 0.2, 1),
            text_size=self.size,
            halign='left',
            valign='center',
            size_hint_x=0.92,
            font_size=16,
            padding=[10, 0, 0, 0]
        )
        self.add_widget(name_label)

        # Size
        size_label = Label(
            text=size,
            color=(0.5, 0.5, 0.5, 1),
            text_size=self.size,
            halign='right',
            valign='center',
            size_hint_x=0.08,  # Reduzido de 0.15 para 0.08
            font_size=16
        )
        self.add_widget(size_label)

    def _update_rect(self, instance, value):
        """Atualiza a posição e tamanho do retângulo de fundo"""
        if hasattr(self, 'rect'):
            self.rect.pos = instance.pos
            self.rect.size = instance.size

class TransferSoftwareScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.software_items = []
        self.load_software_list()

    def load_software_list(self):
        # Diretório onde estão os executáveis
        software_dir = r"C:\Users\gabri\Downloads\Softwares"  # Ajuste para o diretório correto
        
        # Verifica se o diretório existe
        if not os.path.exists(software_dir):
            return

        # Lista todos os executáveis no diretório
        for file in os.listdir(software_dir):
            if file.endswith(('.exe', '.msi')):
                file_path = os.path.join(software_dir, file)
                size = self.get_file_size(file_path)
                software_item = SoftwareItem(name=file, size=size)
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
        self.manager.current = 'backup_start_screen'

    def proceed_next(self):
        """Avança para a próxima etapa com os softwares selecionados"""
        selected_software = self.get_selected_software()
        # Implementar a lógica para a próxima etapa aqui
        pass