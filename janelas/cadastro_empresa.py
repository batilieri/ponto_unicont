import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
                             QComboBox, QDateEdit, QTextEdit, QPushButton, QGridLayout,
                             QVBoxLayout, QHBoxLayout, QFrame, QGroupBox, QMessageBox,
                             QGraphicsDropShadowEffect, QDialog)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon, QFont, QPixmap, QColor


# Janela de cadastro (formulário da Empresa)
class CompanyForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Empresa | Incluir - Editar")
        self.setGeometry(100, 100, 650, 580)
        # Estilos (CSS)
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

        # Cria o widget central e o layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(5)

        # Layout do título (com ícone e texto)
        title_layout = QHBoxLayout()
        icon_label = QLabel()
        # Substitua "company_icon.png" pelo caminho do ícone desejado
        icon_label.setPixmap(QPixmap("company_icon.png").scaled(28, 28, Qt.AspectRatioMode.KeepAspectRatio))
        title_label = QLabel("Empresa")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #0078d7;")
        title_layout.addWidget(icon_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)

        # Grid layout para organizar os group boxes
        content_layout = QGridLayout()
        content_layout.setSpacing(5)

        # 1º GroupBox: Dados de Identificação
        gb_identificacao = QGroupBox("Dados de Identificação")
        id_layout = QGridLayout(gb_identificacao)
        id_layout.setContentsMargins(15, 20, 15, 15)
        id_layout.setSpacing(5)

        id_layout.addWidget(QLabel("Razão Social:"), 0, 0)
        self.razao_social_field = QLineEdit()
        id_layout.addWidget(self.razao_social_field, 0, 1, 1, 3)

        id_layout.addWidget(QLabel("Nome Fantasia:"), 1, 0)
        self.nome_fantasia_field = QLineEdit()
        id_layout.addWidget(self.nome_fantasia_field, 1, 1, 1, 3)

        id_layout.addWidget(QLabel("CNPJ:"), 2, 0)
        self.cnpj_field = QLineEdit()
        id_layout.addWidget(self.cnpj_field, 2, 1)

        id_layout.addWidget(QLabel("Inscrição Estadual:"), 3, 0)
        self.ie_field = QLineEdit()
        id_layout.addWidget(self.ie_field, 3, 1)

        id_layout.addWidget(QLabel("Data de Fundação:"), 4, 0)
        self.fundacao_date = QDateEdit()
        self.fundacao_date.setDate(QDate(2020, 1, 1))
        self.fundacao_date.setCalendarPopup(True)
        id_layout.addWidget(self.fundacao_date, 4, 1)

        # Adiciona sombra no group box
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        gb_identificacao.setGraphicsEffect(shadow)

        # 2º GroupBox: Endereço e Contato
        gb_endereco = QGroupBox("Endereço e Contato")
        end_layout = QGridLayout(gb_endereco)
        end_layout.setContentsMargins(15, 20, 15, 15)
        end_layout.setSpacing(5)

        end_layout.addWidget(QLabel("Endereço:"), 0, 0)
        self.endereco_field = QLineEdit()
        end_layout.addWidget(self.endereco_field, 0, 1, 1, 3)

        end_layout.addWidget(QLabel("Bairro:"), 1, 0)
        self.bairro_field = QLineEdit()
        end_layout.addWidget(self.bairro_field, 1, 1)

        end_layout.addWidget(QLabel("CEP:"), 1, 2)
        self.cep_field = QLineEdit()
        end_layout.addWidget(self.cep_field, 1, 3)

        end_layout.addWidget(QLabel("Cidade:"), 2, 0)
        self.cidade_field = QLineEdit()
        end_layout.addWidget(self.cidade_field, 2, 1)

        end_layout.addWidget(QLabel("Estado:"), 2, 2)
        self.estado_field = QComboBox()
        self.estado_field.addItems(["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA",
                                    "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN",
                                    "RO", "RR", "RS", "SC", "SE", "SP", "TO"])
        end_layout.addWidget(self.estado_field, 2, 3)

        end_layout.addWidget(QLabel("Telefone:"), 3, 0)
        self.telefone_field = QLineEdit()
        end_layout.addWidget(self.telefone_field, 3, 1)

        end_layout.addWidget(QLabel("E-mail:"), 4, 0)
        self.email_field = QLineEdit()
        end_layout.addWidget(self.email_field, 4, 1, 1, 3)

        # Adiciona sombra ao group box
        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(10)
        shadow2.setColor(QColor(0, 0, 0, 30))
        shadow2.setOffset(0, 2)
        gb_endereco.setGraphicsEffect(shadow2)

        # Frame para última atualização (opcional)
        update_frame = QFrame()
        update_layout = QVBoxLayout(update_frame)
        update_layout.setContentsMargins(0, 0, 0, 0)

        last_update = QLabel("Última alteração")
        last_update.setFont(QFont("Segoe UI", 8))
        update_layout.addWidget(last_update)

        admin_update = QLabel("Administrador - 24/02/2025")
        admin_update.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        update_layout.addWidget(admin_update)

        # Botões
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

        # Adiciona os group boxes no layout de conteúdo
        content_layout.addWidget(gb_identificacao, 0, 0, 1, 4)
        content_layout.addWidget(gb_endereco, 1, 0, 1, 4)

        main_layout.addLayout(content_layout)
        main_layout.addLayout(buttons_layout)

        # Conecta os botões
        save_btn.clicked.connect(self.save_company)
        cancel_btn.clicked.connect(self.close)

    def save_company(self):
        # Lógica para salvar os dados (pode ser expandida)
        QMessageBox.information(self, "Informação", "Dados da empresa salvos com sucesso!")


# Janela principal com um botão para abrir o formulário de cadastro
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Janela Principal")
        self.setGeometry(100, 100, 400, 300)

        # Cria um botão centralizado
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addStretch()
        self.open_button = QPushButton("Abrir Cadastro")
        self.open_button.setFixedSize(150, 40)
        self.open_button.clicked.connect(self.abrir_cadastro)
        layout.addWidget(self.open_button, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        self.setCentralWidget(central_widget)

        # Variável para manter a referência à janela de cadastro
        self.cadastro_window = None

    def abrir_cadastro(self):
        self.cadastro_window = CompanyForm()
        self.cadastro_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
