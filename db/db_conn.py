import os

from peewee import (SqliteDatabase)

from db.database import db_proxy
from models.users_model import UserModel

def init_db():
    try:
        db_folder = 'data'
        db_name = 'blue_macaw.db'

        os.makedirs(db_folder, exist_ok=True)
        db_path = os.path.join(db_folder, db_name)

        db = SqliteDatabase(db_path)
        db_proxy.initialize(db)

        db.connect()
        print("Conexão com o banco de dados estabelecida.")
        db.create_tables([UserModel], safe=True)

        print("Tabelas 'users' e 'backup_logs' verificadas/criadas com sucesso.")
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
    finally:
        if not db.is_closed():
            db.close()