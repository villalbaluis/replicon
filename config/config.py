import os
import json
from dotenv import load_dotenv
import base64

# Cargar variables de entorno
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class Config:
    # URLs y configuración de red
    LOGIN_URL = os.getenv('LOGIN_URL')
    
    # Configuración de Selenium
    WEBDRIVER_TIMEOUT = int(os.getenv('WEBDRIVER_TIMEOUT', 45))  # Aumentado de 30 a 45 segundos
    SCROLL_BEHAVIOR = os.getenv('SCROLL_BEHAVIOR', 'smooth')
    
    # Configuración de la aplicación
    APP_TITLE = os.getenv('APP_TITLE', 'ReplicionAutomator - Por Hector David Rubio Tabares')
    APP_WIDTH = int(os.getenv('APP_WIDTH', 1400))  # Ajuste: ventana un poco más ancha
    APP_HEIGHT = int(os.getenv('APP_HEIGHT', 1600))  # Altura aumentada de 1400 a 1600
    
    # Configuración de credenciales
    APP_NAME = "ReplicionAutomator"
    
    # Validar configuraciones críticas
    if not LOGIN_URL:
        raise ValueError("LOGIN_URL debe estar definido en el archivo .env")
    
    @staticmethod
    def save_credentials(email, password):
        """Guardar credenciales de forma segura (codificado base64 simple)"""
        try:
            config_dir = os.path.dirname(__file__)
            creds_path = os.path.join(config_dir, '.credentials')
            
            # Codificación simple con base64
            email_encoded = base64.b64encode(email.encode()).decode()
            password_encoded = base64.b64encode(password.encode()).decode()
            
            creds_data = {
                "email": email_encoded,
                "password": password_encoded
            }
            
            with open(creds_path, 'w') as f:
                json.dump(creds_data, f)
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def load_credentials():
        """Cargar credenciales guardadas"""
        try:
            config_dir = os.path.dirname(__file__)
            creds_path = os.path.join(config_dir, '.credentials')
            
            if not os.path.exists(creds_path):
                return None, None
            
            with open(creds_path, 'r') as f:
                creds_data = json.load(f)
            
            email = base64.b64decode(creds_data["email"]).decode()
            password = base64.b64decode(creds_data["password"]).decode()
            
            return email, password
        except Exception:
            return None, None
    
    @staticmethod
    def clear_credentials():
        """Limpiar credenciales guardadas"""
        try:
            config_dir = os.path.dirname(__file__)
            creds_path = os.path.join(config_dir, '.credentials')
            
            if os.path.exists(creds_path):
                os.remove(creds_path)
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def load_horarios():
        """Cargar horarios desde archivo JSON"""
        config_dir = os.path.dirname(__file__)
        horarios_path = os.path.join(config_dir, 'horarios.json')
        
        try:
            with open(horarios_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Horarios por defecto si no existe el archivo
            return [
                {"start_time": "7:00am", "end_time": "1:00pm"},
                {"start_time": "2:00pm", "end_time": "4:00pm"}
            ]
    
    @staticmethod
    def save_horarios(horarios):
        """Guardar horarios en archivo JSON"""
        config_dir = os.path.dirname(__file__)
        horarios_path = os.path.join(config_dir, 'horarios.json')
        
        with open(horarios_path, 'w', encoding='utf-8') as f:
            json.dump(horarios, f, indent=2, ensure_ascii=False)