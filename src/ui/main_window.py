"""
Automatizador de Replicon - Interfaz Principal
==============================================

Interfaz gráfica moderna para automatizar el registro de horas en Replicon.
Incluye funcionalidades de procesamiento CSV, automatización web y reportes.

Autor: Hector David Rubio Tabares
Fecha: 2025
"""

import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFileDialog, 
                             QMessageBox, QTextEdit, QTabWidget, QListWidget,
                             QListWidgetItem, QFrame, QProgressBar, QApplication, QDialog,
                             QSystemTrayIcon, QMenu, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QAction
from selenium.webdriver.common.by import By

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.ui.styles import MAIN_STYLE, BUTTON_SUCCESS, BUTTON_DANGER, BUTTON_WARNING
from src.ui.horario_dialog import HorarioDialog
from src.core.selenium_handler import SeleniumHandler
from src.core.csv_processor import CSVProcessor
from src.core.account_mapper import AccountMapper
from config.config import Config

class AutomationWorker(QThread):
    """Worker thread para ejecutar la automatización sin bloquear la UI"""
    progress_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, email, password, csv_file, horarios, mapeo_cuentas, headless=False):
        super().__init__()
        self.email = email
        self.password = password
        self.csv_file = csv_file
        self.horarios = horarios
        self.mapeo_cuentas = mapeo_cuentas
        self.headless = headless
        self.selenium_handler = None  # Referencia al handler para poder cerrarlo
        
    def run(self):
        try:
            # Inicializar componentes
            self.selenium_handler = SeleniumHandler()
            csv_processor = CSVProcessor()
            csv_processor.set_csv_file(self.csv_file)
            
            # Procesar CSV
            self.progress_update.emit("Procesando archivo CSV...")
            time_entries = csv_processor.process_csv_with_pandas(self.horarios, self.mapeo_cuentas)
            
            # Configurar navegador (en segundo plano si se especifica)
            self.progress_update.emit("Iniciando navegador...")
            self.selenium_handler.setup_driver(headless=self.headless)
            
            # Login
            self.progress_update.emit("Iniciando sesión...")
            self.selenium_handler.login(self.email, self.password)
            
            # Seleccionar mes
            self.progress_update.emit("Seleccionando mes...")
            self.selenium_handler.select_month()
            
            # Procesar entradas de forma optimizada
            total_entries = len(time_entries)
            for i, daily_entries in enumerate(time_entries, start=2):
                self.progress_update.emit(f"Procesando día {i-1} de {total_entries}...")
                
                # Verificar si es día de vacaciones o feriado
                vacation_elements = self.selenium_handler.find_elements_safe(
                    By.XPATH, f"//li[{i}]/ul/li/div/span[contains(text(), 'Col-Vacations')]"
                )
                holiday_elements = self.selenium_handler.find_elements_safe(
                    By.XPATH, f"//li[{i}]/div/div[@class='holidayIndicator']"
                )
                
                if vacation_elements or holiday_elements:
                    continue
                
                # Filtrar entradas válidas
                valid_entries = [entry for entry in daily_entries 
                               if entry["project"] not in ["Vacation", "No work"]]
                
                if valid_entries:
                    # Procesar todas las entradas del día de una vez (optimizado)
                    self.selenium_handler.batch_entries_same_day(i, valid_entries)
            
            # Cerrar navegador
            self.selenium_handler.close_driver()
            
            self.finished.emit(True, "Proceso completado exitosamente")
            
        except Exception as e:
            # Asegurar que se cierre el navegador en caso de error
            if self.selenium_handler:
                try:
                    self.selenium_handler.close_driver()
                except:
                    pass
            self.finished.emit(False, f"Error en el proceso: {str(e)}")
    
    def close_browser(self):
        """Cerrar navegador si está abierto"""
        if self.selenium_handler:
            try:
                self.selenium_handler.close_driver()
            except:
                pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.account_mapper = AccountMapper()
        self.csv_processor = CSVProcessor()
        self.horarios = self.config.load_horarios()
        self.csv_file = None
        self.worker = None
        self.tray_icon = None
        
        self.init_ui()
        self.load_saved_credentials()  # Cargar credenciales guardadas
        
    def get_app_icon(self):
        """Obtener el icono de la aplicación"""
        # Intentar diferentes rutas para el icono
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets", "icon.ico"),
            os.path.join(sys._MEIPASS, "assets", "icon.ico") if hasattr(sys, '_MEIPASS') else None,
            "assets/icon.ico",
            "./assets/icon.ico"
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                return QIcon(path)
        
        # Icono por defecto si no se encuentra ninguno
        return self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
    
    def setup_system_tray(self):
        """Configurar icono en bandeja del sistema"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(self, "Bandeja del sistema", 
                               "No se detectó bandeja del sistema en este equipo.")
            return
        
        # Crear icono para la bandeja
        self.tray_icon = QSystemTrayIcon(self)
        
        # Usar el mismo icono que la ventana principal
        self.tray_icon.setIcon(self.get_app_icon())
        
        # Crear menú contextual
        tray_menu = QMenu()
        
        show_action = QAction("Mostrar", self)
        show_action.triggered.connect(self.show_from_tray)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Salir", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Mostrar icono en bandeja
        self.tray_icon.show()
        self.tray_icon.showMessage(
            "Automatizador de Replicon",
            "La aplicación se está ejecutando en segundo plano",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
    
    def show_from_tray(self):
        """Mostrar ventana desde la bandeja del sistema"""
        self.show()
        self.raise_()
        self.activateWindow()
    
    def tray_icon_activated(self, reason):
        """Manejar clics en el icono de la bandeja"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_from_tray()
        
    def init_ui(self):
        """Inicializar la interfaz de usuario"""
        self.setWindowTitle(self.config.APP_TITLE)
        self.setGeometry(100, 100, self.config.APP_WIDTH, self.config.APP_HEIGHT)
        
        # Configurar icono de la ventana
        self.setWindowIcon(self.get_app_icon())
        
        # Hacer ventana no redimensionable
        self.setFixedSize(self.config.APP_WIDTH, self.config.APP_HEIGHT)
        
        # Aplicar estilos
        self.setStyleSheet(MAIN_STYLE)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal (sin margen superior para reducir espacio)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 2, 10, 10)
        main_layout.setSpacing(6)
        
        # Crear tabs
        tab_widget = QTabWidget()
        # Reducir espacio entre la barra de tabs y el contenido
        tab_widget.setStyleSheet("QTabWidget::pane{top:-6px;} QTabBar::tab{padding:4px 10px;}")
        
        # Tab de automatización
        automation_tab = self.create_automation_tab()
        tab_widget.addTab(automation_tab, "Automatización")
        
        # Tab de configuración
        config_tab = self.create_config_tab()
        tab_widget.addTab(config_tab, "Configuración")
        
        # Tab de reportes
        reports_tab = self.create_reports_tab()
        tab_widget.addTab(reports_tab, "Reportes")
        
        # Tab de documentación
        docs_tab = self.create_documentation_tab()
        tab_widget.addTab(docs_tab, "Documentación")
        
        main_layout.addWidget(tab_widget)
        
        # Centrar ventana
        self.center_window()
    
    def create_automation_tab(self):
        """Crear tab de automatización principal"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 4, 6, 6)
        layout.setSpacing(8)
        
        # Frame de credenciales
        cred_frame = QFrame()
        cred_layout = QVBoxLayout(cred_frame)
        
        # Para alineación consistente usamos un ancho fijo de labels
        label_width = 110  # Alineación estable

        # Email
        email_layout = QHBoxLayout()
        email_label = QLabel("Correo:")
        email_label.setFixedWidth(label_width)
        email_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        email_layout.addWidget(email_label)
        self.email_entry = QLineEdit()
        self.email_entry.setPlaceholderText("usuario@empresa.com")
        email_layout.addWidget(self.email_entry, 1)
        cred_layout.addLayout(email_layout)

        # Password
        password_layout = QHBoxLayout()
        password_label = QLabel("Contraseña:")
        password_label.setFixedWidth(label_width)
        password_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        password_layout.addWidget(password_label)
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_entry.setPlaceholderText("Contraseña")
        password_layout.addWidget(self.password_entry, 1)
        cred_layout.addLayout(password_layout)

        # Checkbox Remember me
        remember_layout = QHBoxLayout()
        remember_spacer = QLabel("")  # Espaciador para alineación
        remember_spacer.setFixedWidth(label_width)
        remember_layout.addWidget(remember_spacer)
        self.remember_checkbox = QCheckBox("Recordar mis credenciales")
        self.remember_checkbox.setStyleSheet("QCheckBox { font-size: 12px; color: #666; }")
        remember_layout.addWidget(self.remember_checkbox)
        remember_layout.addStretch()  # Empujar a la izquierda
        cred_layout.addLayout(remember_layout)

        # Archivo CSV
        csv_layout = QHBoxLayout()
        csv_label_title = QLabel("Archivo CSV:")
        csv_label_title.setFixedWidth(label_width)
        csv_label_title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        csv_layout.addWidget(csv_label_title)
        self.csv_label = QLabel("No seleccionado")
        self.csv_label.setStyleSheet("color: #bbb;")
        csv_layout.addWidget(self.csv_label, 1)
        self.select_csv_btn = QPushButton("Seleccionar CSV")
        self.select_csv_btn.clicked.connect(self.select_csv_file)
        csv_layout.addWidget(self.select_csv_btn)
        cred_layout.addLayout(csv_layout)
        
        layout.addWidget(cred_frame)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Iniciar Automatización")
        self.start_btn.setStyleSheet(BUTTON_SUCCESS)
        self.start_btn.clicked.connect(self.start_automation)
        self.start_btn.setEnabled(False)
        buttons_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Detener")
        self.stop_btn.setStyleSheet(BUTTON_DANGER)
        self.stop_btn.clicked.connect(self.stop_automation)
        self.stop_btn.setEnabled(False)
        buttons_layout.addWidget(self.stop_btn)
        
        layout.addLayout(buttons_layout)

        # Opciones adicionales (en una sola fila)
        options_layout = QHBoxLayout()
        self.background_checkbox = QCheckBox("Segundo plano (oculto)")
        self.background_checkbox.setToolTip("Ejecuta el navegador de forma invisible")
        self.minimize_tray_checkbox = QCheckBox("Minimizar a bandeja")
        self.minimize_tray_checkbox.setToolTip("La ventana se ocultará en la bandeja mientras corre")
        options_layout.addWidget(self.background_checkbox)
        options_layout.addWidget(self.minimize_tray_checkbox)
        options_layout.addStretch(1)
        layout.addLayout(options_layout)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Log de actividad
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setPlaceholderText("Los mensajes de actividad aparecerán aquí...")
        layout.addWidget(self.log_text)
        
        # Conectar validación de campos
        self.email_entry.textChanged.connect(self.validate_fields)
        self.password_entry.textChanged.connect(self.validate_fields)
        
        return widget
    
    def create_config_tab(self):
        """Crear tab de configuración"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Horarios
        horarios_frame = QFrame()
        horarios_layout = QVBoxLayout(horarios_frame)
        
        horarios_layout.addWidget(QLabel("Horarios Configurados:"))
        
        self.horarios_list = QListWidget()
        self.update_horarios_list()
        horarios_layout.addWidget(self.horarios_list)
        
        # Botones de horarios
        horarios_buttons = QHBoxLayout()
        
        add_horario_btn = QPushButton("Agregar Horario")
        add_horario_btn.clicked.connect(self.add_horario_dialog)
        horarios_buttons.addWidget(add_horario_btn)
        
        edit_horario_btn = QPushButton("Editar Seleccionado")
        edit_horario_btn.setStyleSheet(BUTTON_WARNING)
        edit_horario_btn.clicked.connect(self.edit_horario_dialog)
        horarios_buttons.addWidget(edit_horario_btn)
        
        remove_horario_btn = QPushButton("Eliminar Seleccionado")
        remove_horario_btn.setStyleSheet(BUTTON_DANGER)
        remove_horario_btn.clicked.connect(self.remove_horario)
        horarios_buttons.addWidget(remove_horario_btn)
        
        horarios_layout.addLayout(horarios_buttons)
        layout.addWidget(horarios_frame)
        
        return widget
    
    def create_reports_tab(self):
        """Crear tab de reportes"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Botón para generar reporte
        generate_report_btn = QPushButton("Generar Reporte de Horas")
        generate_report_btn.clicked.connect(self.generate_hours_report)
        layout.addWidget(generate_report_btn)
        
        # Área de reporte
        self.report_text = QTextEdit()
        self.report_text.setPlaceholderText("El reporte de horas aparecerá aquí...")
        layout.addWidget(self.report_text)
        
        return widget
    
    def create_documentation_tab(self):
        """Crear tab de documentación y ayuda"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Título
        title_label = QLabel("📖 Guía de Uso - ReplicionAutomator")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Información del autor
        author_label = QLabel("👤 Creado por: <b>Hector David Rubio Tabares</b> • Versión 2025")
        author_label.setStyleSheet("font-size: 12px; color: #666; margin-bottom: 15px;")
        layout.addWidget(author_label)
        
        # Área de documentación con scroll
        docs_area = QTextEdit()
        docs_area.setReadOnly(True)
        docs_content = """
<h3>🚀 Pasos para usar la aplicación:</h3>

<p><b>1. Configurar credenciales:</b></p>
<ul>
<li>Ingresa tu correo electrónico de Replicon</li>
<li>Ingresa tu contraseña</li>
</ul>

<p><b>2. Seleccionar archivo CSV:</b></p>
<ul>
<li>Haz clic en "Seleccionar CSV" para elegir tu archivo de datos</li>
<li>El archivo debe tener columnas: Date, Start Time, End Time, Project</li>
<li>Puedes generar un archivo demo usando el botón de abajo</li>
</ul>

<p><b>3. Configurar horarios (pestaña Configuración):</b></p>
<ul>
<li>Define los horarios de trabajo (ej: 7:00am - 1:00pm, 2:00pm - 4:00pm)</li>
<li>Estos horarios se usarán para distribuir las horas del CSV</li>
</ul>

<p><b>4. Opciones de ejecución:</b></p>
<ul>
<li><b>Segundo plano:</b> El navegador será invisible durante la automatización</li>
<li><b>Minimizar a bandeja:</b> La ventana se ocultará en la bandeja del sistema</li>
</ul>

<p><b>5. Iniciar automatización:</b></p>
<ul>
<li>Haz clic en "Iniciar Automatización"</li>
<li>El proceso se ejecutará automáticamente</li>
<li>Puedes ver el progreso en el área de actividad</li>
</ul>

<h3>📋 Formato del archivo CSV:</h3>

<p>Tu archivo CSV debe tener estas columnas exactas:</p>
<ul>
<li><b>Cuenta:</b> Código de la cuenta (ej: PROD, DEV, TEST)</li>
<li><b>Projecto:</b> Código del proyecto (ej: PI, QA, DOC)</li>
<li><b>EXT (opcional):</b> Entradas especiales con horarios específicos</li>
</ul>

<p><b>Ejemplo de archivo CSV:</b></p>
<pre>
Cuenta,Projecto
PROD,PI
DEV,QA
TEST,DOC
</pre>

<p><b>Formato EXT (avanzado):</b></p>
<p>Si necesitas horarios específicos, puedes usar la columna EXT:</p>
<pre>
Cuenta,Projecto,EXT
PROD,PI,EXT/PROD:PI:0900:1200;PROD:PI:1300:1700
</pre>
<p>Donde: CUENTA:PROYECTO:INICIO:FIN (horarios en formato militar 24h)</p>

<p><b>Formato ND (solo EXT):</b></p>
<p>Si solo quieres registrar horarios específicos sin crear entradas normales, usa ND:</p>
<pre>
Cuenta,Projecto,EXT
ND,ND,EXT/PROD:PI:1600:2000
</pre>
<p><b>ND,ND</b> = No crear entradas normales, solo procesar las entradas EXT especificadas</p>

<h3>🔧 Configuración:</h3>
<p>Toda la configuración se realiza desde la interfaz de la aplicación:</p>
<ul>
<li><b>Horarios:</b> Usa la pestaña "Configuración" para definir tus horarios de trabajo</li>
<li><b>Tamaño de ventana:</b> Puedes redimensionar arrastrando los bordes de la ventana</li>
<li><b>Credenciales:</b> Se configuran en la pestaña principal "Automatización"</li>
</ul>

<h3>⚠️ Solución de problemas:</h3>
<ul>
<li>Si el CSV no es válido, verifica que tenga las columnas correctas</li>
<li>Si falla el login, verifica tus credenciales en la pestaña principal</li>
<li>Si no encuentra elementos en la página, asegúrate de usar la URL correcta de Replicon</li>
<li>Si la aplicación se cierra inesperadamente, revisa los mensajes en el área de actividad</li>
</ul>

<h3>💡 Consejos:</h3>
<ul>
<li>Usa el archivo CSV demo para probar la aplicación antes de usar tus datos reales</li>
<li>La ventana se puede redimensionar para adaptarse a tu pantalla</li>
<li>El modo "segundo plano" es útil para que no interfiera con otras aplicaciones</li>
<li>Puedes usar "minimizar a bandeja" para ocultar la ventana durante la ejecución</li>
</ul>
"""
        docs_area.setHtml(docs_content)
        layout.addWidget(docs_area)
        
        # Botón para generar CSV demo
        demo_btn = QPushButton("📁 Generar Archivo CSV Demo")
        demo_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }")
        demo_btn.clicked.connect(self.generate_demo_csv)
        layout.addWidget(demo_btn)
        
        return widget
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        x = (screen.width() - window.width()) // 2
        y = (screen.height() - window.height()) // 2
        self.move(x, y)
    
    def select_csv_file(self):
        """Seleccionar archivo CSV"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo CSV",
            "",
            "CSV files (*.csv);;All files (*.*)"
        )
        
        if file_path:
            self.csv_file = file_path
            filename = os.path.basename(file_path)
            self.csv_label.setText(f"Archivo CSV: {filename}")
            
            # Validar formato del CSV
            self.csv_processor.set_csv_file(file_path)
            is_valid, message = self.csv_processor.validate_csv_format()
            
            if not is_valid:
                QMessageBox.warning(self, "Archivo inválido", f"El archivo CSV no es válido:\n{message}")
                self.csv_file = None
                self.csv_label.setText("Archivo CSV: No seleccionado")
            else:
                self.log_message(f"Archivo CSV cargado correctamente: {filename}")
            
            self.validate_fields()
    
    def validate_fields(self):
        """Validar campos obligatorios"""
        email_valid = bool(self.email_entry.text().strip())
        password_valid = bool(self.password_entry.text().strip())
        csv_valid = bool(self.csv_file)
        
        self.start_btn.setEnabled(email_valid and password_valid and csv_valid)
    
    def start_automation(self):
        """Iniciar proceso de automatización"""
        if self.worker and self.worker.isRunning():
            return
        
        # Configurar UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminado
        
        # Limpiar log
        self.log_text.clear()
        
        # Verificar si debe minimizar a bandeja
        if self.minimize_tray_checkbox.isChecked():
            self.setup_system_tray()
            self.hide()
            self.log_message("Aplicación minimizada a bandeja del sistema...")
        
        self.log_message("Iniciando automatización...")
        
        # Guardar credenciales si está marcado el checkbox
        self.save_credentials_if_checked()
        
        # Obtener modo segundo plano
        headless_mode = self.background_checkbox.isChecked()
        if headless_mode:
            self.log_message("Modo segundo plano activado - navegador oculto")
        
        # Crear worker thread
        self.worker = AutomationWorker(
            self.email_entry.text().strip(),
            self.password_entry.text().strip(),
            self.csv_file,
            self.horarios,
            self.account_mapper.get_mapping(),
            headless=headless_mode
        )
        
        # Conectar señales
        self.worker.progress_update.connect(self.log_message)
        self.worker.finished.connect(self.automation_finished)
        
        # Iniciar worker
        self.worker.start()
    
    def stop_automation(self):
        """Detener proceso de automatización"""
        if self.worker and self.worker.isRunning():
            # Cerrar navegador antes de terminar el worker
            self.worker.close_browser()
            # Terminar worker
            self.worker.terminate()
            self.worker.wait()
        
        self.automation_finished(False, "Proceso detenido por el usuario")
    
    def automation_finished(self, success, message):
        """Manejar finalización de automatización"""
        # Restaurar UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        # Mostrar resultado
        if success:
            self.log_message("✅ " + message)
            # Si está en la bandeja, mostrar notificación
            if self.tray_icon and self.tray_icon.isVisible():
                self.tray_icon.showMessage(
                    "Automatización Completada",
                    message,
                    QSystemTrayIcon.MessageIcon.Information,
                    5000
                )
            else:
                QMessageBox.information(self, "Éxito", message)
        else:
            self.log_message("❌ " + message)
            # Si está en la bandeja, mostrar notificación de error
            if self.tray_icon and self.tray_icon.isVisible():
                self.tray_icon.showMessage(
                    "Error en Automatización",
                    message,
                    QSystemTrayIcon.MessageIcon.Critical,
                    5000
                )
            else:
                QMessageBox.critical(self, "Error", message)
    
    def log_message(self, message):
        """Agregar mensaje al log"""
        self.log_text.append(f"[{QTimer().remainingTime()}] {message}")
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def update_horarios_list(self):
        """Actualizar lista de horarios"""
        self.horarios_list.clear()
        for i, horario in enumerate(self.horarios):
            item_text = f"{horario['start_time']} - {horario['end_time']}"
            self.horarios_list.addItem(item_text)
    
    def add_horario_dialog(self):
        """Diálogo para agregar horario"""
        dialog = HorarioDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            nuevo_horario = dialog.get_horario()
            if nuevo_horario:
                self.horarios.append(nuevo_horario)
                self.config.save_horarios(self.horarios)
                self.update_horarios_list()
                self.log_message(f"Horario agregado: {nuevo_horario['start_time']} - {nuevo_horario['end_time']}")
    
    def edit_horario_dialog(self):
        """Diálogo para editar horario"""
        current_row = self.horarios_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Advertencia", "Seleccione un horario para editar")
            return
        
        horario_actual = self.horarios[current_row]
        dialog = HorarioDialog(self, horario_actual)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            horario_editado = dialog.get_horario()
            if horario_editado:
                self.horarios[current_row] = horario_editado
                self.config.save_horarios(self.horarios)
                self.update_horarios_list()
                self.log_message(f"Horario editado: {horario_editado['start_time']} - {horario_editado['end_time']}")
    
    def remove_horario(self):
        """Eliminar horario seleccionado"""
        current_row = self.horarios_list.currentRow()
        if current_row >= 0:
            del self.horarios[current_row]
            self.config.save_horarios(self.horarios)
            self.update_horarios_list()
            self.log_message("Horario eliminado")
    
    def generate_hours_report(self):
        """Generar reporte de horas con detalles semanales y horas extra"""
        if not self.csv_file:
            QMessageBox.warning(self, "Advertencia", "Seleccione un archivo CSV primero")
            return
        
        try:
            # Procesar CSV para obtener entradas
            time_entries = self.csv_processor.process_csv_with_pandas(
                self.horarios, 
                self.account_mapper.get_mapping()
            )
            
            # Calcular resumen
            summary = self.csv_processor.calculate_hours_summary(time_entries)
            
            # Obtener mes y año del archivo CSV
            import os
            from datetime import datetime
            csv_name = os.path.basename(self.csv_file)
            # Intentar extraer mes y año del nombre del archivo
            current_date = datetime.now()
            month_name = current_date.strftime("%B %Y")
            
            # Generar reporte
            report = f"""
📊 REPORTE MENSUAL DE HORAS - {month_name.upper()}
═══════════════════════════════════════════

📅 RESUMEN GENERAL:
─────────────────
• Total de días: {summary['total_days']}
• Total de horas: {summary['total_hours']:.2f}h
• Promedio de horas por día: {summary['average_hours_per_day']:.2f}h

⏰ ANÁLISIS DE HORAS:
──────────────────
• Horas regulares: {summary['regular_hours']:.2f}h
• Horas extra diarias: {summary['overtime_daily']:.2f}h
• Horas extra semanales: {summary['overtime_weekly']:.2f}h
• Estándar diario: {summary['standard_hours_per_day']}h
• Estándar semanal: {summary['standard_hours_per_week']}h

📈 HORAS POR SEMANA DEL MES:
───────────────────────────
"""
            
            for week, week_data in summary['hours_by_week'].items():
                week_hours = week_data['hours']
                week_days = week_data['days']
                avg_daily = week_hours / week_days if week_days > 0 else 0
                overtime_week = max(0, week_hours - summary['standard_hours_per_week'])
                
                report += f"• {week}: {week_hours:.2f}h ({week_days} días, promedio {avg_daily:.2f}h/día)"
                if overtime_week > 0:
                    report += f" (Extra: {overtime_week:.2f}h)"
                report += "\n"
            
            report += f"""
🏢 HORAS DE TRABAJO POR PROYECTO:
───────────────────────────────
"""
            
            # Separar proyectos de trabajo y tiempo libre
            work_projects = {}
            time_off_projects = {}
            
            for project, hours in summary['hours_by_project'].items():
                if project in ['Vacation', 'No work', 'Holiday', 'Weekend', 'ND', 'Desconocido']:
                    time_off_projects[project] = hours
                else:
                    work_projects[project] = hours
            
            # Mostrar proyectos de trabajo con porcentajes basados solo en horas trabajadas
            work_total = sum(work_projects.values())
            for project, hours in work_projects.items():
                percentage = (hours / work_total) * 100 if work_total > 0 else 0
                report += f"• {project}: {hours:.2f}h ({percentage:.1f}%)\n"
            
            # Mostrar tiempo libre por separado
            if time_off_projects:
                report += f"""
🏖️ TIEMPO LIBRE / VACACIONES:
───────────────────────────
"""
                for project, hours in time_off_projects.items():
                    report += f"• {project}: {hours:.2f}h\n"
            
            # Agregar análisis de eficiencia
            efficiency_score = (summary['regular_hours'] / summary['total_hours']) * 100 if summary['total_hours'] > 0 else 0
            report += f"""
📊 ANÁLISIS DE EFICIENCIA:
────────────────────────
• Porcentaje de horas regulares: {efficiency_score:.1f}%
• Porcentaje de horas extra: {100 - efficiency_score:.1f}%
"""
            
            if summary['overtime_daily'] > 10:
                report += "⚠️ ALERTA: Alto nivel de horas extra detectado\n"
            elif summary['overtime_daily'] > 0:
                report += "⚡ Horas extra moderadas\n"
            else:
                report += "✅ Sin horas extra registradas\n"
            
            self.report_text.setText(report)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar reporte: {str(e)}")
    
    def generate_demo_csv(self):
        """Generar archivo CSV demo con datos de ejemplo"""
        try:
            from datetime import datetime, timedelta
            import csv
            import os
            
            # Obtener ruta para guardar el archivo demo
            downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
            demo_filename = f"demo_replicon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            demo_path = os.path.join(downloads_folder, demo_filename)
            
            # Datos de ejemplo con formato correcto (Cuenta, Projecto)
            demo_data = [
                ["PROD", "PI"],
                ["PROD", "QA"],
                ["DEV", "WEB"],
                ["DEV", "API"],
                ["TEST", "AUTO"],
                ["TEST", "MAN"],
                ["DOC", "USER"],
                ["DOC", "TECH"],
                ["MAINT", "SYS"],
                ["MAINT", "DB"],
                # Ejemplos con EXT (horarios específicos)
                ["PROD", "SPEC", "EXT/PROD:SPEC:0900:1200;PROD:SPEC:1300:1600"],
                ["DEV", "URGENT", "EXT/DEV:URGENT:0800:1000;DEV:URGENT:1400:1800"],
                # Ejemplo con ND (solo entradas EXT, sin horarios normales)
                ["ND", "ND", "EXT/PROD:PI:1600:2000"],
                ["ND", "ND", "EXT/DEV:API:0700:0900;DEV:API:1900:2100"],
            ]
            
            # Escribir archivo CSV
            with open(demo_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Escribir encabezados correctos
                writer.writerow(["Cuenta", "Projecto", "EXT"])
                
                # Escribir datos de ejemplo
                writer.writerows(demo_data)
            
            # Confirmar creación
            QMessageBox.information(
                self, 
                "CSV Demo Creado", 
                f"Archivo demo creado exitosamente:\n\n{demo_path}\n\n"
                f"El archivo contiene {len(demo_data)} entradas de ejemplo con el formato correcto."
            )
            
            self.log_message(f"Archivo CSV demo creado: {demo_filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al crear archivo demo: {str(e)}")
    
    def closeEvent(self, event):
        """Manejar cierre de ventana"""
        if self.tray_icon and self.tray_icon.isVisible():
            # Si hay proceso ejecutándose, minimizar a bandeja
            if self.worker and self.worker.isRunning():
                self.hide()
                self.tray_icon.showMessage(
                    "Automatizador de Replicon",
                    "La aplicación sigue ejecutándose en segundo plano",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000
                )
                event.ignore()
            else:
                # Si no hay proceso, preguntar si quiere cerrar
                reply = QMessageBox.question(self, "Confirmar cierre",
                                           "¿Desea cerrar la aplicación?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    event.accept()
                else:
                    self.hide()
                    event.ignore()
        else:
            # Comportamiento normal si no está en bandeja
            event.accept()
    
    def closeEvent(self, event):
        """Manejar cierre de aplicación"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, 
                "Confirmar cierre",
                "Hay un proceso en ejecución. ¿Desea cerrarlo y salir?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.worker.terminate()
                self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
    
    def load_saved_credentials(self):
        """Cargar credenciales guardadas si existen"""
        try:
            email, password = self.config.load_credentials()
            if email and password:
                self.email_entry.setText(email)
                self.password_entry.setText(password)
                self.remember_checkbox.setChecked(True)
        except Exception:
            # Si hay error cargando credenciales, simplemente no las carga
            pass
    
    def save_credentials_if_checked(self):
        """Guardar credenciales si está marcado el checkbox"""
        if self.remember_checkbox.isChecked():
            email = self.email_entry.text().strip()
            password = self.password_entry.text().strip()
            if email and password:
                self.config.save_credentials(email, password)
        else:
            # Si no está marcado, borrar credenciales guardadas
            self.config.clear_credentials()