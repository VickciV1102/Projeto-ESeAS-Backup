class BackupSession:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.reset()
    
    def reset(self):
        """Reseta a sessão de backup"""
        self.user_id = None
        self.user_name = None
        self.backup_id = None
        self.ticket_number = None  # Número do chamado
        self.start_time = None
        self.end_time = None
        self.source_path = None
        self.destination_path = None
        
        # Dados do backup de arquivos
        self.file_backup_files = 0
        self.file_backup_size = 0
        
        # Dados do backup de software
        self.software_backup_files = 0
        self.software_backup_size = 0
        self.software_destination_path = None
    
    def set_user(self, user_id, user_name):
        """Define o usuário autenticado"""
        self.user_id = user_id
        self.user_name = user_name
    
    def set_ticket_number(self, ticket_number):
        """Define o número do chamado"""
        self.ticket_number = ticket_number
    
    def set_file_backup_data(self, files, size, source, destination):
        """Armazena dados do backup de arquivos"""
        self.file_backup_files = files
        self.file_backup_size = size
        if not self.source_path:
            self.source_path = source
        if not self.destination_path:
            self.destination_path = destination
    
    def set_software_backup_data(self, files, size, destination):
        """Armazena dados do backup de software"""
        self.software_backup_files = files
        self.software_backup_size = size
        self.software_destination_path = destination
    
    def get_total_files(self):
        """Retorna o total de arquivos copiados"""
        return self.file_backup_files + self.software_backup_files
    
    def get_total_size(self):
        """Retorna o tamanho total copiado"""
        return self.file_backup_size + self.software_backup_size
    
    def get_summary(self):
        """Retorna um resumo da sessão"""
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
            'backup_id': self.backup_id,
            'ticket_number': self.ticket_number,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'source_path': self.source_path,
            'destination_path': self.destination_path,
            'total_files': self.get_total_files(),
            'total_size': self.get_total_size(),
            'file_backup_files': self.file_backup_files,
            'file_backup_size': self.file_backup_size,
            'software_backup_files': self.software_backup_files,
            'software_backup_size': self.software_backup_size
        }

def get_backup_session():
    return BackupSession()