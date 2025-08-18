import pandas as pd
from os import path
import unicodedata
import re
import matplotlib.pyplot as plt

# --- Visão Geral do Script ---
# Este script combina dados da Relação Anual de Informações Sociais (RAIS) com informações
# de projetos do Instituto Alpargatas (IA) para o ano de 2024. O objetivo é realizar
# uma análise exploratória, visualizando a distribuição de empregos por setor econômico
# nas cidades onde o IA atua.

# --- Seção 1: Funções de Preparação de Dados ---
# Esta seção define as funções para carregar, limpar e padronizar os dados de ambas as fontes.

def standardize_name(name):
    """
    Objetivo: Padronizar o nome das cidades para permitir a junção (merge) precisa
    entre as bases de dados.
    
    Detalhes:
    - A função remove acentos, converte a string para minúsculas e elimina
      caracteres especiais, garantindo a consistência.
    - É usada para criar uma chave de junção (`merge`) limpa, minimizando erros
      de correspondência.
    """
    if isinstance(name, str):
        # Remove acentos
        name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('utf-8')
        # Converte para minúsculas
        name = name.lower()
        # Remove caracteres que não são letras ou números
        name = re.sub(r'[^a-z0-9 ]', '', name)
        # Remove espaços extras
        name = re.sub(r'\s+', ' ', name).strip()
    return name

def load_rais_tabela4(file_path):
    """
    Objetivo: Carregar e formatar a Tabela 4 da RAIS a partir de um arquivo Excel.
    
    Detalhes:
    - A função lê a planilha 'TABELA 4', pulando as linhas de cabeçalho irrelevantes.
    - Renomeia as colunas de emprego por setor para nomes mais significativos.
    - Converte as colunas numéricas para o tipo inteiro, tratando valores ausentes.
    - Retorna um DataFrame pronto para ser mesclado.
    """
    try:
        df = pd.read_excel(file_path, sheet_name='TABELA 4', skiprows=12)
        df = df.dropna(subset=['UF', 'Código', 'Município'])
        df.rename(columns={
            'Município': 'ds_mun',
            'UF': 'sg_uf',
            'Código': 'id_mundv',
            'Unnamed: 5': 'Agropecuaria_2024',
            'Unnamed: 9': 'Industria_2024',
            'Unnamed: 13': 'Construcao_2024',
            'Unnamed: 17': 'Comercio_2024',
            'Unnamed: 21': 'Servicos_2024',
            'Unnamed: 25': 'Total_2024'
        }, inplace=True)
        df_rais = df[['sg_uf', 'id_mundv', 'ds_mun',
                      'Agropecuaria_2024', 'Industria_2024', 'Construcao_2024',
                      'Comercio_2024', 'Servicos_2024', 'Total_2024']].copy()
        
        cols_to_convert = ['Agropecuaria_2024', 'Industria_2024', 'Construcao_2024',
                           'Comercio_2024', 'Servicos_2024', 'Total_2024']
        for col in cols_to_convert:
            df_rais.loc[:, col] = pd.to_numeric(df_rais[col], errors='coerce').fillna(0).astype(int)
            
        return df_rais
        
    except Exception as e:
        print(f"Erro ao carregar a Tabela 4 da RAIS: {e}")
        return pd.DataFrame()

def load_ia_projetos(file_path, year=2024):
    """
    Objetivo: Carregar e formatar os dados de projetos do Instituto Alpargatas (IA)
    para um ano específico.
    
    Detalhes:
    - Lê a planilha do ano especificado, tratando a inconsistência nos nomes das
      colunas de estado ('UF' ou 'ESTADO').
    - Filtra as linhas de observação e agrupa os dados por cidade e estado para
      obter um resumo total de projetos, instituições e beneficiados.
    """
    try:
        df_ia = pd.read_excel(file_path, sheet_name=str(year), skiprows=5)
        
        # Identificar as colunas de cidade e estado
        if "CIDADES" in df_ia.columns and "UF" in df_ia.columns:
            df_ia.rename(columns={"UF": "sg_uf", "CIDADES": "ds_mun"}, inplace=True)
        elif "CIDADES" in df_ia.columns and "ESTADO" in df_ia.columns:
            df_ia.rename(columns={"ESTADO": "sg_uf", "CIDADES": "ds_mun"}, inplace=True)
        else:
            raise ValueError("Colunas 'CIDADES' e 'UF' ou 'ESTADO' não encontradas.")

        # Filtrar as linhas de observação e agrupar por cidade
        df_ia = df_ia[~df_ia['ds_mun'].str.contains('Obs.:', na=False)]
        df_ia = df_ia.groupby(["ds_mun", "sg_uf"], as_index=False).sum(numeric_only=True)
        
        # Renomear as colunas de métricas
        ultimas_3 = list(df_ia.columns[-3:])
        df_ia.rename(columns={ultimas_3[0]: "nprojetos", ultimas_3[1]: "ninstituicoes", ultimas_3[2]: "nbeneficiados"}, inplace=True)

        return df_ia

    except Exception as e:
        print(f"Erro ao carregar a planilha do ano {year}: {e}")
        return pd.DataFrame()

# --- Seção 2: Início do Script Principal e Análise de Dados ---

# Caminhos dos arquivos
rais_file_path = 'data/MT/tabelas-rais-2024-parcial.xlsx'
ia_file_path = 'data/Projetos_de_Atuac807a771o_-_IA_-_2020_a_2025 (1).xlsx'
year_to_process = 2024

# Carregar os dataframes utilizando as funções de apoio.
df_rais = load_rais_tabela4(rais_file_path)
df_ia = load_ia_projetos(ia_file_path, year=year_to_process)

# Verifica se os dataframes foram carregados corretamente.
if df_rais.empty or df_ia.empty:
    print("Não foi possível carregar um ou ambos os dataframes. O script será encerrado.")
else:
    # Padronizar as colunas de nome das cidades para a junção.
    df_rais['ds_mun_std'] = df_rais['ds_mun'].apply(standardize_name)
    df_ia['ds_mun_std'] = df_ia['ds_mun'].apply(standardize_name)

    # Realizar o merge (junção) dos dataframes usando a coluna de nome padronizada.
    # O `how='inner'` garante que apenas os municípios presentes em ambas as bases
    # sejam mantidos na análise.
    df_combinado = pd.merge(df_rais, df_ia, on='ds_mun_std', how='inner', suffixes=('_rais', '_ia'))

    if df_combinado.empty:
        print("O merge resultou em um dataframe vazio. Verifique a compatibilidade dos nomes de cidade.")
    else:
        # Calcular os totais de emprego por setor econômico (RAIS) nas cidades em comum.
        setores_2024_rais = ['Agropecuaria_2024', 'Industria_2024', 'Construcao_2024',
                            'Comercio_2024', 'Servicos_2024']
        total_por_setor_rais = df_combinado[setores_2024_rais].sum().reset_index()
        total_por_setor_rais.columns = ['Setor', 'Total_2024_RAIS']
        total_por_setor_rais['Setor'] = total_por_setor_rais['Setor'].str.replace('_2024', '')

        # Calcular os totais de projetos, instituições e beneficiados (IA) nas cidades em comum.
        setores_2024_ia = ['nprojetos', 'ninstituicoes', 'nbeneficiados']
        total_por_setor_ia = df_combinado[setores_2024_ia].sum().reset_index()
        total_por_setor_ia.columns = ['Setor', 'Total_2024_IA']

        # Exibir os resultados para validação e referência.
        print(f"Cidades em comum entre os arquivos RAIS e Projetos IA para o ano {year_to_process}:")
        print(df_combinado[['ds_mun_rais', 'ds_mun_ia', 'sg_uf_rais']])
        
        print("\n------------------------------------------------\n")
        print("DataFrame com os valores totais de 2024 por setor econômico (RAIS):")
        print(total_por_setor_rais)
        
        print("\n------------------------------------------------\n")
        print("DataFrame com os valores totais de 2024 para os projetos IA:")
        print(total_por_setor_ia)

# --- Seção 3: Geração do Gráfico de Pizza ---
# Esta seção utiliza os dados processados para gerar uma visualização que mostra
# a distribuição percentual do emprego por setor.

if not df_combinado.empty:
    
    # Prepara os dados do total de empregos por setor.
    setores_2024_rais = ['Agropecuaria_2024', 'Industria_2024', 'Construcao_2024',
                        'Comercio_2024', 'Servicos_2024']
    total_por_setor_rais = df_combinado[setores_2024_rais].sum().reset_index()
    total_por_setor_rais.columns = ['Setor', 'Total_2024_RAIS']
    total_por_setor_rais['Setor'] = total_por_setor_rais['Setor'].str.replace('_2024', '')

    # Extrai os rótulos e tamanhos das fatias do gráfico de pizza.
    labels = total_por_setor_rais['Setor']
    sizes = total_por_setor_rais['Total_2024_RAIS']

    # Cria e exibe o gráfico de pizza.
    plt.figure(figsize=(10, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title('Distribuição de Empregos por Setor Econômico (2024)', fontsize=16, fontweight='bold')
    plt.ylabel('') # Remove o rótulo do eixo y para o gráfico de pizza
    plt.show()