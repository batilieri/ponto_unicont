#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from banco.bancoSQlite import BancoSQLite

from datetime import datetime


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
