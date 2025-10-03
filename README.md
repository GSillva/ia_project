# 📊 Projeto IA - Dashboard Alpargatas

Este repositório contém um conjunto de análises e um dashboard interativo desenvolvido para a **Alpargatas**, com foco em dados educacionais, de mercado de trabalho e cursos. O arquivo principal é o `dashboard_alpargatas.py`, enquanto os demais scripts e notebooks foram utilizados nas análises que alimentam este painel.

---

## 🚀 Instalação

1. **Clonar o repositório:**

   ```bash
   git clone https://github.com/GSillva/ia_project.git
   cd ia_project
   ```

2. **Criar ambiente virtual (opcional, mas recomendado):**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. **Instalar dependências:**

   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Executando o Dashboard

O dashboard principal foi desenvolvido em Python, utilizando bibliotecas de análise de dados e visualização.

```bash
streamlit run dashboard_alpargatas.py
```

Após rodar, acesse o link indicado no terminal (geralmente `http://127.0.0.1:8050/`) para visualizar o dashboard no navegador.

---

## ▶️ Acesso aos dados de: RAIS.py, ideb_f.py, caged_f

'''
As bases de dados que eles solicitam devem estar em uma pasta 'data' conforme especificado no código, bases não foram possíveis de serem carregadas nesse repositório.

Para rodar os códigos faça no terminal: python código.py
'''
## 📂 Estrutura dos Arquivos

* **`dashboard_alpargatas.py`** → Arquivo principal do projeto. Contém a aplicação interativa (dashboard).
* **`analise_educacional.py`** → Script com análises exploratórias de dados educacionais.
* **`RAIS.py`** → Processamento e análise de dados da RAIS (Relação Anual de Informações Sociais).
* **`ideb_f.py`** → Análises relacionadas ao IDEB junto ao Instituto IA.
* **`caged_f.py`** → Análises relacionadas a programas de formação tecnica do Instituto IA.
* **`buscar_cursos.py`** → Script para buscar e organizar informações sobre cursos.
* **`Alpargatas.ipynb`** → Notebook Jupyter com experimentações e análises adicionais.
* **Arquivos de dados (`.csv`, `.xlsx`)** → Bases utilizadas nas análises e no dashboard.

---

## 🛠️ Notas

* Certifique-se de ter o **Python 3.8+** instalado.
* Algumas análises dependem de arquivos de dados locais (já presentes no repositório).
* Recomenda-se utilizar o ambiente virtual para evitar conflitos de dependências.

---

## 📌 Autores

Projeto desenvolvido por **GSillva** e colaboradores, com foco em integração de dados para apoio estratégico na Alpargatas.
