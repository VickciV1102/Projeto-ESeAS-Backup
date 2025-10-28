class UserSessionManager:
    _instance = None
    
    # Singleton para gerenciamento de sessão de usuário
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
            
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.end_session()
    
    def end_session(self):
        """Reseta a sessão de backup"""
        self.user_id = None
        self.user_name = None
    
    def set_user(self, user_id, user_name):
        """Define o usuário autenticado"""
        self.user_id = user_id
        self.user_name = user_name
        
    def get_user(self) -> dict:
        return {'user_id': self.user_id, 'user_name': self.user_name}
        
    def get_summary(self):
        """Retorna um resumo da sessão"""
        return {
            'user_id': self.user_id,
            'user_name': self.user_name,
        }

def get_user_session():
    return BackupSessionManager()