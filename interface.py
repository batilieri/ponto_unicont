import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QLineEdit, QFormLayout,
                             QDateEdit, QComboBox, QTableWidget, QTableWidgetItem, QFileDialog,
                             QGroupBox, QScrollArea, QSplitter, QFrame, QStackedWidget,
                             QCheckBox, QSpinBox, QMessageBox, QRadioButton, QToolBar)
from PyQt6.QtCore import Qt, QDate, QSize, QTimer
from PyQt6.QtGui import QIcon, QPixmap, QColor, QFont, QPalette, QAction

from banco.bancoSQlite import BancoSQLite


class MainWindow(QMainWindow, BancoSQLite):
    def __init__(self):
        super().__init__()

        # Configurações da janela principal
        self.setWindowTitle("HRPulse - Sistema de Gestão de RH")
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
                border-radius: 4px;
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
        title = QLabel("Bem-vindo ao HRPulse")
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
        footer = QLabel("© 2025 HRPulse - Todos os direitos reservados")
        footer.setStyleSheet("color: #6c757d; margin-top: 20px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(footer)

        self.stack.addWidget(home_widget)

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
        self.companies_table.setColumnCount(5)
        self.companies_table.setHorizontalHeaderLabels(["ID", "Nome", "CNPJ", "Endereço", "Ações"])
        self.companies_table.horizontalHeader().setStretchLastSection(True)
        self.companies_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.companies_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Dados de exemplo
        sample_companies = [
            (1, "TechSolutions LTDA", "12.345.678/0001-90", "Rua Principal, 123 - São Paulo, SP"),
            (2, "Global Comércio S.A.", "98.765.432/0001-10", "Av. Brasil, 500 - Rio de Janeiro, RJ"),
            (3, "Indústria Nacional LTDA", "45.678.901/0001-23", "Rua Industrial, 789 - Belo Horizonte, MG")
        ]

        self.companies_table.setRowCount(len(sample_companies))

        for row, (id, name, cnpj, address) in enumerate(sample_companies):
            self.companies_table.setItem(row, 0, QTableWidgetItem(str(id)))
            self.companies_table.setItem(row, 1, QTableWidgetItem(name))
            self.companies_table.setItem(row, 2, QTableWidgetItem(cnpj))
            self.companies_table.setItem(row, 3, QTableWidgetItem(address))

            actions_cell = QWidget()
            actions_layout = QHBoxLayout(actions_cell)
            actions_layout.setContentsMargins(5, 0, 5, 0)

            edit_btn = QPushButton("Editar")
            edit_btn.setFixedWidth(70)
            edit_btn.setStyleSheet("padding: 4px;")

            delete_btn = QPushButton("Excluir")
            delete_btn.setFixedWidth(70)
            delete_btn.setStyleSheet("padding: 4px; background-color: #f72585;")

            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)

            self.companies_table.setCellWidget(row, 4, actions_cell)

        layout.addWidget(self.companies_table)

        self.stack.addWidget(companies_widget)

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
        company_filter.addItems(["Todas", "TechSolutions LTDA", "Global Comércio S.A.", "Indústria Nacional LTDA"])
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
            ["ID", "Nome", "Empresa", "Departamento", "Cargo", "Status", "Ações"])
        self.employees_table.horizontalHeader().setStretchLastSection(True)
        self.employees_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.employees_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Dados de exemplo
        sample_employees = [
            (1, "João Silva", "TechSolutions LTDA", "TI", "Desenvolvedor", "Ativo"),
            (2, "Maria Oliveira", "TechSolutions LTDA", "RH", "Analista de RH", "Ativo"),
            (3, "Pedro Santos", "Global Comércio S.A.", "Financeiro", "Contador", "Férias"),
            (4, "Ana Costa", "Global Comércio S.A.", "Marketing", "Gerente de Marketing", "Ativo"),
            (5, "Lucas Pereira", "Indústria Nacional LTDA", "Operações", "Supervisor", "Afastado")
        ]

        self.employees_table.setRowCount(len(sample_employees))

        for row, (id, name, company, dept, position, status) in enumerate(sample_employees):
            self.employees_table.setItem(row, 0, QTableWidgetItem(str(id)))
            self.employees_table.setItem(row, 1, QTableWidgetItem(name))
            self.employees_table.setItem(row, 2, QTableWidgetItem(company))
            self.employees_table.setItem(row, 3, QTableWidgetItem(dept))
            self.employees_table.setItem(row, 4, QTableWidgetItem(position))

            status_item = QTableWidgetItem(status)
            if status == "Ativo":
                status_item.setForeground(QColor("#28a745"))
            elif status == "Férias":
                status_item.setForeground(QColor("#fd7e14"))
            elif status == "Afastado":
                status_item.setForeground(QColor("#dc3545"))

            self.employees_table.setItem(row, 5, status_item)

            actions_cell = QWidget()
            actions_layout = QHBoxLayout(actions_cell)
            actions_layout.setContentsMargins(5, 0, 5, 0)

            edit_btn = QPushButton("Editar")
            edit_btn.setFixedWidth(70)
            edit_btn.setStyleSheet("padding: 4px;")

            delete_btn = QPushButton("Excluir")
            delete_btn.setFixedWidth(70)
            delete_btn.setStyleSheet("padding: 4px; background-color: #f72585;")

            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)

            self.employees_table.setCellWidget(row, 6, actions_cell)

        layout.addWidget(self.employees_table)

        self.stack.addWidget(employees_widget)

    def init_timesheet_screen(self):
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
        company_combo.addItems(
            ["Selecione uma empresa", "TechSolutions LTDA", "Global Comércio S.A.", "Indústria Nacional LTDA"])
        import_form.addRow("Empresa:", company_combo)

        date_from = QDateEdit()
        date_from.setDate(QDate.currentDate().addDays(-30))
        date_from.setCalendarPopup(True)
        import_form.addRow("Data Inicial:", date_from)

        date_to = QDateEdit()
        date_to.setDate(QDate.currentDate())
        date_to.setCalendarPopup(True)
        import_form.addRow("Data Final:", date_to)

        import_file_layout = QHBoxLayout()
        import_file_path = QLineEdit()
        import_file_path.setPlaceholderText("Selecione o arquivo...")
        import_file_path.setReadOnly(True)

        browse_btn = QPushButton("Procurar")
        browse_btn.clicked.connect(lambda: self.browse_file(import_file_path))

        import_file_layout.addWidget(import_file_path)
        import_file_layout.addWidget(browse_btn)

        import_form.addRow("Arquivo:", import_file_layout)

        format_combo = QComboBox()
        format_combo.addItems(["CSV", "TXT", "XLS", "XLSX"])
        import_form.addRow("Formato:", format_combo)

        import_btn = QPushButton("Importar Dados")
        import_btn.clicked.connect(self.import_timesheet)
        import_form.addRow("", import_btn)

        import_layout.addWidget(import_group)
        import_layout.addStretch()

        # Tab de Exportação
        export_tab = QWidget()
        export_layout = QVBoxLayout(export_tab)

        export_group = QGroupBox("Exportar Dados de Ponto")
        export_form = QFormLayout(export_group)

        export_company_combo = QComboBox()
        export_company_combo.addItems(
            ["Todas as empresas", "TechSolutions LTDA", "Global Comércio S.A.", "Indústria Nacional LTDA"])
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

        # Tab de Visualização
        view_tab = QWidget()
        view_layout = QVBoxLayout(view_tab)

        view_filters = QGroupBox("Filtros")
        view_filters_layout = QHBoxLayout(view_filters)

        view_filters_layout.addWidget(QLabel("Funcionário:"))
        employee_filter = QComboBox()
        employee_filter.addItems(
            ["Todos", "João Silva", "Maria Oliveira", "Pedro Santos", "Ana Costa", "Lucas Pereira"])
        view_filters_layout.addWidget(employee_filter)

        view_filters_layout.addWidget(QLabel("Data:"))
        view_date = QDateEdit()
        view_date.setDate(QDate.currentDate())
        view_date.setCalendarPopup(True)
        view_filters_layout.addWidget(view_date)

        view_filter_btn = QPushButton("Filtrar")
        view_filters_layout.addWidget(view_filter_btn)

        view_layout.addWidget(view_filters)

        # Tabela de ponto
        view_table = QTableWidget()
        view_table.setColumnCount(6)
        view_table.setHorizontalHeaderLabels(
            ["Funcionário", "Data", "Entrada", "Saída Almoço", "Retorno Almoço", "Saída"])

        # Dados de exemplo
        sample_timesheet = [
            ("João Silva", "24/02/2025", "08:00", "12:00", "13:00", "17:00"),
            ("Maria Oliveira", "24/02/2025", "09:00", "12:30", "13:30", "18:00"),
            ("Pedro Santos", "24/02/2025", "08:30", "12:15", "13:15", "17:30"),
            ("Ana Costa", "24/02/2025", "09:30", "13:00", "14:00", "18:30"),
            ("Lucas Pereira", "24/02/2025", "08:15", "12:00", "13:00", "17:15")
        ]

        view_table.setRowCount(len(sample_timesheet))

        for row, (employee, date, entry, lunch_out, lunch_in, exit_time) in enumerate(sample_timesheet):
            view_table.setItem(row, 0, QTableWidgetItem(employee))
            view_table.setItem(row, 1, QTableWidgetItem(date))
            view_table.setItem(row, 2, QTableWidgetItem(entry))
            view_table.setItem(row, 3, QTableWidgetItem(lunch_out))
            view_table.setItem(row, 4, QTableWidgetItem(lunch_in))
            view_table.setItem(row, 5, QTableWidgetItem(exit_time))

        view_layout.addWidget(view_table)

        # Adicionar as tabs
        tabs.addTab(import_tab, "Importação")
        tabs.addTab(export_tab, "Exportação")
        tabs.addTab(view_tab, "Visualização")

        layout.addWidget(tabs)

        self.stack.addWidget(timesheet_widget)

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
            ["Todas as empresas", "TechSolutions LTDA", "Global Comércio S.A.", "Indústria Nacional LTDA"])
        hours_filter_layout.addRow("Empresa:", hours_company)

        hours_dept = QComboBox()
        hours_dept.addItems(["Todos os departamentos", "TI", "RH", "Financeiro", "Marketing", "Operações"])
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
            ("João Silva", "TechSolutions LTDA", "160:00", "5:30", "0:00"),
            ("Maria Oliveira", "TechSolutions LTDA", "158:45", "0:00", "1:15"),
            ("Pedro Santos", "Global Comércio S.A.", "162:30", "2:30", "0:00"),
            ("Ana Costa", "Global Comércio S.A.", "165:00", "5:00", "0:00"),
            ("Lucas Pereira", "Indústria Nacional LTDA", "120:00", "0:00", "40:00")
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
            ["Todas as empresas", "TechSolutions LTDA", "Global Comércio S.A.", "Indústria Nacional LTDA"])
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
            ("Lucas Pereira", "Indústria Nacional LTDA", "15/02/2025", "Falta", "Atestado médico"),
            ("Maria Oliveira", "TechSolutions LTDA", "18/02/2025", "Atraso", "Trânsito (30 min)"),
            ("Pedro Santos", "Global Comércio S.A.", "10/02/2025", "Saída antecipada", "Consulta médica (1 hora)"),
            ("Ana Costa", "Global Comércio S.A.", "22/02/2025", "Atraso", "Transporte público (15 min)"),
            ("Lucas Pereira", "Indústria Nacional LTDA", "23/02/2025", "Falta", "Não justificada")
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
            ["Todas as empresas", "TechSolutions LTDA", "Global Comércio S.A.", "Indústria Nacional LTDA"])
        employees_filter_layout.addRow("Empresa:", employees_report_company)

        employees_report_dept = QComboBox()
        employees_report_dept.addItems(["Todos os departamentos", "TI", "RH", "Financeiro", "Marketing", "Operações"])
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
            ("João Silva", "TechSolutions LTDA", "TI", "Desenvolvedor", "15/01/2023", "Ativo", "40h/semana"),
            ("Maria Oliveira", "TechSolutions LTDA", "RH", "Analista de RH", "05/03/2022", "Ativo", "40h/semana"),
            ("Pedro Santos", "Global Comércio S.A.", "Financeiro", "Contador", "22/08/2021", "Férias", "40h/semana"),
            ("Ana Costa", "Global Comércio S.A.", "Marketing", "Gerente de Marketing", "10/05/2020", "Ativo",
             "40h/semana"),
            ("Lucas Pereira", "Indústria Nacional LTDA", "Operações", "Supervisor", "03/11/2022", "Afastado",
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

    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit,
        QComboBox, QHBoxLayout, QPushButton
    )
    from PyQt6.QtCore import Qt

    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit,
        QComboBox, QHBoxLayout, QPushButton
    )
    from PyQt6.QtCore import Qt

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
            coluna = ("nome", "cnpj", "endereco", "cidade", "estado", "telefone", "email")  # Colunas na ordem correta

            nome = self.name_emp.text()
            cnpj = self.cnpj.text()
            endereco = self.address_emp.text()
            cidade = self.city_emp.text()
            estado = self.estado_emp.currentText()
            telefone = self.phone_emp.text()
            email = self.email.text()

            # Criar a tabela com os campos na ordem correta
            campos = {coluna[i]: "TEXT" for i in range(len(coluna))}
            self.criar_tabela("cadastro_empresa", campos)

            # Criar dicionário de dados
            dados = {coluna[i]: valor or "NULL" for i, valor in
                     enumerate([nome, cnpj, endereco, cidade, estado, telefone, email])}

            # Verificação extra para evitar erro ao inserir no banco
            if not cnpj.strip():
                raise ValueError("O CNPJ não pode estar vazio.")

            print(dados)  # Depuração

            # Inserir ou atualizar os dados no banco de dados
            self.inserir_ou_atualizar_registro("cadastro_empresa", dados, cnpj)

        except Exception as e:
            print(f"Ocorreu um erro ao cadastrar: {e}")

    def show_add_employee_form(self):
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

        name = QLineEdit()
        name.setPlaceholderText("Nome completo")
        personal_layout.addRow("Nome:", name)

        cpf = QLineEdit()
        cpf.setPlaceholderText("000.000.000-00")
        personal_layout.addRow("CPF:", cpf)

        birth_date = QDateEdit()
        birth_date.setCalendarPopup(True)
        birth_date.setDate(QDate(1990, 1, 1))
        personal_layout.addRow("Data de Nascimento:", birth_date)

        gender = QComboBox()
        gender.addItems(["Selecione", "Masculino", "Feminino", "Outro", "Prefiro não informar"])
        personal_layout.addRow("Gênero:", gender)

        marital_status = QComboBox()
        marital_status.addItems(["Selecione", "Solteiro(a)", "Casado(a)", "Divorciado(a)", "Viúvo(a)", "União Estável"])
        personal_layout.addRow("Estado Civil:", marital_status)

        phone = QLineEdit()
        phone.setPlaceholderText("(00) 00000-0000")
        personal_layout.addRow("Telefone:", phone)

        email = QLineEdit()
        email.setPlaceholderText("email@exemplo.com")
        personal_layout.addRow("Email:", email)

        address = QLineEdit()
        address.setPlaceholderText("Endereço completo")
        personal_layout.addRow("Endereço:", address)

        # Tab de Dados Profissionais
        professional_tab = QWidget()
        professional_layout = QFormLayout(professional_tab)

        company = QComboBox()


        company.addItems(
            ["Selecione uma empresa", "TechSolutions LTDA", "Global Comércio S.A.", "Indústria Nacional LTDA"])
        professional_layout.addRow("Empresa:", company)

        department = QComboBox()
        department.addItems(["Selecione um departamento", "TI", "RH", "Financeiro", "Marketing", "Operações"])
        professional_layout.addRow("Departamento:", department)

        position = QLineEdit()
        position.setPlaceholderText("Cargo do funcionário")
        professional_layout.addRow("Cargo:", position)

        hire_date = QDateEdit()
        hire_date.setCalendarPopup(True)
        hire_date.setDate(QDate.currentDate())
        professional_layout.addRow("Data de Admissão:", hire_date)

        salary = QLineEdit()
        salary.setPlaceholderText("0,00")
        professional_layout.addRow("Salário:", salary)

        workload = QComboBox()
        workload.addItems(["40h/semana", "44h/semana", "30h/semana", "20h/semana", "Outra"])
        professional_layout.addRow("Jornada de Trabalho:", workload)

        status = QComboBox()
        status.addItems(["Ativo", "Inativo", "Férias", "Afastado"])
        professional_layout.addRow("Status:", status)

        # Tab de Documentos
        documents_tab = QWidget()
        documents_layout = QFormLayout(documents_tab)

        rg = QLineEdit()
        rg.setPlaceholderText("00.000.000-0")
        documents_layout.addRow("RG:", rg)

        pis = QLineEdit()
        pis.setPlaceholderText("000.00000.00-0")
        documents_layout.addRow("PIS/PASEP:", pis)

        ctps = QLineEdit()
        ctps.setPlaceholderText("0000000 série 000-0")
        documents_layout.addRow("CTPS:", ctps)

        bank = QComboBox()
        bank.addItems(
            ["Selecione", "Banco do Brasil", "Caixa Econômica", "Itaú", "Bradesco", "Santander", "Nubank", "Inter",
             "Outro"])
        documents_layout.addRow("Banco:", bank)

        account = QLineEdit()
        account.setPlaceholderText("Agência e conta")
        documents_layout.addRow("Conta Bancária:", account)

        # Adicionar tabs ao TabWidget
        tabs.addTab(personal_tab, "Dados Pessoais")
        tabs.addTab(professional_tab, "Dados Profissionais")
        tabs.addTab(documents_tab, "Documentos")

        layout.addWidget(tabs)

        buttons = QHBoxLayout()
        save = QPushButton("Salvar")
        save.clicked.connect(dialog.close)

        cancel = QPushButton("Cancelar")
        cancel.setStyleSheet("background-color: #6c757d;")
        cancel.clicked.connect(dialog.close)

        buttons.addWidget(save)
        buttons.addWidget(cancel)

        layout.addLayout(buttons)

        dialog.setLayout(layout)
        dialog.show()

    def browse_file(self, line_edit):
        file_name, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo", "",
                                                   "Todos os Arquivos (*);;Arquivos CSV (*.csv);;Arquivos de Texto (*.txt);;Arquivos Excel (*.xls *.xlsx)")
        if file_name:
            line_edit.setText(file_name)

        # Métodos para importação e exportação

    def import_employees(self):
        QMessageBox.information(self, "Importação de Funcionários", "Iniciando importação de funcionários...")

    def export_employees(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Exportar Funcionários", "",
                                                   "Arquivos CSV (*.csv);;Arquivos de Texto (*.txt);;Arquivos Excel (*.xlsx)")
        if file_name:
            QMessageBox.information(self, "Exportação de Funcionários",
                                    f"Funcionários exportados com sucesso para {file_name}")

    def export_companies(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Exportar Empresas", "",
                                                   "Arquivos CSV (*.csv);;Arquivos de Texto (*.txt);;Arquivos Excel (*.xlsx)")
        if file_name:
            QMessageBox.information(self, "Exportação de Empresas", f"Empresas exportadas com sucesso para {file_name}")

    def import_timesheet(self):
        QMessageBox.information(self, "Importação de Ponto", "Iniciando importação de dados de ponto...")

    def export_timesheet(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Exportar Dados de Ponto", "",
                                                   "Arquivos CSV (*.csv);;Arquivos de Texto (*.txt);;Arquivos Excel (*.xlsx)")
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
