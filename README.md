# ReplicionAutomator

Una aplicación moderna para automatizar el registro de horas en Replicon.

**Autor:** Hector David Rubio Tabares  
**Versión:** 2025  
**Licencia:** Desarrollo Personal

## Estructura del Proyecto

```
ReplicionAutomator/
│
├── src/
│   ├── core/           # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── selenium_handler.py
│   │   ├── csv_processor.py
│   │   └── account_mapper.py
│   │
│   ├── ui/             # Interfaz de usuario
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   └── styles.py
│   │
│   └── __init__.py
│
├── config/             # Archivos de configuración
│   ├── .env
│   ├── horarios.json
│   └── config.py
│
├── assets/            # Iconos y recursos
│
├── main.py           # Punto de entrada
├── requirements.txt  # Dependencias
└── README.md        # Este archivo
```

## Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
```

2. Activar entorno virtual:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecutar la aplicación:
```bash
python main.py
```

## Características

- ✅ Interfaz moderna con PyQt6
- ✅ Configuración externa (archivos .env y JSON)
- ✅ Horarios personalizables
- ✅ Reporte de horas extra
- ✅ Arquitectura modular y profesional