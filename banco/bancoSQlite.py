import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import colorlog
import logging
import datetime
import contextlib
from datetime import datetime
from typing import Dict, Any
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox


def setup_logger() -> logging.Logger:
    """Configura e retorna um logger colorido."""
    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
    )

    logger = colorlog.getLogger('SQLiteDB')
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Remove handlers duplicados
    for handler in logger.handlers[:-1]:
        logger.removeHandler(handler)

    return logger


logger = setup_logger()


class BancoSQLite:
    """Classe para gerenciar operações com banco de dados SQLite."""

    def __init__(self):
        super().__init__()
        """Inicializa a conexão com o banco de dados."""
        try:
            self.db_path = Path(__file__).parent.parent / "banco" / "ponto_uniconte.db"
            os.makedirs(self.db_path.parent, exist_ok=True)

            self.conn = sqlite3.connect(str(self.db_path))
            self.cursor = self.conn.cursor()
            logger.info(f"Banco de dados inicializado em: {self.db_path}")
            self.criar_tabelas_log_ponto()
            self.cadastro_ponto_alteracao()

        except Exception as e:
            logger.error(f"Erro na inicialização do banco: {str(e)}")
            raise

    @contextlib.contextmanager
    def transaction(self):
        """Context manager para gerenciar transações."""
        try:
            yield
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def criar_tabela(self, nome_tabela: str, campos: Dict[str, str]) -> bool:
        """
        Cria uma nova tabela com os campos especificados.

        Args:
            nome_tabela: Nome da tabela a ser criada
            campos: Dicionário com nome do campo e seu tipo
                   Exemplo: {'nome': 'TEXT', 'idade': 'INTEGER'}

        Returns:
            bool: True se a tabela foi criada com sucesso, False caso contrário
        """
        try:
            campos_sql = ', '.join([f"{nome} {tipo}" for nome, tipo in campos.items()])

            query = f"""
                CREATE TABLE IF NOT EXISTS {nome_tabela} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {campos_sql},
                    data_cadastro TEXT,
                    ultima_modificacao TEXT
                )
            """

            with self.transaction():
                self.cursor.execute(query)
                logger.info(f"Tabela '{nome_tabela}' criada com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro ao criar tabela '{nome_tabela}': {str(e)}")
            return False

    def _converter_valor(self, valor: Any) -> Any:
        """Converte valores para formato adequado ao SQLite."""
        if isinstance(valor, bytes):
            return valor.decode('utf-8', 'ignore').strip()
        return valor

    def inserir_ou_atualizar_registro(self, nome_tabela: str, dados: Dict[str, Any], campo_chave: str) -> bool:
        """
        Insere um novo registro na tabela ou atualiza se já existir.

        Args:
            nome_tabela: Nome da tabela
            dados: Dicionário com os dados a serem inseridos/atualizados
                  Exemplo: {'nome': 'João', 'idade': 30}
            campo_chave: Nome do campo que serve como chave única

        Returns:
            bool: True se a operação foi bem sucedida, False caso contrário
        """
        try:
            timestamp = datetime.now().isoformat()

            # Verifica se o registro já existe
            valor_chave = dados.get(campo_chave)
            query_verificacao = f"SELECT * FROM {nome_tabela} WHERE {campo_chave} = ?"

            with self.transaction():
                self.cursor.execute(query_verificacao, (self._converter_valor(valor_chave),))
                registro_existente = self.cursor.fetchone()

                if registro_existente:
                    # Prepara dados para atualização
                    dados['ultima_modificacao'] = timestamp

                    # Monta a query de UPDATE
                    set_clause = ', '.join([f"{campo} = ?" for campo in dados.keys()])
                    query = f"UPDATE {nome_tabela} SET {set_clause} WHERE {campo_chave} = ?"

                    # Prepara valores para UPDATE
                    valores = [self._converter_valor(v) for v in dados.values()]
                    valores.append(self._converter_valor(valor_chave))  # Adiciona o valor da chave

                    self.cursor.execute(query, valores)
                    logger.info(f"Registro atualizado com sucesso em '{nome_tabela}'")
                else:
                    # Insere novo registro
                    dados.update({
                        'data_cadastro': timestamp,
                        'ultima_modificacao': timestamp
                    })

                    campos = ', '.join(dados.keys())
                    placeholders = ', '.join(['?' for _ in dados])
                    query = f"INSERT INTO {nome_tabela} ({campos}) VALUES ({placeholders})"

                    valores = [self._converter_valor(v) for v in dados.values()]

                    self.cursor.execute(query, valores)
                    logger.info(f"Registro inserido com sucesso em '{nome_tabela}'")

                return True

        except Exception as e:
            logger.error(f"Erro ao inserir/atualizar registro em '{nome_tabela}': {str(e)}")
            return False

    def atualizar_registro(self, nome_tabela: str, id_registro: int, dados: Dict[str, Any]) -> bool:
        """
        Atualiza um registro existente.

        Args:
            nome_tabela: Nome da tabela
            id_registro: ID do registro a ser atualizado
            dados: Dicionário com os campos a serem atualizados

        Returns:
            bool: True se o registro foi atualizado com sucesso, False caso contrário
        """
        try:
            dados['ultima_modificacao'] = datetime.now().isoformat()  # Correção aqui
            set_clause = ', '.join([f"{campo} = ?" for campo in dados.keys()])
            query = f"UPDATE {nome_tabela} SET {set_clause} WHERE id = ?"

            valores = [self._converter_valor(v) for v in dados.values()]
            valores.append(id_registro)

            with self.transaction():
                self.cursor.execute(query, valores)
                if self.cursor.rowcount == 0:
                    logger.warning(f"Nenhum registro atualizado em '{nome_tabela}' para ID {id_registro}")
                    return False
                logger.info(f"Registro {id_registro} atualizado com sucesso em '{nome_tabela}'")
            return True

        except Exception as e:
            logger.error(f"Erro ao atualizar registro {id_registro} em '{nome_tabela}': {str(e)}")
            return False

    def consultar_registros(self, nome_tabela: str, filtros: Optional[Dict[str, Any]] = None) -> List[tuple]:
        """
        Consulta registros com filtros opcionais.

        Args:
            nome_tabela: Nome da tabela
            filtros: Dicionário com filtros (opcional)
                    Exemplo: {'nome': 'João', 'idade': 30}

        Returns:
            List[tuple]: Lista de registros encontrados
        """
        try:
            query = f"SELECT * FROM {nome_tabela}"
            valores = []

            if filtros:
                where_clause = ' AND '.join([f"{campo} = ?" for campo in filtros.keys()])
                query += f" WHERE {where_clause}"
                valores = [self._converter_valor(v) for v in filtros.values()]

            self.cursor.execute(query, valores)
            resultados = self.cursor.fetchall()
            logger.info(f"Consulta executada em '{nome_tabela}': {len(resultados)} registros encontrados")
            return resultados

        except Exception as e:
            logger.error(f"Erro ao consultar registros em '{nome_tabela}': {str(e)}")
            return []

    def busca_dados_tabelas(self) -> List[str]:
        """
        Lista todas as tabelas do banco.

        Returns:
            List[str]: Lista com nomes das tabelas
        """
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tabelas = [tabela[0] for tabela in self.cursor.fetchall()]
            logger.info(f"Listadas {len(tabelas)} tabelas")
            return tabelas

        except Exception as e:
            logger.error(f"Erro ao listar tabelas: {str(e)}")
            return []

    def estrutura_tabela(self, nome_tabela: str) -> List[tuple]:
        """
        Retorna a estrutura de uma tabela específica.

        Args:
            nome_tabela: Nome da tabela

        Returns:
            List[tuple]: Lista com informações dos campos da tabela
        """
        try:
            self.cursor.execute(f"PRAGMA table_info({nome_tabela})")
            estrutura = self.cursor.fetchall()
            logger.info(f"Estrutura da tabela '{nome_tabela}' obtida com sucesso")
            return estrutura

        except Exception as e:
            logger.error(f"Erro ao obter estrutura da tabela '{nome_tabela}': {str(e)}")
            return []

    def excluir_registro(self, nome_tabela: str, registro_id: int) -> bool:
        """
        Exclui um registro da tabela especificada pelo ID.

        Args:
            nome_tabela (str): Nome da tabela do banco de dados.
            registro_id (int): ID do registro a ser excluído.

        Returns:
            bool: True se a exclusão foi realizada com sucesso, False caso contrário.
        """
        try:
            with self.transaction():
                query = f"DELETE FROM {nome_tabela} WHERE id = ?"
                self.cursor.execute(query, (registro_id,))
            logger.info(f"Registro com ID {registro_id} excluído com sucesso da tabela '{nome_tabela}'.")
            return True
        except Exception as e:
            logger.error(f"Erro ao excluir registro com ID {registro_id} da tabela '{nome_tabela}': {str(e)}")
            return False

    def cadastro_ponto(self):
        try:
            with self.transaction():
                query = """
                CREATE TABLE IF NOT EXISTS ponto (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cpf TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        tipo TEXT CHECK(tipo IN ('entrada', 'saida')),
                        codigo_empresa INTEGER NOT NULL,
                        FOREIGN KEY (codigo_empresa) REFERENCES cadastro_empresa(id),
                        FOREIGN KEY (cpf) REFERENCES cadastro_funcionario(cpf)
                    );

                    """
                self.cursor.execute(query)
            logger.info(f"Tabela ponto criada com sucesso!")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar a tabela ponto. {e}")
            return False

    def cadastro_ponto_alteracao(self):
        try:
            with self.transaction():
                query = """
                            CREATE TABLE IF NOT EXISTS ponto_alteracoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ponto_id INTEGER NOT NULL,
                campo_alterado TEXT NOT NULL,
                valor_antigo TEXT NOT NULL,
                valor_novo TEXT NOT NULL,
                data_alteracao TEXT NOT NULL,
                FOREIGN KEY (ponto_id) REFERENCES ponto(id)
            );

                    """
                self.cursor.execute(query)
            logger.info(f"Tabela ponto_alteracoes criada com sucesso!")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar a tabela ponto. {e}")
            return False

    def inserir_atualizar_ponto(self, cpf, timestamp, tipo, codigo_empresa):
        try:
            with self.transaction():
                # Verifica se já existe um registro para o mesmo CPF e timestamp
                query_verificar = """
                SELECT id FROM ponto WHERE cpf = ? AND timestamp = ?
                """
                self.cursor.execute(query_verificar, (cpf, timestamp))
                resultado = self.cursor.fetchone()

                if resultado:
                    # Atualizar o registro existente
                    query_update = """
                    UPDATE ponto 
                    SET tipo = ?, codigo_empresa = ?
                    WHERE id = ?
                    """
                    self.cursor.execute(query_update, (tipo, codigo_empresa, resultado[0]))
                    logger.info(f"Registro atualizado para CPF {cpf} em {timestamp}.")
                else:
                    # Inserir um novo registro
                    query_insert = """
                    INSERT INTO ponto (cpf, timestamp, tipo, codigo_empresa)
                    VALUES (?, ?, ?, ?)
                    """
                    self.cursor.execute(query_insert, (cpf, timestamp, tipo, codigo_empresa))
                    logger.info(f"Novo registro inserido para CPF {cpf} em {timestamp}.")

            return True
        except Exception as e:
            logger.error(f"Erro ao inserir/atualizar ponto. {e}")
            return False

    def fechar_conexao(self) -> None:
        """Fecha a conexão com o banco de dados."""
        try:
            self.conn.close()
            logger.info("Conexão com o banco de dados fechada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao fechar conexão com o banco: {str(e)}")

    from datetime import datetime, timedelta
    from collections import defaultdict

    def calcular_horas_extras_faltantes(self, cpf, data, jornada_diaria=8):
        try:
            with self.transaction():
                # Buscar registros do funcionário para a data especificada
                query = """
                SELECT timestamp, tipo FROM ponto 
                WHERE cpf = ? AND timestamp LIKE ?
                ORDER BY timestamp
                """
                self.cursor.execute(query, (cpf, f"{data}%"))
                registros = self.cursor.fetchall()

                if not registros:
                    logger.warning(f"Nenhum registro encontrado para CPF {cpf} em {data}.")
                    return None

                # Converter registros para datetime
                pontos = []
                for timestamp, tipo in registros:
                    pontos.append((datetime.fromisoformat(timestamp), tipo))

                # Calcular horas trabalhadas
                total_trabalhado = timedelta()
                entrada = None

                for horario, tipo in pontos:
                    if tipo == "entrada":
                        entrada = horario
                    elif tipo == "saida" and entrada:
                        total_trabalhado += (horario - entrada)
                        entrada = None  # Resetar para próxima entrada

                # Converter total para horas
                horas_trabalhadas = total_trabalhado.total_seconds() / 3600

                # Calcular horas extras ou faltantes
                if horas_trabalhadas > jornada_diaria:
                    horas_extras = horas_trabalhadas - jornada_diaria
                    horas_faltantes = 0
                else:
                    horas_extras = 0
                    horas_faltantes = jornada_diaria - horas_trabalhadas

                return {
                    "cpf": cpf,
                    "data": data,
                    "horas_trabalhadas": round(horas_trabalhadas, 2),
                    "horas_extras": round(horas_extras, 2),
                    "horas_faltantes": round(horas_faltantes, 2),
                }
        except Exception as e:
            logger.error(f"Erro ao calcular horas extras/faltantes. {e}")
            return None

    def visualiza_ponto(self, mes_ano):
        """
        Visualiza os registros de ponto de funcionários para um mês/ano específico.
        Considera:
          - Entrada da manhã: clique mais próximo das 08:00 (tipo 'entrada').
          - Saída da manhã: clique mais próximo das 12:00 (tipo 'saida'); se não houver, fica "00:00:00".
          - Entrada da tarde: clique mais próximo das 13:00 (tipo 'entrada').
          - Saída da tarde: clique mais próximo das 18:00 (tipo 'saida'); se não houver, fica "00:00:00".
        Formato esperado para mes_ano: 'MM/YYYY' (ex: '02/2025')
        """
        try:
            import datetime

            # Extrair mês e ano e formatar o padrão da data
            mes, ano = mes_ano.split('/')
            mes_formatado = mes.zfill(2)
            padrao = f'{ano}-{mes_formatado}-%'

            # Buscar registros brutos
            query = """
                SELECT 
                    p.id,
                    f.cpf,
                    f.nome,
                    substr(p.timestamp, 1, 10) as data_registro,
                    substr(p.timestamp, 12, 8) as horario,
                    p.tipo
                FROM ponto p
                JOIN cadastro_funcionario f ON p.cpf = f.CPF
                WHERE p.timestamp LIKE ?
                ORDER BY f.nome, p.timestamp
            """
            self.cursor.execute(query, (padrao,))
            registros_brutos = self.cursor.fetchall()

            if not registros_brutos:
                logger.warning(f"Nenhum registro de ponto encontrado para {mes_ano}.")
                return []

            # Agrupar registros por (CPF, nome, data)
            registros_por_pessoa_dia = {}
            for ponto_id, CPF, nome, data_registro, horario, tipo in registros_brutos:
                chave = (CPF, nome, data_registro)
                if chave not in registros_por_pessoa_dia:
                    registros_por_pessoa_dia[chave] = []
                registros_por_pessoa_dia[chave].append((horario, tipo, ponto_id))

            # Função auxiliar para converter string para objeto time
            def str_to_time(t_str):
                return datetime.datetime.strptime(t_str, "%H:%M:%S").time()

            # Função que seleciona o registro do tipo esperado cuja distância para o horário alvo seja mínima
            def seleciona_registro(registros, target_time, expected_type):
                candidatos = [r for r in registros if r[1] == expected_type]
                if not candidatos:
                    return "00:00:00"
                return min(
                    candidatos,
                    key=lambda r: abs(datetime.datetime.combine(datetime.date.today(), str_to_time(r[0])) -
                                      datetime.datetime.combine(datetime.date.today(), target_time))
                )[0]

            resultado = []
            for (CPF, nome, data_registro), registros in registros_por_pessoa_dia.items():
                # Separar registros em manhã e tarde com base no horário
                registros_manha = [r for r in registros if r[0] < '13:00:00']
                registros_tarde = [r for r in registros if r[0] >= '13:00:00']

                # Seleciona os cliques mais próximos dos horários de referência
                entrada_manha = seleciona_registro(registros_manha, datetime.time(8, 0, 0), 'entrada')
                saida_manha = seleciona_registro(registros_manha, datetime.time(12, 0, 0), 'saida')
                entrada_tarde = seleciona_registro(registros_tarde, datetime.time(13, 0, 0), 'entrada')
                saida_tarde = seleciona_registro(registros_tarde, datetime.time(18, 0, 0), 'saida')

                # Converter a data para o formato DD/MM/YYYY
                if '-' in data_registro:
                    ano_db, mes_db, dia_db = data_registro.split('-')
                    data_formatada = f"{dia_db}/{mes_db}/{ano_db}"
                else:
                    data_formatada = data_registro  # Caso a data já esteja formatada

                resultado.append((CPF, nome, data_formatada, entrada_manha, saida_manha, entrada_tarde, saida_tarde))

            # Ordenar o resultado por data e nome corretamente
            resultado.sort(key=lambda x: (
                datetime.datetime.strptime(x[2], '%d/%m/%Y'),  # Ordenação pela data correta
                x[1]  # Ordenação pelo nome
            ))

            print(f"Encontrados {len(resultado)} registros de ponto para {mes_ano}.")
            return resultado

        except Exception as e:
            logger.error(f"Erro ao visualizar ponto: {str(e)}")
            return []



    def salvar_alteracao_ponto(self, cpf, data, campo, valor_novo):
        """
        Salva a alteração registrando em uma tabela de log sem alterar o timestamp original.
        """
        try:
            # Converter data para o formato SQL, se necessário
            if '/' in data:
                dia, mes, ano = data.split('/')
                data_sql = f"{ano}-{mes}-{dia}"
            else:
                data_sql = data

            # Consultar o registro atual na tabela ponto
            query_atual = """
              SELECT id, timestamp FROM ponto
              WHERE cpf = ? AND date(substr(timestamp, 1, 10)) = ? AND tipo = ?
              """

            tipo = 'entrada' if campo in ['entrada', 'retorno_almoco'] else 'saida'
            self.cursor.execute(query_atual, (cpf, data_sql, tipo))
            resultado = self.cursor.fetchone()

            if not resultado:
                logger.warning(f"Registro não encontrado para CPF {cpf} na data {data}")
                return False

            ponto_id, timestamp_atual = resultado

            # Inserir a alteração na tabela de log
            query_log = """
              INSERT INTO ponto_alteracoes (ponto_id, campo_alterado, valor_antigo, valor_novo, data_alteracao)
              VALUES (?, ?, ?, ?, datetime('now'))
              """
            self.cursor.execute(query_log, (ponto_id, campo, timestamp_atual, valor_novo))
            self.conn.commit()

            logger.info(f"Alteração registrada com sucesso para CPF {cpf}, campo {campo}.")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar alteração de ponto: {str(e)}")
            self.conn.rollback()
            return False

    def criar_tabelas_log_ponto(self):

        # Criar tabela de log de alterações
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS log_alteracoes_ponto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_alteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cpf TEXT NOT NULL,
            funcionario TEXT NOT NULL,
            data TEXT NOT NULL,
            campo_alterado TEXT NOT NULL,
            valor_antigo TEXT,
            valor_novo TEXT,
            usuario TEXT
        )
        ''')
        self.conn.commit()

    def registrar_alteracao_ponto(self, cpf, funcionario, data, campo, valor_antigo, valor_novo, usuario="Sistema"):
        """
        Registra uma alteração feita na tabela de ponto.

        Args:
            cpf (str): CPF do funcionário
            funcionario (str): Nome do funcionário
            data (str): Data do registro (formato DD/MM/YYYY)
            campo (str): Nome do campo alterado
            valor_antigo (str): Valor antes da alteração
            valor_novo (str): Valor após a alteração
            usuario (str, opcional): Usuário que fez a alteração
        """
        try:
            query = '''
            INSERT INTO log_alteracoes_ponto 
            (cpf, funcionario, data, campo_alterado, valor_antigo, valor_novo, usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            self.cursor.execute(query, (cpf, funcionario, data, campo, valor_antigo, valor_novo, usuario))
            self.conn.commit()
            logger.info(f"Alteração registrada: {funcionario}, {data}, {campo}: {valor_antigo} -> {valor_novo}")
            return True
        except Exception as e:
            logger.error(f"Erro ao registrar alteração: {str(e)}")
            return False



    def visualizar_historico_alteracoes(self, cpf=None, data_inicio=None, data_fim=None):
        """
        Retorna o histórico de alterações de ponto.

        Args:
            cpf (str, opcional): Filtrar por CPF
            data_inicio (str, opcional): Data inicial (formato YYYY-MM-DD)
            data_fim (str, opcional): Data final (formato YYYY-MM-DD)

        Returns:
            list: Lista de alterações encontradas
        """
        try:
            query = "SELECT * FROM log_alteracoes_ponto WHERE 1=1"
            params = []

            if cpf:
                query += " AND cpf = ?"
                params.append(cpf)

            if data_inicio:
                query += " AND data_alteracao >= ?"
                params.append(f"{data_inicio} 00:00:00")

            if data_fim:
                query += " AND data_alteracao <= ?"
                params.append(f"{data_fim} 23:59:59")

            query += " ORDER BY data_alteracao DESC"

            self.cursor.execute(query, params)
            resultados = self.cursor.fetchall()

            return resultados

        except Exception as e:
            logger.error(f"Erro ao buscar histórico de alterações: {str(e)}")
            return []
