from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
from datetime import datetime

class HorarioDialog(QDialog):
    """Diálogo para agregar/editar horarios"""
    
    def __init__(self, parent=None, horario=None):
        super().__init__(parent)
        self.horario = horario
        self.init_ui()
        
        if horario:
            self.start_time_edit.setText(horario['start_time'])
            self.end_time_edit.setText(horario['end_time'])
    
    def init_ui(self):
        self.setWindowTitle("Configurar Horario")
        self.setModal(True)
        self.resize(300, 150)
        
        layout = QVBoxLayout(self)
        
        # Hora de inicio
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Hora de inicio:"))
        self.start_time_edit = QLineEdit()
        self.start_time_edit.setPlaceholderText("Ej: 8:00am")
        start_layout.addWidget(self.start_time_edit)
        layout.addLayout(start_layout)
        
        # Hora de fin
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("Hora de fin:"))
        self.end_time_edit = QLineEdit()
        self.end_time_edit.setPlaceholderText("Ej: 5:00pm")
        end_layout.addWidget(self.end_time_edit)
        layout.addLayout(end_layout)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save_horario)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def save_horario(self):
        start_time = self.start_time_edit.text().strip()
        end_time = self.end_time_edit.text().strip()
        
        if not start_time or not end_time:
            QMessageBox.warning(self, "Error", "Debe completar ambos campos")
            return
        
        # Validar formato de hora
        if not self.validate_time_format(start_time) or not self.validate_time_format(end_time):
            QMessageBox.warning(self, "Error", "Formato de hora inválido. Use formato como '8:00am' o '5:30pm'")
            return
        
        # Validar que la hora de fin sea posterior a la de inicio
        if not self.validate_time_order(start_time, end_time):
            QMessageBox.warning(self, "Error", "La hora de fin debe ser posterior a la hora de inicio")
            return
        
        self.result_horario = {
            'start_time': start_time,
            'end_time': end_time
        }
        
        self.accept()
    
    def validate_time_format(self, time_str):
        """Validar formato de hora"""
        try:
            datetime.strptime(time_str, "%I:%M%p")
            return True
        except ValueError:
            return False
    
    def validate_time_order(self, start_time, end_time):
        """Validar que el orden de las horas sea correcto"""
        try:
            fmt = "%I:%M%p"
            start = datetime.strptime(start_time, fmt)
            end = datetime.strptime(end_time, fmt)
            return end > start
        except ValueError:
            return False
    
    def get_horario(self):
        """Obtener el horario configurado"""
        return getattr(self, 'result_horario', None)