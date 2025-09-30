#!/usr/bin/env python3
"""
Script para crear el instalador de ReplicionAutomator

Autor: Hector David Rubio Tabares
Año: 2025
"""

import subprocess
import sys
import os

def create_executable():
    """Crear ejecutable con PyInstaller"""
    
    # Comando PyInstaller
    cmd = [
        'pyinstaller',
        '--onefile',                    # Un solo archivo ejecutable
        '--windowed',                   # Sin consola (no abre ventana de comandos)
        '--name=ReplicionAutomator',    # Nombre del ejecutable
        '--icon=assets/icon.ico',       # Icono de la aplicación
        '--add-data=config;config',     # Incluir carpeta config
        '--add-data=assets;assets',     # Incluir carpeta assets
        '--distpath=dist',              # Carpeta de distribución
        '--workpath=build',             # Carpeta de trabajo temporal
        '--specpath=.',                 # Donde guardar el archivo .spec
        'main.py'                       # Archivo principal
    ]
    
    print("🔨 Creando ejecutable...")
    print(f"Comando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Ejecutable creado exitosamente!")
        print(f"📁 Ubicación: dist/ReplicionAutomator.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al crear ejecutable: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def create_installer_script():
    """Crear script adicional para instalador NSIS (opcional)"""
    nsis_script = """
; ReplicionAutomator Installer
; Creado por Hector David Rubio Tabares

!include "MUI2.nsh"

Name "ReplicionAutomator"
OutFile "ReplicionAutomator_Installer.exe"
InstallDir "$PROGRAMFILES\\ReplicionAutomator"
RequestExecutionLevel admin

!define MUI_ABORTWARNING
!define MUI_ICON "assets\\icon.ico"
!define MUI_UNICON "assets\\icon.ico"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "Spanish"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File "dist\\ReplicionAutomator.exe"
    File "assets\\icon.ico"
    File "README.md"
    
    CreateDirectory "$SMPROGRAMS\\ReplicionAutomator"
    CreateShortCut "$SMPROGRAMS\\ReplicionAutomator\\ReplicionAutomator.lnk" "$INSTDIR\\ReplicionAutomator.exe" "" "$INSTDIR\\icon.ico"
    CreateShortCut "$DESKTOP\\ReplicionAutomator.lnk" "$INSTDIR\\ReplicionAutomator.exe" "" "$INSTDIR\\icon.ico"
    
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\ReplicionAutomator" "DisplayName" "ReplicionAutomator"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\ReplicionAutomator" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\ReplicionAutomator" "Publisher" "Hector David Rubio Tabares"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\ReplicionAutomator" "DisplayVersion" "1.0.0"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\ReplicionAutomator.exe"
    Delete "$INSTDIR\\icon.ico"
    Delete "$INSTDIR\\README.md"
    Delete "$INSTDIR\\Uninstall.exe"
    
    Delete "$SMPROGRAMS\\ReplicionAutomator\\ReplicionAutomator.lnk"
    RMDir "$SMPROGRAMS\\ReplicionAutomator"
    Delete "$DESKTOP\\ReplicionAutomator.lnk"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\ReplicionAutomator"
    
    RMDir "$INSTDIR"
SectionEnd
"""
    
    with open("installer.nsi", "w", encoding="utf-8") as f:
        f.write(nsis_script)
    
    print("📄 Script NSIS creado: installer.nsi")
    print("💡 Para crear instalador completo, instala NSIS y ejecuta: makensis installer.nsi")

if __name__ == "__main__":
    print("🚀 ReplicionAutomator - Generador de Instalador")
    print("👤 Creado por: Hector David Rubio Tabares")
    print("=" * 50)
    
    # Verificar que PyInstaller esté instalado
    try:
        subprocess.run(['pyinstaller', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller no está instalado. Ejecuta: pip install pyinstaller")
        sys.exit(1)
    
    # Verificar que el icono existe
    if not os.path.exists("assets/icon.ico"):
        print("⚠️  Icono no encontrado en assets/icon.ico")
        print("💡 Continuando sin icono...")
    
    # Crear ejecutable
    if create_executable():
        print("\n✅ ¡Proceso completado!")
        print("📁 Ejecutable creado en: dist/ReplicionAutomator.exe")
        print("🎯 Este archivo es standalone y no necesita Python instalado")
        
        # Crear script NSIS opcional
        create_installer_script()
        
        print("\n🎉 ¡Listo para distribuir!")
    else:
        print("\n❌ Error en el proceso")
        sys.exit(1)