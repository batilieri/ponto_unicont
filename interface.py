import os
import re
import sys
from collections import defaultdict
from datetime import datetime

from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QColor, QAction
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QFormLayout,
                             QDateEdit, QComboBox, QTableWidget, QTableWidgetItem, QFileDialog,
                             QGroupBox, QStackedWidget,
                             QCheckBox, QSpinBox, QMessageBox, QRadioButton, QToolBar, QGridLayout, QDialog)
from banco.bancoSQlite import BancoSQLite, logger
import re
import datetime


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

    def init_companies_screen(self):
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

    def show_add_company_form(self):
        dialog = QWidget(self, Qt.WindowType.Dialog)
        dialog.setWindowTitle("Adicionar Nova Empresa")
        dialog.setMinimumWidth(400)
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

        layout.addLayout(form)  # Adiciona o formulário ao layout principal

        buttons = QHBoxLayout()

        def save_and_close():
            self.save_data()
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

        self.name_emp.returnPressed.connect(lambda: self.cnpj.setFocus())
        self.cnpj.returnPressed.connect(lambda: self.address_emp.setFocus())
        self.address_emp.returnPressed.connect(lambda: self.city_emp.setFocus())
        self.city_emp.returnPressed.connect(lambda: self.estado_emp.setFocus())
        self.phone_emp.returnPressed.connect(lambda: self.email.setFocus())
        self.email.returnPressed.connect(lambda: save.click())  # Pressionar Enter no email clica em "Salvar"

        dialog.show()

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
            print(f"Ocorreu um erro ao cadastrar: {e}")

    # ---------------------------------------------------------------------------------------------
    # Cadastro de Colaborador

    def init_employees_screen(self):
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
                print(f"Erro ao carregar empresas: {e}")
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
        try:
            # Define a ordem das colunas conforme a estrutura da tabela
            colunas = (
                "n_folha", "nome", "CPF", "data_admissao", "estado_civil", "telefone",
                "empresa", "departamento", "cargo", "salario", "jornada_trabalho",
                "status", "pis_pasep", "ctps", "banco", "contabancaria"
            )

            # Recupera os valores dos widgets do formulário
            n_folha = self.num_folha.text()
            nome = self.name_func.text()
            cpf = self.cpf.text()
            # Obtém a data no formato desejado (por exemplo, "yyyy-MM-dd")
            data_admissao = self.data_adimissap.date().toString("yyyy-MM-dd")
            estado_civil = self.estado_civil.currentText()
            telefone = self.telefone.text()

            # Para o campo empresa, o QComboBox exibe "código - nome".
            # Separa apenas o código (assumindo que seja numérico)
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

            # Define a estrutura da tabela em um dicionário
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

            # Cria a tabela "cadastro_funcionario", se necessário
            self.criar_tabela("cadastro_funcionario", estrutura_funcionario)
            self.cadastro_ponto()  # Cria a tabela ponto que vai usar FK da cadastro_funcionario

            # Cria o dicionário com os dados a serem inseridos
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

            # Valida os campos obrigatórios
            if not n_folha.strip():
                raise ValueError("O N° Folha é obrigatório e deve ser numérico.")
            if not nome.strip():
                raise ValueError("O nome é obrigatório.")
            if not cpf.strip():
                raise ValueError("O CPF é obrigatório.")
            if not empresa_codigo.strip():
                raise ValueError("O Código da empresa é obrigatório")

            # Insere ou atualiza o registro no banco de dados.
            # Neste exemplo, estamos usando o CPF como chave única.
            self.inserir_ou_atualizar_registro("cadastro_funcionario", dados, cpf)

            # Caso exista um método para atualizar a visualização dos funcionários
            if hasattr(self, "load_employees_data"):
                self.load_employees_data()

            # self.load_employees_data()
            logger.info("Funcionário cadastrado com sucesso!")
        except Exception as e:
            logger.error(f"Ocorreu um erro ao cadastrar o funcionário: {e}")
            # Exibe a mensagem de erro com um QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Erro")
            msg.setText(f"Ocorreu um erro ao cadastrar o funcionário: {e}")
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
        # Aba de novo funcionário
        dialog = QWidget(self, Qt.WindowType.Dialog)
        dialog.setWindowTitle("Adicionar Novo Funcionário")
        dialog.setMinimumWidth(500)
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
        self.telefone.returnPressed.connect(lambda: self.email_func.setFocus())  # pula para a aba "Dados Profissionais"

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

        dialog.show()

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

            # Tab de Exportação
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

            export_date_from = QDateEdit()
            export_date_from.setDate(QDate.currentDate().addDays(-30))
            export_date_from.setCalendarPopup(True)
            export_form.addRow("Data Inicial:", export_date_from)

            export_date_to = QDateEdit()
            export_date_to.setDate(QDate.currentDate())
            export_date_to.setCalendarPopup(True)
            export_form.addRow("Data Final:", export_date_to)

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
            export_btn.clicked.connect(self.export_timesheet)
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
            employee_filter = QComboBox()
            employee_filter.addItems(["Não desenvolvido 😎"])
            view_filters_layout.addWidget(employee_filter)

            view_filters_layout.addWidget(QLabel("Data:"))
            self.view_date = QDateEdit()
            view_date = self.view_date
            view_date.setDate(QDate.currentDate())
            view_date.setCalendarPopup(True)
            view_filters_layout.addWidget(view_date)

            # Criando o botão novamente e adicionando ao layout
            view_filter_btn = QPushButton("Filtrar")
            view_filters_layout.addWidget(view_filter_btn)
            # Conectar o botão de filtro à função de atualização
            view_filter_btn.clicked.connect(lambda: self.update_table_ponto(view_table, view_date))

            # Adicionando o grupo de filtros ao layout principal
            view_layout.addWidget(view_filters)

            # Tabela de ponto
            self.view_table = QTableWidget()
            view_table = self.view_table
            try:
                view_table.itemChanged.disconnect(self.auto_save)
            except (TypeError, RuntimeError):
                pass  # Apenas ignora se não estiver conectado

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
            self.editando_via_codigo = False

            def on_item_changed(item: QTableWidgetItem):
                if not item:
                    return

                # Se a edição foi feita via código, ignoramos
                if self.editando_via_codigo:
                    return

                # Verifica se já foi marcado como edição manual
                if not item.data(Qt.ItemDataRole.UserRole):
                    item.setData(Qt.ItemDataRole.UserRole, True)  # Marca como edição manual
                    return

                # Chama auto_save apenas se foi modificação manual
                self.auto_save(item)

            view_table.itemChanged.connect(on_item_changed)

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
            print(e)

    def auto_save(self, item):
        """
        Função chamada quando um item da tabela é alterado.
        Salva automaticamente no banco e fornece feedback ao usuário.
        """
        try:
            # Temporariamente desativa o sinal para evitar loop infinito
            self.view_table.blockSignals(True)

            row = item.row()
            col = item.column()

            def get_text_or_default(table, row, col, default=""):
                """ Retorna o texto da célula ou um valor padrão se a célula for None. """
                cell = table.item(row, col)
                return cell.text().strip() if cell is not None else default

            # Obtendo os valores das células
            cpf = get_text_or_default(self.view_table, row, 0)
            funcionario = get_text_or_default(self.view_table, row, 1)
            data = get_text_or_default(self.view_table, row, 2)

            # Verificação para evitar salvar dados inválidos
            if not cpf or not data:
                self.view_table.blockSignals(False)
                return

            # Mapeamento de colunas para os nomes dos campos no banco
            campos = {
                3: "entrada",
                4: "saida_almoco",
                5: "retorno_almoco",
                6: "saida"
            }

            if col in campos:
                campo = campos[col]
                valor_novo = item.text().strip()

                # Verificar formato do horário (deve ser HH:MM:SS ou estar vazio)
                if valor_novo and not re.match(r'^([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$', valor_novo):
                    QMessageBox.warning(self, "Formato Inválido", "O horário deve estar no formato HH:MM:SS.")
                    self.view_table.blockSignals(False)
                    return

                # Converter data para formato SQL (YYYY-MM-DD)
                if '/' in data:
                    dia, mes, ano = data.split('/')
                    data_sql = f"{ano}-{mes}-{dia}"
                else:
                    data_sql = data

                # Obter horário atual para log
                timestamp_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Registrar a alteração no banco
                sucesso = self.salvar_alteracao_ponto(cpf, data_sql, campo, valor_novo)

                if sucesso:
                    if valor_novo == "00:00:00":
                        item.setBackground(QColor("#ffcccc"))  # Vermelho claro
                    else:
                        item.setBackground(QColor("#ccffcc"))  # Verde claro
                else:
                    QMessageBox.critical(self, "Erro ao Salvar", "Não foi possível salvar a alteração no banco.")
                    self.update_table_ponto(self.view_table, self.view_date)  # Reverter alteração

        except Exception as e:
            logger.error("Erro ao processar alteração: %s", e)

        finally:
            # Reativar o sinal para evitar bloqueios permanentes
            self.view_table.blockSignals(False)

    def update_table_ponto(self, table, date_widget):
        """
        Atualiza a tabela de ponto com os dados filtrados pela data.
        """
        try:
            # Obter mês/ano selecionado
            date_filter = date_widget.date().toString("MM/yyyy")

            # Buscar dados de ponto
            registros = self.visualiza_ponto(date_filter)

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

                # Definir cores
                for i, item in enumerate(itens[3:]):  # Apenas colunas de horário
                    if item.text() == "00:00:00":
                        item.setBackground(QColor("#ffcccc"))  # Vermelho claro
                    else:
                        item.setBackground(QColor("#ccffcc"))  # Verde claro

                # Adicionar itens à tabela
                for col, item in enumerate(itens):
                    table.setItem(row, col, item)

            # Mostrar mensagem com quantidade de registros
            print(f"Tabela atualizada com {len(registros)} registros para {date_filter}")

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
            empresa = self.company_combo.currentText()
            data_inicial = self.date_from.date().toString("dd/MM/yyyy")
            data_final = self.date_to.date().toString("dd/MM/yyyy")
            formato_selecionado = self.format_combo.currentText()

            # Filtra registros por data
            registros_filtrados = self._filtrar_registros_por_data(registros, data_inicial, data_final)

            for p in registros_filtrados:
                print(p)
                if len(p["codigo"]) > 9 > len(p["valor"]):
                    # Importa para o banco os dados
                    self.inserir_atualizar_ponto(cpf=p["codigo"], timestamp=p["timestamp"],
                                                 tipo=p["tipo"], codigo_empresa=empresa)

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
        """
        Filtra os registros de ponto com base no intervalo de datas selecionado.
        """
        # Converte strings para objetos de data
        formato_data = "%d/%m/%Y"
        data_inicial = datetime.strptime(data_inicial, formato_data)
        data_final = datetime.strptime(data_final, formato_data)

        registros_filtrados = [
            p for p in registros if data_inicial <= datetime.strptime(p["data"], formato_data) <= data_final
        ]

        return registros_filtrados

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
                print(f"Erro de leitura do arquivo: {e}")
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

            # Se a linha tiver pelo menos 45 caracteres, extrai o código; caso contrário, pega o que houver a partir do índice 34
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
            print(f"Erro ao fazer parsing da linha: {e}")
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
            print(f"Erro ao processar arquivo Excel: {e}")
            return []

    def _salvar_registros(self, registros, empresa, formato):
        """
        Salva os registros no banco de dados ou gera arquivo
        """
        try:
            # Lógica de salvamento no banco ou geração de arquivo
            if not registros:
                raise ValueError("Nenhum registro para salvar")

            # Exemplo de salvamento (adapte conforme sua necessidade)
            # self._salvar_no_banco_de_dados(registros

            # Ou exportar para um arquivo conforme o formato
            if formato == 'CSV':
                self._exportar_csv(registros, empresa)
            elif formato == 'TXT':
                self._exportar_txt(registros, empresa)

        except Exception as e:
            print(f"Erro ao salvar registros: {e}")
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
            raise

    # ------------------------------------ Relatórios --------------------------------------------------
    def init_reports_screen(self):
        reports_widget = QWidget()
        layout = QVBoxLayout(reports_widget)

        # Título
        title = QLabel("Relatórios")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #343a40; margin-bottom: 20px;")
        layout.addWidget(title)

        # Tabs para diferentes relatórios
        tabs = QTabWidget()

        # Tab de Horas Trabalhadas
        hours_tab = QWidget()
        hours_layout = QVBoxLayout(hours_tab)

        hours_filter = QGroupBox("Filtros")
        hours_filter_layout = QFormLayout(hours_filter)

        hours_company = QComboBox()
        hours_company.addItems(
            ["Não desenvolvido 😎"])
        hours_filter_layout.addRow("Empresa:", hours_company)

        hours_dept = QComboBox()
        hours_dept.addItems(["Não desenvolvido 😎"])
        hours_filter_layout.addRow("Departamento:", hours_dept)

        hours_date_from = QDateEdit()
        hours_date_from.setDate(QDate.currentDate().addDays(-30))
        hours_date_from.setCalendarPopup(True)
        hours_filter_layout.addRow("Data Inicial:", hours_date_from)

        hours_date_to = QDateEdit()
        hours_date_to.setDate(QDate.currentDate())
        hours_date_to.setCalendarPopup(True)
        hours_filter_layout.addRow("Data Final:", hours_date_to)

        hours_generate = QPushButton("Gerar Relatório")
        hours_filter_layout.addRow("", hours_generate)

        hours_layout.addWidget(hours_filter)

        hours_table = QTableWidget()
        hours_table.setColumnCount(5)
        hours_table.setHorizontalHeaderLabels(
            ["Funcionário", "Empresa", "Total Horas", "Horas Extras", "Horas Faltantes"])

        # Dados de exemplo
        sample_hours = [
            ("Não desenvolvido 😎", "Teste tupla 01", "160:00", "5:30", "0:00"),
            ("Não desenvolvido 😎", "Teste tupla 02", "158:45", "0:00", "1:15"),
        ]

        hours_table.setRowCount(len(sample_hours))

        for row, (employee, company, total, extra, missing) in enumerate(sample_hours):
            hours_table.setItem(row, 0, QTableWidgetItem(employee))
            hours_table.setItem(row, 1, QTableWidgetItem(company))
            hours_table.setItem(row, 2, QTableWidgetItem(total))

            extra_item = QTableWidgetItem(extra)
            if extra != "0:00":
                extra_item.setForeground(QColor("#28a745"))
            hours_table.setItem(row, 3, extra_item)

            missing_item = QTableWidgetItem(missing)
            if missing != "0:00":
                missing_item.setForeground(QColor("#dc3545"))
            hours_table.setItem(row, 4, missing_item)

        hours_layout.addWidget(hours_table)

        export_buttons = QHBoxLayout()
        export_csv = QPushButton("Exportar CSV")
        export_csv.setStyleSheet("background-color: #6c757d;")

        export_txt = QPushButton("Exportar TXT")
        export_txt.setStyleSheet("background-color: #6c757d;")

        export_pdf = QPushButton("Exportar PDF")
        export_pdf.setStyleSheet("background-color: #6c757d;")

        export_buttons.addWidget(export_csv)
        export_buttons.addWidget(export_txt)
        export_buttons.addWidget(export_pdf)
        export_buttons.addStretch()

        hours_layout.addLayout(export_buttons)

        # Tab de Faltas e Atrasos
        absences_tab = QWidget()
        absences_layout = QVBoxLayout(absences_tab)

        absences_filter = QGroupBox("Filtros")
        absences_filter_layout = QFormLayout(absences_filter)

        absences_company = QComboBox()
        absences_company.addItems(
            ["Não Desenvolvido 😎"])
        absences_filter_layout.addRow("Empresa:", absences_company)

        absences_type = QComboBox()
        absences_type.addItems(["Todos os tipos", "Faltas", "Atrasos", "Saídas antecipadas"])
        absences_filter_layout.addRow("Tipo:", absences_type)

        absences_date_from = QDateEdit()
        absences_date_from.setDate(QDate.currentDate().addDays(-30))
        absences_date_from.setCalendarPopup(True)
        absences_filter_layout.addRow("Data Inicial:", absences_date_from)

        absences_date_to = QDateEdit()
        absences_date_to.setDate(QDate.currentDate())
        absences_date_to.setCalendarPopup(True)
        absences_filter_layout.addRow("Data Final:", absences_date_to)

        absences_generate = QPushButton("Gerar Relatório")
        absences_filter_layout.addRow("", absences_generate)

        absences_layout.addWidget(absences_filter)

        absences_table = QTableWidget()
        absences_table.setColumnCount(5)
        absences_table.setHorizontalHeaderLabels(["Funcionário", "Empresa", "Data", "Tipo", "Observação"])

        # Dados de exemplo
        sample_absences = [
            ("Não desenvolvido", "Teste 01", "15/02/2025", "Falta", "Atestado médico")
        ]

        absences_table.setRowCount(len(sample_absences))

        for row, (employee, company, date, absence_type, note) in enumerate(sample_absences):
            absences_table.setItem(row, 0, QTableWidgetItem(employee))
            absences_table.setItem(row, 1, QTableWidgetItem(company))
            absences_table.setItem(row, 2, QTableWidgetItem(date))

            type_item = QTableWidgetItem(absence_type)
            if absence_type == "Falta":
                type_item.setForeground(QColor("#dc3545"))
            elif absence_type == "Atraso":
                type_item.setForeground(QColor("#fd7e14"))
            else:
                type_item.setForeground(QColor("#6c757d"))

            absences_table.setItem(row, 3, type_item)
            absences_table.setItem(row, 4, QTableWidgetItem(note))

        absences_layout.addWidget(absences_table)

        absences_export = QHBoxLayout()
        absences_csv = QPushButton("Exportar CSV")
        absences_csv.setStyleSheet("background-color: #6c757d;")

        absences_txt = QPushButton("Exportar TXT")
        absences_txt.setStyleSheet("background-color: #6c757d;")

        absences_pdf = QPushButton("Exportar PDF")
        absences_pdf.setStyleSheet("background-color: #6c757d;")

        absences_export.addWidget(absences_csv)
        absences_export.addWidget(absences_txt)
        absences_export.addWidget(absences_pdf)
        absences_export.addStretch()

        absences_layout.addLayout(absences_export)

        # Tab de Relatório de Funcionários
        employees_tab = QWidget()
        employees_layout = QVBoxLayout(employees_tab)

        employees_filter = QGroupBox("Filtros")
        employees_filter_layout = QFormLayout(employees_filter)

        employees_report_company = QComboBox()
        employees_report_company.addItems(
            ["Não desenvolvido"])
        employees_filter_layout.addRow("Empresa:", employees_report_company)

        employees_report_dept = QComboBox()
        employees_report_dept.addItems(["Não Desenvolvido"])
        employees_filter_layout.addRow("Departamento:", employees_report_dept)

        employees_report_status = QComboBox()
        employees_report_status.addItems(["Todos", "Ativo", "Inativo", "Férias", "Afastado"])
        employees_filter_layout.addRow("Status:", employees_report_status)

        employees_report_generate = QPushButton("Gerar Relatório")
        employees_filter_layout.addRow("", employees_report_generate)

        employees_layout.addWidget(employees_filter)

        employees_report_table = QTableWidget()
        employees_report_table.setColumnCount(7)
        employees_report_table.setHorizontalHeaderLabels(
            ["Nome", "Empresa", "Departamento", "Cargo", "Data Admissão", "Status", "Jornada"])

        # Dados de exemplo
        sample_employees_report = [
            ("teste 01", "teste 01", "TI", "Desenvolvedor", "15/01/2023", "Ativo", "40h/semana"),
            ("teste 01", "teste 01", "RH", "Analista de RH", "05/03/2022", "Ativo", "40h/semana"),
            ("teste 01", "teste 01.", "Financeiro", "Contador", "22/08/2021", "Férias", "40h/semana"),
            ("teste 01", "teste 01", "Marketing", "Gerente de Marketing", "10/05/2020", "Ativo",
             "40h/semana"),
            ("teste 01", "teste 01", "Operações", "Supervisor", "03/11/2022", "Afastado",
             "44h/semana")
        ]

        employees_report_table.setRowCount(len(sample_employees_report))

        for row, (name, company, dept, position, hire_date, status, workload) in enumerate(sample_employees_report):
            employees_report_table.setItem(row, 0, QTableWidgetItem(name))
            employees_report_table.setItem(row, 1, QTableWidgetItem(company))
            employees_report_table.setItem(row, 2, QTableWidgetItem(dept))
            employees_report_table.setItem(row, 3, QTableWidgetItem(position))
            employees_report_table.setItem(row, 4, QTableWidgetItem(hire_date))

            status_item = QTableWidgetItem(status)
            if status == "Ativo":
                status_item.setForeground(QColor("#28a745"))
            elif status == "Férias":
                status_item.setForeground(QColor("#fd7e14"))
            elif status == "Afastado":
                status_item.setForeground(QColor("#dc3545"))

            employees_report_table.setItem(row, 5, status_item)
            employees_report_table.setItem(row, 6, QTableWidgetItem(workload))

        employees_layout.addWidget(employees_report_table)

        employees_report_export = QHBoxLayout()
        employees_report_csv = QPushButton("Exportar CSV")
        employees_report_csv.setStyleSheet("background-color: #6c757d;")

        employees_report_txt = QPushButton("Exportar TXT")
        employees_report_txt.setStyleSheet("background-color: #6c757d;")

        employees_report_pdf = QPushButton("Exportar PDF")
        employees_report_pdf.setStyleSheet("background-color: #6c757d;")

        employees_report_export.addWidget(employees_report_csv)
        employees_report_export.addWidget(employees_report_txt)
        employees_report_export.addWidget(employees_report_pdf)
        employees_report_export.addStretch()

        employees_layout.addLayout(employees_report_export)

        # Adicionar as tabs
        tabs.addTab(hours_tab, "Horas Trabalhadas")
        tabs.addTab(absences_tab, "Faltas e Atrasos")
        tabs.addTab(employees_tab, "Funcionários")

        layout.addWidget(tabs)

        self.stack.addWidget(reports_widget)

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
        file_name, _ = QFileDialog.getSaveFileName(self, "Exportar Funcionários", "",
                                                   "Arquivos CSV (*.csv);;Arquivos de Texto (*.txt);;Arquivos Excel ("
                                                   "*.xlsx)")
        if file_name:
            QMessageBox.information(self, "Exportação de Funcionários",
                                    f"Funcionários exportados com sucesso para {file_name}")

    def export_companies(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Exportar Empresas", "",
                                                   "Arquivos CSV (*.csv);;Arquivos de Texto (*.txt);;Arquivos Excel ("
                                                   "*.xlsx)")
        if file_name:
            QMessageBox.information(self, "Exportação de Empresas", f"Empresas exportadas com sucesso para {file_name}")

    def import_timesheet(self):
        QMessageBox.information(self, "Importação de Ponto", "Iniciando importação de dados de ponto...")

    def export_timesheet(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Exportar Dados de Ponto", "",
                                                   "Arquivos CSV (*.csv);;Arquivos de Texto (*.txt);;Arquivos Excel ("
                                                   "*.xlsx)")
        if file_name:
            QMessageBox.information(self, "Exportação de Ponto",
                                    f"Dados de ponto exportados com sucesso para {file_name}")

    def save_settings(self):
        QMessageBox.information(self, "Configurações", "Configurações salvas com sucesso!")

    # Função principal para iniciar a aplicação


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
