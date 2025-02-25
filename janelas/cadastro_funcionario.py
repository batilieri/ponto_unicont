import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
                             QComboBox, QDateEdit, QTextEdit, QPushButton, QGridLayout,
                             QVBoxLayout, QHBoxLayout, QFrame, QGroupBox, QMessageBox,
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon, QFont, QPixmap, QColor


class CadastroFuncionario(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Funcionários | Incluir - Editar")
        self.setGeometry(100, 100, 650, 580)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                border: 1px solid #dcdcdc;
                border-radius: 8px;
                margin-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #444;
                font-weight: bold;
            }
            QLabel {
                color: #444;
            }
            QLineEdit, QComboBox, QDateEdit, QTextEdit {
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                padding: 6px;
                background-color: #fafafa;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
                border: 1px solid #0078d7;
                background-color: white;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0063b1;
            }
            QPushButton:pressed {
                background-color: #004e8c;
            }
            QPushButton#secondary {
                background-color: #f0f0f0;
                color: #444;
                border: 1px solid #dcdcdc;
            }
            QPushButton#secondary:hover {
                background-color: #e5e5e5;
            }
            QPushButton#secondary:pressed {
                background-color: #d9d9d9;
            }
        """)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(5)

        # Title with icon
        title_layout = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap("employee_icon.png").scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio))
        title_label = QLabel("Funcionários")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #0078d7;")
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)

        # Content layout
        content_layout = QGridLayout()
        content_layout.setSpacing(5)

        # Identification data section
        id_group = QGroupBox("Dados de Identificação")
        id_layout = QGridLayout(id_group)
        id_layout.setContentsMargins(15, 20, 15, 15)
        id_layout.setSpacing(10)

        id_layout.addWidget(QLabel("Nº Folha:"), 0, 0)
        id_layout.addWidget(QLineEdit(), 0, 1)

        id_layout.addWidget(QLabel("Nome:"), 1, 0)
        name_field = QLineEdit()
        id_layout.addWidget(name_field, 1, 1, 1, 3)

        # Add shadow effect to group box
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        id_group.setGraphicsEffect(shadow)

        # Generic data section
        generic_group = QGroupBox("Dados Genéricos")
        generic_layout = QGridLayout(generic_group)
        generic_layout.setContentsMargins(15, 20, 15, 15)
        generic_layout.setSpacing(5)

        generic_layout.addWidget(QLabel("CPF:"), 0, 0)
        cpf_field = QLineEdit()
        cpf_field.setStyleSheet("color: #0078d7; font-weight: bold;")
        generic_layout.addWidget(cpf_field, 0, 1)

        generic_layout.addWidget(QLabel("Nº Identificador:"), 1, 0)
        generic_layout.addWidget(QLineEdit(), 1, 1)

        generic_layout.addWidget(QLabel("Senha:"), 1, 2)
        password_field = QLineEdit()
        password_field.setEchoMode(QLineEdit.EchoMode.Password)
        generic_layout.addWidget(password_field, 1, 3)

        generic_layout.addWidget(QLabel("Nº PIS/PASEP:"), 2, 0)
        pis_field = QLineEdit()
        pis_field.setStyleSheet("color: #0078d7; font-weight: bold;")
        generic_layout.addWidget(pis_field, 2, 1)

        pis_link = QLabel('<a href="#" style="color: #0078d7; text-decoration: none;">Superior Nº PIS/PASEP</a>')
        pis_link.setOpenExternalLinks(True)
        generic_layout.addWidget(pis_link, 2, 2)

        generic_layout.addWidget(QLabel("Empresa:"), 3, 0)
        company_combo = QComboBox()
        company_combo.setStyleSheet("color: #0078d7; font-weight: bold;")
        generic_layout.addWidget(company_combo, 3, 1)

        generic_layout.addWidget(QLabel("Estrutura:"), 4, 0)
        structure_combo = QComboBox()
        structure_combo.addItem("1 - Escala Normal")
        generic_layout.addWidget(structure_combo, 4, 1)

        generic_layout.addWidget(QLabel("Horário:"), 5, 0)
        generic_layout.addWidget(QComboBox(), 5, 1)

        generic_layout.addWidget(QLabel("Função:"), 6, 0)
        function_combo = QComboBox()
        function_combo.addItem("Suporte Sistemas")
        generic_layout.addWidget(function_combo, 6, 1)

        generic_layout.addWidget(QLabel("Departamento:"), 7, 0)
        dept_combo = QComboBox()
        dept_combo.addItem("SCI")
        generic_layout.addWidget(dept_combo, 7, 1)

        generic_layout.addWidget(QLabel("Admissão:"), 8, 0)
        admission_date = QDateEdit()
        admission_date.setDate(QDate(2019, 10, 24))
        admission_date.setCalendarPopup(True)
        generic_layout.addWidget(admission_date, 8, 1)

        generic_layout.addWidget(QLabel("Demissão:"), 9, 0)
        dismissal_date = QDateEdit()
        dismissal_date.setCalendarPopup(True)
        generic_layout.addWidget(dismissal_date, 9, 1)

        generic_layout.addWidget(QLabel("Motivo de Demissão:"), 10, 0)
        generic_layout.addWidget(QComboBox(), 10, 1)

        # Add shadow effect to group box
        shadow3 = QGraphicsDropShadowEffect()
        shadow3.setBlurRadius(10)
        shadow3.setColor(QColor(0, 0, 0, 30))
        shadow3.setOffset(0, 2)
        generic_group.setGraphicsEffect(shadow3)


        # # Note about blue fields
        # note_frame = QFrame()
        # note_frame.setFrameShape(QFrame.Shape.NoFrame)
        # note_frame.setStyleSheet("background-color: #e8f5ff; border-radius: 6px; padding: 8px;")
        # note_layout = QHBoxLayout(note_frame)

        # note_icon = QLabel("ℹ️")
        # note_icon.setFont(QFont("Segoe UI", 10))
        # note_layout.addWidget(note_icon)
        #
        # note_text = QLabel(
        #     "Os campos em azul são utilizados para relatórios, arquivos e comprovantes exigidos pelas portarias do MTE.")
        # note_text.setWordWrap(True)
        # note_text.setStyleSheet("color: #0078d7;")
        # note_layout.addWidget(note_text)

        # Add shadow effect to note frame
        shadow6 = QGraphicsDropShadowEffect()
        shadow6.setBlurRadius(10)
        shadow6.setColor(QColor(0, 0, 0, 30))
        shadow6.setOffset(0, 2)
        # note_frame.setGraphicsEffect(shadow6)

        # Last update info
        update_frame = QFrame()
        update_frame.setFrameShape(QFrame.Shape.NoFrame)
        update_layout = QVBoxLayout(update_frame)
        update_layout.setContentsMargins(0, 0, 0, 0)

        last_update = QLabel("Última alteração")
        last_update.setFont(QFont("Segoe UI", 8))
        update_layout.addWidget(last_update)

        admin_update = QLabel("Administrador - 24/02/2025")
        admin_update.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        update_layout.addWidget(admin_update)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(update_frame)
        buttons_layout.addStretch()
        save_btn = QPushButton("Concluir")
        save_btn.setIcon(QIcon.fromTheme("dialog-ok-apply"))
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setObjectName("secondary")
        cancel_btn.setIcon(QIcon.fromTheme("dialog-cancel"))
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)

        # Add all sections to the grid layout
        content_layout.addWidget(id_group, 0, 0, 1, 4)
        content_layout.addWidget(generic_group, 1, 0, 1, 4)
        # content_layout.addWidget(note_frame, 3, 0, 1, 4)

        main_layout.addLayout(content_layout)
        main_layout.addLayout(buttons_layout)

        # Connect buttons
        save_btn.clicked.connect(self.save_employee)
        cancel_btn.clicked.connect(self.close)

    def save_employee(self):
        QMessageBox.information(self, "Informação", "Dados salvos com sucesso!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CadastroFuncionario()
    window.show()
    sys.exit(app.exec())