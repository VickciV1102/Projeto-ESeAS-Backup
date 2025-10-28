from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.core.window import Window
from peewee import DoesNotExist

from models.users_model import UserModel
from .manager.backup_session_manager import BackupSessionManager
from .manager.user_session_manager import UserSessionManager

Builder.load_file('views/login_view.kv')

class LoginScreenController(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_session = UserSessionManager()

    def do_login(self, login, password):
        
        user: UserModel = UserModel.select().where((UserModel.username == login) & (UserModel.password == password)).first()   

        if (not user):
            self.ids.error_label.text = 'Usuário ou Senha inválida'
            return
        
        self.user_session.set_user(user.user_id, user.name)
        
        print(f"✓ Usuário {user.name} (ID: {user.user_id}) armazenado na sessão")

        self.manager.current = 'options_screen'

    def on_enter(self, *args):
        self.ids.login_input.focus = True

class AdminUserInit:
    @classmethod
    def init_admin_user(cls):
        try:
            UserModel.get(UserModel.username == "admin")
            print("Usuário admin já existe!")
        except DoesNotExist:
            print("Usuário admin não encontrado")
            print("Iniciando cadastro de usuário 'admin'...")
            
            UserModel.create(
                name='admin',
                username="admin",
                email="admin@bmacaw.com",
                password="admin",
            )
            
            print("Usuário admin criado!")