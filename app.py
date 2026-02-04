import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# --- Estilo customizado dos filtros (multiselect) ---
st.markdown("""
<style>
/* Tag selecionada */
span[data-baseweb="tag"] {
    background-color: #21B4D9 !important;
    color: white !important;
}

/* Texto dentro da tag */
span[data-baseweb="tag"] span {
    color: white !important;
}

/* Ícone X (remover) */
span[data-baseweb="tag"] svg {
    fill: white !important;
}

/* Hover */
span[data-baseweb="tag"]:hover {
    background-color: #1aa3c4 !important;
}
</style>
""", unsafe_allow_html=True)

# --- Carregamento dos dados ---
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# --- Valores disponíveis para os filtros ---
anos_disponiveis = sorted(df['ano'].unique())
senioridades_disponiveis = sorted(df['senioridade'].unique())
contratos_disponiveis = sorted(df['contrato'].unique())
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())

# --- Função para selecionar todos os filtros ---
def selecionar_todos():
    st.session_state.filtro_ano = anos_disponiveis
    st.session_state.filtro_senioridade = senioridades_disponiveis
    st.session_state.filtro_contrato = contratos_disponiveis
    st.session_state.filtro_tamanho = tamanhos_disponiveis

# --- Inicialização do session_state ---
if "filtro_ano" not in st.session_state:
    st.session_state.filtro_ano = anos_disponiveis

if "filtro_senioridade" not in st.session_state:
    st.session_state.filtro_senioridade = senioridades_disponiveis

if "filtro_contrato" not in st.session_state:
    st.session_state.filtro_contrato = contratos_disponiveis

if "filtro_tamanho" not in st.session_state:
    st.session_state.filtro_tamanho = tamanhos_disponiveis    

# --- Barra Lateral (Filtros) ---
st.sidebar.header("Filtros 🔎")
st.sidebar.caption(
    "Use os filtros abaixo para explorar os dados salariais "
    "por ano, senioridade, contrato e tamanho da empresa."
)
st.sidebar.markdown("---")

anos_selecionados = st.sidebar.multiselect(
    "Ano",
    anos_disponiveis,
    key="filtro_ano"
)

senioridades_selecionadas = st.sidebar.multiselect(
    "Senioridade",
    senioridades_disponiveis,
    key="filtro_senioridade"
)

contratos_selecionados = st.sidebar.multiselect(
    "Tipo de Contrato",
    contratos_disponiveis,
    key="filtro_contrato"
)

tamanhos_selecionados = st.sidebar.multiselect(
    "Tamanho da Empresa",
    tamanhos_disponiveis,
    key="filtro_tamanho"
)

st.sidebar.markdown("---")
st.sidebar.caption("Ações rápidas")

st.sidebar.button(
    "Selecionar todos os filtros",
    on_click=selecionar_todos
)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
st.title("Dashboard de Análise de Salários na Área de Dados (Kaique) 📊")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_comum = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

# --- Paleta de cores do Dashboard ---
COR_DESTAQUE = '#00FFEE'   
COR_PRINCIPAL = '#21B4D9'        
COR_SECUNDARIA = '#112EA6'       
COR_FORTE = '#B114D9'   

# Escala contínua (degradê)
escala_degrade = [
    COR_DESTAQUE,
    COR_PRINCIPAL,
    COR_SECUNDARIA,
    COR_FORTE
]

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''},
            color='usd', 
            color_continuous_scale=escala_degrade
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''},
            color_discrete_sequence=[COR_DESTAQUE]
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5,
            color_discrete_sequence=[
                COR_DESTAQUE,
                COR_SECUNDARIA,
                COR_FORTE,
            ]
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index()

        grafico_paises = px.choropleth(
            media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'},
            color_continuous_scale=escala_degrade
        )

        grafico_paises.update_layout(
            title_x=0.1,
            plot_bgcolor='#0E1117',
            paper_bgcolor='#0E1117',
            font=dict(color='white')
        )

        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")


# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)