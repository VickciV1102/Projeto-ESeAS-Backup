"""
Script de migração para adicionar a coluna ticket_number na tabela backup_logs
Execute este script uma única vez para atualizar o banco de dados
"""

from db import db_conn
from peewee import CharField
from models.backup_logs_model import BackupLog

def migrate():
    print("=" * 50)
    print("MIGRAÇÃO: Adicionando coluna ticket_number")
    print("=" * 50)
    
    # Conectar ao banco
    db_conn.init_db()
    
    try:
        # Verificar se a coluna já existe
        cursor = BackupLog._meta.database.execute_sql(
            "PRAGMA table_info(backup_logs)"
        )
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'ticket_number' in columns:
            print("✓ Coluna 'ticket_number' já existe!")
        else:
            print("Adicionando coluna 'ticket_number'...")
            
            # Adicionar a coluna
            BackupLog._meta.database.execute_sql(
                'ALTER TABLE backup_logs ADD COLUMN ticket_number VARCHAR(255)'
            )
            
            print("✓ Coluna 'ticket_number' adicionada com sucesso!")
        
        print("=" * 50)
        print("Migração concluída!")
        print("=" * 50)
        
    except Exception as e:
        print(f"✗ Erro na migração: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    migrate()
