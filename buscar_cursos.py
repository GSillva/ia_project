import pandas as pd

# 1. Lista de cidades e UFs para a busca
cidades_alvo = [
    ('Itatuba', 'PB'),
    ('Mogeiro', 'PB'),
    ('Ingá', 'PB'),
    ('Bananeiras', 'PB'),
    ('Alagoa Nova', 'PB'),
    ('Serra Redonda', 'PB'),
    ('Santa Rita', 'MA'), # Maranhão
    ('Caturité', 'PB'),
    ('Lagoa Seca', 'PB'),
    ('Queimadas', 'BA'), # Bahia
    ('Queimadas', 'PB'),
    ('Santa Rita', 'PB'), # Paraíba
    ('Guarabira', 'PB'),
    ('Carpina', 'PE'), # Pernambuco
    ('Campina Grande', 'PB'),
    ('João Pessoa', 'PB'),
    ('Montes Claros', 'MG'), # Minas Gerais
    ('Cabaceiras', 'PB')
]

# Nomes dos arquivos de entrada e saída
arquivo_entrada = 'Sistec_Cursos_Tecnicos_ativos_120922.csv'
arquivo_saida_csv = 'cursos_encontrados.csv'
arquivo_saida_excel = 'cursos_encontrados.xlsx'

try:
    # 2. Carregar o arquivo CSV
    print(f"Lendo o arquivo '{arquivo_entrada}'...")
    df = pd.read_csv(arquivo_entrada, sep=';', encoding='latin-1')
    print("Arquivo lido com sucesso. Buscando cursos...")

    # Normaliza as colunas de texto para garantir a correspondência
    df['MUNICÍPIO'] = df['MUNICÍPIO'].str.strip().str.upper()
    df['UF'] = df['UF'].str.strip().str.upper()

    # 3. Filtrar os dados
    resultados = []
    for cidade, uf in cidades_alvo:
        cidade_normalizada = cidade.strip().upper()
        uf_normalizada = uf.strip().upper()
        
        filtro_cidade = df[(df['MUNICÍPIO'] == cidade_normalizada) & (df['UF'] == uf_normalizada)]
        
        if not filtro_cidade.empty:
            resultados.append(filtro_cidade)

    # 4. Consolidar e exibir os resultados
    if resultados:
        cursos_encontrados = pd.concat(resultados, ignore_index=True)
        
        print("\n--- Cursos Técnicos Encontrados ---")
        colunas_para_exibir = [
            'CURSO', 'UNIDADE DE ENSINO', 'MUNICÍPIO', 'UF', 
            'CARGA HORÁRIA CURSO', 'MODALIDADE'
        ]
        colunas_existentes = [col for col in colunas_para_exibir if col in cursos_encontrados.columns]
        print(cursos_encontrados[colunas_existentes].to_string())

        # --- NOVO: SALVANDO OS RESULTADOS EM ARQUIVO ---
        
        # Opção 1: Salvar em um arquivo CSV (Recomendado)
        cursos_encontrados.to_csv(arquivo_saida_csv, index=False, sep=';', encoding='utf-8-sig')
        print(f"\n✅ Resultados salvos com sucesso no arquivo: '{arquivo_saida_csv}'")

        # Opção 2: Salvar em um arquivo Excel (.xlsx)
        # Para usar esta opção, primeiro instale a biblioteca necessária: pip install openpyxl
        # Depois, remova o '#' da linha abaixo para ativá-la.
        # cursos_encontrados.to_excel(arquivo_saida_excel, index=False, sheet_name='Cursos')
        # print(f"\n✅ Resultados salvos com sucesso no arquivo: '{arquivo_saida_excel}'")

    else:
        print("\nNenhum curso técnico encontrado para as cidades e estados especificados.")

except FileNotFoundError:
    print(f"\nERRO: O arquivo '{arquivo_entrada}' não foi encontrado.")
    print("Por favor, certifique-se de que o arquivo CSV está na mesma pasta que este script Python.")
except Exception as e:
    print(f"\nOcorreu um erro inesperado: {e}")
