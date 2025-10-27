from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.core.window import Window
from peewee import DoesNotExist

from models.users_model import UserModel
from utils.backup_session import get_backup_session

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
                backup_session = get_backup_session()
                backup_session.set_user(user.user_id, user.name)
                print(f"✓ Usuário {user.name} (ID: {user.user_id}) armazenado na sessão")

                self.manager.current = 'options'

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