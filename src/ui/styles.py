# Estilos modernos para la aplicación PyQt6

MAIN_STYLE = """
QMainWindow {
    background-color: #2C3E50;
    color: #ECF0F1;
}

QFrame {
    background-color: #34495E;
    border-radius: 10px;
    padding: 10px;
    margin: 5px;
}

QLabel {
    color: #ECF0F1;
    font-size: 12px;
    font-weight: bold;
    padding: 5px;
}

QLineEdit {
    background-color: #ECF0F1;
    border: 2px solid #3498DB;
    border-radius: 8px;
    padding: 8px;
    font-size: 12px;
    color: #2C3E50;
}

QLineEdit:focus {
    border-color: #2980B9;
    background-color: #FFFFFF;
}

QPushButton {
    background-color: #3498DB;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 12px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2980B9;
}

QPushButton:pressed {
    background-color: #21618C;
}

QPushButton:disabled {
    background-color: #BDC3C7;
    color: #7F8C8D;
}

QTextEdit {
    background-color: #ECF0F1;
    border: 2px solid #3498DB;
    border-radius: 8px;
    padding: 8px;
    font-size: 11px;
    color: #2C3E50;
}

QListWidget {
    background-color: #ECF0F1;
    border: 2px solid #3498DB;
    border-radius: 8px;
    padding: 5px;
    color: #2C3E50;
    font-size: 11px;
}

QListWidget::item {
    padding: 5px;
    border-bottom: 1px solid #BDC3C7;
}

QListWidget::item:selected {
    background-color: #3498DB;
    color: white;
}

QTabWidget::pane {
    border: 2px solid #3498DB;
    border-radius: 8px;
    background-color: #34495E;
}

QTabBar::tab {
    background-color: #2C3E50;
    color: #ECF0F1;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background-color: #3498DB;
    color: white;
}

QTabBar::tab:hover {
    background-color: #2980B9;
}

QProgressBar {
    border: 2px solid #3498DB;
    border-radius: 8px;
    text-align: center;
    background-color: #ECF0F1;
}

QProgressBar::chunk {
    background-color: #3498DB;
    border-radius: 6px;
}

QMenuBar {
    background-color: #2C3E50;
    color: #ECF0F1;
    padding: 4px;
}

QMenuBar::item {
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #3498DB;
}

QMenu {
    background-color: #34495E;
    color: #ECF0F1;
    border: 1px solid #3498DB;
    border-radius: 6px;
}

QMenu::item {
    padding: 6px 12px;
}

QMenu::item:selected {
    background-color: #3498DB;
}
"""

CARD_STYLE = """
QFrame {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 12px;
    padding: 15px;
    margin: 8px;
}

QFrame:hover {
    border-color: #3498DB;
    box-shadow: 0px 4px 8px rgba(52, 152, 219, 0.3);
}
"""

BUTTON_SUCCESS = """
QPushButton {
    background-color: #27AE60;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 12px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #229954;
}

QPushButton:pressed {
    background-color: #1E8449;
}
"""

BUTTON_DANGER = """
QPushButton {
    background-color: #E74C3C;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 12px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #C0392B;
}

QPushButton:pressed {
    background-color: #A93226;
}
"""

BUTTON_WARNING = """
QPushButton {
    background-color: #F39C12;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 12px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #E67E22;
}

QPushButton:pressed {
    background-color: #D68910;
}
"""