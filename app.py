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

background:#0F172A;

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

div[data-testid="metric-container"]{

background:white;

padding:10px;

border-radius:18px;

border:1px solid #E5E7EB;

box-shadow:
0 4px 12px rgba(0,0,0,.06);

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
# CARREGAR
# ==================================================

ARQUIVO = "data/Controle_Financeiro_Pequenas_Empresas.xlsx"


@st.cache_data
def carregar():

    vendas = pd.read_excel(
        ARQUIVO,
        sheet_name="Vendas"
    )

    despesas = pd.read_excel(
        ARQUIVO,
        sheet_name="Despesas"
    )

    return vendas, despesas


vendas, despesas = carregar()


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
"Despesas"
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


st.divider()

st.caption(
"InsightFinance • versão 2.1"
)