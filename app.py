"""SVP-IPS - Dashboard de Validacion de Presencialidad PGU.

Prototipo que demuestra como el cruce de datos entre PDI y fuentes
alternativas (Servel, Fonasa) reduce el numero de suspensiones
indebidas de la PGU.
"""

import altair as alt
import pandas as pd
import streamlit as st

from modules.data import generar_base_pdi, generar_fonasa, generar_servel
from modules.logic import (
    calcular_estado_cascada,
    serializar_cascada,
    serializar_conectores,
)
from modules.style import (
    COLOR_AZUL_CLARO,
    COLOR_AZUL_IPS,
    COLOR_GRIS,
    COLOR_VERDE,
    activar_tema_altair,
    aplicar_estilos,
)


SEED_PDI = 42
PCT_SERVEL = 0.40
PCT_FONASA = 0.20
N_RECHAZADOS_PDI = 13_000


def _init_state() -> None:
    if "servel_cargado" not in st.session_state:
        st.session_state.servel_cargado = False
    if "fonasa_cargado" not in st.session_state:
        st.session_state.fonasa_cargado = False
    if "data_loaded" not in st.session_state:
        with st.spinner("Cargando base PDI..."):
            df_pdi = generar_base_pdi(n=N_RECHAZADOS_PDI, seed=SEED_PDI)
            df_servel = generar_servel(df_pdi, pct=PCT_SERVEL, seed=SEED_PDI)
            df_fonasa = generar_fonasa(
                df_pdi, df_servel, pct=PCT_FONASA, seed=SEED_PDI
            )
            st.session_state.df_pdi = df_pdi
            st.session_state.df_servel = df_servel
            st.session_state.df_fonasa = df_fonasa
            st.session_state.data_loaded = True


def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### SVP-IPS")
        st.caption("Sistema de Validacion de Presencialidad")
        st.divider()

        st.markdown("**Contexto - Crisis PGU/PDI**")
        st.caption(
            "El IPS paga PGU a 2.200.000 pensionados. La PDI informo que "
            "13.000 estaban fuera de Chile por mas de 180 dias y la PGU "
            "les fue suspendida. Esta herramienta demuestra como el cruce "
            "con fuentes alternativas reduce esos rechazos."
        )

        st.divider()
        st.markdown("**Carga de fuentes**")

        st.markdown(
            "<span style='color:#2E7D32; font-weight:600;'>&#10004; PDI</span> "
            f"<span style='color:#1A1A1A;'>cargada "
            f"({N_RECHAZADOS_PDI:,} casos rechazados)</span>",
            unsafe_allow_html=True,
        )

        st.button(
            "Cargar Archivo Servel",
            key="btn_servel",
            type="primary",
            use_container_width=True,
            on_click=lambda: st.session_state.__setitem__("servel_cargado", True),
            disabled=st.session_state.servel_cargado,
        )
        if st.session_state.servel_cargado:
            st.markdown(
                "<small style='color:#2E7D32;'>&#10004; Servel cargado - "
                "40% de los rechazados tenian voto en Chile</small>",
                unsafe_allow_html=True,
            )

        st.button(
            "Cargar Archivo Fonasa",
            key="btn_fonasa",
            type="primary",
            use_container_width=True,
            on_click=lambda: st.session_state.__setitem__("fonasa_cargado", True),
            disabled=st.session_state.fonasa_cargado,
        )
        if st.session_state.fonasa_cargado:
            st.markdown(
                "<small style='color:#2E7D32;'>&#10004; Fonasa cargado - "
                "20% adicional de los rechazados tuvieron atencion medica</small>",
                unsafe_allow_html=True,
            )

        if st.button("Reiniciar simulacion", use_container_width=True):
            st.session_state.servel_cargado = False
            st.session_state.fonasa_cargado = False
            st.rerun()

        st.divider()
        st.caption("Sprint 1 - Prototipo | Datos simulados")


def _render_banner_universo(estado: dict) -> None:
    universo = estado["universo_pgu"]
    rechazados = estado["total_pdi"]
    tasa = (rechazados / universo) * 100 if universo else 0
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(90deg, #003B71 0%, #1F5DA8 100%);
            color: #FFFFFF;
            padding: 14px 22px;
            border-radius: 8px;
            margin-bottom: 16px;
            border-left: 6px solid #2E7D32;
        ">
            <div style="font-size: 0.95rem; font-weight: 600; opacity: 0.9;">
                UNIVERSO PGU
            </div>
            <div style="font-size: 1.5rem; font-weight: 700; margin-top: 4px;">
                {universo:,} beneficiarios
                <span style="font-size: 1rem; font-weight: 500; opacity: 0.85; margin-left: 12px;">
                    | Tasa de error PDI: {tasa:.2f}%
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_metrics(estado: dict) -> None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="Rechazados por PDI (inicial)",
            value=f"{estado['total_pdi']:,}",
            help="Casos que la PDI marco fuera de Chile > 180 dias y se les suspendio la PGU.",
        )
    with col2:
        delta = estado["rec_total"] if estado["rec_total"] > 0 else None
        st.metric(
            label="Recuperados (en Chile)",
            value=f"{estado['rec_total']:,}",
            delta=delta,
            delta_color="normal",
            help="Beneficiarios cuya PGU debe rehabilitarse porque estaban en Chile.",
        )
    with col3:
        delta_pend = (
            estado["pendientes"] - estado["total_pdi"]
            if estado["rec_total"] > 0
            else None
        )
        st.metric(
            label="Aun suspendidos (erroneamente)",
            value=f"{estado['pendientes']:,}",
            delta=delta_pend,
            delta_color="inverse",
            help="Casos donde la suspension de PGU se mantiene (sin cruce que lo refute).",
        )


def _render_waterfall(estado: dict) -> None:
    df_cascada = serializar_cascada(estado["pasos_cascada"])
    df_conectores = serializar_conectores(df_cascada)

    color_scale = alt.Scale(
        domain=["inicio", "reduccion", "pendiente"],
        range=[COLOR_AZUL_IPS, COLOR_VERDE, COLOR_GRIS],
    )

    base = alt.Chart(df_cascada).encode(
        x=alt.X("Paso:N", sort=None, title="Etapa del cruce")
    )

    barras = base.mark_bar(size=70).encode(
        y=alt.Y("Inicio:Q", title="Casos"),
        y2=alt.Y2("Fin:Q"),
        color=alt.Color("Tipo:N", scale=color_scale, legend=None),
        tooltip=[
            alt.Tooltip("Paso:N", title="Etapa"),
            alt.Tooltip("DeltaLabel:N", title="Variacion"),
            alt.Tooltip("Acumulado:Q", title="Acumulado", format=","),
        ],
    )

    conectores = (
        alt.Chart(df_conectores)
        .mark_rule(strokeDash=[5, 4], strokeWidth=1.5, color="#5F6B7A", opacity=0.7)
        .encode(
            x=alt.X("x:N", sort=None),
            x2=alt.X2("x2:N"),
            y=alt.Y("y:Q"),
        )
    )

    label_delta = base.mark_text(
        align="center",
        baseline="bottom",
        dy=-8,
        color="#1A1A1A",
        fontSize=13,
        fontWeight="bold",
    ).encode(
        y=alt.Y("Fin:Q"),
        text=alt.Text("DeltaLabel:N"),
    )

    label_acumulado = base.mark_text(
        align="center",
        baseline="top",
        dy=4,
        color=COLOR_AZUL_IPS,
        fontSize=12,
        fontWeight="bold",
    ).encode(
        y=alt.Y("Fin:Q"),
        text=alt.Text("Acumulado:Q", format=","),
    )

    chart = (
        (conectores + barras + label_delta + label_acumulado)
        .properties(
            height=380,
            title=alt.TitleParams(
                text="Cascada de mitigacion de errores PGU",
                subtitle=[
                    "Cuantos casos quedan con la PGU suspendida tras cada cruce.",
                    "Azul = total inicial | Verde = recuperados | Gris = los que AUN quedan suspendidos.",
                ],
                fontSize=16,
                color=COLOR_AZUL_IPS,
                subtitleFontSize=11,
                subtitleColor="#5F6B7A",
            ),
        )
        .configure_axis(labelFontSize=11, titleFontSize=12)
    )

    st.altair_chart(chart, use_container_width=True)


def _render_tabla_recuperados(estado: dict) -> None:
    df = estado["df_recuperados"]
    if df.empty:
        st.info("Aun no se han validado beneficiarios. Cargue Servel o Fonasa.")
        return

    filtro = st.multiselect(
        "Filtrar por fuente",
        options=["Servel", "Fonasa"],
        default=list(df["Fuente"].unique()),
    )
    df_show = df[df["Fuente"].isin(filtro)].reset_index(drop=True)
    st.dataframe(
        df_show.rename(
            columns={
                "RUT": "RUT",
                "Nombre": "Beneficiario",
                "Fuente": "Fuente",
                "Fecha_Validacion": "Fecha",
                "Detalle": "Detalle",
            }
        ),
        use_container_width=True,
        height=380,
        hide_index=True,
    )
    st.caption(f"Mostrando {len(df_show):,} beneficiarios validados.")


def _render_alerts(estado: dict) -> None:
    if estado["rec_total"] == 0:
        st.warning(
            "Cargue **Servel** desde el panel lateral para iniciar la "
            "recuperacion de beneficiarios."
        )
        return

    if st.session_state.servel_cargado and estado["rec_servel"] > 0:
        st.success(
            f"Se recuperaron **{estado['rec_servel']:,}** beneficiarios "
            f"vía **Servel** (votacion registrada en Chile)."
        )
    if st.session_state.fonasa_cargado and estado["rec_fonasa"] > 0:
        st.success(
            f"Se recuperaron **{estado['rec_fonasa']:,}** beneficiarios "
            f"adicionales vía **Fonasa** (atencion medica en Chile)."
        )


def main() -> None:
    st.set_page_config(
        page_title="SVP-IPS - Dashboard PGU",
        page_icon=":shield:",
        layout="wide",
    )
    activar_tema_altair()
    aplicar_estilos()
    _init_state()

    st.title(":shield: Dashboard de Validacion de Presencialidad PGU")
    st.markdown(
        "Cruce automatico de registros **PDI** contra fuentes alternativas "
        "para mitigar errores en la suspension de la **PGU**."
    )
    st.divider()

    _render_sidebar()

    estado = calcular_estado_cascada(
        df_pdi=st.session_state.df_pdi,
        df_servel=st.session_state.df_servel,
        df_fonasa=st.session_state.df_fonasa,
        servel_cargado=st.session_state.servel_cargado,
        fonasa_cargado=st.session_state.fonasa_cargado,
    )

    _render_banner_universo(estado)
    _render_metrics(estado)
    st.divider()
    _render_alerts(estado)

    col_chart, col_table = st.columns([3, 2])
    with col_chart:
        st.markdown("##### Cascada: como se reduce el rechazo erroneo de PDI")
        _render_waterfall(estado)
    with col_table:
        st.markdown("##### Beneficiarios a rehabilitar (PGU)")
        _render_tabla_recuperados(estado)

    st.divider()
    st.caption(
        "Prototipo Sprint 1 | Datos simulados | "
        "RUTs generados con DV modulo 11 (100% ficticios)"
    )


if __name__ == "__main__":
    main()
