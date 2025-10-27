from peewee import DatabaseProxy

db_proxy = DatabaseProxy()
db = db_proxy  # Alias para compatibilidade com backup_logs_model