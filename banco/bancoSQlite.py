import sqlite3
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import colorlog
import logging
import contextlib


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
            dados['ultima_modificacao'] = datetime.now().isoformat()
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
        Método para visualizar os registros de ponto de funcionários em um mês e ano específicos.
        Formato esperado para mes_ano: 'MM/YYYY' (ex: '02/2025')
        """
        try:
            # Extrair mês e ano da string no formato MM/YYYY
            mes, ano = mes_ano.split('/')

            # Formatar mês com dois dígitos
            mes_formatado = mes.zfill(2)

            # Padrão para busca LIKE
            padrao = f'{ano}-{mes_formatado}-%'

            # Buscar registros do funcionário para o mês e ano especificados
            query = """
                SELECT 
                    f.nome, 
                    strftime('%d/%m/%Y', substr(p.timestamp, 1, 10)) AS data, 
                    MIN(CASE WHEN p.tipo = 'entrada' THEN substr(p.timestamp, 12, 8) END) AS entrada_manha,
                    MAX(CASE WHEN p.tipo = 'saida' AND substr(p.timestamp, 12, 8) < '12:30' THEN substr(p.timestamp, 12, 8) END) AS saida_manha,
                    MIN(CASE WHEN p.tipo = 'entrada' AND substr(p.timestamp, 12, 8) > '12:30' THEN substr(p.timestamp, 12, 8) END) AS entrada_tarde,
                    MAX(CASE WHEN p.tipo = 'saida' AND substr(p.timestamp, 12, 8) > '12:30' THEN substr(p.timestamp, 12, 8) END) AS saida_tarde
                FROM ponto p
                JOIN cadastro_funcionario f ON p.cpf = f.CPF
                WHERE p.timestamp LIKE ?
                GROUP BY f.nome, DATE(substr(p.timestamp, 1, 10))
                ORDER BY DATE(substr(p.timestamp, 1, 10)), f.nome;
            """

            self.cursor.execute(query, (padrao,))
            registros = self.cursor.fetchall()

            # Caso não haja registros, retorna lista vazia
            if not registros:
                logger.warning(f"Nenhum registro de ponto encontrado para {mes_ano}.")
                return []

            print(f"Encontrados {len(registros)} registros de ponto para {mes_ano}.")
            return registros

        except Exception as e:
            logger.error(f"Erro ao visualizar pontos. {e}")
            return None

    def verificar_registros(self):
        query = "SELECT COUNT(*) FROM ponto"
        self.cursor.execute(query)
        total = self.cursor.fetchone()[0]
        print(f"Total de registros na tabela ponto: {total}")
        return total

    def verificar_formato_timestamp(self):
        query = "SELECT timestamp FROM ponto LIMIT 10"
        self.cursor.execute(query)
        resultados = self.cursor.fetchall()
        for resultado in resultados:
            print(resultado[0])
        return resultados

    def depurar_registros_ponto(self, mes, ano):
        """
        Função para depurar os registros de ponto e identificar problemas
        """
        try:
            # Usar uma consulta extremamente simples para verificar se há dados para este mês/ano
            query_simples = """
                SELECT COUNT(*) 
                FROM ponto 
                WHERE timestamp LIKE ?
            """

            # Adicionar caracteres curinga antes e depois para capturar qualquer formato
            padrao = f'%{ano}%{mes.zfill(2)}%'

            self.cursor.execute(query_simples, (padrao,))
            total = self.cursor.fetchone()[0]
            print(f"Total de registros encontrados para '%{ano}%{mes.zfill(2)}%': {total}")

            # Se temos registros, vamos ver alguns exemplos
            if total > 0:
                query_exemplos = """
                    SELECT timestamp, tipo, cpf 
                    FROM ponto 
                    WHERE timestamp LIKE ? 
                    LIMIT 5
                """
                self.cursor.execute(query_exemplos, (padrao,))
                exemplos = self.cursor.fetchall()
                print("Exemplos de registros encontrados:")
                for ex in exemplos:
                    print(ex)

            # Verificar uso correto dos tipos de entrada/saída
            query_tipos = """
                SELECT tipo, COUNT(*) 
                FROM ponto 
                GROUP BY tipo
            """
            self.cursor.execute(query_tipos)
            tipos = self.cursor.fetchall()
            print("Tipos de registro e contagens:")
            for t in tipos:
                print(t)

            return total

        except Exception as e:
            print(f"Erro na depuração: {e}")
            return None

    def buscar_ponto_sem_join(self, mes_ano):
        """
        Busca apenas na tabela ponto, sem JOIN
        """
        try:
            mes, ano = mes_ano.split('/')
            mes_formatado = mes.zfill(2)

            # Padrão para busca
            padrao = f'{ano}-{mes_formatado}'

            query = """
                SELECT id, cpf, timestamp, tipo
                FROM ponto
                WHERE timestamp LIKE ?
                LIMIT 20
            """

            self.cursor.execute(query, (padrao + '%',))
            registros = self.cursor.fetchall()

            if not registros:
                print(f"Nenhum registro encontrado na tabela ponto para {mes_ano}.")
            else:
                print(f"Encontrados {len(registros)} registros na tabela ponto.")
                for r in registros:
                    print(r)

            return registros

        except Exception as e:
            print(f"Erro na consulta sem JOIN: {e}")
            return None

dados = BancoSQLite()

print(dados.depurar_registros_ponto("02", "2025"))
# print(dados.visualiza_ponto("02/2025"))


info = dados.buscar_ponto_sem_join("02/2025")
for i in info:
    print(i)