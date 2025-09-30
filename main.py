#!/usr/bin/env python3
"""
Automatizador de Replicon - Aplicación principal
================================================

Aplicación moderna para automatizar el registro de horas en Replicon.
Construida con PyQt6 y arquitectura modular profesional.

Autor: Hector David Rubio Tabares
Fecha: 2025
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(__file__))

from src.ui.main_window import MainWindow

def main():
    """Función principal de la aplicación"""
    
    # Crear aplicación
    app = QApplication(sys.argv)
    
    # Configuraciones globales de la aplicación
    app.setApplicationName("Automatizador de Replicon")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Tu Empresa")
    
    # Habilitar DPI scaling para pantallas de alta resolución (PyQt6 ya lo hace automáticamente)
    # app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    # app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Establecer icono de la aplicación (si existe)
    icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    try:
        # Crear y mostrar ventana principal
        window = MainWindow()
        window.show()
        
        # Ejecutar aplicación
        return app.exec()
        
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())