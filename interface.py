import csv
import os
import re
import sys
from collections import defaultdict
from datetime import datetime

from PyQt6.QtCore import Qt, QDate, QSize, QRectF
from PyQt6.QtGui import QColor, QAction, QShortcut, QKeySequence, QPainter, QFont, QPageLayout, QFontMetrics
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QFormLayout,
                             QDateEdit, QComboBox, QTableWidget, QTableWidgetItem, QFileDialog,
                             QGroupBox, QStackedWidget,
                             QCheckBox, QSpinBox, QMessageBox, QRadioButton, QToolBar, QGridLayout, QDialog,
                             QInputDialog, QHeaderView, QTextEdit, QDialogButtonBox)
from banco.bancoSQlite import BancoSQLite, logger

from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
import re


class TimesheetTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.editing_item = None
        self.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked | QTableWidget.EditTrigger.SelectedClicked)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            current_item = self.currentItem()
            current_row = self.currentRow()
            current_col = self.currentColumn()

            if current_item and self.isPersistentEditorOpen(current_item):
                # Pegue o editor atual para obter o valor real que está sendo editado
                editor = self.cellWidget(current_row, current_col)
                if editor:
                    try:
                        # Tente pegar o texto diretamente do editor
                        new_value = editor.text().strip()
                        print(f"Valor do editor: {new_value}")
                    except:
                        # Se não conseguir, use o texto do item
                        new_value = current_item.text().strip()
                else:
                    new_value = current_item.text().strip()

                print(f"Valor antes de fechar editor: {new_value}")
                self.closePersistentEditor(current_item)

                # Armazene informações para processamento posterior
                self.editing_item = {
                    'item': current_item,
                    'row': current_row,
                    'col': current_col,
                    'value': new_value
                }

                # Vamos garantir que o valor seja mantido após fechar o editor
                current_item.setText(new_value)

                # Use um timer para processar após todas as atualizações da UI
                QTimer.singleShot(50, self.process_edited_item)
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def process_edited_item(self):
        if not self.editing_item:
            return

        item = self.editing_item['item']
        row = self.editing_item['row']
        col = self.editing_item['col']
        valor_novo = self.editing_item['value']

        # Imprime novamente para verificar se o valor ainda é o mesmo
        print(f"Processando item editado: {valor_novo}")

        try:
            def get_text_or_default(row, col, default=""):
                cell = self.item(row, col)
                return cell.text().strip() if cell else default

            cpf = get_text_or_default(row, 0)
            data = get_text_or_default(row, 2)

            print(f"Salvando valor: {valor_novo} para CPF: {cpf}, Data: {data}, Coluna: {col}")

            if not cpf or not data or not valor_novo:
                self.editing_item = None
                return

            # Mapear colunas para os campos do banco
            campos = {
                3: "entrada",
                4: "saida_almoco",
                5: "retorno_almoco",
                6: "saida"
            }

            if col in campos:
                campo = campos[col]

                # Validação do horário digitado
                if not re.match(r'^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$', valor_novo):
                    QMessageBox.warning(self, "Formato Inválido", "O horário deve estar no formato HH:MM:SS.")
                    self.editing_item = None
                    return

                # Converter data para formato SQL (YYYY-MM-DD)
                if '/' in data:
                    dia, mes, ano = data.split('/')
                    data_sql = f"{ano}-{mes}-{dia}"
                else:
                    data_sql = data

                # Modificar diretamente o item antes de salvar no banco
                item.setText(valor_novo)

                # Chamar função de salvamento no banco com o valor correto
                sucesso = self.parent_window.salvar_alteracao_ponto(cpf, data_sql, campo, valor_novo)

                if sucesso:
                    item.setBackground(QColor("#ccffcc"))  # Verde para sucesso
                else:
                    QMessageBox.critical(self, "Erro", "Falha ao salvar no banco.")

        except Exception as e:
            print(f"Erro ao salvar: {e}")
            logger.error("Erro", e)

        finally:
            self.editing_item = None


class MainWindow(QMainWindow, BancoSQLite):
    def __init__(self):
        super().__init__()

        # Configurações da janela principal
        self.sample_companies = None
        self.city_emp = None
        self.address_emp = None
        self.cnpj = None
        self.estado_emp = None
        self.phone_emp = None
        self.email = None
        self.name_emp = None
        self.employees_table = None
        self.companies_table = None
        self.setWindowTitle("HRUniconte - Sistema de Gestão de RH")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QPushButton {
                background-color: #4361ee;
                color: white;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a56d4;
            }
            QPushButton:pressed {
                background-color: #2a46c4;
            }
            QPushButton.danger {
                background-color: #f72585;
            }
            QPushButton.danger:hover {
                background-color: #e01e79;
            }
            QPushButton.secondary {
                background-color: #6c757d;
            }
            QPushButton.secondary:hover {
                background-color: #5a6268;
            }
            QLineEdit, QDateEdit, QComboBox, QSpinBox {
                border: 1px solid #ced4da;
                border-radius: 1px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus, QDateEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 1px solid #4361ee;
            }
            QTableWidget {
                border: none;
                gridline-color: #e9ecef;
                selection-background-color: #4361ee;
                selection-color: white;
            }
            QHeaderView::section {
                background-color: #343a40;
                color: white;
                padding: 8px;
                border: none;
            }
            QTabWidget::pane {
                border: none;
                background-color: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                color: #6c757d;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                color: #4361ee;
                font-weight: bold;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
                color: #4361ee;
            }
        """)

        # Criar barra de ferramentas
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(20, 20))
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #343a40;
                spacing: 10px;
                padding: 5px;
            }
            QToolButton {
                color: white;
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QToolButton:hover {
                background-color: #4361ee;
            }
        """)

        # Adicionar ações à barra de ferramentas
        actions = [
            ("Início", self.show_home),
            ("Empresas", self.show_companies),
            ("Funcionários", self.show_employees),
            ("Ponto", self.show_timesheet),
            ("Relatórios", self.show_reports),
            ("Configurações", self.show_settings)
        ]

        for name, function in actions:
            action = QAction(name, self)
            action.triggered.connect(function)
            self.toolbar.addAction(action)

        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        # Widget central com stack
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Stack widget para gerenciar as diferentes telas
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        # Inicializa as telas
        self.init_home_screen()
        self.init_companies_screen()
        self.init_employees_screen()
        self.init_timesheet_screen()
        self.init_reports_screen()
        self.init_settings_screen()

        # Exibe a tela inicial
        self.show_home()

    def init_home_screen(self):
        home_widget = QWidget()
        layout = QVBoxLayout(home_widget)

        # Título e boas-vindas
        title = QLabel("Bem-vindo ao HRUnicont")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #343a40; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Sistema de Gestão de Recursos Humanos")
        subtitle.setStyleSheet("font-size: 16px; color: #6c757d; margin-bottom: 40px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Cards de acesso rápido
        cards_layout = QHBoxLayout()

        quick_access_cards = [
            ("Cadastrar Empresa", "Adicione uma nova empresa ao sistema", self.show_companies),
            ("Cadastrar Funcionário", "Adicione um novo funcionário ao sistema", self.show_employees),
            ("Importar Ponto", "Importe dados de ponto dos funcionários", self.show_timesheet),
            ("Gerar Relatórios", "Visualize e exporte relatórios", self.show_reports)
        ]

        for title, desc, function in quick_access_cards:
            card = QGroupBox()
            card_layout = QVBoxLayout(card)

            title_label = QLabel(title)
            title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #343a40;")

            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: #6c757d;")
            desc_label.setWordWrap(True)

            button = QPushButton("Acessar")
            button.clicked.connect(function)

            card_layout.addWidget(title_label)
            card_layout.addWidget(desc_label)
            card_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignRight)

            card.setStyleSheet("""
                QGroupBox {
                    background-color: white;
                    border-radius: 8px;
                    padding: 15px;
                }
                QGroupBox:hover {
                    background-color: #f8f9fa;
                }
            """)

            cards_layout.addWidget(card)

        layout.addLayout(cards_layout)
        layout.addStretch()

        # Rodapé
        footer = QLabel("© 2025 Batiliere - Todos os direitos reservados")
        footer.setStyleSheet("color: #6c757d; margin-top: 20px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

        self.stack.addWidget(home_widget)

    def load_companies_data(self):
        """
        Recupera os registros do banco de dados e preenche a tabela.
        """
        companies = self.consultar_registros("cadastro_empresa")
        self.companies_table.setRowCount(len(companies))

        for row, company in enumerate(companies):
            # Supondo que a consulta retorne:
            # (id, nome, cnpj, endereco, cidade, estado, telefone, email, data_cadastro, alteracao)
            id, nome, cnpj, endereco, cidade, estado, telefone, email, data_cadastro, alteracao = company

            self.companies_table.setItem(row, 0, QTableWidgetItem(str(id)))
            self.companies_table.setItem(row, 1, QTableWidgetItem(nome))
            self.companies_table.setItem(row, 2, QTableWidgetItem(cnpj))
            self.companies_table.setItem(row, 3, QTableWidgetItem(endereco))
            self.companies_table.setItem(row, 4, QTableWidgetItem(cidade))
            self.companies_table.setItem(row, 5, QTableWidgetItem(estado))
            self.companies_table.setItem(row, 6, QTableWidgetItem(telefone))
            self.companies_table.setItem(row, 7, QTableWidgetItem(email))

            # Cria a célula de ações
            actions_cell = QWidget()
            actions_layout = QHBoxLayout(actions_cell)
            actions_layout.setContentsMargins(5, 0, 5, 0)

            edit_btn = QPushButton("Editar")
            edit_btn.setFixedWidth(60)
            edit_btn.setStyleSheet("padding: 4px;")
            # Conecta o botão de editar passando o id do registro
            edit_btn.clicked.connect(lambda _, ind=id: self.edit_company(ind))

            delete_btn = QPushButton("Excluir")
            delete_btn.setFixedWidth(60)
            delete_btn.setStyleSheet("padding: 4px; background-color: #f72585; color: white;")
            # Conecta o botão de excluir passando o id do registro
            delete_btn.clicked.connect(lambda _, ind=id: self.delete_company(ind))

            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            actions_cell.setLayout(actions_layout)

            self.companies_table.setCellWidget(row, 8, actions_cell)

    # Estes métodos devem ser definidos fora de load_companies_data, como métodos da classe
    def edit_company(self, company_id):
        try:
            """
            Método para editar uma empresa.
            Aqui você pode:
              - Recuperar os dados atuais do registro do banco de dados.
              - Preencher um formulário de edição com os dados recuperados.
              - Exibir o formulário para o usuário modificar os dados.
              - Após salvar, atualizar o registro no banco e recarregar a tabela.
            """
            print(f"Editar empresa com ID: {company_id}")

            dados = self.consultar_registros("cadastro_empresa", filtros={"id": int(company_id)})
            print(dados)
            self.show_edit_company_form(dados)
        except Exception as e:
            print(f"Erro ao Editar empresa: {e}")
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao Editar o Registro: {e}")

    def delete_company(self, company_id):
        from PyQt6.QtWidgets import QMessageBox  # Se estiver usando PyQt6

        try:
            confirm = QMessageBox.question(
                self,
                "Confirmar Exclusão",
                f"Tem certeza que deseja excluir a empresa {company_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                print(f"Excluindo empresa com ID: {company_id}")
                self.excluir_registro("cadastro_empresa", company_id)
                self.load_companies_data()
        except Exception as e:
            print(f"Erro ao excluir empresa: {e}")
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao excluir: {e}")

    def show_edit_company_form(self, dados):
        try:
            """
            Exibe o formulário de edição preenchido com os dados do registro selecionado.
    
            Args:
                dados (List[tuple]): Lista com os dados retornados da consulta.
                    Exemplo:
                    [(id, nome, cnpj, endereco, cidade, estado, telefone, email, data_cadastro, alteracao)]
            """
            if not dados:
                logger.error("Nenhum dado encontrado para edição.")
                return

            # Desempacota o primeiro registro da lista
            registro = dados[0]
            company_id, nome, cnpj, endereco, cidade, estado, telefone, email, data_cadastro, alteracao = registro

            # Cria um diálogo para edição
            dialog = QWidget(self, Qt.WindowType.Dialog)
            dialog.setWindowTitle("Editar Empresa")
            dialog.setMinimumWidth(400)
            dialog.setStyleSheet("background-color: white; border-radius: 8px;")

            layout = QVBoxLayout(dialog)

            title = QLabel("Editar Empresa")
            title.setStyleSheet("font-size: 18px; font-weight: bold; color: #343a40; margin-bottom: 20px;")
            layout.addWidget(title)

            form = QFormLayout()

            # Cria e preenche os campos do formulário de edição
            name_emp = QLineEdit()
            name_emp.setPlaceholderText("Nome da empresa")
            name_emp.setText(nome)
            form.addRow("Nome:", name_emp)

            cnpj_emp = QLineEdit()
            cnpj_emp.setPlaceholderText("00.000.000/0000-00")
            cnpj_emp.setText(cnpj)
            form.addRow("CNPJ:", cnpj_emp)

            address_emp = QLineEdit()
            address_emp.setPlaceholderText("Endereço completo")
            address_emp.setText(endereco)
            form.addRow("Endereço:", address_emp)

            city_emp = QLineEdit()
            city_emp.setPlaceholderText("Cidade")
            city_emp.setText(cidade)
            form.addRow("Cidade:", city_emp)

            estado_emp = QComboBox()
            estados = ["Selecione", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
                       "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ",
                       "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
            estado_emp.addItems(estados)
            index = estado_emp.findText(estado)
            if index >= 0:
                estado_emp.setCurrentIndex(index)
            else:
                estado_emp.setCurrentIndex(0)
            form.addRow("Estado:", estado_emp)

            phone_emp = QLineEdit()
            phone_emp.setPlaceholderText("(00) 0000-0000")
            phone_emp.setText(telefone)
            form.addRow("Telefone:", phone_emp)

            email_emp = QLineEdit()
            email_emp.setPlaceholderText("email@empresa.com")
            email_emp.setText(email)
            form.addRow("Email:", email_emp)

            layout.addLayout(form)

            buttons = QHBoxLayout()

            def update_and_close():
                # Aqui você deve implementar a lógica de atualização
                # Exemplo: chamando um método que atualiza o registro no banco de dados
                novos_dados = {
                    "nome": name_emp.text(),
                    "cnpj": cnpj_emp.text(),
                    "endereco": address_emp.text(),
                    "cidade": city_emp.text(),
                    "estado": estado_emp.currentText(),
                    "telefone": phone_emp.text(),
                    "email": email_emp.text()
                }
                self.atualizar_registro("cadastro_empresa", company_id, novos_dados)
                self.load_companies_data()
                dialog.close()

            save = QPushButton("Salvar")
            save.setStyleSheet("background-color: #28a745; color: white; padding: 6px; border-radius: 4px;")
            save.clicked.connect(update_and_close)

            cancel = QPushButton("Cancelar")
            cancel.setStyleSheet("background-color: #dc3545; color: white; padding: 6px; border-radius: 4px;")
            cancel.clicked.connect(dialog.close)

            buttons.addWidget(save)
            buttons.addWidget(cancel)

            layout.addLayout(buttons)
            dialog.setLayout(layout)
            dialog.show()
        except Exception as e:
            logger.error("Erro", e)

    def init_companies_screen(self):
        try:
            companies_widget = QWidget()
            layout = QVBoxLayout(companies_widget)

            # Título
            title = QLabel("Gestão de Empresas")
            title.setStyleSheet("font-size: 20px; font-weight: bold; color: #343a40; margin-bottom: 20px;")
            layout.addWidget(title)

            # Botões de ação
            actions_layout = QHBoxLayout()
            add_btn = QPushButton("Nova Empresa")
            add_btn.clicked.connect(self.show_add_company_form)
            export_btn = QPushButton("Exportar")
            export_btn.setStyleSheet("background-color: #6c757d;")
            export_btn.clicked.connect(self.export_companies)
            actions_layout.addWidget(add_btn)
            actions_layout.addWidget(export_btn)
            actions_layout.addStretch()
            layout.addLayout(actions_layout)

            # Tabela de empresas
            self.companies_table = QTableWidget()
            self.companies_table.setColumnCount(9)
            # Definindo larguras específicas para cada coluna:
            self.companies_table.setColumnWidth(0, 80)  # Coluna "ID"
            self.companies_table.setColumnWidth(1, 250)  # Coluna "Nome"
            self.companies_table.setColumnWidth(2, 110)  # Coluna "CNPJ"
            self.companies_table.setColumnWidth(3, 130)  # Coluna "Endereço"
            self.companies_table.setColumnWidth(4, 100)  # Coluna "Cidade"
            self.companies_table.setColumnWidth(5, 60)  # Coluna "Estado"
            self.companies_table.setColumnWidth(6, 120)  # Coluna "Telefone"
            self.companies_table.setColumnWidth(7, 150)  # Coluna "E-mail"
            self.companies_table.setColumnWidth(8, 100)  # Coluna "Ações"
            self.companies_table.setHorizontalHeaderLabels([
                "Código", "Nome", "CNPJ", "Endereço", "Cidade",
                "Estado", "Telefone", "E-mail", "Ações"
            ])
            self.companies_table.horizontalHeader().setStretchLastSection(True)
            self.companies_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.companies_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

            layout.addWidget(self.companies_table)
            self.stack.addWidget(companies_widget)

            # Carrega os dados do banco
            self.load_companies_data()
        except Exception as e:
            logger.error("Erro", e)

    def show_add_company_form(self):
        try:
            dialog = QDialog(self)  # Definir a janela principal como pai
            dialog.setWindowTitle("Adicionar Nova Empresa")
            dialog.setMinimumSize(400, 400)  # Ajuste o tamanho conforme necessário
            dialog.setStyleSheet("background-color: white; border-radius: 8px;")

            layout = QVBoxLayout(dialog)

            title = QLabel("Cadastro de Empresa")
            title.setStyleSheet("font-size: 18px; font-weight: bold; color: #343a40; margin-bottom: 20px;")
            layout.addWidget(title)

            form = QFormLayout()

            self.name_emp = QLineEdit()
            self.name_emp.setPlaceholderText("Nome da empresa")
            form.addRow("Nome:", self.name_emp)

            self.cnpj = QLineEdit()
            self.cnpj.setPlaceholderText("00.000.000/0000-00")
            form.addRow("CNPJ:", self.cnpj)

            self.address_emp = QLineEdit()
            self.address_emp.setPlaceholderText("Endereço completo")
            form.addRow("Endereço:", self.address_emp)

            self.city_emp = QLineEdit()
            self.city_emp.setPlaceholderText("Cidade")
            form.addRow("Cidade:", self.city_emp)

            self.estado_emp = QComboBox()
            self.estado_emp.addItems(
                ["Selecione", "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB",
                 "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"])
            form.addRow("Estado:", self.estado_emp)

            self.phone_emp = QLineEdit()
            self.phone_emp.setPlaceholderText("(00) 0000-0000")
            form.addRow("Telefone:", self.phone_emp)

            self.email = QLineEdit()
            self.email.setPlaceholderText("email@empresa.com")
            form.addRow("Email:", self.email)

            layout.addLayout(form)

            buttons = QHBoxLayout()

            def save_and_close():
                self.save_data()
                dialog.accept()

            save = QPushButton("Salvar")
            save.setStyleSheet("background-color: #28a745; color: white; padding: 6px; border-radius: 4px;")
            save.clicked.connect(save_and_close)

            cancel = QPushButton("Cancelar")
            cancel.setStyleSheet("background-color: #dc3545; color: white; padding: 6px; border-radius: 4px;")
            cancel.clicked.connect(dialog.reject)

            buttons.addWidget(save)
            buttons.addWidget(cancel)

            layout.addLayout(buttons)
            dialog.setLayout(layout)

            # Obtém a posição da janela principal
            parent_rect = self.frameGeometry()
            # Obtém o tamanho do diálogo
            dialog_rect = dialog.frameGeometry()
            # Move o centro do diálogo para o centro da janela principal
            dialog_rect.moveCenter(parent_rect.center())
            # Aplica a nova posição ao diálogo
            dialog.move(dialog_rect.topLeft())

            dialog.exec()  # Exibe o diálogo modal
        except Exception as e:
            logger.error("Erro", e)

    def save_data(self):
        try:
            colunas = ("nome", "cnpj", "endereco", "cidade", "estado", "telefone", "email")

            nome = self.name_emp.text()
            cnpj = self.cnpj.text()
            endereco = self.address_emp.text()
            cidade = self.city_emp.text()
            estado = self.estado_emp.currentText()
            telefone = self.phone_emp.text()
            email = self.email.text()

            # Cria a tabela, se necessário
            campos = {colunas[i]: "TEXT" for i in range(len(colunas))}
            self.criar_tabela("cadastro_empresa", campos)

            # Cria o dicionário de dados
            dados = {colunas[i]: valor or " " for i, valor in
                     enumerate([nome, cnpj, endereco, cidade, estado, telefone, email])}

            # Validação extra para evitar erro
            if not cnpj.strip():
                raise ValueError("O CNPJ não pode estar vazio.")

            # Insere ou atualiza os dados no banco de dados
            dados = self.inserir_ou_atualizar_registro("cadastro_empresa", dados, cnpj)
            print("Cadastro da empresa:", dados)
            # Atualiza os dados da tabela sem recriar toda a tela
            self.load_companies_data()
            self.init_employees_screen()
            self.load_employees_data()


        except Exception as e:
            logger.error("Erro", e)

    # ---------------------------------------------------------------------------------------------
    # Cadastro de Colaborador

    def init_employees_screen(self):
        try:
            employees_widget = QWidget()
            layout = QVBoxLayout(employees_widget)

            # Título
            title = QLabel("Gestão de Funcionários")
            title.setStyleSheet("font-size: 20px; font-weight: bold; color: #343a40; margin-bottom: 20px;")
            layout.addWidget(title)

            # Botões de ação
            actions_layout = QHBoxLayout()

            add_btn = QPushButton("Novo Funcionário")
            add_btn.clicked.connect(self.show_add_employee_form)

            import_btn = QPushButton("Importar")
            import_btn.setStyleSheet("background-color: #4cc9f0;")
            import_btn.clicked.connect(self.import_employees)

            export_btn = QPushButton("Exportar")
            export_btn.setStyleSheet("background-color: #6c757d;")
            export_btn.clicked.connect(self.export_employees)

            actions_layout.addWidget(add_btn)
            actions_layout.addWidget(import_btn)
            actions_layout.addWidget(export_btn)
            actions_layout.addStretch()

            layout.addLayout(actions_layout)

            # Filtros
            filter_group = QGroupBox("Filtros")
            filter_layout = QHBoxLayout(filter_group)

            filter_layout.addWidget(QLabel("Empresa:"))
            company_filter = QComboBox()
            empresas = self.consultar_registros("cadastro_empresa")
            if empresas:
                for i in empresas:
                    codigo = i[0]
                    nome = i[1]
                    company_filter.addItem(f"{codigo} - {nome}")
            else:
                company_filter.addItem("Nenhuma empresa cadastrada")
            filter_layout.addWidget(company_filter)

            filter_layout.addWidget(QLabel("Departamento:"))
            dept_filter = QComboBox()
            dept_filter.addItems(["Todos", "TI", "RH", "Financeiro", "Marketing", "Operações"])
            filter_layout.addWidget(dept_filter)

            filter_layout.addWidget(QLabel("Status:"))
            status_filter = QComboBox()
            status_filter.addItems(["Todos", "Ativo", "Inativo", "Férias", "Afastado"])
            filter_layout.addWidget(status_filter)

            filter_btn = QPushButton("Filtrar")
            filter_layout.addWidget(filter_btn)

            layout.addWidget(filter_group)

            # Tabela de funcionários
            self.employees_table = QTableWidget()
            self.employees_table.setColumnCount(7)
            self.employees_table.setHorizontalHeaderLabels(
                ["Código", "Empresa", "N° Folha", "Nome", "CPF", "Status", "Ações"]
            )
            self.employees_table.horizontalHeader().setStretchLastSection(True)
            self.employees_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.employees_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

            # Carrega os dados reais do banco
            funcionarios = self.consultar_registros("cadastro_funcionario")
            if funcionarios:
                print(funcionarios)
                self.employees_table.setRowCount(len(funcionarios))
                for row, emp in enumerate(funcionarios):
                    # Considere que a tupla 'emp' possua a seguinte ordem:
                    # (n_folha, nome, CPF, data_admissao, estado_civil, telefone,
                    #  empresa, departamento, cargo, salario, jornada_trabalho,
                    #  status, pis_pasep, ctps, banco, contabancaria)
                    # ["Código", "Empresa", "N° Folha", "Nome", "CPF", "Status", "Ações"]
                    codigo_func = emp[0]
                    empresa_func = emp[7]
                    n_folha = emp[1]
                    nome_func = emp[2]
                    cpf = emp[3]
                    status = emp[12]

                    self.employees_table.setItem(row, 0, QTableWidgetItem(str(codigo_func)))
                    self.employees_table.setItem(row, 1, QTableWidgetItem(str(empresa_func)))
                    self.employees_table.setItem(row, 2, QTableWidgetItem(str(n_folha)))
                    self.employees_table.setItem(row, 3, QTableWidgetItem(nome_func))
                    self.employees_table.setItem(row, 4, QTableWidgetItem(cpf))
                    self.employees_table.setItem(row, 5, QTableWidgetItem(status))
                    self.employees_table.setColumnWidth(3, 350)  # Funcionário

                    # Status com cores personalizadas
                    status_item = QTableWidgetItem(status)
                    if status == "Ativo":
                        status_item.setForeground(QColor("#28a745"))  # verde para ativo
                    elif status == "Férias":
                        status_item.setForeground(QColor("#fd7e14"))  # laranja para férias
                    elif status == "Afastado":
                        status_item.setForeground(QColor("#dc3545"))  # vermelho para afastado
                    elif status == "Inativo":
                        status_item.setForeground(QColor("#6c757d"))  # cinza para inativo
                    else:
                        status_item.setForeground(QColor("black"))

                    # Insere o status colorido na coluna correta (índice 5)
                    self.employees_table.setItem(row, 5, status_item)

                    # Célula de ações: botões Editar e Excluir
                    actions_cell = QWidget()
                    actions_layout = QHBoxLayout(actions_cell)
                    actions_layout.setContentsMargins(5, 0, 5, 0)

                    # Cria botão de editar
                    edit_btn = QPushButton("Editar")
                    edit_btn.setFixedWidth(70)
                    edit_btn.setStyleSheet("padding: 4px;")
                    # Use uma função parcial para fixar o valor de n_folha
                    edit_btn.clicked.connect(lambda _, nf=cpf: self.show_edit_employee_form(nf))

                    delete_btn = QPushButton("Excluir")
                    delete_btn.setFixedWidth(70)
                    delete_btn.setStyleSheet("padding: 4px; background-color: #f72585;")
                    delete_btn.clicked.connect(lambda _, nf=codigo_func: self.excluir_funcionario(nf))

                    actions_layout.addWidget(edit_btn)
                    actions_layout.addWidget(delete_btn)
                    actions_layout.addStretch()
                    actions_cell.setLayout(actions_layout)

                    self.employees_table.setCellWidget(row, 6, actions_cell)

            else:
                # Se não houver funcionários cadastrados
                self.employees_table.setRowCount(0)

            layout.addWidget(self.employees_table)
            self.stack.addWidget(employees_widget)  # Gestão de F
        except Exception as e:
            logger.error("Erro", e)

    def load_employees_data(self):
        try:
            print("Carregando dados de funcionários...")
            # Consulta os registros reais do banco de dados
            funcionarios = self.consultar_registros("cadastro_funcionario")

            if funcionarios:
                print(f"Encontrados {len(funcionarios)} funcionários")
                self.employees_table.setRowCount(len(funcionarios))

                for row, emp in enumerate(funcionarios):
                    print(f"Processando funcionário {row + 1}: {emp}")

                    # Verifica o tamanho da tupla para evitar erros de índice
                    num_campos = len(emp)

                    # Ajuste os índices de acordo com a estrutura real do seu banco de dados
                    codigo_func = emp[0] if num_campos > 0 else ""
                    n_folha = emp[1] if num_campos > 1 else ""
                    nome_func = emp[2] if num_campos > 2 else ""
                    cpf = emp[3] if num_campos > 3 else ""
                    empresa_func = emp[7] if num_campos > 7 else ""
                    status = emp[12] if num_campos > 12 else "Ativo"

                    self.employees_table.setItem(row, 0, QTableWidgetItem(str(codigo_func)))
                    self.employees_table.setItem(row, 1, QTableWidgetItem(str(empresa_func)))
                    self.employees_table.setItem(row, 2, QTableWidgetItem(str(n_folha)))
                    self.employees_table.setItem(row, 3, QTableWidgetItem(nome_func))
                    self.employees_table.setItem(row, 4, QTableWidgetItem(cpf))

                    status_item = QTableWidgetItem(status)
                    if status == "Ativo":
                        status_item.setForeground(QColor("#28a745"))  # verde para ativo
                    elif status == "Férias":
                        status_item.setForeground(QColor("#fd7e14"))  # laranja para férias
                    elif status == "Afastado":
                        status_item.setForeground(QColor("#dc3545"))  # vermelho para afastado
                    elif status == "Inativo":
                        status_item.setForeground(QColor("#6c757d"))  # cinza para inativo
                    else:
                        status_item.setForeground(QColor("black"))
                    self.employees_table.setItem(row, 5, status_item)

                    # Célula de ações: botões Editar e Excluir
                    actions_cell = QWidget()
                    actions_layout = QHBoxLayout(actions_cell)
                    actions_layout.setContentsMargins(5, 0, 5, 0)

                    # IMPORTANTE: Criando uma referência fixa para o n_folha
                    current_n_folha = str(n_folha)
                    print(current_n_folha)
                    # Cria botão de editar
                    edit_btn = QPushButton("Editar")
                    edit_btn.setFixedWidth(70)
                    edit_btn.setStyleSheet("padding: 4px;")
                    # Use uma função parcial para fixar o valor de n_folha
                    edit_btn.clicked.connect(lambda _, nf=cpf: self.show_edit_employee_form(nf))

                    # Cria botão de excluir
                    delete_btn = QPushButton("Excluir")
                    delete_btn.setFixedWidth(70)
                    delete_btn.setStyleSheet("padding: 4px; background-color: #f72585; color: white;")
                    delete_btn.clicked.connect(lambda _, nf=codigo_func: self.excluir_funcionario(nf))

                    # Adiciona os botões ao layout
                    actions_layout.addWidget(edit_btn)
                    actions_layout.addWidget(delete_btn)
                    actions_layout.addStretch()

                    # Define o layout na célula
                    actions_cell.setLayout(actions_layout)

                    # Define a célula na tabela
                    self.employees_table.setCellWidget(row, 6, actions_cell)

                    print(f"Linha {row} adicionada com sucesso")

                print("Tabela de funcionários atualizada com sucesso!")
            else:
                # Se não houver funcionários cadastrados
                self.employees_table.setRowCount(0)
                print("Nenhum funcionário encontrado no banco de dados.")

        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Erro ao carregar dados de funcionários: {e}")
            print(f"Traceback: {traceback_str}")
            logger.error(f"Erro ao carregar dados de funcionários: {e}")
            logger.error(f"Traceback: {traceback_str}")
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao carregar os funcionários: {e}")

    def show_edit_employee_form(self, cpf):
        """
        Exibe o formulário de edição preenchido com os dados do funcionário selecionado,
        organizado em abas como no formulário de adição.

        Args:
            cpf: cpf do funcionario para ediçao
        """
        try:
            print(f"Iniciando edição do funcionário com N° Folha: {cpf}")

            # Consulta os dados do funcionário no banco
            dados = self.consultar_registros("cadastro_funcionario", filtros={"cpf": str(cpf)})
            print(f"Dados consultados: {dados}")

            if not dados or len(dados) == 0:
                print(f"Nenhum funcionário encontrado com cpf: {cpf}")
                QMessageBox.warning(self, "Aviso", "Funcionário não encontrado!")
                return

            # Desempacota o primeiro registro da lista
            registro = dados[0]
            print(f"Registro encontrado: {registro}")

            # Verifica o número de campos retornados para ajustar o desempacotamento
            num_campos = len(registro)
            print(f"Número de campos no registro: {num_campos}")

            # Extrai os campos com verificação de índice
            codigo = registro[0] if num_campos > 0 else 0
            n_folha = registro[1] if num_campos > 1 else ""
            nome = registro[2] if num_campos > 2 else ""
            cpf = registro[3] if num_campos > 3 else ""
            data_admissao = registro[4] if num_campos > 4 else ""
            estado_civil = registro[5] if num_campos > 5 else ""
            telefone = registro[6] if num_campos > 6 else ""
            empresa = registro[7] if num_campos > 7 else ""
            departamento = registro[8] if num_campos > 8 else ""
            cargo = registro[9] if num_campos > 9 else ""
            salario = registro[10] if num_campos > 10 else ""
            jornada_trabalho = registro[11] if num_campos > 11 else ""
            status = registro[12] if num_campos > 12 else "Ativo"
            pis_pasep = registro[13] if num_campos > 13 else ""
            ctps = registro[14] if num_campos > 14 else ""
            banco = registro[15] if num_campos > 15 else ""
            conta_bancaria = registro[16] if num_campos > 16 else ""
            email = registro[17] if num_campos > 17 else ""  # Adicione se existir no seu DB

            # Cria um diálogo para edição
            dialog = QDialog(self)
            dialog.setWindowTitle("Editar Funcionário")
            dialog.setMinimumWidth(500)
            dialog.setStyleSheet("background-color: white; border-radius: 8px;")

            layout = QVBoxLayout(dialog)

            title = QLabel("Editar Funcionário")
            title.setStyleSheet("font-size: 18px; font-weight: bold; color: #343a40; margin-bottom: 20px;")
            layout.addWidget(title)

            # Usar tabs para organizar o formulário
            tabs = QTabWidget()

            # ======================= Tab de Dados Pessoais =======================
            personal_tab = QWidget()
            personal_layout = QFormLayout(personal_tab)

            # Combo de empresas
            empresa_combo = QComboBox()
            try:
                empresas = self.consultar_registros("cadastro_empresa")
                print("cadastro empres:", empresas)
                if empresas:
                    for emp in empresas:
                        empresa_combo.addItem(f"{emp[0]} - {emp[1]}")
                    # Encontra a empresa atual para selecioná-la
                    empresa_str = str(empresa)
                    for i in range(empresa_combo.count()):
                        if empresa_str in empresa_combo.itemText(i).split(" - ")[0]:
                            empresa_combo.setCurrentIndex(i)
                            break
                else:
                    empresa_combo.addItem("Nenhuma empresa cadastrada")
            except Exception as e:
                logger.error("Erro", e)
                empresa_combo.addItem("Erro ao carregar empresas")
            personal_layout.addRow("Empresa:", empresa_combo)

            # Campo N° Folha (read-only)
            n_folha_field = QLineEdit()
            n_folha_field.setText(str(n_folha))
            n_folha_field.setReadOnly(True)  # O número de folha não deve ser alterado
            personal_layout.addRow("N° Folha:", n_folha_field)

            # Campo Nome
            nome_field = QLineEdit()
            nome_field.setText(nome)
            personal_layout.addRow("Nome:", nome_field)

            # Campo CPF
            cpf_field = QLineEdit()
            cpf_field.setText(cpf)
            personal_layout.addRow("CPF:", cpf_field)

            # Campo Data de Admissão
            data_admissao_field = QDateEdit()
            data_admissao_field.setCalendarPopup(True)
            # Converte a string de data para QDate
            if isinstance(data_admissao, str) and data_admissao:
                try:
                    # Tente diferentes formatos de data
                    if "-" in data_admissao:
                        data = QDate.fromString(data_admissao, "yyyy-MM-dd")
                    elif "/" in data_admissao:
                        data = QDate.fromString(data_admissao, "dd/MM/yyyy")
                    else:
                        data = QDate.currentDate()

                    if data.isValid():
                        data_admissao_field.setDate(data)
                    else:
                        data_admissao_field.setDate(QDate.currentDate())
                except:
                    data_admissao_field.setDate(QDate.currentDate())
            else:
                data_admissao_field.setDate(QDate.currentDate())
            personal_layout.addRow("Data de Admissão:", data_admissao_field)

            # Campo Estado Civil
            estado_civil_combo = QComboBox()
            estados_civis = ["Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)", "União Estável"]
            estado_civil_combo.addItems(estados_civis)
            index = estado_civil_combo.findText(estado_civil)
            if index >= 0:
                estado_civil_combo.setCurrentIndex(index)
            personal_layout.addRow("Estado Civil:", estado_civil_combo)

            # Campo Telefone
            telefone_field = QLineEdit()
            telefone_field.setText(telefone)
            personal_layout.addRow("Telefone:", telefone_field)

            # ======================= Tab de Dados Profissionais =======================
            professional_tab = QWidget()
            professional_layout = QFormLayout(professional_tab)

            # Campo Email (se existir)
            email_field = QLineEdit()
            email_field.setText(email if email else "")
            professional_layout.addRow("Email:", email_field)

            # Campo Departamento
            departamento_field = QLineEdit()
            departamento_field.setText(departamento)
            professional_layout.addRow("Departamento:", departamento_field)

            # Campo Cargo
            cargo_field = QLineEdit()
            cargo_field.setText(cargo)
            professional_layout.addRow("Cargo:", cargo_field)

            # Campo Salário
            salario_field = QLineEdit()
            salario_field.setText(str(salario))
            professional_layout.addRow("Salário:", salario_field)

            # Campo Jornada de Trabalho
            jornada_combo = QComboBox()
            jornadas = ["44h/semana", "40h/semana", "30h/semana", "20h/semana", "Outra"]
            jornada_combo.addItems(jornadas)
            index = -1
            for i, j in enumerate(jornadas):
                if j in str(jornada_trabalho):
                    index = i
                    break
            if index >= 0:
                jornada_combo.setCurrentIndex(index)
            else:
                jornada_combo.addItem(str(jornada_trabalho))
                jornada_combo.setCurrentIndex(jornada_combo.count() - 1)
            professional_layout.addRow("Jornada de Trabalho:", jornada_combo)

            # Campo Status
            status_combo = QComboBox()
            status_options = ["Ativo", "Inativo", "Férias", "Afastado"]
            status_combo.addItems(status_options)
            index = status_combo.findText(status)
            if index >= 0:
                status_combo.setCurrentIndex(index)
            professional_layout.addRow("Status:", status_combo)

            # ======================= Tab de Documentos =======================
            documents_tab = QWidget()
            documents_layout = QFormLayout(documents_tab)

            # Campo PIS/PASEP
            pis_field = QLineEdit()
            pis_field.setText(pis_pasep)
            documents_layout.addRow("PIS/PASEP:", pis_field)

            # Campo CTPS
            ctps_field = QLineEdit()
            ctps_field.setText(ctps)
            documents_layout.addRow("CTPS:", ctps_field)

            # Campo Banco
            banco_combo = QComboBox()
            bancos = ["Banco do Brasil", "Caixa Econômica", "Itaú", "Bradesco", "Santander", "Nubank", "Inter", "Outro"]
            banco_combo.addItems(bancos)
            index = banco_combo.findText(banco)
            if index >= 0:
                banco_combo.setCurrentIndex(index)
            else:
                banco_combo.addItem(str(banco))
                banco_combo.setCurrentIndex(banco_combo.count() - 1)
            documents_layout.addRow("Banco:", banco_combo)

            # Campo Conta Bancária
            conta_field = QLineEdit()
            conta_field.setText(conta_bancaria)
            documents_layout.addRow("Conta Bancária:", conta_field)

            # Adiciona as abas ao TabWidget
            tabs.addTab(personal_tab, "Dados Pessoais")
            tabs.addTab(professional_tab, "Dados Profissionais")
            tabs.addTab(documents_tab, "Documentos")

            layout.addWidget(tabs)

            # Botões de ação
            buttons_layout = QHBoxLayout()

            save_btn = QPushButton("Salvar")
            save_btn.setStyleSheet("background-color: #28a745; color: white; padding: 6px; border-radius: 4px;")

            cancel_btn = QPushButton("Cancelar")
            cancel_btn.setStyleSheet("background-color: #dc3545; color: white; padding: 6px; border-radius: 4px;")
            cancel_btn.clicked.connect(dialog.close)

            buttons_layout.addStretch()
            buttons_layout.addWidget(save_btn)
            buttons_layout.addWidget(cancel_btn)

            layout.addLayout(buttons_layout)

            # Função para salvar as alterações
            def update_employee():
                try:
                    # Pega o código da empresa da ComboBox (formato: "ID - Nome")
                    empresa_text = empresa_combo.currentText()
                    selected_empresa = empresa_text.split(" - ")[0] if " - " in empresa_text else empresa_text

                    # Converte a data para string no formato adequado
                    data_formatada = data_admissao_field.date().toString("yyyy-MM-dd")

                    # Prepara os novos dados
                    novos_dados = {
                        "nome": nome_field.text(),
                        "CPF": cpf_field.text(),
                        "data_admissao": data_formatada,
                        "estado_civil": estado_civil_combo.currentText(),
                        "telefone": telefone_field.text(),
                        "empresa": selected_empresa,
                        "departamento": departamento_field.text(),
                        "cargo": cargo_field.text(),
                        "salario": salario_field.text(),
                        "jornada_trabalho": jornada_combo.currentText(),
                        "status": status_combo.currentText(),
                        "pis_pasep": pis_field.text(),
                        "ctps": ctps_field.text(),
                        "banco": banco_combo.currentText(),
                        "contabancaria": conta_field.text(),
                        #  "email": email_field.text()  # Adicione se existir no seu DB
                    }

                    print(f"Atualizando funcionário {codigo} com dados: {novos_dados}")

                    # Atualiza o registro no banco de dados
                    self.atualizar_registro("cadastro_funcionario", codigo, novos_dados)

                    # Exibe mensagem de sucesso
                    QMessageBox.information(self, "Sucesso", "Funcionário atualizado com sucesso!")

                    # Recarrega os dados da tabela
                    self.load_employees_data()

                    # Fecha o diálogo
                    dialog.close()

                except Exception as e:
                    print(f"Erro ao atualizar funcionário: {e}")
                    if hasattr(self, 'logger'):
                        self.logger.error(f"Erro ao atualizar funcionário: {e}")
                    QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao atualizar: {e}")

            # Conecta o botão salvar à função de atualização
            save_btn.clicked.connect(update_employee)

            # Adiciona navegação entre campos (Tab order)
            # Aba Dados Pessoais
            QWidget.setTabOrder(n_folha_field, nome_field)
            QWidget.setTabOrder(nome_field, cpf_field)
            QWidget.setTabOrder(cpf_field, data_admissao_field)
            QWidget.setTabOrder(data_admissao_field, estado_civil_combo)
            QWidget.setTabOrder(estado_civil_combo, telefone_field)

            # Aba Dados Profissionais
            QWidget.setTabOrder(telefone_field, email_field)
            QWidget.setTabOrder(email_field, departamento_field)
            QWidget.setTabOrder(departamento_field, cargo_field)
            QWidget.setTabOrder(cargo_field, salario_field)
            QWidget.setTabOrder(salario_field, jornada_combo)
            QWidget.setTabOrder(jornada_combo, status_combo)

            # Aba Documentos
            QWidget.setTabOrder(status_combo, pis_field)
            QWidget.setTabOrder(pis_field, ctps_field)
            QWidget.setTabOrder(ctps_field, banco_combo)
            QWidget.setTabOrder(banco_combo, conta_field)
            QWidget.setTabOrder(conta_field, save_btn)
            QWidget.setTabOrder(save_btn, cancel_btn)

            # Conectar Enter nos campos de texto para avançar para o próximo campo
            nome_field.returnPressed.connect(lambda: cpf_field.setFocus())
            cpf_field.returnPressed.connect(lambda: data_admissao_field.setFocus())
            telefone_field.returnPressed.connect(lambda: tabs.setCurrentIndex(1))  # Muda para a aba Dados Profissionais
            email_field.returnPressed.connect(lambda: departamento_field.setFocus())
            departamento_field.returnPressed.connect(lambda: cargo_field.setFocus())
            cargo_field.returnPressed.connect(lambda: salario_field.setFocus())
            salario_field.returnPressed.connect(lambda: jornada_combo.setFocus())
            pis_field.returnPressed.connect(lambda: ctps_field.setFocus())
            ctps_field.returnPressed.connect(lambda: banco_combo.setFocus())
            conta_field.returnPressed.connect(lambda: save_btn.click())  # Pressionar Enter em Conta clica em "Salvar"

            # Exibe o diálogo na forma modal
            dialog.exec()

        except Exception as e:
            print(f"Erro ao exibir formulário de edição: {e}")
            if hasattr(self, 'logger'):
                self.logger.error(f"Erro ao exibir formulário de edição: {e}")
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro ao abrir o formulário: {e}")

    def salva_funcionario(self):
                """
                Saves the employee data from the form to the database.

                This method retrieves the values from the form fields, validates them, and inserts or updates the employee record in the database.
                """
                try:
                    # Define the column order according to the table structure
                    # Retrieve values from the form widgets
                    n_folha = self.num_folha.text()
                    nome = self.name_func.text()
                    cpf = self.cpf.text()
                    # Get the date in the desired format (e.g., "yyyy-MM-dd")
                    data_admissao = self.data_adimissap.date().toString("yyyy-MM-dd")
                    estado_civil = self.estado_civil.currentText()
                    telefone = self.telefone.text()

                    # For the company field, the QComboBox displays "code - name".
                    # Separate only the code (assuming it is numeric)
                    empresa_str = self.empresa_func.currentText()

                    if " - " in empresa_str:
                        empresa_codigo = empresa_str.split(" - ")[0].strip()
                        print(empresa_codigo)
                    else:
                        empresa_codigo = ""

                    departamento = self.department.currentText()
                    cargo = self.cargo.text()
                    salario = self.salario.text()
                    jornada_trabalho = self.jornada_trabalho.currentText()
                    status = self.status.currentText()
                    pis_pasep = self.pis.text()
                    ctps = self.ctps.text()
                    banco = self.banco.currentText()
                    contabancaria = self.conta.text()

                    # Define the table structure in a dictionary
                    estrutura_funcionario = {
                        "n_folha": "INTEGER UNIQUE NOT NULL",
                        "nome": "TEXT NOT NULL",
                        "CPF": "TEXT UNIQUE NOT NULL",
                        "data_admissao": "TEXT",
                        "estado_civil": "TEXT",
                        "telefone": "TEXT",
                        "empresa": "INTEGER",
                        "departamento": "TEXT",
                        "cargo": "TEXT",
                        "salario": "REAL",
                        "jornada_trabalho": "TEXT",
                        "status": "TEXT",
                        "pis_pasep": "TEXT",
                        "ctps": "TEXT",
                        "banco": "TEXT",
                        "contabancaria": "TEXT"
                    }

                    # Create the "cadastro_funcionario" table if necessary
                    self.criar_tabela("cadastro_funcionario", estrutura_funcionario)
                    self.cadastro_ponto()  # Create the "ponto" table that will use FK from "cadastro_funcionario"

                    # Create a dictionary with the data to be inserted
                    dados = {
                        "n_folha": int(n_folha) if n_folha.isdigit() else None,
                        "nome": nome,
                        "CPF": cpf,
                        "data_admissao": data_admissao,
                        "estado_civil": estado_civil,
                        "telefone": telefone,
                        "empresa": int(empresa_codigo) if empresa_codigo.isdigit() else None,
                        "departamento": departamento,
                        "cargo": cargo,
                        "salario": float(salario) if salario.replace(".", "", 1).isdigit() else 0.0,
                        "jornada_trabalho": jornada_trabalho,
                        "status": status,
                        "pis_pasep": pis_pasep,
                        "ctps": ctps,
                        "banco": banco,
                        "contabancaria": contabancaria
                    }

                    # Validate required fields
                    if not n_folha.strip():
                        raise ValueError("O N° Folha é obrigatório e deve ser numérico.")
                    if not nome.strip():
                        raise ValueError("O nome é obrigatório.")
                    if not cpf.strip():
                        raise ValueError("O CPF é obrigatório.")
                    if not empresa_codigo.strip():
                        raise ValueError("O Código da empresa é obrigatório")

                    # Insert or update the record in the database.
                    # In this example, we are using the CPF as a unique key.
                    retorno = self.inserir_ou_atualizar_registro("cadastro_funcionario", dados, cpf)
                    print(retorno)
                    if retorno:
                        if "UNIQUE" in retorno:
                            QMessageBox.critical(self, "Erro", f"O número da folha já existe no banco!")
                        elif retorno:
                            print("Deu certo")
                        elif "cadastro_funcionario.n_folha" in retorno:
                            QMessageBox.critical(self, "Erro",
                                                 f"Verifique se está inforado o número da folha em outro funcionário!\n{retorno}")

                    # If there is a method to update the employee view
                    if hasattr(self, "load_employees_data"):
                        self.load_employees_data()

                    logger.info("Funcionário cadastrado com sucesso!")
                except Exception as e:
                    logger.warning(f"Ocorreu um problema ao cadastrar o funcionário: {e}")  # Change from error to warning
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Icon.Warning)  # Warning icon (exclamation mark)
                    msg.setWindowTitle("Atenção")
                    msg.setText(f"Número da folha do funcionário já existente!\nVerifique se o funcionário já está cadastrado!"
                                f"\nErro: {e}")
                    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg.exec()

    def excluir_funcionario(self, company_id):
        """
        Exclui o registro do funcionário com base no CPF informado.

        Args:
            cpf (str): CPF do funcionário a ser excluído.
            :param company_id:
        """
        try:
            confirm = QMessageBox.question(
                self,
                "Confirmar Exclusão",
                f"Tem certeza que deseja excluir o funcionário {company_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                print(f"Excluindo empresa com ID: {company_id}")
                self.excluir_registro("cadastro_empresa", company_id)

            # Solicita confirmação do usuário
            confirm = QMessageBox.question(
                self,
                "Confirmação",
                "Deseja realmente excluir o funcionário?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if confirm == QMessageBox.StandardButton.Yes:
                # Chama o método para excluir o registro
                if self.excluir_registro("cadastro_funcionario", company_id):
                    QMessageBox.information(self, "Sucesso", "Funcionário excluído com sucesso!")
                    self.load_employees_data()  # Recarrega os dados na interface, se necessário
                else:
                    QMessageBox.critical(self, "Erro", "Erro ao excluir o funcionário.")
        except Exception as e:
            logger.error(f"Erro na exclusão do funcionário  {company_id}: {e}")
            QMessageBox.critical(self, "Erro", f"Ocorreu um erro: {e}")

    def show_add_employee_form(self):
        try:
            # Aba de novo funcionário
            dialog = QDialog(self)  # Define a janela principal como pai
            dialog.setWindowTitle("Adicionar Novo Funcionário")
            dialog.setMinimumSize(500, 400)  # Ajuste conforme necessário
            dialog.setStyleSheet("background-color: white; border-radius: 8px;")

            layout = QVBoxLayout(dialog)

            title = QLabel("Cadastro de Funcionário")
            title.setStyleSheet("font-size: 18px; font-weight: bold; color: #343a40; margin-bottom: 20px;")
            layout.addWidget(title)

            # Usar tabs para organizar o formulário
            tabs = QTabWidget()

            # Tab de Dados Pessoais
            personal_tab = QWidget()
            personal_layout = QFormLayout(personal_tab)

            self.empresa_func = QComboBox()

            empresas = self.consultar_registros("cadastro_empresa")
            for i in empresas:
                if empresas:
                    codigo = i[0]
                    nome = i[1]
                    self.empresa_func.addItems([str(codigo) + " - " + nome])
                else:
                    self.empresa_func.addItems(["Nenhuma empresa cadastrada"])

            personal_layout.addRow("Empresa:", self.empresa_func)

            self.num_folha = QLineEdit()
            self.num_folha.setPlaceholderText("N° Folha - Campo Obrigatório")
            personal_layout.addRow("N° Folha:", self.num_folha)

            self.name_func = QLineEdit()
            self.name_func.setPlaceholderText("Nome completo - Campo Obrigatório")
            personal_layout.addRow("Nome:", self.name_func)

            self.cpf = QLineEdit()
            self.cpf.setPlaceholderText("000.000.000-00 - Campo Obrigatório")
            personal_layout.addRow("CPF:", self.cpf)

            self.data_adimissap = QDateEdit()
            self.data_adimissap.setCalendarPopup(True)
            self.data_adimissap.setDate(QDate.currentDate())
            personal_layout.addRow("Data de Admissão:", self.data_adimissap)

            self.estado_civil = QComboBox()
            self.estado_civil.addItems(
                ["Selecione", "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)", "União Estável"])
            personal_layout.addRow("Estado Civil:", self.estado_civil)

            self.telefone = QLineEdit()
            self.telefone.setPlaceholderText("(00) 00000-0000")
            personal_layout.addRow("Telefone:", self.telefone)

            # Tab de Dados Profissionais
            professional_tab = QWidget()
            professional_layout = QFormLayout(professional_tab)

            self.email_func = QLineEdit()
            self.email_func.setPlaceholderText("email@exemplo.com")
            professional_layout.addRow("Email:", self.email_func)

            self.department = QComboBox()
            self.department.addItems(["Selecione um departamento", "TI", "RH", "Financeiro", "Marketing", "Operações"])
            professional_layout.addRow("Departamento:", self.department)

            self.cargo = QLineEdit()
            self.cargo.setPlaceholderText("Cargo do funcionário")
            professional_layout.addRow("Cargo:", self.cargo)

            self.salario = QLineEdit()
            self.salario.setPlaceholderText("0,00")
            professional_layout.addRow("Salário:", self.salario)

            self.jornada_trabalho = QComboBox()
            self.jornada_trabalho.addItems(["44h/semana", "40h/semana", "30h/semana", "20h/semana", "Outra"])
            professional_layout.addRow("Jornada de Trabalho:", self.jornada_trabalho)

            self.status = QComboBox()
            self.status.addItems(["Ativo", "Inativo", "Férias", "Afastado"])
            professional_layout.addRow("Status:", self.status)

            # Tab de Documentos
            documents_tab = QWidget()
            documents_layout = QFormLayout(documents_tab)

            self.pis = QLineEdit()
            self.pis.setPlaceholderText("000.00000.00-0")
            documents_layout.addRow("PIS/PASEP:", self.pis)

            self.ctps = QLineEdit()
            self.ctps.setPlaceholderText("0000000 série 000-0")
            documents_layout.addRow("CTPS:", self.ctps)

            self.banco = QComboBox()
            self.banco.addItems(
                ["Selecione", "Banco do Brasil", "Caixa Econômica", "Itaú", "Bradesco", "Santander", "Nubank", "Inter",
                 "Outro"])
            documents_layout.addRow("Banco:", self.banco)

            self.conta = QLineEdit()
            self.conta.setPlaceholderText("Agência e conta")
            documents_layout.addRow("Conta Bancária:", self.conta)

            # Adicionar tabs ao TabWidget
            tabs.addTab(personal_tab, "Dados Pessoais")
            tabs.addTab(professional_tab, "Dados Profissionais")
            tabs.addTab(documents_tab, "Documentos")

            layout.addWidget(tabs)

            buttons = QHBoxLayout()

            def save_and_close():
                self.salva_funcionario()
                dialog.close()  # Fecha o diálogo após salvar

            save = QPushButton("Salvar")
            save.setStyleSheet("background-color: #28a745; color: white; padding: 6px; border-radius: 4px;")
            save.clicked.connect(save_and_close)

            cancel = QPushButton("Cancelar")
            cancel.setStyleSheet("background-color: #dc3545; color: white; padding: 6px; border-radius: 4px;")
            cancel.clicked.connect(dialog.close)

            buttons.addWidget(save)
            buttons.addWidget(cancel)

            layout.addLayout(buttons)  # Adiciona os botões ao layout principal

            dialog.setLayout(layout)

            # Conexões na aba "Dados Pessoais"
            self.num_folha.returnPressed.connect(lambda: self.name_func.setFocus())
            self.name_func.returnPressed.connect(lambda: self.cpf.setFocus())
            self.cpf.returnPressed.connect(lambda: self.data_adimissap.setFocus())
            # QDateEdit não possui returnPressed; use editingFinished:
            self.data_adimissap.editingFinished.connect(lambda: self.estado_civil.setFocus())
            # Para QComboBox, utilize o sinal activated (o parâmetro _ ignora o índice):
            self.estado_civil.activated.connect(lambda _: self.telefone.setFocus())
            self.telefone.returnPressed.connect(
                lambda: self.email_func.setFocus())  # pula para a aba "Dados Profissionais"

            # Conexões na aba "Dados Profissionais"
            # Supondo que queremos preencher o campo Departamento primeiro
            self.email_func.returnPressed.connect(lambda: self.department.setFocus())
            self.department.activated.connect(lambda _: self.cargo.setFocus())
            self.cargo.returnPressed.connect(lambda: self.salario.setFocus())
            self.salario.returnPressed.connect(lambda: self.jornada_trabalho.setFocus())
            self.jornada_trabalho.activated.connect(lambda _: self.status.setFocus())
            self.status.activated.connect(lambda _: self.pis.setFocus())  # pula para a aba "Documentos"

            # Conexões na aba "Documentos"
            self.pis.returnPressed.connect(lambda: self.ctps.setFocus())
            self.ctps.returnPressed.connect(lambda: self.banco.setFocus())
            self.banco.activated.connect(lambda _: self.conta.setFocus())
            self.conta.returnPressed.connect(lambda: save.click())  # Pressionar Enter em Conta clica em "Salvar"

            # Obtém a posição da janela principal
            parent_rect = self.frameGeometry()
            # Obtém o tamanho do diálogo
            dialog_rect = dialog.frameGeometry()
            # Move o centro do diálogo para o centro da janela principal
            dialog_rect.moveCenter(parent_rect.center())
            # Aplica a nova posição ao diálogo
            dialog.move(dialog_rect.topLeft())

            dialog.show()

        except Exception as e:
            logger.error("Erro", e)

    # ----------------------- Importação Do ponto

    def init_timesheet_screen(self):
        try:

            timesheet_widget = QWidget()
            layout = QVBoxLayout(timesheet_widget)

            # Título
            title = QLabel("Gestão de Ponto")
            title.setStyleSheet("font-size: 20px; font-weight: bold; color: #343a40; margin-bottom: 20px;")
            layout.addWidget(title)

            # Tabs
            tabs = QTabWidget()

            # Tab de Importação
            import_tab = QWidget()
            import_layout = QVBoxLayout(import_tab)

            import_group = QGroupBox("Importar Arquivos de Ponto")
            import_form = QFormLayout(import_group)

            company_combo = QComboBox()

            empresas = self.consultar_registros("cadastro_empresa")
            if empresas:
                for i in empresas:
                    codigo = i[0]
                    nome = i[1]
                    company_combo.addItem(f"{codigo} - {nome}")
            else:
                company_combo.addItem("Nenhuma empresa cadastrada")

            import_form.addRow("Empresa:", company_combo)

            date_from = QDateEdit()
            date_from.setDate(QDate.currentDate().addDays(-30))
            date_from.setCalendarPopup(True)
            import_form.addRow("Data Inicial:", date_from)

            date_to = QDateEdit()
            date_to.setDate(QDate.currentDate())
            date_to.setCalendarPopup(True)
            import_form.addRow("Data Final:", date_to)

            self.import_file_layout = QHBoxLayout()
            import_file_path = QLineEdit()
            import_file_path.setPlaceholderText("Selecione o arquivo...")
            import_file_path.setReadOnly(True)

            browse_btn = QPushButton("Procurar")
            self.import_file_path = import_file_path  # Salve como atributo
            browse_btn.clicked.connect(lambda: self.browse_file())

            self.import_file_layout.addWidget(import_file_path)
            self.import_file_layout.addWidget(browse_btn)

            import_form.addRow("Arquivo:", self.import_file_layout)

            format_combo = QComboBox()
            format_combo.addItems(["TXT", "CSV", "XLS", "XLSX"])
            import_form.addRow("Formato:", format_combo)

            import_btn = QPushButton("Importar Dados")
            import_btn.clicked.connect(self.import_dados)
            import_form.addRow("", import_btn)

            import_layout.addWidget(import_group)
            import_layout.addStretch()

            # Tab de Exportação--------------------------------------
            export_tab = QWidget()
            export_layout = QVBoxLayout(export_tab)

            export_group = QGroupBox("Exportar Dados de Ponto")
            export_form = QFormLayout(export_group)

            export_company_combo = QComboBox()
            if empresas:
                for i in empresas:
                    codigo = i[0]
                    nome = i[1]
                    export_company_combo.addItem(f"{codigo} - {nome}")
            else:
                export_company_combo.addItem("Nenhuma empresa cadastrada")
            export_form.addRow("Empresa:", export_company_combo)

            export_dept_combo = QComboBox()
            export_dept_combo.addItems(["Todos os departamentos", "TI", "RH", "Financeiro", "Marketing", "Operações"])
            export_form.addRow("Departamento:", export_dept_combo)

            self.exporta_data_inicial = QDateEdit()
            self.exporta_data_inicial.setDate(QDate.currentDate().addDays(-30))
            self.exporta_data_inicial.setCalendarPopup(True)
            export_form.addRow("Data Inicial:", self.exporta_data_inicial)

            self.exporta_data_final = QDateEdit()
            self.exporta_data_final.setDate(QDate.currentDate())
            self.exporta_data_final.setCalendarPopup(True)
            export_form.addRow("Data Inicial:", self.exporta_data_final)

            export_format_group = QGroupBox("Formato de Exportação")
            export_format_layout = QVBoxLayout(export_format_group)

            csv_radio = QRadioButton("CSV")
            csv_radio.setChecked(True)
            txt_radio = QRadioButton("TXT")
            excel_radio = QRadioButton("Excel (XLSX)")

            export_format_layout.addWidget(csv_radio)
            export_format_layout.addWidget(txt_radio)
            export_format_layout.addWidget(excel_radio)

            export_form.addRow("", export_format_group)

            export_btn = QPushButton("Exportar Dados")
            export_btn.clicked.connect(self.exportar_ponto_sci)
            export_form.addRow("", export_btn)

            export_layout.addWidget(export_group)
            export_layout.addStretch()

            # Tab de Visualização ---------------------------------------------
            view_tab = QWidget()
            view_layout = QVBoxLayout(view_tab)

            # Grupo de filtros
            view_filters = QGroupBox("Filtros")
            view_filters_layout = QHBoxLayout(view_filters)

            # Adicionando os widgets ao layout
            view_filters_layout.addWidget(QLabel("Funcionário:"))
            funcionarios = self.visualizar_tabela("cadastro_funcionario")
            self.filtra_funcionario = QComboBox()
            self.filtra_funcionario.addItem(f"Nenhum selecionado")
            for fun in funcionarios:
                cod = fun[1]
                name = fun[2]
                self.filtra_funcionario.addItem(f"{cod} - {name}")

            view_filters_layout.addWidget(self.filtra_funcionario)

            view_filters_layout.addWidget(QLabel("Data:"))
            self.view_date = QDateEdit()
            view_date = self.view_date
            view_date.setDate(QDate.currentDate())
            view_date.setCalendarPopup(True)
            view_filters_layout.addWidget(view_date)
            print_btn = QPushButton("Imprimir")
            view_filters_layout.addWidget(print_btn)
            print_btn.clicked.connect(lambda: self.imprimir_tabela(view_table))
            # Criando o botão novamente e adicionando ao layout
            view_filter_btn = QPushButton("Filtrar")
            view_filters_layout.addWidget(view_filter_btn)
            # Conectar o botão de filtro à função de atualização com funcionário e data
            view_filter_btn.clicked.connect(lambda: self.update_table_ponto(view_table,
                                                                            view_date, self.filtra_funcionario))

            # Adicionando o grupo de filtros ao layout principal
            view_layout.addWidget(view_filters)
            # Botão para imprimir a tabela

            # Tabela de ponto
            self.view_table = TimesheetTable(self)
            view_table = self.view_table
            view_table.setColumnCount(7)
            view_table.setHorizontalHeaderLabels(
                ["CPF", "Funcionário", "Data", "Entrada", "Saída Almoço", "Retorno Almoço", "Saída"])
            view_Date_filter = view_date.date().toString("MM/yyyy")
            # Dados de exemplo
            sample_timesheet = self.visualiza_ponto(view_Date_filter)

            view_table.setRowCount(len(sample_timesheet))
            # Definindo largura fixa para cada coluna
            view_table.setColumnWidth(0, 150)  # Data
            view_table.setColumnWidth(1, 350)  # Funcionário
            view_table.setColumnWidth(2, 100)  # Data
            view_table.setColumnWidth(3, 120)  # Entrada
            view_table.setColumnWidth(4, 120)  # Saída Almoço
            view_table.setColumnWidth(5, 120)  # Retorno Almoço
            view_table.setColumnWidth(6, 120)  # Saída

            def format_cell(value):
                """Define a cor de fundo da célula baseado no valor do horário"""
                item = QTableWidgetItem(value)
                color = QColor("#ffcccc") if value == "00:00:00" else QColor("#ccffcc")
                item.setBackground(color)
                return item

            for row, (cpf, employee, date, entry, lunch_out, lunch_in, exit_time) in enumerate(sample_timesheet):
                view_table.setItem(row, 0, QTableWidgetItem(cpf))
                view_table.setItem(row, 1, QTableWidgetItem(employee))
                view_table.setItem(row, 2, QTableWidgetItem(date))
                view_table.setItem(row, 3, format_cell(entry))
                view_table.setItem(row, 4, format_cell(lunch_out))
                view_table.setItem(row, 5, format_cell(lunch_in))
                view_table.setItem(row, 6, format_cell(exit_time))

            view_layout.addWidget(view_table)
            # self.view_table = TimesheetTable(self)
            self.shortcut_delete = QShortcut(QKeySequence("Ctrl+Alt+D"), self)
            self.shortcut_delete.activated.connect(self.confirm_delete_entries)
            # Adicionar as tabs
            tabs.addTab(import_tab, "Importação")
            tabs.addTab(view_tab, "Visualização")
            tabs.addTab(export_tab, "Exportação")

            layout.addWidget(tabs)

            self.stack.addWidget(timesheet_widget)
            self.company_combo = company_combo
            self.date_from = date_from
            self.date_to = date_to
            self.format_combo = format_combo
        except Exception as e:
            logger.error("Erro", e)

    def imprimir_tabela(self, table):
        if table.rowCount() == 0:
            QMessageBox.warning(self, "Aviso", "Não há dados para imprimir.")
            return

        try:
            printer = QPrinter()
            print_dialog = QPrintDialog(printer, self)
            if print_dialog.exec() > 0:
                painter = QPainter()
                if not painter.begin(printer):
                    raise Exception("Falha ao iniciar o processo de impressão.")

                scale_factor = 1.2
                painter.scale(scale_factor, scale_factor)

                title_font = QFont("Arial", 14, QFont.Weight.Bold)
                header_font = QFont("Arial", 8, QFont.Weight.Bold)
                row_font = QFont("Arial", 8)

                page_rect = printer.pageLayout().paintRect(QPageLayout.Unit.Point)

                x_margin = 20
                y_margin = 20
                current_y = y_margin

                painter.setFont(title_font)
                title_text = "RELATÓRIO"
                title_rect = QRectF(x_margin, current_y, page_rect.width() - 2 * x_margin, 30)
                painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, title_text)
                current_y += 40

                painter.setFont(row_font)
                current_y += 20

                num_cols = table.columnCount()
                weights = [1] * num_cols
                total_weight = sum(weights)
                table_width = page_rect.width() - 2 * x_margin

                header_metrics = QFontMetrics(header_font)
                header_height = header_metrics.height() + 10
                row_metrics = QFontMetrics(row_font)
                row_height = row_metrics.height() + 8

                def print_table_header(y_position):
                    painter.setFont(header_font)
                    current_x = x_margin
                    for col in range(num_cols):
                        col_width = (weights[col] / total_weight) * table_width
                        header_text = table.horizontalHeaderItem(col).text()
                        rect = QRectF(current_x, y_position, col_width, header_height)
                        painter.drawRect(rect)
                        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, header_text)
                        current_x += col_width
                    return y_position + header_height

                current_y = print_table_header(current_y)
                painter.setFont(row_font)

                for row in range(table.rowCount()):
                    if current_y + row_height > page_rect.height() - y_margin:
                        printer.newPage()
                        current_y = y_margin
                        current_y = print_table_header(current_y)
                        painter.setFont(row_font)
                    current_x = x_margin
                    for col in range(num_cols):
                        col_width = (weights[col] / total_weight) * table_width
                        rect = QRectF(current_x, current_y, col_width, row_height)
                        painter.drawRect(rect)
                        item = table.item(row, col)
                        text = item.text() if item else ""
                        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
                        current_x += col_width
                    current_y += row_height

                current_y += 20
                footer_text = f"Data de impressão: {QDate.currentDate().toString('dd/MM/yyyy')}"
                painter.drawText(int(x_margin), int(current_y), footer_text)

                current_y += 40
                painter.drawText(x_margin, current_y, "Responsável:")
                painter.drawLine(x_margin + 100, current_y, x_margin + 300, current_y)

                current_y += 40
                painter.drawText(x_margin, current_y, "Supervisor:")
                painter.drawLine(x_margin + 100, current_y, x_margin + 300, current_y)

                painter.end()
                QMessageBox.information(self, "Sucesso", "Tabela enviada para impressão.")

        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

    def confirm_delete_entries(self):
        try:
            print("Chamou confirm_delete_entries")
            reply = QMessageBox.question(
                self,
                "Excluir lançamentos",
                "Deseja excluir todos os lançamentos?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            print("Resposta do QMessageBox:", reply)
            if reply == QMessageBox.StandardButton.Yes:
                print("Usuário confirmou; solicitando senha...")
                password, ok = QInputDialog.getText(
                    self,
                    "Confirmação de Senha",
                    "Informe a senha:",
                    QLineEdit.EchoMode.Password
                )
                print("Senha digitada:", password, "Ok:", ok)
                if ok and password == "batiliere":
                    self.view_table.clearContents()
                    self.deleta_todos_dados("ponto")
                else:
                    QMessageBox.warning(self, "Senha inválida", "A senha informada está incorreta!")
        except Exception as e:
            logger.error("Erro", e)

    def update_table_ponto(self, table, date_widget, employee_widget):
        """
        Atualiza a tabela de ponto com os dados filtrados pela data e pelo funcionário.
        """
        try:
            # Obter mês/ano selecionado
            date_filter = date_widget.date().toString("MM/yyyy")

            # Obter funcionário selecionado
            employee_text = employee_widget.currentText()  # Exemplo: "123 - João Silva"
            employee_id = employee_text.split(" - ")[0]  # Pegando apenas o código

            # Buscar dados de ponto filtrados por data e funcionário
            registros = self.visualiza_ponto_filtro(date_filter, employee_id)

            # Limpar tabela atual
            table.setRowCount(0)

            # Preencher tabela com novos dados
            for row, registro in enumerate(registros):
                cpf, nome, data, entrada, saida_almoco, retorno_almoco, saida = registro

                # Adicionar nova linha
                table.insertRow(row)

                # Criar itens da tabela
                itens = [
                    QTableWidgetItem(cpf),
                    QTableWidgetItem(nome),
                    QTableWidgetItem(data),
                    QTableWidgetItem(entrada),
                    QTableWidgetItem(saida_almoco),
                    QTableWidgetItem(retorno_almoco),
                    QTableWidgetItem(saida)
                ]

                # Definir cores para horários vazios
                for i, item in enumerate(itens[3:]):  # Apenas colunas de horário
                    if item.text() == "00:00:00":
                        item.setBackground(QColor("#ffcccc"))  # Vermelho claro
                    else:
                        item.setBackground(QColor("#ccffcc"))  # Verde claro

                # Adicionar itens à tabela
                for col, item in enumerate(itens):
                    table.setItem(row, col, item)

            # Mostrar mensagem com quantidade de registros
            print(f"Tabela atualizada com {len(registros)} registros para {date_filter} e funcionário {employee_id}")

        except Exception as e:
            logger.error(f"Erro ao atualizar tabela: {str(e)}")

    def import_dados(self):
        """
        Método principal para importação de dados de ponto
        """
        try:
            # Verifica se um arquivo foi selecionado
            file_path = self.import_file_path.text()
            if not file_path:
                QMessageBox.warning(self, "Erro", "Selecione um arquivo para importação.")
                return

            # Valida se o arquivo existe
            if not os.path.exists(file_path):
                QMessageBox.critical(self, "Erro", "O arquivo selecionado não existe.")
                return

            # Obtém informações do arquivo
            file_size = os.path.getsize(file_path)
            file_extension = os.path.splitext(file_path)[1].lower()

            # Validações de tamanho e tipo de arquivo
            if file_size == 0:
                QMessageBox.warning(self, "Erro", "O arquivo está vazio.")
                return

            if file_extension not in ['.txt', '.csv', '.xls', '.xlsx']:
                QMessageBox.warning(self, "Erro", "Formato de arquivo não suportado.")
                return

            # Lê os registros do arquivo
            registros = self.processar_pontos(self._processar_arquivo(file_path))

            # Obtém dados do formulário
            empresa = self.company_combo.currentText()  # Ex: "3 - uniconte"
            codigo_empresa = empresa.split(" - ")[0].strip()  # Resultado: "3"

            data_inicial = self.date_from.date().toString("dd/MM/yyyy")
            data_final = self.date_to.date().toString("dd/MM/yyyy")
            formato_selecionado = self.format_combo.currentText()

            # Filtra registros por data
            registros_filtrados = self._filtrar_registros_por_data(registros, data_inicial, data_final)

            for p in registros_filtrados:
                print(p)
                if len(p["codigo"]) > 9 > len(p["valor"]):
                    # Importa para o banco os dados utilizando o número da empresa separado
                    self.inserir_atualizar_ponto(cpf=p["codigo"],
                                                 timestamp=p["timestamp"],
                                                 tipo=p["tipo"],
                                                 codigo_empresa=codigo_empresa)

            self.update_table_ponto(self.view_table, self.view_date, self.filtra_funcionario)
            # Mensagem de sucesso
            QMessageBox.information(
                self,
                "Importação Concluída",
                f"Importação realizada com sucesso!\n"
                f"Empresa: {empresa}\n"
                f"Registros importados: {len(registros_filtrados)}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro de Importação",
                f"Ocorreu um erro durante a importação:\n{str(e)}"
            )

    def processar_pontos(self, registros):
        if not registros:
            QMessageBox.warning(self, "Aviso", "Nenhum registro válido encontrado no arquivo.")
            return
        try:
            # Dicionário para agrupar registros por CPF e data
            registros_por_funcionario = defaultdict(list)
            # Organizar os registros por funcionário e data
            for r in registros:
                if len(r["codigo"]) > 9:
                    cpf = r['codigo']
                    data = r['timestamp'][:10]  # Pega a parte da data "YYYY-MM-DD"
                    registros_por_funcionario[(cpf, data)].append(r)

            # Processar cada funcionário por dia
            resultado = []
            for (cpf, data), pontos in registros_por_funcionario.items():
                # Ordenar os registros do dia pelo timestamp
                pontos.sort(key=lambda x: x['timestamp'])

                # Definir entrada/saída alternadamente
                for i, ponto in enumerate(pontos):
                    tipo = 'entrada' if i % 2 == 0 else 'saida'
                    ponto['tipo'] = tipo
                    resultado.append(ponto)

            return resultado
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro de Importação",
                f"Ocorreu durante a conversão dos arquivos, antes de salvar no banco: \n{str(e)}"
            )

    def _filtrar_registros_por_data(self, registros, data_inicial, data_final):
        try:
            """
            Filtra os registros de ponto com base no intervalo de datas selecionado.
            """
            # Converte strings para objetos de data
            formato_data = "%d/%m/%Y"
            data_inicial = datetime.strptime(data_inicial, formato_data)
            data_final = datetime.strptime(data_final, formato_data)

            registros_filtrados = [
                p for p in registros if data_inicial <= datetime.strptime(p["data"], formato_data) <= data_final]
            return registros_filtrados
        except Exception as e:
            logger.error("Erro", e)

    def _processar_arquivo(self, file_path):
        """
        Processa o arquivo de diferentes formatos
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower()

            # Processamento para arquivos de texto
            if file_extension in ['.txt', '.csv']:
                return self._processar_arquivo_texto(file_path)

            # Processamento para arquivos Excel
            elif file_extension in ['.xls', '.xlsx']:
                return self._processar_arquivo_excel(file_path)

            else:
                raise ValueError("Formato de arquivo não suportado")

        except Exception as e:
            print(f"Erro ao processar arquivo: {e}")
            return []

    def _processar_arquivo_texto(self, file_path):
        """
        Processa arquivos de texto (TXT/CSV)
        """
        registros = []
        try:
            with open(file_path, 'r', encoding='utf-8') as arquivo:
                for linha in arquivo:
                    linha = linha.strip()
                    if linha:  # Ignora linhas vazias
                        registro = self._parse_line(linha)
                        if registro:
                            registros.append(registro)
            return registros
        except UnicodeDecodeError:
            # Tenta com outro encoding se UTF-8 falhar
            try:
                with open(file_path, 'r', encoding='latin-1') as arquivo:
                    for linha in arquivo:
                        linha = linha.strip()
                        if linha:
                            registro = self._parse_line(linha)
                            if registro:
                                registros.append(registro)
                return registros
            except Exception as e:
                logger.error("Erro", e)
                return []

    def _parse_line(self, line):
        """
        Faz o parsing de uma linha de registro com o seguinte layout:
          - posições 0 a 9: Identificador (registro)
          - posições 10 a 33: Timestamp (24 caracteres)
          - posições 34 a 44: Código (11 caracteres)
          - posições 45 em diante: Valor (ex: '1AFA', 'A1F5', etc.)
        Caso a linha não contenha todos os campos, os campos ausentes serão tratados como vazios.
        """
        try:
            registro = line[:10]
            timestamp = line[10:34]

            # Converter o timestamp para um objeto datetime
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
            # Formatar a data como dd/mm/aaaa
            data_formatada = dt.strftime("%d/%m/%Y")
            # Extrair a hora no formato HH:MM:SS
            hora_formatada = dt.strftime("%H:%M:%S")

            # Se a linha tiver pelo menos 45 caracteres, extrai o código; caso contrário, pega o que houver a partir
            # do índice 34
            codigo = line[34:45] if 45 <= len(line) < 90 else line[34:]
            # Se a linha tiver mais de 45 caracteres, extrai o valor (removendo espaços extras)
            valor = line[45:].strip() if len(line) > 45 else ""

            return {
                "registro": registro,
                "timestamp": timestamp,
                "data": data_formatada,
                "hora": hora_formatada,
                "codigo": codigo.strip(),
                "valor": valor
            }
        except Exception as e:
            logger.error("Erro", e)
            return None  # Retorna None em caso de erro

    def _processar_arquivo_excel(self, file_path):
        """
        Processa arquivos Excel
        """
        try:
            import pandas as pd

            # Lê o arquivo Excel
            df = pd.read_excel(file_path)

            registros = []
            for _, row in df.iterrows():
                # Adapte esta parte conforme o layout específico do seu arquivo Excel
                registro = {
                    'data': row['Data'].strftime('%d/%m/%Y'),
                    'hora': row['Hora'].strftime('%H:%M:%S'),
                    'registro': str(row.get('Registro', '')),
                    'codigo': str(row.get('Codigo', '')),
                    'valor': str(row.get('Valor', ''))
                }
                registros.append(registro)

            return registros

        except ImportError:
            QMessageBox.warning(
                self,
                "Erro",
                "Biblioteca pandas não instalada. Instale com: pip install pandas openpyxl"
            )
            return []
        except Exception as e:
            logger.error("Erro", e)
            return []

    def _salvar_registros(self, registros, empresa, formato):
        """
        Salva os registros no banco de dados ou gera arquivo
        """
        try:
            # Lógica de salvamento no banco ou geração de arquivo
            if not registros:
                raise ValueError("Nenhum registro para salvar")
            if formato == 'CSV':
                self._exportar_csv(registros, empresa)
            elif formato == 'TXT':
                self._exportar_txt(registros, empresa)

        except Exception as e:
            QMessageBox.critical(self, "Erro:", f"Erro ao salvar: {str(e)}")
            raise

    def browse_file(self, line_edit=None):
        """
        Método de seleção de arquivo com diagnóstico detalhado
        """
        try:
            # Imprime informações de diagnóstico
            print("Método browse_file iniciado")
            print(f"Parâmetro line_edit: {line_edit}")

            # Tenta obter o widget correto se não for passado
            if line_edit is None:
                if hasattr(self, 'import_file_path'):
                    line_edit = self.import_file_path
                else:
                    print("ERRO: Não foi possível encontrar o widget de linha de texto")
                    return None

            # Verifica o tipo do widget
            print(f"Tipo do widget: {type(line_edit)}")

            # Abre diálogo de seleção de arquivo
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Selecionar Arquivo",
                "",
                "Todos os Arquivos (*);;Arquivos de Texto (*.txt);;Arquivos CSV (*.csv);;Arquivos Excel (*.xls *.xlsx)"
            )

            # Diagnóstico do arquivo selecionado
            print(f"Arquivo selecionado: {file_name}")

            # Verifica se um arquivo foi selecionado
            if not file_name:
                print("Nenhum arquivo selecionado")
                return None

            # Valida existência do arquivo
            if not os.path.exists(file_name):
                print(f"ERRO: Arquivo não encontrado - {file_name}")
                return None

            # Tenta definir o texto no widget
            try:
                line_edit.setText(file_name)
                print(f"Caminho do arquivo definido: {file_name}")
            except Exception as set_text_error:
                print(f"ERRO ao definir texto: {set_text_error}")
                return None

            return file_name

        except Exception as e:
            # Captura qualquer exceção inesperada
            print(f"ERRO CRÍTICO no browse_file: {e}")
            import traceback
            traceback.print_exc()

            # Mostra mensagem de erro
            try:
                QMessageBox.critical(
                    self,
                    "Erro Crítico",
                    f"Ocorreu um erro ao selecionar o arquivo:\n{str(e)}"
                )
            except Exception as msg_error:
                print(f"ERRO ao mostrar mensagem: {msg_error}")

            return None

    def _exportar_csv(self, registros, empresa):
        """
        Exporta registros para um arquivo CSV
        """
        import csv
        from datetime import datetime

        try:
            # Gera nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ponto_{empresa.split(' - ')[0]}_{timestamp}.csv"
            path = os.path.join(os.path.expanduser("~"), "Downloads", filename)

            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(path), exist_ok=True)

            # Escreve o arquivo CSV
            with open(path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = registros[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for registro in registros:
                    writer.writerow(registro)

            return path
        except Exception as e:
            print(f"Erro ao exportar CSV: {e}")
            QMessageBox.critical(self, "Erro de Processamento", f"Erro ao exportar CSV: {str(e)}")
            raise

    def _exportar_txt(self, registros, empresa):
        """
        Exporta registros para um arquivo TXT
        """
        from datetime import datetime

        try:
            # Gera nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ponto_{empresa.split(' - ')[0]}_{timestamp}.txt"
            path = os.path.join(os.path.expanduser("~"), "Downloads", filename)

            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(path), exist_ok=True)

            # Escreve o arquivo TXT
            with open(path, 'w', encoding='utf-8') as txtfile:
                # Escreve cabeçalho
                headers = registros[0].keys()
                txtfile.write("\t".join(headers) + "\n")

                # Escreve registros
                for registro in registros:
                    line = "\t".join(str(registro[field]) for field in headers)
                    txtfile.write(line + "\n")

            return path
        except Exception as e:
            print(f"Erro ao exportar TXT: {e}")
            QMessageBox.critical(self, "Erro de Processamento", f"Erro ao exportar TXT: {str(e)}")
            raise

    def _exportar_excel(self, registros, empresa):
        """
        Exporta registros para um arquivo Excel
        """
        try:
            import pandas as pd
            from datetime import datetime

            # Gera nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ponto_{empresa.split(' - ')[0]}_{timestamp}.xlsx"
            path = os.path.join(os.path.expanduser("~"), "Downloads", filename)

            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(path), exist_ok=True)

            # Converte para DataFrame e salva
            df = pd.DataFrame(registros)
            df.to_excel(path, index=False)

            return path
        except ImportError:
            raise ImportError("Biblioteca pandas não instalada. Instale com: pip install pandas openpyxl")
        except Exception as e:
            print(f"Erro ao exportar Excel: {e}")
            QMessageBox.critical(self, "Erro de Processamento", f"Erro ao exportar Excel: {str(e)}")
            raise

    # ------------------------------------ Relatórios --------------------------------------------------

    def init_reports_screen(self):
        try:
            reports_widget = QWidget()
            layout = QVBoxLayout(reports_widget)
            # Título
            title = QLabel("Relatórios")
            title.setStyleSheet("font-size: 20px; font-weight: bold; color: #343a40; margin-bottom: 20px;")
            layout.addWidget(title)
            # Tabs para diferentes relatórios
            tabs = QTabWidget()
            hours_tab = QWidget()
            hours_layout = QVBoxLayout(hours_tab)

            # Grupo de Filtros
            hours_filter = QGroupBox("Filtros")
            hours_filter_layout = QFormLayout(hours_filter)

            # ComboBox de Empresa
            hours_company = QComboBox()
            hours_company.addItem("Não Selecionado")
            empresas = self.consultar_registros("cadastro_empresa")
            if empresas:
                for i in empresas:
                    codigo = i[0]
                    nome = i[1]
                    hours_company.addItem(f"{codigo} - {nome}")
            hours_filter_layout.addRow("Empresa:", hours_company)

            # Data Inicial
            hours_date_from = QDateEdit()
            hours_date_from.setDate(QDate.currentDate().addDays(-30))
            hours_date_from.setCalendarPopup(True)
            hours_filter_layout.addRow("Data Inicial:", hours_date_from)
            # Data Final
            hours_date_to = QDateEdit()
            hours_date_to.setDate(QDate.currentDate())
            hours_date_to.setCalendarPopup(True)
            hours_filter_layout.addRow("Data Final:", hours_date_to)
            # Botão para gerar relatório
            hours_generate = QPushButton("Gerar Relatório")
            hours_filter_layout.addRow("", hours_generate)
            hours_layout.addWidget(hours_filter)
            # Tabela de horas
            hours_table = QTableWidget()
            hours_table.setColumnCount(6)
            hours_table.setHorizontalHeaderLabels(
                ["Funcionário", "Empresa", "Data", "Total Horas", "Horas Extras", "Horas Faltantes"]
            )
            hours_layout.addWidget(hours_table)
            # Configurar a coluna 0 ("Funcionário") para se expandir com a tela
            header = hours_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

            # Função local que lê os filtros e atualiza a tabela
            def generate_hours_report():
                # Verifica a empresa
                company_code = 0  # Se "Não Selecionado", mantém 0
                if hours_company.currentIndex() > 0:
                    texto_combo = hours_company.currentText()
                    company_code = int(texto_combo.split(" - ")[0])
                date_from_str = hours_date_from.date().toString("dd/MM/yyyy")
                date_to_str = hours_date_to.date().toString("dd/MM/yyyy")
                dados = self.calcular_horas_extras_faltantes_por_empresa(
                    company_code,
                    date_from_str,
                    date_to_str,
                    False
                )
                hours_table.setRowCount(len(dados))
                for row, (nome, empresa_codigo, data, total, extra, faltante) in enumerate(dados):
                    empresa = str(empresa_codigo)
                    hours_table.setItem(row, 0, QTableWidgetItem(nome))
                    hours_table.setItem(row, 1, QTableWidgetItem(empresa))
                    hours_table.setItem(row, 2, QTableWidgetItem(data))
                    hours_table.setItem(row, 3, QTableWidgetItem(total))
                    hours_table.setColumnWidth(0, 250)
                    extra_item = QTableWidgetItem(extra)
                    if extra != "00:00":
                        extra_item.setForeground(QColor("#28a745"))
                    hours_table.setItem(row, 4, extra_item)
                    missing_item = QTableWidgetItem(faltante)
                    if faltante != "00:00":
                        missing_item.setForeground(QColor("#dc3545"))
                    hours_table.setItem(row, 5, missing_item)

            hours_generate.clicked.connect(generate_hours_report)

            # Função para exportar para CSV
            def export_to_csv():
                if hours_table.rowCount() == 0:
                    QMessageBox.warning(self, "Aviso", "Não há dados para exportar.")
                    return
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Salvar arquivo CSV", "", "Arquivos CSV (*.csv);;Todos os arquivos (*)"
                )
                if file_path:
                    try:
                        with open(file_path, 'w', newline='', encoding='utf-8') as file:
                            writer = csv.writer(file, delimiter=';')
                            headers = [hours_table.horizontalHeaderItem(col).text() for col in
                                       range(hours_table.columnCount())]
                            writer.writerow(headers)
                            for row in range(hours_table.rowCount()):
                                row_data = []
                                for col in range(hours_table.columnCount()):
                                    item = hours_table.item(row, col)
                                    row_data.append(item.text() if item is not None else "")
                                writer.writerow(row_data)
                        QMessageBox.information(self, "Sucesso", f"Dados exportados com sucesso para {file_path}")
                    except Exception as e:
                        QMessageBox.critical(self, "Erro", f"Erro ao exportar para CSV: {str(e)}")

            def print_report():
                if hours_table.rowCount() == 0:
                    QMessageBox.warning(self, "Aviso", "Não há dados para imprimir.")
                    return
                try:
                    printer = QPrinter()
                    print_dialog = QPrintDialog(printer, self)
                    if print_dialog.exec() > 0:
                        painter = QPainter()
                        if not painter.begin(printer):
                            raise Exception("Falha ao iniciar o processo de impressão.")

                        # Aplicar um fator de escala para ampliar a tabela
                        scale_factor = 1.2  # Aumenta 20%
                        painter.scale(scale_factor, scale_factor)

                        # Configurações de fontes
                        title_font = QFont("Arial", 14, QFont.Weight.Bold)
                        header_font = QFont("Arial", 8, QFont.Weight.Bold)
                        row_font = QFont("Arial", 8)

                        # Obter a área imprimível (em pontos)
                        page_rect = printer.pageLayout().paintRect(QPageLayout.Unit.Point)
                        # Reduzir as margens para usar mais espaço da folha (valores ajustados para a escala)
                        x_margin = 20
                        y_margin = 20
                        current_y = y_margin

                        # Imprimir título do relatório (centralizado)
                        painter.setFont(title_font)
                        title_text = "RELATÓRIO DE HORAS TRABALHADAS"
                        title_rect = QRectF(x_margin, current_y, page_rect.width() - 2 * x_margin, 30)
                        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, title_text)
                        current_y += 40

                        # Imprimir informações dos filtros
                        painter.setFont(row_font)
                        data_inicial = hours_date_from.date().toString("dd/MM/yyyy")
                        data_final = hours_date_to.date().toString("dd/MM/yyyy")
                        filtro_text = f"Período: {data_inicial} a {data_final}"
                        painter.drawText(int(x_margin), int(current_y), filtro_text)
                        current_y += 20
                        empresa_texto = hours_company.currentText()
                        painter.drawText(int(x_margin), int(current_y), f"Empresa: {empresa_texto}")
                        current_y += 30

                        # Configurar tabela com pesos para as colunas (usando a largura da área disponível)
                        num_cols = hours_table.columnCount()
                        # Por exemplo, manter a coluna "Funcionário" com peso 2 e as demais com peso 1
                        weights = [2] + [1] * (num_cols - 1)
                        total_weight = sum(weights)
                        table_width = page_rect.width() - 2 * x_margin

                        header_metrics = QFontMetrics(header_font)
                        header_height = header_metrics.height() + 10
                        row_metrics = QFontMetrics(row_font)
                        row_height = row_metrics.height() + 8

                        def print_table_header(y):
                            painter.setFont(header_font)
                            current_x = x_margin
                            for col in range(num_cols):
                                col_width = (weights[col] / total_weight) * table_width
                                header_text = hours_table.horizontalHeaderItem(col).text()
                                rect = QRectF(current_x, y, col_width, header_height)
                                painter.drawRect(rect)
                                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, header_text)
                                current_x += col_width
                            return y + header_height

                        current_y = print_table_header(current_y)
                        painter.setFont(row_font)

                        # Imprimir as linhas da tabela
                        for row in range(hours_table.rowCount()):
                            if current_y + row_height > page_rect.height() - y_margin:
                                printer.newPage()
                                current_y = y_margin
                                current_y = print_table_header(current_y)
                                painter.setFont(row_font)
                            current_x = x_margin
                            for col in range(num_cols):
                                col_width = (weights[col] / total_weight) * table_width
                                rect = QRectF(current_x, current_y, col_width, row_height)
                                painter.drawRect(rect)
                                item = hours_table.item(row, col)
                                text = item.text() if item is not None else ""
                                painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
                                current_x += col_width
                            current_y += row_height

                        # Rodapé com data de impressão
                        current_y += 20
                        footer_text = f"Data de impressão: {QDate.currentDate().toString('dd/MM/yyyy')}"
                        painter.drawText(int(x_margin), int(current_y), footer_text)

                        # Após imprimir o rodapé (footer_text), acrescente algo assim:

                        current_y += 40

                        # Desenha o título "Responsável:"
                        painter.drawText(x_margin, current_y, "Responsável:")
                        # Desenha a linha para assinatura (por exemplo, 200 pixels de largura)
                        line_start_x = x_margin + 100
                        line_end_x = line_start_x + 200
                        painter.drawLine(line_start_x, current_y, line_end_x, current_y)

                        current_y += 40

                        # Desenha o título "Supervisor:"
                        painter.drawText(x_margin, current_y, "Supervisor:")
                        # Linha para assinatura
                        line_start_x = x_margin + 100
                        line_end_x = line_start_x + 200
                        painter.drawLine(line_start_x, current_y, line_end_x, current_y)

                        painter.end()
                        QMessageBox.information(self, "Sucesso", "Relatório enviado para impressão.")
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Erro ao imprimir relatório: {str(e)}")

            # Botões de exportar e imprimir
            export_buttons = QHBoxLayout()
            print_button = QPushButton("Imprimir")
            print_button.setStyleSheet("background-color: #17a2b8;")
            print_button.clicked.connect(print_report)
            export_csv = QPushButton("Exportar CSV")
            export_csv.setStyleSheet("background-color: #17a2b8;")
            export_csv.clicked.connect(export_to_csv)
            export_buttons.addWidget(print_button)
            export_buttons.addWidget(export_csv)
            export_buttons.addStretch()
            hours_layout.addLayout(export_buttons)
            tabs.addTab(hours_tab, "Horas Trabalhadas")
            layout.addWidget(tabs)
            self.stack.addWidget(reports_widget)

            # ----- Nova Aba "Funcionário" -----
            funcionario_tab = QWidget()
            funcionario_layout = QVBoxLayout(funcionario_tab)

            # Grupo de Filtros para Relatório Individual
            funcionario_filter = QGroupBox("Filtros")
            funcionario_filter_layout = QFormLayout(funcionario_filter)

            # Combobox de Empresa (para filtrar a empresa)
            empresa_combo = QComboBox()
            empresa_combo.addItem("Não Selecionado")
            empresas = self.consultar_registros("cadastro_empresa")
            if empresas:
                for i in empresas:
                    codigo = i[0]
                    nome = i[1]
                    empresa_combo.addItem(f"{codigo} - {nome}")
            funcionario_filter_layout.addRow("Empresa:", empresa_combo)

            # Combobox para pesquisar Funcionário
            # Aqui, armazenamos o CPF (usado para o join com a tabela ponto) como item data
            funcionario_combo = QComboBox()
            funcionario_combo.addItem("Selecione o Funcionário")
            funcionarios = self.consultar_registros("cadastro_funcionario")
            if funcionarios:
                for f in funcionarios:
                    # f[0] é o id, f[2] é o nome e f[3] (assumindo a ordem) é o CPF
                    codigo = f[0]
                    nome = f[2]
                    cpf = f[3]  # Certifique-se de que a consulta retorne o CPF na posição correta
                    funcionario_combo.addItem(f"{codigo} - {nome}", cpf)
            funcionario_filter_layout.addRow("Funcionário:", funcionario_combo)

            # Opções de Data (mesmas que na aba de Horas Trabalhadas)
            func_date_from = QDateEdit()
            func_date_from.setDate(QDate.currentDate().addDays(-30))
            func_date_from.setCalendarPopup(True)
            funcionario_filter_layout.addRow("Data Inicial:", func_date_from)

            func_date_to = QDateEdit()
            func_date_to.setDate(QDate.currentDate())
            func_date_to.setCalendarPopup(True)
            funcionario_filter_layout.addRow("Data Final:", func_date_to)

            # Botão para gerar relatório do Funcionário
            func_generate = QPushButton("Gerar Relatório")
            funcionario_filter_layout.addRow("", func_generate)

            funcionario_layout.addWidget(funcionario_filter)

            # Adiciona a aba "Relatório Individual" ao QTabWidget
            tabs.addTab(funcionario_tab, "Relatório Individual")

            # Função que gera o relatório individual com os filtros e salva um arquivo CSV
            # Função que gera o relatório individual com os filtros e salva um arquivo CSV
            def gerar_relatorio_individual():
                try:
                    import datetime
                    from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
                    from PyQt6.QtPrintSupport import QPrintDialog, QPrinter
                    from PyQt6.QtGui import QTextDocument

                    # Obtém os filtros
                    empresa_sel = empresa_combo.currentText()
                    company_code = None
                    if empresa_sel != "Não Selecionado":
                        company_code = int(empresa_sel.split(" - ")[0])
                    employee_cpf = None
                    if funcionario_combo.currentIndex() > 0:
                        employee_cpf = funcionario_combo.itemData(funcionario_combo.currentIndex())
                    date_from = func_date_from.date().toString("yyyy-MM-dd") + " 00:00:00"
                    date_to = func_date_to.date().toString("yyyy-MM-dd") + " 23:59:59"

                    # Monta a consulta (baseada na função visualiza_ponto, com filtros adicionais)
                    query = """
                        SELECT p.id, f.CPF, f.nome, substr(p.timestamp, 1, 10) as data_registro,
                               substr(p.timestamp, 12, 8) as horario, p.tipo
                        FROM ponto p
                        JOIN cadastro_funcionario f ON p.cpf = f.CPF
                        WHERE p.timestamp BETWEEN ? AND ?
                    """
                    params = [date_from, date_to]
                    if company_code is not None:
                        query += " AND p.codigo_empresa = ?"
                        params.append(company_code)
                    if employee_cpf is not None:
                        query += " AND f.CPF = ?"
                        params.append(employee_cpf)
                    query += " ORDER BY f.nome, p.timestamp"

                    self.cursor.execute(query, params)
                    registros = self.cursor.fetchall()
                    if not registros:
                        QMessageBox.information(self, "Aviso",
                                                "Nenhum registro encontrado para os filtros selecionados.")
                        return

                    # Agrupa os registros por (CPF, nome, data)
                    registros_por_pessoa_dia = {}
                    for ponto_id, CPF, nome, data_registro, horario, tipo in registros:
                        chave = (CPF, nome, data_registro)
                        if chave not in registros_por_pessoa_dia:
                            registros_por_pessoa_dia[chave] = []
                        registros_por_pessoa_dia[chave].append((horario, tipo))

                    def str_to_time(t_str):
                        return datetime.datetime.strptime(t_str, "%H:%M:%S").time()

                    def seleciona_registro(registros, target_time, expected_type):
                        candidatos = [r for r in registros if r[1] == expected_type]
                        if not candidatos:
                            return "00:00:00"
                        return min(candidatos, key=lambda r: abs(
                            datetime.datetime.combine(datetime.date.today(), str_to_time(r[0])) -
                            datetime.datetime.combine(datetime.date.today(), target_time)))[0]

                    resultado = []
                    for (CPF, nome, data_registro), regs in registros_por_pessoa_dia.items():
                        # Ordena os registros por horário
                        regs.sort(key=lambda x: str_to_time(x[0]))

                        # Identifica entradas e saídas automaticamente
                        entradas_saidas = []
                        for i, (horario, tipo) in enumerate(regs):
                            if tipo == 'entrada':
                                entradas_saidas.append(("Entrada", horario))
                            elif tipo == 'saida':
                                entradas_saidas.append(("Saída", horario))

                        # Preenche os registros de entrada e saída
                        registros_formatados = []
                        for i in range(0, len(entradas_saidas), 2):
                            entrada = entradas_saidas[i][1] if i < len(entradas_saidas) else "00:00:00"
                            saida = entradas_saidas[i + 1][1] if i + 1 < len(entradas_saidas) else "00:00:00"
                            registros_formatados.append(f"Entrada: {entrada} | Saída: {saida}")

                        if '-' in data_registro:
                            ano_db, mes_db, dia_db = data_registro.split('-')
                            data_formatada = f"{dia_db}/{mes_db}/{ano_db}"
                        else:
                            data_formatada = data_registro

                        resultado.append((CPF, nome, data_formatada, " | ".join(registros_formatados)))

                    # Cria um diálogo de prévia com uma tabela para exibir o relatório
                    preview_dialog = QDialog(self)
                    preview_dialog.setWindowTitle("Prévia do Relatório Individual")
                    preview_dialog.resize(1000, 600)  # Aumenta o tamanho da janela de prévia
                    dlg_layout = QVBoxLayout(preview_dialog)

                    # Cabeçalho do relatório
                    cabecalho = QLabel(f"""
                        <h2>Relatório de Ponto</h2>
                        <b>Empresa:</b> {empresa_sel if empresa_sel != "Não Selecionado" else "Todas"}<br>
                        <b>Funcionário:</b> {funcionario_combo.currentText() if funcionario_combo.currentIndex() > 0 else "Todos"}<br>
                        <b>Período:</b> {func_date_from.date().toString("dd/MM/yyyy")} a {func_date_to.date().toString("dd/MM/yyyy")}<br>
                        <hr>
                    """)
                    cabecalho.setStyleSheet("font-size: 12pt;")
                    dlg_layout.addWidget(cabecalho)

                    # Tabela para exibir os registros
                    tabela = QTableWidget()
                    tabela.setColumnCount(4)
                    tabela.setHorizontalHeaderLabels(["CPF", "Nome", "Data", "Registros de Ponto"])
                    tabela.setRowCount(len(resultado))

                    # Preenche a tabela com os dados
                    for i, linha in enumerate(resultado):
                        for j, valor in enumerate(linha):
                            item = QTableWidgetItem(valor)
                            item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)  # Torna os itens não editáveis
                            tabela.setItem(i, j, item)

                    # Ajusta o tamanho das colunas
                    tabela.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
                    dlg_layout.addWidget(tabela)

                    # Botão de impressão
                    btn_imprimir = QPushButton("Imprimir Relatório")
                    dlg_layout.addWidget(btn_imprimir)

                    def imprimir_relatorio():
                        printer = QPrinter()
                        dialog = QPrintDialog(printer, self)
                        if dialog.exec() == QDialog.DialogCode.Accepted:
                            documento = QTextDocument()
                            html = f"""
                                <h2>Relatório de Ponto</h2>
                                <b>Empresa:</b> {empresa_sel if empresa_sel != "Não Selecionado" else "Todas"}<br>
                                <b>Funcionário:</b> {funcionario_combo.currentText() if funcionario_combo.currentIndex() > 0 else "Todos"}<br>
                                <b>Período:</b> {func_date_from.date().toString("dd/MM/yyyy")} a {func_date_to.date().toString("dd/MM/yyyy")}<br>
                                <hr>
                                <table border="1" cellpadding="5">
                                    <tr>
                                        <th>CPF</th>
                                        <th>Nome</th>
                                        <th>Data</th>
                                        <th>Registros de Ponto</th>
                                    </tr>
                            """
                            for linha in resultado:
                                html += f"""
                                    <tr>
                                        <td>{linha[0]}</td>
                                        <td>{linha[1]}</td>
                                        <td>{linha[2]}</td>
                                        <td>{linha[3]}</td>
                                    </tr>
                                """
                            html += "</table>"
                            html += """
                            <br><br>
                            <table style="width:60%; margin:40px auto;">
                                <tr>
                                    <td style="width:50%; text-align:center; padding-right:40px;">
                                        __________________________<br>
                                        Colaborador
                                    </td>
                                    <td style="width:50%; text-align:center; padding-left:40px;">
                                        __________________________<br>
                                        Supervisor
                                    </td>
                                </tr>
                            </table>
                            """

                            documento.setHtml(html)
                            documento.print(printer)

                    btn_imprimir.clicked.connect(imprimir_relatorio)

                    # Botões de ação
                    button_box = QDialogButtonBox(
                        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
                    dlg_layout.addWidget(button_box)
                    button_box.accepted.connect(preview_dialog.accept)
                    button_box.rejected.connect(preview_dialog.reject)

                    # Se o usuário confirmar a prévia, solicita salvar o arquivo
                    if preview_dialog.exec() == QDialog.DialogCode.Accepted:
                        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Relatório Individual", "",
                                                                   "CSV Files (*.csv);;All Files (*)")
                        if file_path:
                            import csv
                            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                                writer = csv.writer(f, delimiter=';')
                                writer.writerow(["CPF", "Nome", "Data", "Registros de Ponto"])
                                for linha in resultado:
                                    writer.writerow(linha)
                            QMessageBox.information(self, "Sucesso", f"Relatório salvo com sucesso em {file_path}")

                except Exception as e:
                    print(e)
            # Adiciona o QTabWidget ao layout principal
            func_generate.clicked.connect(gerar_relatorio_individual)
            layout.addWidget(tabs)
            self.stack.addWidget(reports_widget)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro de Processamento",
                f"Erro ao carregar informações dos relatórios: {str(e)}"
            )


    def init_settings_screen(self):
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)

        # Título
        title = QLabel("Configurações do Sistema")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #343a40; margin-bottom: 20px;")
        layout.addWidget(title)

        # Configurações de Importação/Exportação
        import_export_group = QGroupBox("Configurações de Importação/Exportação")
        import_export_layout = QFormLayout(import_export_group)

        default_import_format = QComboBox()
        default_import_format.addItems(["CSV", "TXT", "XLS", "XLSX"])
        import_export_layout.addRow("Formato padrão de importação:", default_import_format)

        default_export_format = QComboBox()
        default_export_format.addItems(["CSV", "TXT", "XLSX"])
        import_export_layout.addRow("Formato padrão de exportação:", default_export_format)

        delimiter = QComboBox()
        delimiter.addItems([",", ";", "Tab", "|"])
        import_export_layout.addRow("Delimitador CSV:", delimiter)

        encoding = QComboBox()
        encoding.addItems(["UTF-8", "ISO-8859-1", "Windows-1252"])
        import_export_layout.addRow("Encoding:", encoding)

        layout.addWidget(import_export_group)

        # Configurações de Interface
        ui_group = QGroupBox("Configurações de Interface")
        ui_layout = QFormLayout(ui_group)

        theme = QComboBox()
        theme.addItems(["Claro", "Escuro", "Sistema"])
        ui_layout.addRow("Tema:", theme)

        confirm_delete = QCheckBox()
        confirm_delete.setChecked(True)
        ui_layout.addRow("Confirmar antes de excluir:", confirm_delete)

        rows_per_page = QSpinBox()
        rows_per_page.setMinimum(10)
        rows_per_page.setMaximum(100)
        rows_per_page.setValue(20)
        rows_per_page.setSingleStep(5)
        ui_layout.addRow("Linhas por página:", rows_per_page)

        layout.addWidget(ui_group)

        # Configurações de Ponto
        timesheet_group = QGroupBox("Configurações de Ponto")
        timesheet_layout = QFormLayout(timesheet_group)

        workday_hours = QSpinBox()
        workday_hours.setMinimum(4)
        workday_hours.setMaximum(12)
        workday_hours.setValue(8)
        timesheet_layout.addRow("Horas de trabalho diárias padrão:", workday_hours)

        tolerance = QSpinBox()
        tolerance.setMinimum(0)
        tolerance.setMaximum(60)
        tolerance.setValue(10)
        tolerance.setSuffix(" min")
        timesheet_layout.addRow("Tolerância para atrasos:", tolerance)

        auto_import = QCheckBox()
        auto_import.setChecked(False)
        timesheet_layout.addRow("Importação automática de ponto:", auto_import)

        layout.addWidget(timesheet_group)

        # Botões
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("Salvar Configurações")
        save_btn.clicked.connect(self.save_settings)

        reset_btn = QPushButton("Restaurar Padrões")
        reset_btn.setStyleSheet("background-color: #6c757d;")

        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(reset_btn)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)
        layout.addStretch()

        self.stack.addWidget(settings_widget)

        # Métodos de navegação

    def show_home(self):
        self.stack.setCurrentIndex(0)

    def show_companies(self):
        self.stack.setCurrentIndex(1)

    def show_employees(self):
        self.stack.setCurrentIndex(2)

    def show_timesheet(self):
        self.stack.setCurrentIndex(3)

    def show_reports(self):
        self.stack.setCurrentIndex(4)

    def show_settings(self):
        self.stack.setCurrentIndex(5)

        # Métodos para formulários e ações

        # Métodos para importação e exportação

    def import_employees(self):
        QMessageBox.information(self, "Importação de Funcionários", "Iniciando importação de funcionários...")

    def export_employees(self):
        employees_data = self.visualizar_tabela("cadastro_funcionario")

        # Substituir ',' por ';' nos dados
        dados = [tuple(str(field).replace(',', ';') for field in employee) for employee in employees_data]

        file_name, _ = QFileDialog.getSaveFileName(
            self, "Exportar Funcionários", "",
            "Arquivos CSV (*.csv);;Arquivos de Texto (*.txt);;Arquivos Excel (*.xlsx)"
        )

        if file_name:
            try:
                with open(file_name, mode='w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file, delimiter=';')  # Alterado para ponto e vírgula

                    # Escrevendo o cabeçalho
                    header = ["ID", "NúmeroFolha", "Nome", "CPF", "Data de Admissão", "Estado Civil",
                              "Endereço", "Empresa", "Setor", "Telefone", "Salário", "Carga Horária",
                              "Status", "E-mail", "Data de Nascimento", "Gênero", "Observações",
                              "Criado em", "Atualizado em"]
                    writer.writerow(header)

                    # Escrevendo os dados
                    for employee in dados:
                        writer.writerow(employee)

                QMessageBox.information(self, "Exportação de Funcionários",
                                        f"Funcionários exportados com sucesso para {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Erro na Exportação",
                                     f"Ocorreu um erro ao exportar os funcionários: {str(e)}")

    def export_companies(self):
        employees_data = self.visualizar_tabela("cadastro_empresa")

        # Substituir ',' por ';' nos dados
        dados = [tuple(str(field).replace(',', ';') for field in employee) for employee in employees_data]

        file_name, _ = QFileDialog.getSaveFileName(
            self, "Exportar Funcionários", "",
            "Arquivos CSV (*.csv);;Arquivos de Texto (*.txt);;Arquivos Excel (*.xlsx)"
        )

        if file_name:
            try:
                with open(file_name, mode='w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file, delimiter=';')  # Alterado para ponto e vírgula

                    # Escrevendo o cabeçalho
                    header = ["ID", "Nome", "CNPJ", "Endereço", "Cidade", "Estado",
                              "Telefone", "Email", "DataCadastro", "DataAlteraçao"
                              ]
                    writer.writerow(header)

                    # Escrevendo os dados
                    for employee in dados:
                        writer.writerow(employee)

                QMessageBox.information(self, "Exportação de Empresas",
                                        f"Empresas exportadas com sucesso para {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Erro na Exportação",
                                     f"Ocorreu um erro ao exportar as Empresas: {str(e)}")

    def import_timesheet(self):
        QMessageBox.information(self, "Importação de Ponto", "Ainda não disponível")

    def exportar_ponto_sci(self):
        try:
            # Captura as datas de início e fim definidas na interface
            data_inicio = self.exporta_data_inicial.text()
            data_fim = self.exporta_data_final.text()
            periodo = f"{data_inicio} a {data_fim}"

            print(data_inicio, data_fim)

            # Obtém os dados do ponto para o período especificado
            dados = self.exporta_ponto_periodo(data_inicio, data_fim)
            print(dados)

            # Cria um nome padrão para o arquivo com a data de hoje
            data_hoje = datetime.now().strftime("%Y-%m-%d")
            nome_padrao = f"exportacao_ponto_{data_hoje}.txt"

            # Abre a caixa de diálogo para o usuário definir onde salvar o arquivo TXT com o nome padrão
            file_name, _ = QFileDialog.getSaveFileName(self, "Exportar Dados de Ponto", nome_padrao,
                                                       "Arquivos de Texto (*.txt)")
            if file_name:
                with open(file_name, 'w', encoding='utf-8') as arquivo:
                    for linha in dados:
                        arquivo.write(linha + "\n")

                QMessageBox.information(self, "Exportação de Ponto",
                                        f"Dados de ponto exportados com sucesso para {file_name}")
        except Exception as e:
            QMessageBox.critical(self, "Erro de Processamento", f"Erro ao exportar Excel: {str(e)}")
            print(e)

    def save_settings(self):
        QMessageBox.information(self, "Configurações", "Configurações salvas com sucesso!")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
