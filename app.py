import streamlit as st
import pandas as pd
import yaml
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

# ==================================================
# CONFIG
# ==================================================

st.set_page_config(
    page_title="InsightFinance",
    layout="wide",
    page_icon="📊"
)
# ==================================================
# LOGIN
# ==================================================

with open("usuarios.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"]
)

authenticator.login()

if st.session_state["authentication_status"] is False:
    st.error("Usuário ou senha incorretos")
    st.stop()

elif st.session_state["authentication_status"] is None:
    st.warning("Digite login e senha")
    st.stop()

elif st.session_state["authentication_status"]:

    st.sidebar.success(
        f"Olá {st.session_state['name']}"
    )

    authenticator.logout(
        "Sair",
        "sidebar"
    )
# ==================================================
# ESTILO
# ==================================================

st.markdown("""

<style>

/* REMOVE ESPAÇO SUPERIOR DO STREAMLIT */

.block-container{

padding-top:1rem;
padding-bottom:0rem;

}

/* Fundo */

.main{

background:#F5F7FA;

}

/* Sidebar */

[data-testid="stSidebar"]{

background:
linear-gradient(
180deg,
#06111F,
#0F172A,
#1E293B
);

}

[data-testid="stSidebar"] *{

color:white;

}

/* Título */

h1{

font-size:34px;
font-weight:800;
color:#0F172A;

margin-bottom:0;

}

/* KPIs */

/* KPIs */

div[data-testid="metric-container"]{

background:white;

padding:16px;

border-radius:18px;

border-left:5px solid #2563EB;

border:1px solid #E5E7EB;

box-shadow:
0 8px 20px rgba(0,0,0,.05);

}


/* Tabelas */

.stDataFrame{

background:white;

border-radius:14px;

padding:5px;

}

/* Alerta */

.stAlert{

border-radius:12px;

}

/* Subtítulos */

h3{

color:#1E293B;
font-weight:700;
margin-top:0;

}

/* ==========================
BOTÕES SIDEBAR
========================== */

.stButton > button{

background:#1E293B;
color:white;

border:none;

border-radius:10px;

padding:8px 16px;

font-weight:600;

}

.stButton > button:hover{

background:#334155;

color:white;

}

/* Upload */

[data-testid="stFileUploader"]{

background:#1E293B;

border-radius:10px;

padding:10px;

color:white;

}

/* BOTÃO INTERNO DO UPLOAD */

[data-testid="stFileUploader"] button{

background:#1E293B !important;

color:white !important;

border:none !important;

border-radius:10px !important;

font-weight:600;

}

/* Hover */

[data-testid="stFileUploader"] button:hover{

background:#334155 !important;

color:white !important;

}
                      
</style>

""", unsafe_allow_html=True)

# ==================================================
# CABEÇALHO
# ==================================================

from datetime import datetime

col1,col2,col3 = st.columns([5,2,2])

with col1:

    st.title("📊 InsightFinance")

    st.caption(
        "Gestão financeira inteligente"
    )

with col2:

    st.metric(
        "Status",
        "Saudável"
    )

with col3:

    st.metric(
        "Data",
        datetime.today().strftime("%d/%m/%Y")
    )

# ==================================================
# UPLOAD EXCEL
# ==================================================

arquivo_upload = st.sidebar.file_uploader(

    "Enviar planilha",

    type=["xlsx"]

)


if "arquivo_atual" not in st.session_state:

    st.session_state.arquivo_atual = (
        "dados/Controle_Financeiro_Pequenas_Empresas.xlsx"
    )


if arquivo_upload is not None:

    st.session_state.arquivo_atual = (
        arquivo_upload
    )

    st.sidebar.success(
        "Planilha carregada"
    )


ARQUIVO = (
    st.session_state.arquivo_atual
)

# ==================================================
# CARREGAR
# ==================================================

@st.cache_data
def carregar(arquivo):

    vendas = pd.read_excel(

        arquivo,

        sheet_name="Vendas"

    )

    despesas = pd.read_excel(

        arquivo,

        sheet_name="Despesas"

    )

    return vendas, despesas

vendas, despesas = carregar(
    ARQUIVO
)

# ==================================================
# LIMPEZA
# ==================================================

vendas = vendas.dropna(
subset=["Cliente"]
)

despesas = despesas.dropna(
subset=["Categoria"]
)

vendas["Valor Total"] = pd.to_numeric(
vendas["Valor Total"],
errors="coerce"
).fillna(0)

despesas["Valor"] = pd.to_numeric(
despesas["Valor"],
errors="coerce"
).fillna(0)

# ==================================================
# MENU
# ==================================================

pagina = st.sidebar.radio(

"Menu",

[
"Dashboard",

"Vendas",

"Despesas",

"Guia"

]

)

# ==================================================
# DASHBOARD
# ==================================================

if pagina == "Dashboard":

    receita = vendas["Valor Total"].sum()
    gasto = despesas["Valor"].sum()
    lucro = receita - gasto

    margem = (
        lucro/receita*100
        if receita > 0
        else 0
    )

    ticket = (
        receita/len(vendas)
        if len(vendas)>0
        else 0
    )

    st.subheader("Resumo Financeiro")

    c1,c2,c3,c4,c5 = st.columns(5)

    c1.metric("Receita",f"R$ {receita:,.0f}")
    c2.metric("Despesas",f"R$ {gasto:,.0f}")
    c3.metric("Lucro",f"R$ {lucro:,.0f}")
    c4.metric("Margem",f"{margem:.1f}%")
    c5.metric("Ticket",f"R$ {ticket:,.0f}")

    if lucro > 0:
        st.success("🟢 Situação financeira saudável")
    else:
        st.error("🔴 Empresa em prejuízo")

    ranking = (

        vendas
        .groupby("Cliente")
        ["Valor Total"]
        .sum()
        .sort_values(
            ascending=False
        )

    )

    graf = (

        despesas
        .groupby("Categoria")
        ["Valor"]
        .sum()

    )

    col1,col2,col3 = st.columns([1,1,1])

    with col1:

        with st.container(border=True):

            st.subheader("🏆 Clientes")

            st.bar_chart(
                ranking,
                height=150
            )

    with col2:

        with st.container(border=True):

            st.subheader("💸 Despesas")

            st.bar_chart(
                graf,
                height=150
            )

    with col3:

        with st.container(border=True):

            st.subheader(
                "📋 Últimos"
            )

            st.dataframe(

    vendas[
        ["Cliente","Produto","Valor Total"]
    ].tail(5),

    height=170,

    use_container_width=True
)
# ==================================================
# VENDAS
# ==================================================

elif pagina == "Vendas":

    st.subheader(
        "📋 Histórico de vendas"
    )

    st.dataframe(

        vendas,

        use_container_width=True

    )

# ==================================================
# DESPESAS
# ==================================================

elif pagina == "Despesas":

    st.subheader(
        "💸 Histórico despesas"
    )

    st.dataframe(

        despesas,

        use_container_width=True

    )

elif pagina == "Guia":

    st.header("📘 Como usar")

    st.info(
"""
1 Atualize a planilha Excel

2 Salve o arquivo

3 Atualize o sistema

4 Consulte Dashboard
"""
    )

    with open(
"dados/Controle_Financeiro_Pequenas_Empresas.xlsx",
"rb"
    ) as f:

        st.download_button(

"📥 Baixar planilha modelo",

data=f,

file_name="Modelo_InsightFinance.xlsx"

        )

