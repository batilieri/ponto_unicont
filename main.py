#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from banco.bancoSQlite import BancoSQLite

def _parse_line(line):
    try:
        """
                Faz o parsing de uma linha de registro com o seguinte layout:
                  - posições 0 a 9: Identificador (registro)
                  - posições 10 a 33: Timestamp (24 caracteres)
                  - posições 34 a 44: Código (11 caracteres)
                  - posições 45 em diante: Valor (ex: '1AFA', 'A1F5', etc.)
                Caso a linha não contenha todos os campos, os campos ausentes serão tratados como vazios.
                """
        registro = line[:10]
        timestamp = line[10:34]
        # Se a linha tiver pelo menos 45 caracteres, extrai o código; caso contrário, pega o que houver a partir do
        # índice 34
        codigo = line[34:45] if 45 <= len(line) < 90 else line[34:]
        # Se a linha tiver mais de 45 caracteres, extrai o valor (removendo espaços extras)
        valor = line[45:].strip() if len(line) > 45 else ""

        return {
            "registro": registro,
            "timestamp": timestamp,
            "codigo": codigo.strip(),
            "valor": valor
        }
    except Exception as e:
        print(e)


def ler_registros(arquivo):
    try:
        """
                Abre o arquivo e lê todos os registros, aplicando a função de parsing para cada linha.
                """
        registros = []
        with open(arquivo, encoding="ANSI") as f:
            for linha in f:
                linha = linha.rstrip("\n")
                if linha.strip():  # ignora linhas vazias
                    registros.append(_parse_line(linha))
        return registros
    except Exception as e:
        print(e)


class ManipulaPonto:
    def __init__(self, local_arquivo):
        self.bd = BancoSQLite()
        self._diretorio = local_arquivo

    def cadastro_escritorio(self):
        pass

    def cadastro_colaborador(self):
        pass

    def ponto_entrada_saida(self):
        pass




def main():
    arquivo = r"C:\Users\eliba\Área de Trabalho\André_ponto\00004004330218916.txt"  # nome do arquivo com os registros
    registros = ler_registros(arquivo)

    # Exibe os registros lidos com os campos extraídos
    for reg in registros:
        print("Registro: ", reg["registro"])
        print("Timestamp:", reg["timestamp"])
        print("Código:   ", reg["codigo"])
        print("Valor:    ", reg["valor"])
        print("-" * 40)


if __name__ == "__main__":
    main()

#
# def parse_ponto_file(filepath):
#     """
#     Processa um arquivo de ponto eletrônico e extrai as informações
#
#     Args:
#         filepath: Caminho para o arquivo de ponto
#
#     Returns:
#         Dicionário contendo informações da empresa e registros de ponto
#     """
#     try:
#         # Tenta abrir e ler o arquivo
#         with open(filepath, 'r', encoding='utf-8') as file:
#             content = file.read()
#     except UnicodeDecodeError:
#         # Se falhar com UTF-8, tenta com latin-1
#         with open(filepath, 'r', encoding='latin-1') as file:
#             content = file.read()
#
#     lines = content.strip().split('\n')
#
#     # Inicializa dicionários e listas
#     header = None
#     registros = []
#     funcionarios = {}
#
#     for line in lines:
#         # Pular linha vazia
#         if not line.strip():
#             continue
#
#         # Identifica o tipo de registro
#         reg_id = line[:10]
#
#         # Header - informações da empresa
#         if reg_id.startswith("0000000001"):
#             header = {
#                 "cnpj": line[29:47].strip(),
#                 "nome_empresa": line[47:147].strip(),
#                 "data_inicio": line[169:179] if len(line) > 178 else "",
#                 "data_fim": line[179:189] if len(line) > 188 else "",
#                 "data_geracao": line[189:208] if len(line) > 207 else ""
#             }
#
#         # Trailer - ignorar
#         elif reg_id.startswith("999999999"):
#             continue
#
#         # Registros de ponto
#         else:
#             timestamp = line[0:26]
#
#             # Validar formato da data
#             try:
#                 data = timestamp[0:10]
#                 hora = timestamp[11:19]
#                 if not re.match(r'\d{4}-\d{2}-\d{2}', data):
#                     continue
#             except:
#                 continue
#
#             # Registros de identificação de funcionário
#             if len(line) > 45 and line[26:27] == 'I':
#                 cpf = line[27:38].strip()
#                 nome = line[38:88].strip()
#
#                 funcionarios[cpf] = nome
#
#                 registros.append({
#                     'cpf': cpf,
#                     'nome': nome,
#                     'data': data,
#                     'hora': hora,
#                     'tipo': 'Registro inicial'
#                 })
#
#             # Registros de entrada
#             elif len(line) > 45 and line[26:27] in ['A', 'E']:
#                 cpf = line[27:38].strip()
#                 nome = line[38:88].strip() if len(line) > 88 else funcionarios.get(cpf, "Nome não encontrado")
#
#                 registros.append({
#                     'cpf': cpf,
#                     'nome': nome,
#                     'data': data,
#                     'hora': hora,
#                     'tipo': 'Entrada'
#                 })
#
#             # Registros de saída
#             elif len(line) > 30 and re.match(r'^\d{14}', line) and line[26:38].strip().isdigit():
#                 cpf = line[26:38].strip()
#                 nome = funcionarios.get(cpf, "Nome não encontrado")
#
#                 registros.append({
#                     'cpf': cpf,
#                     'nome': nome,
#                     'data': data,
#                     'hora': hora,
#                     'tipo': 'Saída'
#                 })
#
#     # Criar DataFrame com os registros
#     df = pd.DataFrame(registros)
#
#     # Ordenar e converter data para datetime
#     if not df.empty:
#         df['data'] = pd.to_datetime(df['data'], errors='coerce')
#         df = df.dropna(subset=['data'])
#         df = df.sort_values(['cpf', 'data', 'hora'])
#
#     empresa_info = {
#         'cnpj': header['cnpj'] if header else "",
#         'nome': header['nome_empresa'] if header else ""
#     }
#
#     return {
#         'empresa': empresa_info,
#         'registros': df
#     }
#
#
# def gerar_relatorio(dados):
#     """
#     Gera relatório de horas trabalhadas por funcionário e por dia
#
#     Args:
#         dados: Dicionário com informações da empresa e registros
#
#     Returns:
#         DataFrame com relatório de horas trabalhadas
#     """
#     df = dados['registros']
#
#     if df.empty:
#         return pd.DataFrame()
#
#     # Converter horas para datetime
#     df['hora_dt'] = pd.to_datetime(df['hora'], format='%H:%M:%S', errors='coerce')
#     df = df.dropna(subset=['hora_dt'])
#
#     # Agrupar por funcionário e data
#     relatorio = []
#
#     for (cpf, nome), grupo_func in df.groupby(['cpf', 'nome']):
#         for data, grupo_dia in grupo_func.groupby('data'):
#             entradas = grupo_dia[grupo_dia['tipo'].isin(['Entrada', 'Registro inicial'])]['hora_dt'].tolist()
#             saidas = grupo_dia[grupo_dia['tipo'] == 'Saída']['hora_dt'].tolist()
#
#             # Calcular horas trabalhadas
#             if entradas and saidas:
#                 primeira_entrada = min(entradas)
#                 ultima_saida = max(saidas)
#
#                 # Calcular diferença em horas
#                 tempo_trabalhado = (ultima_saida - primeira_entrada).total_seconds() / 3600
#
#                 # Calcular intervalo se houver mais de uma entrada e saída
#                 intervalo = 0
#                 if len(entradas) > 1 and len(saidas) > 1:
#                     entradas_ordenadas = sorted(entradas)
#                     saidas_ordenadas = sorted(saidas)
#
#                     # Consideramos que cada saída é seguida por uma entrada (exceto a última)
#                     for i in range(len(saidas_ordenadas) - 1):
#                         if i + 1 < len(entradas_ordenadas):
#                             # Tempo entre uma saída e a próxima entrada
#                             pausa = (entradas_ordenadas[i + 1] - saidas_ordenadas[i]).total_seconds() / 3600
#                             if pausa > 0:  # Apenas se for positivo
#                                 intervalo += pausa
#
#                 # Tempo efetivo = tempo total - intervalo
#                 tempo_efetivo = tempo_trabalhado - intervalo
#
#                 relatorio.append({
#                     'cpf': cpf,
#                     'nome': nome,
#                     'data': data.strftime('%Y-%m-%d'),
#                     'primeira_entrada': primeira_entrada.strftime('%H:%M:%S'),
#                     'ultima_saida': ultima_saida.strftime('%H:%M:%S'),
#                     'horas_totais': round(tempo_trabalhado, 2),
#                     'intervalo_horas': round(intervalo, 2),
#                     'horas_efetivas': round(tempo_efetivo, 2)
#                 })
#
#     return pd.DataFrame(relatorio)
#
#     # !/usr/bin/env python3
#     # -*- coding: utf-8 -*-

# def exportar_para_excel(dados, relatorio, nome_arquivo):
#     """
#     Exporta os dados para um arquivo Excel
#
#     Args:
#         dados: Dicionário com informações da empresa e registros
#         relatorio: DataFrame com relatório de horas
#         nome_arquivo: Nome do arquivo de saída
#
#     Returns:
#         Nome do arquivo de saída
#     """
#     nome_base = os.path.splitext(os.path.basename(nome_arquivo))[0]
#     nome_saida = f"{nome_base}_processado.xlsx"
#
#     with pd.ExcelWriter(nome_saida) as writer:
#         # Informações da empresa
#         empresa_df = pd.DataFrame([dados['empresa']])
#         empresa_df.to_excel(writer, sheet_name='Informações', index=False)
#
#         # Registros na primeira aba
#         dados['registros'].to_excel(writer, sheet_name='Registros Detalhados', index=False)
#
#         # Relatório na segunda aba
#         if not relatorio.empty:
#             relatorio.to_excel(writer, sheet_name='Relatório Horas', index=False)
#
#             # Resumo por funcionário
#             resumo = relatorio.groupby('nome').agg({
#                 'horas_efetivas': 'sum',
#                 'data': 'count'
#             }).reset_index()
#             resumo.columns = ['Nome', 'Total Horas', 'Dias Trabalhados']
#             resumo['Média Diária'] = round(resumo['Total Horas'] / resumo['Dias Trabalhados'], 2)
#             resumo.to_excel(writer, sheet_name='Resumo por Funcionário', index=False)
#
#     return nome_saida


# def main():
#     print("Processador de Arquivos de Ponto - UNICONTE")
#     print("=" * 50)
#
#     # Verificar argumentos da linha de comando
#     if len(sys.argv) > 1:
#         arquivo = sys.argv[1]
#     else:
#         # Solicitar nome do arquivo manualmente
#         arquivo = input("Digite o caminho do arquivo de ponto: ")
#
#     if not arquivo or not os.path.exists(arquivo):
#         print("Arquivo não encontrado. Verifique o caminho e tente novamente.")
#         return
#
#     print(f"Processando arquivo: {arquivo}")
#
#     # Processar o arquivo
#     try:
#         dados = parse_ponto_file(arquivo)
#     except Exception as e:
#         print(f"Erro ao processar o arquivo: {e}")
#         return
#
#     # Informações da empresa
#     print(f"\nEmpresa: {dados['empresa']['nome']}")
#     print(f"CNPJ: {dados['empresa']['cnpj']}")
#
#     # Verificar registros
#     if dados['registros'].empty:
#         print("\nNenhum registro de ponto encontrado no arquivo.")
#         return
#
#     # Gerar relatório
#     relatorio = gerar_relatorio(dados)
#
#     # Estatísticas básicas
#     total_registros = len(dados['registros'])
#     total_funcionarios = dados['registros']['cpf'].nunique()
#     print(f"\nTotal de registros processados: {total_registros}")
#     print(f"Total de funcionários encontrados: {total_funcionarios}")
#
#     # Exportar para Excel
#     resposta = input("\nDeseja exportar os dados para Excel? (s/n): ")
#     if resposta.lower() in ['s', 'sim', 'y', 'yes']:
#         nome_saida = exportar_para_excel(dados, relatorio, arquivo)
#         print(f"\nDados exportados para: {nome_saida}")
#
#     # Estatísticas do relatório
#     if not relatorio.empty:
#         print("\n--- Resumo de Horas Trabalhadas ---")
#         print(f"Média de horas efetivas por dia: {relatorio['horas_efetivas'].mean():.2f}")
#         print(f"Total de dias registrados: {len(relatorio)}")
#
#         # Funcionário com mais horas
#         if len(relatorio) > 0:
#             horas_por_func = relatorio.groupby('nome')['horas_efetivas'].sum()
#             func_mais_horas = horas_por_func.idxmax()
#             total_horas = horas_por_func.max()
#             print(f"\nFuncionário com mais horas registradas: {func_mais_horas} ({total_horas:.2f} horas)")
#
#     print("\nProcessamento concluído!")
