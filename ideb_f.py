# -*- coding: utf-8 -*-

import pandas as pd
from os import path
from pandas import read_excel
import matplotlib.pyplot as plt
import numpy as np

# --- Seção de Funções de Apoio ---
# Esta seção contém funções para carregar e padronizar os dados de diferentes fontes,
# preparando-os para a análise principal.

def getdtb(file: str):
    """
    Objetivo: Ler e preparar o arquivo da Divisão Territorial Brasileira (DTB) do IBGE.

    Detalhes:
    - Esta função lê o arquivo Excel do IBGE, pulando as primeiras linhas para ignorar
      o cabeçalho complexo, e seleciona colunas específicas usando seus índices.
    - As colunas de interesse são: 'id_uf', 'ds_uf', 'ds_rgi', 'id_mundv' e 'ds_mun'.
    - Remove duplicatas com base no ID do município para garantir que cada um tenha
      um único registro.
    """
    # As colunas de interesse estão nas posições 0, 1, 5, 7 e 8,
    # conforme a estrutura do arquivo.
    data = read_excel(file, skiprows=6,
                      usecols=[0, 1, 5, 7, 8],
                      engine='xlrd')
    
    # Renomeia as colunas para facilitar a manipulação.
    data.columns = ['id_uf', 'ds_uf', 'ds_rgi',
                    'id_mundv', 'ds_mun']
    
    # Remove duplicatas para garantir a unicidade dos municípios.
    data = data.drop_duplicates(subset=['id_mundv'])
    return data


def formatar_nome_para_merge(df, coluna, novo_nome="ds_formatada"):
    """
    Objetivo: Padronizar os nomes dos municípios para permitir uma junção (merge) precisa
    entre diferentes bases de dados.

    Detalhes:
    - Converte os nomes para maiúsculas.
    - Remove caracteres especiais, acentos, espaços extras e termos indesejados.
    - Aplica um tratamento específico para nomes compostos como "Rio de Janeiro".
    """
    df[novo_nome] = (df[coluna].str.upper()
                               .str.replace("[-.!?'`()*]", "", regex=True)
                               .str.replace("MIXING CENTER", "", regex=False)
                               .str.strip())
    
    # Tratamento especial para o caso do Rio de Janeiro.
    df[novo_nome] = df[novo_nome].str.replace("RIO DE JANEIRO", "RIODEJANEIRO", regex=False)
    
    # Remove espaços em todos os nomes após o tratamento de "Rio de Janeiro".
    df[novo_nome] = df[novo_nome].str.replace(" ", "", regex=False)
    
    return df

def padronizar_cidades_ia(df_ia, df_dtb):
    """
    Objetivo: Vincular os municípios da base do Instituto Alpargatas (IA) aos
    códigos do IBGE.

    Detalhes:
    - Mapeia as siglas de estados (UF) para os nomes completos.
    - Padroniza os nomes das cidades em ambos os DataFrames.
    - Realiza uma junção do tipo `left` entre o DataFrame de IA e o do IBGE.
    - Retorna dois DataFrames: um com os municípios que foram encontrados no IBGE
      e outro com aqueles que não foram, o que é útil para a validação.
    """
    # Mapear UF para o nome do estado.
    uf_mapping = {"PB": "Paraíba", "PE": "Pernambuco",
                  "MG": "Minas Gerais", "SP": "São Paulo",
                  "RJ": "Rio de Janeiro"}
    df_ia['ds_uf'] = df_ia['sg_uf'].map(uf_mapping)

    # Formata os nomes das cidades em ambos os dataframes para o merge.
    df_ia = formatar_nome_para_merge(df_ia.copy(), "ds_mun", "ds_mun_formatada")
    df_dtb_formatado = formatar_nome_para_merge(df_dtb.copy(), "ds_mun", "ds_mun_formatada")
    
    # Realiza o merge com o DataFrame do IBGE.
    df_combinado = df_ia.merge(df_dtb_formatado[['ds_mun_formatada', 'ds_uf', 'ds_mun', 'id_mundv']],
                               how="left",
                               on=['ds_mun_formatada', 'ds_uf'],
                               suffixes=["_ia", "_ibge"],
                               indicator=True)
    
    # Identifica as cidades que não foram encontradas no merge.
    nao_encontrados = df_combinado[df_combinado['_merge'] == 'left_only'].copy()
    df_combinado = df_combinado[df_combinado['_merge'] == 'both'].copy()
    
    # Remove a coluna auxiliar criada pelo merge.
    df_combinado.drop(columns=['_merge'], inplace=True)
    if not nao_encontrados.empty:
      nao_encontrados.drop(columns=['_merge'], inplace=True)
    
    return df_combinado, nao_encontrados

def get_ideb_data(file_path):
    """
    Objetivo: Carregar e preparar os dados do IDEB.

    Detalhes:
    - Lê o arquivo Excel, pulando linhas de cabeçalho irrelevantes.
    - Seleciona as colunas de interesse por índice: UF, Município, Rede, IDEB 2021 e IDEB 2023.
    - Renomeia as colunas para nomes mais significativos.
    - Converte as notas do IDEB para o tipo numérico, substituindo valores não numéricos por NaN.
    - Aplica a função de padronização de nomes de cidade.
    """
    # Define as colunas a serem lidas usando seus índices (baseado em 0).
    cols_to_read = [0, 2, 3, 16, 17]
    
    # Lê o arquivo Excel, pulando 6 linhas e especificando as colunas por índice.
    df_ideb = pd.read_excel(file_path, skiprows=6, usecols=cols_to_read, header=None)
    
    # Renomeia as colunas do DataFrame.
    df_ideb.columns = ['sg_uf', 'ds_municipio', 'rede', 'ideb_2021', 'ideb_2023']
    
    # Converte as colunas de IDEB para tipo numérico.
    df_ideb['ideb_2021'] = pd.to_numeric(df_ideb['ideb_2021'], errors='coerce')
    df_ideb['ideb_2023'] = pd.to_numeric(df_ideb['ideb_2023'], errors='coerce')
    
    # Chama a função de formatação para tratar o nome do município.
    df_ideb = formatar_nome_para_merge(df_ideb, 'ds_municipio', 'ds_mun_formatada')

    return df_ideb

# --- INÍCIO DO SCRIPT PRINCIPAL ---

# 1. Leitura e Preparação das Bases de Dados
print("Iniciando a leitura e preparação das bases de dados.")

# Carrega a base de Divisão Territorial Brasileira (DTB) do IBGE.
data_dir = 'data'
file = path.join(data_dir, "DTB/2024/RELATORIO_DTB_BRASIL_2024_MUNICIPIOS.xls")
df_dtb = getdtb(file)
print("DataFrame do IBGE lido e pronto.")

# Carrega a base de dados do IDEB.
ideb_file_path = "data/IDEB/divulgacao_ensino_medio_municipios_2023.xlsx"
df_ideb = get_ideb_data(ideb_file_path)
print("DataFrame do IDEB lido e preparado.")

# Dicionários para armazenar os resultados do processamento por ano.
dataframes_combinados_por_ano = {}
cidades_nao_encontradas_por_ano = {}

# Carrega o arquivo principal de projetos do IA.
file_path = "data/Projetos_de_Atuac807a771o_-_IA_-_2020_a_2025 (1).xlsx"

# 2. Processamento Anual e Junção dos Dados do IA com o IBGE
# Este laço itera sobre cada ano para processar as planilhas de projetos do IA.
for ano in range(2020, 2026):
    try:
        df_ano = pd.read_excel(file_path, sheet_name=str(ano), skiprows=5)
    except ValueError as e:
        print(f"\nErro ao ler a planilha do ano {ano}: {e}")
        continue

    # Identifica as últimas 3 colunas de interesse de forma dinâmica.
    ultimas_3 = list(df_ano.columns[-3:])

    # Renomeia colunas para manter a consistência, tratando diferentes nomes de cabeçalho.
    if "UF" in df_ano.columns:
        df_ano.rename(columns={"UF": "sg_uf", "CIDADES": "ds_mun"}, inplace=True)
    elif "ESTADO" in df_ano.columns:
        df_ano.rename(columns={"ESTADO": "sg_uf", "CIDADES": "ds_mun"}, inplace=True)
    else:
        print(f"\nNem 'UF' nem 'ESTADO' encontrado no ano {ano}. Ignorando este ano.")
        continue

    # Limpa os dados de observação.
    df_ano = df_ano[~df_ano['ds_mun'].str.contains('Obs.:', na=False)]
    
    # Seleciona as colunas relevantes.
    df_ano = df_ano[df_ano.columns.intersection(["ds_mun", "sg_uf"] + ultimas_3)]
    df_ano.columns = ["ds_mun", "sg_uf", "nprojetos", "ninstituicoes", "nbeneficiados"]

    # Agrupa os dados por município e estado, somando os valores.
    df_ano = df_ano.groupby(["ds_mun", "sg_uf"], as_index=False).sum(numeric_only=True)
    df_ano['ano'] = ano

    # Realiza a padronização e junção com a base do IBGE.
    df_combinado, df_nao_encontrados = padronizar_cidades_ia(df_ano, df_dtb)
    
    # Armazena os DataFrames resultantes.
    dataframes_combinados_por_ano[ano] = df_combinado
    cidades_nao_encontradas_por_ano[ano] = df_nao_encontrados
    
    print(f"\nDataFrame combinado do ano {ano} criado com sucesso.")
    if not df_nao_encontrados.empty:
        print(f"ATENÇÃO: {len(df_nao_encontrados)} cidades não foram encontradas no IBGE para este ano.")
    print("-" * 30)

# Unir todos os dataframes de IA de anos diferentes em um só.
df_ia_completo = pd.concat(dataframes_combinados_por_ano.values(), ignore_index=True)

# 3. Análise Exploratória e Visualização dos Dados

# --- Gráfico 1: Evolução Anual dos Projetos do IA ---
# Agrupa os dados por ano e soma os valores para a visualização de tendências.
df_evolucao = df_ia_completo.groupby('ano').sum(numeric_only=True)

fig, ax1 = plt.subplots(figsize=(12, 8))

# Plota o número de projetos e instituições no eixo Y1.
ax1.set_xlabel('Ano')
ax1.set_ylabel('Nº de Projetos e Instituições', color='blue')
ax1.plot(df_evolucao.index, df_evolucao['nprojetos'], 'bo-', label='Nº de Projetos')
ax1.plot(df_evolucao.index, df_evolucao['ninstituicoes'], 'b^--', label='Nº de Instituições')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.legend(loc='upper left')

# Cria um segundo eixo Y para o número de beneficiados, permitindo
# a visualização em uma escala diferente.
ax2 = ax1.twinx()
ax2.set_ylabel('Nº de Beneficiados', color='red')
ax2.plot(df_evolucao.index, df_evolucao['nbeneficiados'], 'rD-', label='Nº de Beneficiados')
ax2.tick_params(axis='y', labelcolor='red')
ax2.legend(loc='upper right')

ax1.set_title('Evolução Anual dos Projetos do IA (2020-2025)', fontweight='bold')
ax1.set_xticks(df_evolucao.index)
ax1.grid(True)
fig.tight_layout()
plt.show()

# --- Junção Final com a Base do IDEB ---
# Prepara a base de dados consolidada para a análise final com o IDEB.

# Padroniza a coluna 'ds_mun_ia' para o merge com a base do IDEB.
df_ia_completo = formatar_nome_para_merge(df_ia_completo, 'ds_mun_ia', 'ds_mun_ia_formatada')

# Realiza a junção entre a base de IA e a base do IDEB, usando os nomes formatados e o estado como chaves.
df_final = pd.merge(df_ia_completo, df_ideb,
                     left_on=['ds_mun_ia_formatada', 'sg_uf'], 
                     right_on=['ds_mun_formatada', 'sg_uf'],
                     how='left', suffixes=('_ia', '_ideb'))

# Exibe informações sobre o DataFrame final.
print("\nDataFrame final com dados do IDEB e IA:")
print(df_final.head())
print(f"Número de municípios na base final: {df_final['ds_mun_ia'].nunique()}")
print(f"Total de registros na base final: {len(df_final)}")
print("-" * 30)

# --- Gráfico 2: Média do IDEB por Município e Rede de Ensino ---
# Visualiza as notas do IDEB de 2021 e 2023 por município,
# segregadas por rede de ensino (Estadual, Federal, Municipal).

df_grouped = df_final.groupby('ds_mun_ia')

fig, ax = plt.subplots(figsize=(20, 10))

bar_width = 0.12
base_pos = 0
plotted_labels = set()

# Define os pares de rede de ensino e ano para plotagem.
rede_ano_pairs = [
    ('Estadual', '2021'), ('Estadual', '2023'),
    ('Federal', '2021'), ('Federal', '2023'),
    ('Municipal', '2021'), ('Municipal', '2023'),
]

# Define os rótulos de legenda para o gráfico.
legend_labels = {
    ('Estadual', '2021'): 'IDEB 2021 (Estadual)',
    ('Estadual', '2023'): 'IDEB 2023 (Estadual)',
    ('Federal', '2021'): 'IDEB 2021 (Federal)',
    ('Federal', '2023'): 'IDEB 2023 (Federal)',
    ('Municipal', '2021'): 'IDEB 2021 (Municipal)',
    ('Municipal', '2023'): 'IDEB 2023 (Municipal)'
}

# Itera sobre cada grupo de município para criar as barras.
for mun_name, group_df in df_grouped:
    for i, (rede, ano) in enumerate(rede_ano_pairs):
        rede_data = group_df[group_df['rede'] == rede]

        if not rede_data.empty:
            ideb_val = rede_data[f'ideb_{ano}'].iloc[0]
            if pd.notna(ideb_val):
                pos = base_pos + i * bar_width
                label = legend_labels[(rede, ano)] if (rede, ano) not in plotted_labels else ""
                color_idx = i
                ax.bar(pos, ideb_val, width=bar_width, color=f'C{color_idx}', label=label)
                plotted_labels.add((rede, ano))

    base_pos += len(rede_ano_pairs) * bar_width + 0.3

# Rótulos e formatação do gráfico.
ax.set_xlabel('Municípios', fontweight='bold')
ax.set_ylabel('IDEB', fontweight='bold')
ax.set_title('Média do IDEB 2021 e 2023 por Município e Rede de Ensino', fontweight='bold')

# Configura os rótulos do eixo X para os municípios.
tick_positions = [
    i * (len(rede_ano_pairs) * bar_width + 0.3) + (len(rede_ano_pairs) * bar_width) / 2
    for i in range(len(df_grouped))
]
ax.set_xticks(tick_positions)
ax.set_xticklabels(df_grouped.groups.keys(), rotation=90)

ax.legend()
plt.tight_layout()
plt.show()