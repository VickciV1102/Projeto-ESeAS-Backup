from peewee import Model, IntegerField, CharField, DateTimeField, FloatField
from db.database import db
from datetime import datetime

class BackupLog(Model):
    backup_id = IntegerField(primary_key=True)
    user_id = IntegerField()
    backup_type = CharField()
    ticket_number = CharField(null=True)  # Número do chamado
    start_time = DateTimeField(default=datetime.now)
    end_time = DateTimeField(null=True)
    duration = FloatField(null=True)
    source_path = CharField(null=True)
    destination_path = CharField(null=True)
    total_size = FloatField(null=True)
    total_files = IntegerField(null=True)
    copied_files = IntegerField(null=True)
    status = CharField(default='Em progresso')  # Concluído, Parcial, Falha, Interrompido
    
    class Meta:
        database = db
        table_name = 'backup_logs'