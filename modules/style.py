"""Estilos institucionales del SVP-IPS (azul/gris).

Aplica selectores especificos de Streamlit (data-testid) para
sobreescribir el tema por defecto con la paleta institucional.
"""

import altair as alt


COLOR_AZUL_IPS = "#003B71"
COLOR_AZUL_CLARO = "#1F5DA8"
COLOR_AZUL_FONDO = "#EEF2F7"
COLOR_VERDE = "#2E7D32"
COLOR_ROJO = "#C62828"
COLOR_GRIS = "#5F6B7A"
COLOR_GRIS_CLARO = "#F4F6F9"


def tema_altair() -> alt.theme.ThemeConfig:
    """Tema Altair claro alineado a la paleta institucional."""
    return alt.theme.ThemeConfig(
        {
            "config": {
                "view": {"fill": COLOR_GRIS_CLARO, "stroke": "transparent"},
                "background": COLOR_GRIS_CLARO,
                "axis": {
                    "domainColor": COLOR_GRIS,
                    "gridColor": "#D9DEE5",
                    "labelColor": "#1A1A1A",
                    "tickColor": COLOR_GRIS,
                    "titleColor": "#1A1A1A",
                    "labelFontSize": 12,
                    "titleFontSize": 13,
                    "titleFontWeight": "bold",
                },
                "title": {
                    "color": COLOR_AZUL_IPS,
                    "fontSize": 16,
                    "fontWeight": "bold",
                },
                "legend": {
                    "labelColor": "#1A1A1A",
                    "titleColor": COLOR_AZUL_IPS,
                },
                "bar": {"cornerRadiusEnd": 4},
            }
        }
    )


def activar_tema_altair() -> None:
    """Registra y activa el tema institucional (API moderna de Altair 5.5+/6.x)."""
    alt.theme.register("svp_ips", enable=True)(tema_altair)


def aplicar_estilos() -> None:
    """Inyecta CSS institucional con selectores especificos de Streamlit."""
    import streamlit as st

    st.markdown(
        f"""
        <style>
        /* === Base === */
        .stApp {{
            background-color: {COLOR_GRIS_CLARO};
            color: #1A1A1A;
        }}

        /* === Titulos (data-testid especifico) === */
        [data-testid="stHeading"] h1,
        h1.stMarkdown {{
            color: {COLOR_AZUL_IPS} !important;
            font-weight: 700 !important;
            letter-spacing: -0.5px;
        }}
        [data-testid="stHeading"] h2,
        [data-testid="stHeading"] h3 {{
            color: {COLOR_AZUL_IPS} !important;
        }}

        /* === Texto markdown === */
        .stMarkdown, .stMarkdown p, .stMarkdown li {{
            color: #1A1A1A;
        }}

        /* === Metric cards === */
        [data-testid="stMetric"] {{
            background-color: #FFFFFF;
            border: 1px solid #D9DEE5;
            border-top: 5px solid {COLOR_AZUL_IPS};
            border-radius: 8px;
            padding: 16px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }}
        [data-testid="stMetric"] label,
        [data-testid="stMetric"] [data-testid="stMetricLabel"] {{
            color: {COLOR_GRIS} !important;
            font-weight: 600;
            font-size: 0.85rem;
        }}
        [data-testid="stMetric"] [data-testid="stMetricValue"] {{
            color: {COLOR_AZUL_IPS} !important;
            font-weight: 700;
            font-size: 1.8rem;
        }}
        [data-testid="stMetric"] [data-testid="stMetricDelta"] {{
            color: {COLOR_VERDE} !important;
        }}

        /* === Sidebar === */
        [data-testid="stSidebar"] {{
            background-color: {COLOR_AZUL_FONDO};
            border-right: 3px solid {COLOR_AZUL_IPS};
        }}
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] .stMarkdown {{
            color: {COLOR_AZUL_IPS} !important;
        }}
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] small {{
            color: #1A1A1A !important;
        }}

        /* === Botones primary === */
        .stButton > button[kind="primary"] {{
            background-color: {COLOR_AZUL_IPS};
            color: #FFFFFF;
            border: none;
            font-weight: 600;
        }}
        .stButton > button[kind="primary"]:hover {{
            background-color: {COLOR_AZUL_CLARO};
            color: #FFFFFF;
        }}
        .stButton > button[kind="primary"]:disabled,
        .stButton > button[disabled] {{
            background-color: #B0B7C0;
            color: #FFFFFF;
            opacity: 0.85;
        }}
        .stButton > button:not([kind="primary"]) {{
            background-color: #FFFFFF;
            color: {COLOR_AZUL_IPS};
            border: 1.5px solid {COLOR_AZUL_IPS};
        }}

        /* === Alertas === */
        div[data-testid="stAlert"] {{
            border-radius: 6px;
            border-left: 5px solid {COLOR_AZUL_IPS};
        }}

        /* === Divisor === */
        hr {{
            border-color: #D9DEE5;
            margin: 1rem 0;
        }}

        /* === Multiselect === */
        [data-testid="stMultiSelect"] span[data-baseweb="tag"] {{
            background-color: {COLOR_AZUL_IPS};
        }}

        /* === Caption === */
        .stCaption, small, [data-testid="stCaptionContainer"] {{
            color: {COLOR_GRIS} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
