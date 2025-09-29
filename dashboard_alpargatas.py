import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from PIL import Image
import io
import os # <-- ADICIONE ESTA LINHA


# --- Configuração da Página e Estilo ---
st.set_page_config(
    page_title="BI de Diagnóstico da Educação Profissionalizante - Instituto Alpargatas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para injetar CSS customizado com a identidade visual do Instituto Alpargatas
# Função para injetar CSS customizado com a identidade visual do Instituto Alpargatas
# Função para injetar CSS customizado com a identidade visual do Instituto Alpargatas

def apply_custom_css():
    """Aplica a identidade visual do Instituto Alpargatas via CSS."""
    st.markdown("""
        <style>
            /* Cores Primárias da Marca */
            :root {
                --primary-orange: #F26522;
                --corporate-blue: #0055A4;
                --sustainability-green: #009E4D;
                --light-gray-bg: #F0F2F6;
                --dark-text: #333333;
            }

            /* Fundo principal */
            .main .block-container {
                background-color: #FFFFFF;
            }

            /* Barra Lateral */
            [data-testid="stSidebar"] {
                background-color: var(--light-gray-bg);
            }

            /* Títulos (funciona com st.title, st.header, st.subheader e markdown ##) */
            h1, h2, h3,
            [data-testid="stMarkdown"] h1,
            [data-testid="stMarkdown"] h2 {
                color: var(--primary-orange) !important;
                font-weight: bold;
            }
            h3, [data-testid="stMarkdown"] h3 {
                color: var(--corporate-blue) !important;
                font-weight: bold;
            }

            /* Texto */
            body, p, .stMarkdown {
                color: var(--dark-text);
            }

            /* Métricas (KPIs) */
            [data-testid="stMetric"] {
                background-color: #FFFFFF;
                border: 1px solid var(--light-gray-bg);
                border-left: 5px solid var(--primary-orange);
                border-radius: 8px;
                padding: 15px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            [data-testid="stMetricLabel"] {
                font-weight: bold;
            }

            /* Botões e Widgets */
            .stButton>button {
                background-color: var(--corporate-blue);
                color: white;
                border-radius: 5px;
            }
            .stRadio [role="radiogroup"] {
                border: 1px solid var(--corporate-blue);
                border-radius: 8px;
                padding: 10px;
            }
        </style>
    """, unsafe_allow_html=True)





# --- Funções de Carregamento e Processamento de Dados ---
@st.cache_data
def load_vulnerability_data():
    """
    Carrega e limpa os dados de vulnerabilidade social e educacional.
    
    
    Dados extraídos das análises de analise_educacional.py

    """
    data = {
        'municipio': ['Itatuba', 'Mogeiro', 'Ingá', 'Bananeiras', 'Alagoa Nova', 'Serra Redonda', 'Caturité', 'Lagoa Seca', 'Queimadas', 'Santa Rita', 'Guarabira', 'Carpina', 'Campina Grande', 'João Pessoa', 'Montes Claros', 'Cabaceiras'],
        'uf': ['PB', 'PB', 'PB', 'PB', 'PB', 'PB', 'PB', 'PB', 'PB', 'PB', 'PB', 'PE', 'PB', 'PB', 'MG', 'PB'],
        'ive': [0.259, 0.235, 0.213, 0.207, 0.197, 0.157, 0.141, 0.139, 0.130, 0.125, 0.125, 0.112, 0.065, 0.042, 0.036, 0.013],
        'taxa_analfabetismo': [0.278, 0.254, 0.252, 0.250, 0.218, 0.216, 0.164, 0.154, 0.158, 0.144, 0.147, 0.123, 0.080, 0.061, 0.043, 0.093],
        'taxa_cobertura_eja': [0.070, 0.074, 0.157, 0.170, 0.098, 0.275, 0.137, 0.099, 0.178, 0.128, 0.153, 0.089, 0.188, 0.312, 0.162, 0.860],
        'perfil_cluster': ['Força de Trabalho (Adultos)', 'Força de Trabalho (Adultos)', 'Força de Trabalho (Adultos)', 'Força de Trabalho (Adultos)', 'Força de Trabalho (Adultos)', 'Força de Trabalho (Adultos)', 'Força de Trabalho (Adultos)', 'Força de Trabalho (Adultos)', 'Força de Trabalho (Adultos)', 'Analfabetismo Estrutural (Idosos)', 'Analfabetismo Estrutural (Idosos)', 'Analfabetismo Estrutural (Idosos)', 'Analfabetismo Estrutural (Idosos)', 'Analfabetismo Estrutural (Idosos)', 'Analfabetismo Estrutural (Idosos)', 'Analfabetismo Estrutural (Idosos)'],
        'aderente_politica': [False, False, True, True, False, True, False, True, True, True, True, False, True, True, True, True],
        'lat': [-7.35, -7.24, -7.24, -6.75, -7.06, -7.18, -7.38, -7.16, -7.22, -7.13, -6.85, -7.85, -7.23, -7.12, -16.73, -7.50],
        'lon': [-35.65, -35.58, -35.79, -35.63, -35.75, -35.88, -36.05, -35.83, -35.93, -34.97, -35.49, -35.25, -35.88, -34.86, -43.86, -36.28]
    }
    df = pd.DataFrame(data)
    df['municipio_upper'] = df['municipio'].str.upper()
    df['municipio_uf'] = df['municipio'] + ' (' + df['uf'] + ')'
    return df

@st.cache_data
def load_courses_data():
    """Carrega e processa os dados de cursos técnicos."""
   
    # (O conteúdo da sua string de dados de cursos permanece o mesmo)
    df = pd.read_csv('cursos_encontrados.csv', sep=';')
    
    df['MUNICÍPIO_UPPER'] = df['MUNICÍPIO'].str.strip().str.upper()
    return df

@st.cache_data
# REMOVA A FUNÇÃO ANTIGA:
# @st.cache_data
# def load_economic_data():
#     """Carrega dados da matriz econômica local."""
#     data = { ... }
#     df = pd.DataFrame(data)
#     ...
#     return df

# ADICIONE ESTA NOVA FUNÇÃO NO LUGAR:
@st.cache_data
def load_rais_economic_data(file_path):
    """
    Carrega e processa dados de empregos por setor a partir de um arquivo da RAIS.
    """
    try:
        df = pd.read_excel(file_path, sheet_name='TABELA 4', skiprows=12)

        # Renomeia colunas e seleciona as de interesse
        df.rename(columns={
            'Município': 'municipio', 'UF': 'uf', 'Unnamed: 5': 'Agropecuaria',
            'Unnamed: 9': 'Industria', 'Unnamed: 13': 'Construcao',
            'Unnamed: 17': 'Comercio', 'Unnamed: 21': 'Servicos'
        }, inplace=True)
        
        colunas_setores = ['Agropecuaria', 'Industria', 'Construcao', 'Comercio', 'Servicos']
        df_rais = df[['municipio', 'uf'] + colunas_setores].copy()

        # Limpa e converte os dados para formato numérico
        df_rais.dropna(subset=['municipio', 'uf'], inplace=True)
        for setor in colunas_setores:
            df_rais[setor] = pd.to_numeric(df_rais[setor], errors='coerce').fillna(0).astype(int)

        # Transforma os dados do formato "wide" para "long"
        df_long = df_rais.melt(
            id_vars=['municipio', 'uf'],
            value_vars=colunas_setores,
            var_name='setor',
            value_name='vagas'
        )
        
        # Cria a coluna 'municipio_upper' necessária para a Fase 4
        df_long['municipio_upper'] = df_long['municipio'].str.strip().str.upper()
        return df_long

    except FileNotFoundError:
        st.error(f"Arquivo da RAIS não encontrado em '{file_path}'. Verifique o caminho e o nome do arquivo.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao ler o arquivo da RAIS: {e}. Verifique o formato da planilha.")
        return pd.DataFrame()

def get_sector_to_eixo_mapping():
    """Mapeia setores econômicos para eixos tecnológicos."""
    return {
        'Serviços': ['TURISMO, HOSPITALIDADE E LAZER', 'GESTÃO E NEGÓCIOS', 'INFORMAÇÃO E COMUNICAÇÃO', 'AMBIENTE E SAÚDE'],
        'Comércio': ['GESTÃO E NEGÓCIOS'],
        'Agropecuária': ['RECURSOS NATURAIS', 'PRODUÇÃO ALIMENTÍCIA'],
        'Industria': ['CONTROLE E PROCESSOS INDUSTRIAIS', 'PRODUÇÃO INDUSTRIAL'],
        'Construcao': ['INFRAESTRUTURA'] 
    }

# --- Funções para Renderizar as Páginas ("Fases") ---

def show_introduction():
    """Exibe a página de introdução."""
    st.title("Plataforma de Diagnóstico para Expansão da Educação Profissionalizante")
    st.subheader("Instituto Alpargatas")
    st.markdown("""
        Bem-vindo à ferramenta de Business Intelligence (BI) do Instituto Alpargatas, projetada para apoiar a tomada de decisão estratégica na expansão da Educação de Jovens e Adultos (EJA).
        
        Esta plataforma consolida e analisa dados de vulnerabilidade social, educacional e econômica para identificar os municípios com maior potencial de impacto para novas iniciativas de EJA.
        
        **Objetivos da Plataforma:**
        - **Identificar Prioridades:** Apontar municípios com alta vulnerabilidade e baixa cobertura de EJA.
        - **Entender Perfis:** Segmentar os municípios para direcionar as estratégias de abordagem.
        - **Analisar Maturidade:** Avaliar a prontidão institucional dos municípios para parcerias.
        - **Alinhar Vocações:** Cruzar a oferta de cursos técnicos com a demanda da economia local.
        
        Utilize o menu à esquerda para navegar pelas quatro fases da análise.
    """)
    st.info("**Como usar:** Selecione uma das fases no menu lateral para iniciar a sua análise.")

def get_color_for_ive(ive):
    """Retorna uma cor baseada no valor do IVE para o mapa."""
    if ive > 0.2:
        return 'red'
    elif ive > 0.1:
        return 'orange'
    else:
        return 'green'

def show_fase1(df):
    """
    Exibe a Fase 1: Análise Geoespacial e de Indicadores, agora com mais gráficos.
    """
    st.header("Fase 1: Análise Geoespacial e de Indicadores")
    st.markdown("Esta fase oferece uma visão geral dos principais indicadores de vulnerabilidade. O objetivo é identificar geograficamente as áreas mais críticas e entender a distribuição dos desafios.")

    # KPIs Principais
    st.subheader("Indicadores-Chave (KPIs)")
    col1, col2, col3 = st.columns(3)
    col1.metric("IVE Médio", f"{df['ive'].mean():.3f}", help="Média do Índice de Vulnerabilidade à Exclusão nos municípios analisados.")
    col2.metric("Analfabetismo Médio", f"{df['taxa_analfabetismo'].mean():.1%}", help="Média da Taxa de Analfabetismo.")
    col3.metric("Cobertura EJA Média", f"{df['taxa_cobertura_eja'].mean():.1%}", help="Média da Taxa de Cobertura da EJA.")
    
    st.markdown("---")

    # Análise Gráfica Comparativa
    st.subheader("Análise Comparativa dos Indicadores")
    
    # Gráfico 1: Ranking de IVE
    st.markdown("#### Ranking de Vulnerabilidade (IVE)")
    st.markdown("O gráfico abaixo ordena os municípios pelo **Índice de Vulnerabilidade à Exclusão (IVE)**. Valores mais altos indicam maior vulnerabilidade, sinalizando prioridade na análise.")
    
    fig_ive = px.bar(
        df.sort_values('ive', ascending=False),
        x='ive',
        y='municipio_uf',
        orientation='h',
        title='Índice de Vulnerabilidade à Exclusão (IVE) por Município',
        labels={'ive': 'Índice de Vulnerabilidade (IVE)', 'municipio_uf': 'Município'},
        text='ive'
    )
    fig_ive.update_traces(
        marker_color='#F26522',  # Laranja do Instituto Alpargatas
        texttemplate='%{text:.3f}', 
        textposition='outside'
    )
    fig_ive.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_ive, use_container_width=True)

    # Gráfico 2: Correlação entre IVE e Analfabetismo
    st.markdown("#### Correlação: IVE vs. Taxa de Analfabetismo")
    st.markdown("Este gráfico de dispersão ajuda a visualizar a relação entre a vulnerabilidade e o analfabetismo. Municípios no quadrante superior direito representam os maiores desafios.")

    fig_scatter = px.scatter(
        df,
        x='taxa_analfabetismo',
        y='ive',
        text='municipio',
        title='Relação entre IVE e Taxa de Analfabetismo',
        labels={'taxa_analfabetismo': 'Taxa de Analfabetismo', 'ive': 'Índice de Vulnerabilidade (IVE)'},
        color_discrete_sequence=['#0055A4'] # Azul Corporativo
    )
    fig_scatter.update_traces(textposition='top center')
    fig_scatter.update_layout(xaxis_tickformat=".1%")
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

    # Mapa Interativo Aprimorado
    st.subheader("Mapa Temático de Vulnerabilidade")
    st.markdown("""
    O mapa interativo abaixo consolida os indicadores de forma geoespacial:
    - **Cor do Círculo:** Representa o nível do IVE (Vermelho: Alto, Laranja: Médio, Verde: Baixo).
    - **Tamanho do Círculo:** Proporcional à Taxa de Analfabetismo.
    
    Passe o mouse ou clique nos círculos para ver os detalhes de cada município.
    """)
    
    # Centralizar o mapa
    map_center = [df['lat'].mean(), df['lon'].mean()]
    m = folium.Map(location=map_center, zoom_start=7, tiles="CartoDB positron")

    for idx, row in df.iterrows():
        popup_html = f"""
        <b>Município:</b> {row['municipio_uf']}<br>
        <b>IVE:</b> {row['ive']:.3f}<br>
        <b>Analfabetismo:</b> {row['taxa_analfabetismo']:.1%}<br>
        <b>Cobertura EJA:</b> {row['taxa_cobertura_eja']:.1%}
        """
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=row['taxa_analfabetismo'] * 70,  # Fator de escala para o raio
            color=get_color_for_ive(row['ive']),
            fill=True,
            fill_color=get_color_for_ive(row['ive']),
            fill_opacity=0.6,
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(m)

    st_folium(m, width='100%', height=500)

def show_fase2(df):
    """Exibe a Fase 2: Segmentação por Perfis de Analfabetismo."""
    st.header("Fase 2: Segmentação por Perfis de Analfabetismo")
    st.markdown("""
        Com base nos dados demográficos e educacionais, os municípios foram agrupados em dois perfis principais. 
        Entender o perfil dominante em cada localidade é crucial para customizar a abordagem e a oferta de EJA.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Perfil 1: Força de Trabalho (Adultos)")
        st.info("Caracterizado por uma maior concentração de analfabetismo entre adultos (25-59 anos) que estão no mercado de trabalho ou buscando inserção.")
        
        st.markdown("**Características:**")
        st.markdown("- **Público-alvo:** Adultos em idade produtiva.")
        st.markdown("- **Principal Barreira:** Falta de tempo, necessidade de conciliar trabalho e estudo.")
        st.markdown("- **Estratégia Recomendada:** Foco em EJA Profissionalizante, horários flexíveis (noturno), e parcerias com empresas locais para incentivar a matrícula de funcionários.")
        
        with st.expander("Municípios com este perfil"):
            for mun in df[df['perfil_cluster'] == 'Força de Trabalho (Adultos)']['municipio_uf']:
                st.markdown(f"- {mun}")

    with col2:
        st.subheader("Perfil 2: Analfabetismo Estrutural (Idosos)")
        st.warning("Predominância de analfabetismo na população idosa (+60 anos), muitas vezes resultado de um histórico de exclusão educacional.")
        
        st.markdown("**Características:**")
        st.markdown("- **Público-alvo:** Idosos e adultos mais velhos, fora da força de trabalho ativa.")
        st.markdown("- **Principal Barreira:** Desmotivação, dificuldades de locomoção, e falta de programas específicos.")
        st.markdown("- **Estratégia Recomendada:** Foco em EJA como ferramenta de inclusão social e cidadania, alfabetização digital, e parcerias com centros de convivência e secretarias de assistência social.")

        with st.expander("Municípios com este perfil"):
            for mun in df[df['perfil_cluster'] == 'Analfabetismo Estrutural (Idosos)']['municipio_uf']:
                st.markdown(f"- {mun}")

def show_fase3(df):
    """Exibe a Fase 3: Análise de Maturidade Institucional."""
    st.header("Fase 3: Análise de Maturidade Institucional")
    st.markdown("""
        Esta análise classifica os municípios com base na sua **aderência a políticas públicas de educação** e na existência de programas de EJA estruturados. 
        Isso ajuda a definir a estratégia de entrada: em municípios 'aderentes', a expansão pode ser mais rápida; em 'não aderentes', é preciso um trabalho prévio de sensibilização.
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Municípios Aderentes (Alta Maturidade)")
        st.markdown("""
        Possuem políticas de EJA já estabelecidas e demonstram maior abertura e capacidade institucional para novas parcerias.
        - **Oportunidade:** Expansão e qualificação de programas existentes, implementação de projetos-piloto de EJA Profissionalizante.
        - **Facilidade:** Menor barreira de entrada, processos mais ágeis e stakeholders já engajados.
        """)

    with col2:
        st.subheader("❌ Municípios Não Aderentes (Baixa Maturidade)")
        st.markdown("""
        Não possuem políticas claras ou programas ativos de EJA, indicando uma necessidade de construção de base e sensibilização.
        - **Oportunidade:** Grande potencial de impacto e visibilidade.
        - **Desafio Operacional:** Exigem maior esforço na sensibilização de gestores públicos, articulação institucional e construção de processos do zero.
        """)
        
    st.markdown("---")
    st.subheader("Listagem de Municípios por Status")
    
    col_sim, col_nao = st.columns(2)
    
    with col_sim:
        with st.expander(f"✅ **Municípios Aderentes** ({len(df[df['aderente_politica'] == True])})"):
            for mun in df[df['aderente_politica'] == True]['municipio_uf']:
                st.markdown(f"- {mun}")
                
    with col_nao:
        with st.expander(f"❌ **Municípios Não Aderentes** ({len(df[df['aderente_politica'] == False])})"):
            for mun in df[df['aderente_politica'] == False]['municipio_uf']:
                st.markdown(f"- {mun}")

# "Fase 4: Alinhamento Estratégico de Cursos" # Mantenha esta linha
def show_fase4(df_vulnerability, df_economic, df_courses):
    """Exibe a Fase 4: Alinhamento Estratégico de Cursos."""
    st.header("Fase 4: Alinhamento Estratégico de Cursos")
    st.markdown("Esta análise cruza a **matriz econômica local** (setores que mais empregam) com a **oferta de cursos técnicos**, gerando recomendações para maximizar a empregabilidade dos egressos da EJA.")
    
    municipios_options = sorted(df_vulnerability['municipio'].unique())
    selected_municipio = st.selectbox(
        "Selecione um município para análise de alinhamento:",
        options=municipios_options
    )
    
    if selected_municipio:
        municipio_upper = selected_municipio.upper()
        df_eco_mun = df_economic[df_economic['municipio_upper'] == municipio_upper]
        df_crs_mun = df_courses[df_courses['MUNICÍPIO_UPPER'] == municipio_upper]
        
        if df_eco_mun.empty:
            st.warning(f"Não há dados sobre a matriz econômica disponíveis para {selected_municipio}.")
            return
            
        st.subheader(f"Análise de Sinergia para: {selected_municipio}")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("**Matriz Econômica Local**")
            fig_eco = px.pie(df_eco_mun, names='setor', values='vagas',
                             title=f"Setores Empregadores", hole=0.4,
                             color_discrete_sequence=px.colors.sequential.Oranges_r)
            fig_eco.update_traces(textinfo='percent+label', showlegend=False)
            st.plotly_chart(fig_eco, use_container_width=True)
            
        with col2:
            st.markdown("**Alinhamento Estratégico e Recomendações**")
            top_setores = df_eco_mun.sort_values('vagas', ascending=False).head(3)['setor'].tolist()
            mapping = get_sector_to_eixo_mapping()
            eixos_recomendados = list(set([eixo for setor in top_setores for eixo in mapping.get(setor, [])]))
            
            if not eixos_recomendados:
                st.info("Não foi possível gerar recomendações automáticas de eixos tecnológicos para os setores deste município.")
            else:
                st.write(f"Com base nos principais setores (**{', '.join(top_setores)}**), os eixos tecnológicos com maior sinergia são:")
                for eixo in eixos_recomendados:
                    st.markdown(f"- **{eixo}**")
                
                cursos_recomendados = df_crs_mun[df_crs_mun['EIXO TECNOLÓGICO'].isin(eixos_recomendados)]
                
                if not cursos_recomendados.empty:
                    st.success("✅ **Cursos com Alto Alinhamento Estratégico:**")
                    for _, row in cursos_recomendados.iterrows():
                        st.write(f" - **{row['CURSO']}** ({row['MODALIDADE']}) - *{row['UNIDADE DE ENSINO']}*")
                else:
                    st.warning(f"⚠️ **Alerta de Desalinhamento:** Nenhum curso técnico ofertado corresponde aos eixos tecnológicos demandados pela economia local. Identificada oportunidade para desenvolvimento de novos programas de formação.")
                    
        st.markdown("---")
        with st.expander(f"Consultar todos os {len(df_crs_mun)} cursos técnicos disponíveis em {selected_municipio}"):
            if df_crs_mun.empty:
                st.write("Nenhum curso técnico cadastrado para este município na base de dados.")
            else:
                st.dataframe(df_crs_mun[['CURSO', 'EIXO TECNOLÓGICO', 'MODALIDADE', 'UNIDADE DE ENSINO']])

# --- Estrutura Principal da Aplicação ---

# Aplicar o estilo visual
apply_custom_css()
######

df_vulnerability = load_vulnerability_data()
df_courses = load_courses_data()

# --- INÍCIO DA MODIFICAÇÃO ---
# ATENÇÃO: Crie uma pasta 'dados' ao lado do seu script e coloque o arquivo da RAIS nela.
# O nome do arquivo deve ser 'rais_dados_economicos.xlsx' ou você deve alterar o nome abaixo.
rais_file_path = 'tabelas-rais-2024-parcial.xlsx'
df_economic = load_rais_economic_data(rais_file_path)


#######
# Configuração da Barra Lateral (Sidebar)
with st.sidebar:
    try:
        # Certifique-se de que o arquivo 'logo_IA.png' está na mesma pasta do seu script
        st.image("logo_IA.png", use_container_width =True)
    except Exception as e:
        st.warning("Arquivo 'logo_IA.png' não encontrado. A logo não será exibida.")
    
    st.markdown("## **BI de Diagnóstico da Educação Profissionalizante**")
    st.markdown("Plataforma de Análise Estratégica")
    st.markdown("---")
    
    selecao = st.radio(
        "Navegar pelas fases da análise:",
        [
            "Introdução",
            "Fase 1: Análise Geoespacial e de Indicadores",
            "Fase 2: Segmentação por Perfis de Analfabetismo",
            "Fase 3: Análise de Maturidade Institucional",
            "Fase 4: Alinhamento Estratégico de Cursos"
        ],
        key="navigation"
    )

# Lógica para exibir a página selecionada
if selecao == "Introdução":
    show_introduction()
elif selecao == "Fase 1: Análise Geoespacial e de Indicadores":
    show_fase1(df_vulnerability)
elif selecao == "Fase 2: Segmentação por Perfis de Analfabetismo":
    show_fase2(df_vulnerability)
elif selecao == "Fase 3: Análise de Maturidade Institucional":
    show_fase3(df_vulnerability)
elif selecao == "Fase 4: Alinhamento Estratégico de Cursos":
    show_fase4(df_vulnerability, df_economic, df_courses)
