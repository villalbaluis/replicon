# ReplicionAutomator - Instrucciones de Distribución

**Creado por:** Hector David Rubio Tabares  
**Año:** 2025

## Para crear el ejecutable (.exe):

1. **Activar entorno virtual:**
   ```
   .\venv\Scripts\activate
   ```

2. **Ejecutar script de build:**
   ```
   .\build_exe.bat
   ```

3. **El ejecutable se creará en:** `dist\ReplicionAutomator.exe`

## Para distribuir a otros usuarios:

1. **Copia estos archivos/carpetas:**
   - `ReplicionAutomator.exe` (archivo principal)
   - `config\` (carpeta con configuraciones)
   - `README_Usuario.txt` (instrucciones para el usuario)

2. **Requisitos del sistema del usuario:**
   - Windows 10/11
   - Chrome instalado
   - Conexión a internet

## Características del ejecutable optimizado:

- ✅ **Archivo único** - No necesita instalación
- ✅ **Sin consola** - Interfaz limpia
- ✅ **Iconos incluidos** - Interfaz profesional
- ✅ **Optimizado** - Tamaño reducido
- ✅ **Dependencias incluidas** - PyQt6, Selenium, Pandas
- ✅ **Configuración externa** - Fácil de personalizar

## Tamaño estimado del ejecutable:
- Aproximadamente 80-120 MB (incluye todas las dependencias)

## Pruebas antes de distribuir:
1. Probar en máquina limpia (sin Python)
2. Verificar que Chrome esté instalado
3. Probar con diferentes archivos CSV
4. Verificar funcionamiento en segundo plano