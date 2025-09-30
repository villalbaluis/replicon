import json
import os

class AccountMapper:
    """Clase para manejar el mapeo de cuentas y proyectos"""
    
    def __init__(self):
        # Obtener ruta del archivo de mapeo
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.mapeo_file = os.path.join(current_dir, 'config', 'cuentas.json')
        
        # Cargar mapeo desde archivo
        self.mapeo_cuentas = self.load_mapeo_cuentas()
    
    def load_mapeo_cuentas(self):
        """Cargar mapeo de cuentas desde archivo JSON"""
        try:
            with open(self.mapeo_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Archivo de mapeo no encontrado: {self.mapeo_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error al leer archivo de mapeo: {e}")
            return {}
    
    def save_mapeo_cuentas(self):
        """Guardar mapeo de cuentas en archivo JSON"""
        try:
            with open(self.mapeo_file, 'w', encoding='utf-8') as f:
                json.dump(self.mapeo_cuentas, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar mapeo de cuentas: {e}")
            return False
    
    def get_mapping(self):
        """Obtener el mapeo completo de cuentas"""
        return self.mapeo_cuentas
    
    def get_project_name(self, cuenta):
        """Obtener el nombre del proyecto por código de cuenta"""
        return self.mapeo_cuentas.get(cuenta, {}).get("name", "Desconocido")
    
    def get_account_name(self, cuenta, proyecto):
        """Obtener el nombre de la cuenta por código de cuenta y proyecto"""
        company = self.mapeo_cuentas.get(cuenta, {})
        return company.get("projects", {}).get(proyecto, "Desconocido")
    
    def add_account(self, codigo, nombre, proyectos=None):
        """Agregar nueva cuenta al mapeo"""
        if proyectos is None:
            proyectos = {}
        
        self.mapeo_cuentas[codigo] = {
            "name": nombre,
            "projects": proyectos
        }
        # Guardar cambios en archivo
        self.save_mapeo_cuentas()
    
    def update_account(self, codigo, nombre=None, proyectos=None):
        """Actualizar cuenta existente"""
        if codigo in self.mapeo_cuentas:
            if nombre:
                self.mapeo_cuentas[codigo]["name"] = nombre
            if proyectos:
                self.mapeo_cuentas[codigo]["projects"] = proyectos
            # Guardar cambios en archivo
            self.save_mapeo_cuentas()
    
    def remove_account(self, codigo):
        """Eliminar cuenta del mapeo"""
        if codigo in self.mapeo_cuentas:
            del self.mapeo_cuentas[codigo]
            # Guardar cambios en archivo
            self.save_mapeo_cuentas()
    
    def get_all_accounts(self):
        """Obtener lista de todos los códigos de cuenta"""
        return list(self.mapeo_cuentas.keys())
    
    def get_all_projects_for_account(self, cuenta):
        """Obtener todos los proyectos para una cuenta específica"""
        return self.mapeo_cuentas.get(cuenta, {}).get("projects", {})
    
    def search_accounts_by_name(self, nombre_busqueda):
        """Buscar cuentas por nombre"""
        resultado = {}
        for codigo, info in self.mapeo_cuentas.items():
            if nombre_busqueda.lower() in info.get("name", "").lower():
                resultado[codigo] = info
        return resultado
    
    def is_vacation_or_no_work(self, cuenta):
        """Verificar si una cuenta es de vacaciones o no trabajo"""
        project_name = self.get_project_name(cuenta)
        return project_name in ["Vacation", "No work"]
    
    def validate_account_project(self, cuenta, proyecto):
        """Validar si existe la combinación cuenta-proyecto"""
        if cuenta not in self.mapeo_cuentas:
            return False, f"Cuenta '{cuenta}' no encontrada"
        
        projects = self.mapeo_cuentas[cuenta].get("projects", {})
        if proyecto not in projects:
            return False, f"Proyecto '{proyecto}' no encontrado para cuenta '{cuenta}'"
        
        return True, "Combinación válida"