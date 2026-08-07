"""Estilos institucionales del SVP-IPS (azul/gris)."""


COLOR_AZUL = "#0033A0"
COLOR_AZUL_CLARO = "#1F4FB8"
COLOR_GRIS = "#6C757D"
COLOR_GRIS_CLARO = "#F2F4F7"
COLOR_VERDE = "#2E8B57"
COLOR_ROJO = "#C0392B"
COLOR_AMARILLO = "#D4A017"


def aplicar_estilos() -> None:
    """Inyecta CSS institucional en la pagina Streamlit."""
    import streamlit as st

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {COLOR_GRIS_CLARO};
        }}
        h1, h2, h3 {{
            color: {COLOR_AZUL};
        }}
        .stMetric > div {{
            background-color: #FFFFFF;
            border: 1px solid {COLOR_AZUL_CLARO};
            border-left: 6px solid {COLOR_AZUL};
            border-radius: 6px;
            padding: 12px 16px;
        }}
        [data-testid="stSidebar"] {{
            background-color: #FFFFFF;
            border-right: 2px solid {COLOR_AZUL};
        }}
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {{
            color: {COLOR_AZUL};
        }}
        .stButton > button[kind="primary"] {{
            background-color: {COLOR_AZUL};
            color: #FFFFFF;
            border: none;
        }}
        .stButton > button[kind="primary"]:hover {{
            background-color: {COLOR_AZUL_CLARO};
            color: #FFFFFF;
        }}
        div[data-testid="stAlert"] {{
            border-radius: 6px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
