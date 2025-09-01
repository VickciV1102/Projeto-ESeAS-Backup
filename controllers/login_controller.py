from Demos.win32ts_logoff_disconnected import username
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.core.window import Window
from peewee import DoesNotExist

from models.users_model import UserModel

Builder.load_file('views/login_view.kv')

class LoginScreenController(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def do_login(self, login, password):
        print("=" * 30)
        print("Tentativa de login com:")
        print(f"  Usuário: {login}")
        print(f"  Senha: {'*' * len(password)}")
        print("=" * 30)

        user: UserModel = UserModel.get(UserModel.username == login)

        if user is not None:
            password_match = user.password == password

            if password_match:
                self.manager.current = 'backup_setup'

    def on_enter(self, *args):
        self.ids.login_input.focus = True

class AdminUserInit:
    @classmethod
    def init_admin_user(cls ):
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