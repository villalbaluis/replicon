@echo off
REM Script optimizado para crear ejecutable del Automatizador de Replicon
REM Creado por: Hector David Rubio Tabares

echo ========================================
echo  REPLICIONAUTOMATOR - BUILD EJECUTABLE
echo ========================================
echo 👤 Creado por: Hector David Rubio Tabares
echo.

REM Verificar PyInstaller
python -c "import pyinstaller" 2>nul
if errorlevel 1 (
    echo 📦 Instalando PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ Error instalando PyInstaller
        pause
        exit /b 1
    )
)

echo 🔨 Creando ejecutable sin consola...
pyinstaller ^
    --onefile ^
    --windowed ^
    --icon=assets\icon.ico ^
    --name=ReplicionAutomator ^
    --optimize=2 ^
    --add-data="config;config" ^
    --add-data="assets;assets" ^
    --hidden-import=pandas ^
    --hidden-import=selenium ^
    --hidden-import=PyQt6 ^
    --distpath=dist ^
    --workpath=build ^
    --clean ^
    main.py

if errorlevel 1 (
    echo ❌ Error al crear ejecutable
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ BUILD COMPLETADO EXITOSAMENTE
echo ========================================
echo 📁 Ejecutable: dist\ReplicionAutomator.exe
echo 🎯 Características:
echo    - Sin ventana de consola
echo    - Icono personalizado
echo    - Un solo archivo ejecutable
echo    - Incluye todas las dependencias
echo.
echo 📊 Tamaño del archivo:
dir dist\ReplicionAutomator.exe | findstr ReplicionAutomator.exe
echo.
echo 💡 Para distribuir: Copia el archivo .exe y la carpeta config
echo 🚀 Listo para usar sin Python instalado
pause