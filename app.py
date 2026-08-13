"""SVP-IPS - Dashboard de Validacion de Presencialidad PGU.

Prototipo que demuestra como el cruce de datos entre PDI y fuentes
alternativas (Servel, Fonasa, BancoEstado) reduce el numero de
suspensiones indebidas de la PGU.

Sprint 2:
  - 3 fuentes de cruce + validacion DV de RUTs.
  - 4 metricas ejecutivas (% mitigacion, monto fiscal protegido).
  - Tabs Dashboard / Log de Auditoria / Vision Ciudadana.
  - Log exportable a CSV para la Contraloria.
"""

import io
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st

from modules.data import (
    detectar_ruts_invalidos,
    formatear_rut,
    generar_base_pdi,
    generar_bancoestado,
    generar_fonasa,
    generar_servel,
    inyectar_ruts_invalidos,
    validar_rut,
)
from modules.logic import (
    MONTO_PGU_MENSUAL,
    UNIVERSO_PGU,
    calcular_estado_cascada,
    calcular_metricas_sprint2,
    generar_log_auditoria,
    serializar_cascada,
    serializar_conectores,
    serializar_stacked_bar,
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
SEED_BANCOESTADO = 43
SEED_RUTS_INVALIDOS = 99
PCT_SERVEL = 0.40
PCT_FONASA = 0.20
PCT_BANCOESTADO = 0.15
PCT_RUTS_INVALIDOS = 0.05
N_RECHAZADOS_PDI = 13_000


def _init_state() -> None:
    if "servel_cargado" not in st.session_state:
        st.session_state.servel_cargado = False
    if "fonasa_cargado" not in st.session_state:
        st.session_state.fonasa_cargado = False
    if "bancoestado_cargado" not in st.session_state:
        st.session_state.bancoestado_cargado = False
    if "data_loaded" not in st.session_state:
        with st.spinner("Cargando base PDI..."):
            df_pdi_limpio = generar_base_pdi(n=N_RECHAZADOS_PDI, seed=SEED_PDI)
            df_pdi = inyectar_ruts_invalidos(
                df_pdi_limpio, pct=PCT_RUTS_INVALIDOS, seed=SEED_RUTS_INVALIDOS
            )
            df_servel = generar_servel(df_pdi, pct=PCT_SERVEL, seed=SEED_PDI)
            df_fonasa = generar_fonasa(df_pdi, df_servel, pct=PCT_FONASA, seed=SEED_PDI)
            df_bancoestado = generar_bancoestado(
                df_pdi,
                df_servel,
                df_fonasa,
                pct=PCT_BANCOESTADO,
                seed=SEED_BANCOESTADO,
            )
            df_invalidos = detectar_ruts_invalidos(df_pdi)

            st.session_state.df_pdi = df_pdi
            st.session_state.df_pdi_limpio = df_pdi_limpio
            st.session_state.df_servel = df_servel
            st.session_state.df_fonasa = df_fonasa
            st.session_state.df_bancoestado = df_bancoestado
            st.session_state.df_invalidos = df_invalidos
            st.session_state.data_loaded = True


def _render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### SVP-IPS")
        st.caption("Sistema de Validacion de Presencialidad")
        st.divider()

        st.markdown("**Contexto - Cruce PGU/PDI**")
        st.caption(
            "El IPS paga PGU a 2.200.000 pensionados. La PDI reporto que "
            "13.000 estaban fuera de Chile por mas de 180 dias, por lo que "
            "se les suspendio la PGU. Esta herramienta demuestra como el "
            "cruce con fuentes alternativas reduce esa cifra."
        )

        st.divider()
        st.markdown("**Carga de fuentes**")

        st.markdown(
            "<span style='color:#2E7D32; font-weight:600;'>&#10004; PDI</span> "
            f"<span style='color:#1A1A1A;'>cargada "
            f"({N_RECHAZADOS_PDI:,} casos reportados)</span>",
            unsafe_allow_html=True,
        )
        inv = st.session_state.df_invalidos
        if len(inv) > 0:
            st.caption(
                f"Data Sucia detectada: {len(inv):,} RUTs con DV invalido "
                f"({PCT_RUTS_INVALIDOS * 100:.0f}% del origen PDI)."
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
                "40% de los reportados tienen voto en Chile</small>",
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
                "20% adicional de los reportados tuvieron atencion medica</small>",
                unsafe_allow_html=True,
            )

        st.button(
            "Cargar Archivo BancoEstado",
            key="btn_bancoestado",
            type="primary",
            use_container_width=True,
            on_click=lambda: st.session_state.__setitem__("bancoestado_cargado", True),
            disabled=st.session_state.bancoestado_cargado,
        )
        if st.session_state.bancoestado_cargado:
            st.markdown(
                "<small style='color:#2E7D32;'>&#10004; BancoEstado cargado - "
                "15% adicional registra giro presencial en sucursal/cajero</small>",
                unsafe_allow_html=True,
            )

        if st.button("Reiniciar simulacion", use_container_width=True):
            st.session_state.servel_cargado = False
            st.session_state.fonasa_cargado = False
            st.session_state.bancoestado_cargado = False
            st.rerun()

        st.divider()
        st.caption("Sprint 2 - Prototipo | Datos simulados")


def _render_banner_universo(estado: dict) -> None:
    universo = estado.get("universo_pgu", UNIVERSO_PGU)
    reportados = estado.get("total_pdi", 0)
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(90deg, {COLOR_AZUL_IPS} 0%, {COLOR_AZUL_CLARO} 100%);
            color: #FFFFFF;
            padding: 14px 22px;
            border-radius: 8px;
            margin-bottom: 16px;
            border-left: 6px solid {COLOR_VERDE};
        ">
            <div style="font-size: 0.95rem; font-weight: 600; opacity: 0.9;">
                UNIVERSO PGU
            </div>
            <div style="font-size: 1.5rem; font-weight: 700; margin-top: 4px;">
                {universo:,} beneficiarios
                <span style="font-size: 1rem; font-weight: 500; opacity: 0.85; margin-left: 12px;">
                    | Casos reportados por PDI: {reportados:,}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_metricas_sprint2(metricas: dict) -> None:
    total = metricas["total_afectados"]
    recuperados = metricas["recuperados"]
    pct = metricas["pct_mitigacion"]
    monto = metricas["monto_fiscal_protegido"]
    invalidos = metricas["ruts_invalidos_pdi"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Total Afectados PDI",
            value=f"{total:,}",
            help="Casos que la PDI marco fuera de Chile > 180 dias y a los que se les suspendio la PGU.",
        )
    with col2:
        st.metric(
            label="Casos Recuperados",
            value=f"{recuperados:,}",
            delta=recuperados if recuperados > 0 else None,
            delta_color="normal",
            help="Beneficiarios cuya presencia en Chile fue confirmada por Servel, Fonasa o BancoEstado.",
        )
    with col3:
        st.metric(
            label="% Mitigacion de Error",
            value=f"{pct:.1f}%",
            delta=f"{pct:.1f}%" if pct > 0 else None,
            delta_color="normal",
            help="Porcentaje de los casos reportados por PDI que fueron revertidos con cruce de fuentes alternativas.",
        )
    with col4:
        st.metric(
            label="Monto Fiscal Protegido",
            value=f"CLP ${monto:,}",
            delta=f"CLP ${monto:,}" if monto > 0 else None,
            delta_color="normal",
            help=f"Equivalente monetario de los beneficiarios reactivados (recuperados x ${MONTO_PGU_MENSUAL:,} PGU mensual).",
        )

    if invalidos > 0:
        st.warning(
            f"**Mitigacion de riesgo 'Data Sucia':** {invalidos:,} RUTs con "
            f"DV invalido fueron detectados en la base de origen PDI y "
            f"segunados para revision. Equivale al "
            f"{invalidos / total * 100:.1f}% de los casos reportados."
        )


def _render_stacked_bar(estado: dict) -> None:
    df = serializar_stacked_bar(estado)
    if df["Casos"].sum() == 0:
        st.info("Cargue al menos una fuente para ver la distribucion por institucion.")
        return

    color_scale = alt.Scale(
        domain=["Servel", "Fonasa", "BancoEstado"],
        range=["#1565C0", "#2E7D32", "#6A1B9A"],
    )

    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X("Fuente:N", sort=None, title="Institucion"),
            y=alt.Y("Casos:Q", title="Casos recuperados"),
            color=alt.Color("Fuente:N", scale=color_scale, legend=None),
            tooltip=[
                alt.Tooltip("Fuente:N", title="Institucion"),
                alt.Tooltip("Casos:Q", title="Casos", format=","),
            ],
        )
        .properties(
            height=300,
            title=alt.TitleParams(
                text="Recuperados por institucion",
                subtitle="Distribucion de casos validados segun fuente alternativa.",
                fontSize=14,
                color=COLOR_AZUL_IPS,
                subtitleFontSize=11,
                subtitleColor="#5F6B7A",
            ),
        )
    )

    labels = (
        alt.Chart(df)
        .mark_text(align="center", baseline="bottom", dy=-4, fontWeight="bold")
        .encode(
            x=alt.X("Fuente:N", sort=None),
            y=alt.Y("Casos:Q"),
            text=alt.Text("Casos:Q", format=","),
        )
    )

    st.altair_chart(chart + labels, use_container_width=True)


def _render_waterfall(estado: dict) -> None:
    pasos = estado.get("pasos_cascada") or []
    df_cascada = serializar_cascada(pasos)
    if df_cascada.empty:
        st.info("Sin datos para mostrar la cascada.")
        return
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
                text="Cascada de cruce PGU/PDI",
                subtitle=[
                    "Cuantos casos siguen con la PGU suspendida tras cada cruce.",
                    "Azul = reportados por PDI | Verde = confirmados en Chile | Gris = sin cruce.",
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
    df = estado.get("df_recuperados")
    if df is None or df.empty:
        st.info("Aun no se han validado beneficiarios. Cargue Servel, Fonasa o BancoEstado.")
        return

    filtro = st.multiselect(
        "Filtrar por fuente",
        options=["Servel", "Fonasa", "BancoEstado"],
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
    rec_total = estado.get("rec_total", 0)
    if rec_total == 0:
        st.warning(
            "Cargue **Servel** desde el panel lateral para iniciar la "
            "recuperacion de beneficiarios."
        )
        return

    if st.session_state.servel_cargado and estado.get("rec_servel", 0) > 0:
        st.success(
            f"Se recuperaron **{estado['rec_servel']:,}** beneficiarios "
            f"via **Servel** (votacion registrada en Chile)."
        )
    if st.session_state.fonasa_cargado and estado.get("rec_fonasa", 0) > 0:
        st.success(
            f"Se recuperaron **{estado['rec_fonasa']:,}** beneficiarios "
            f"adicionales via **Fonasa** (atencion medica en Chile)."
        )
    if st.session_state.bancoestado_cargado and estado.get("rec_bancoestado", 0) > 0:
        st.success(
            f"Se recuperaron **{estado['rec_bancoestado']:,}** beneficiarios "
            f"adicionales via **BancoEstado** (giro presencial en sucursal/cajero)."
        )


def _render_tab_dashboard(estado: dict, metricas: dict) -> None:
    _render_banner_universo(estado)
    _render_metricas_sprint2(metricas)
    st.divider()
    _render_alerts(estado)

    col_chart, col_table = st.columns([3, 2])
    with col_chart:
        st.markdown("##### Distribucion de recuperados por institucion")
        _render_stacked_bar(estado)
        st.markdown("##### Cascada: reduccion de la cifra de PDI tras los cruces")
        _render_waterfall(estado)
    with col_table:
        st.markdown("##### Beneficiarios a rehabilitar (PGU)")
        _render_tabla_recuperados(estado)


def _render_tab_auditoria(estado: dict) -> None:
    log = generar_log_auditoria(estado.get("df_recuperados"))
    st.markdown("##### Log de Auditoria - Trazabilidad para la Contraloria")
    st.caption(
        "Cada fila corresponde a un beneficiario cuya presencia en Chile "
        "fue confirmada. El ID de Transaccion es un hash SHA-256 truncated "
        "que garantiza unicidad por (RUT, fuente, fecha)."
    )

    if log.empty:
        st.info("Aun no se han validado beneficiarios.")
        return

    col1, col2 = st.columns(2)
    with col1:
        fuentes_disp = sorted(log["Fuente de Validacion"].unique().tolist())
        filtro_fuente = st.multiselect(
            "Filtrar por fuente",
            options=fuentes_disp,
            default=fuentes_disp,
        )
    with col2:
        st.metric("Total hitos registrados", f"{len(log):,}")

    log_filtrado = log[log["Fuente de Validacion"].isin(filtro_fuente)].reset_index(drop=True)
    st.dataframe(log_filtrado, use_container_width=True, height=460, hide_index=True)

    csv_buffer = io.StringIO()
    log_filtrado.to_csv(csv_buffer, index=False, encoding="utf-8")
    csv_bytes = csv_buffer.getvalue().encode("utf-8")
    st.download_button(
        label="Descargar Reporte Contraloria (CSV)",
        data=csv_bytes,
        file_name="Reporte_Trazabilidad_Contraloria.csv",
        mime="text/csv",
        type="primary",
        use_container_width=True,
    )
    st.caption(
        f"Exporta {len(log_filtrado):,} hitos de validacion. "
        f"Generado el {datetime.now().strftime('%Y-%m-%d %H:%M')}."
    )


def _render_tab_ciudadana(estado: dict) -> None:
    st.markdown("##### Vision Ciudadana - Consulta de estado PGU")
    st.caption(
        "Simulacion de la consulta que un pensionado puede hacer sobre el "
        "estado de su PGU tras un cruce de presencialidad exitoso."
    )

    df = estado.get("df_recuperados")
    ruts_ejemplo = []
    if df is not None and not df.empty:
        ruts_ejemplo = df["RUT"].head(5).tolist()

    col1, col2 = st.columns([2, 3])
    with col1:
        rut_input = st.text_input(
            "Ingrese su RUT",
            max_chars=12,
            placeholder="12.345.678-5",
            help="Formato con o sin puntos. Use DV 'K' si corresponde.",
        )
        es_valido = validar_rut(rut_input) if rut_input else False
        if rut_input and not es_valido:
            st.error("RUT invalido. Verifique formato y digito verificador.")
        consultar = st.button(
            "Consultar estado",
            type="primary",
            use_container_width=True,
            disabled=not rut_input,
        )
    with col2:
        if ruts_ejemplo:
            st.caption("RUTs de prueba (recuperados):")
            st.code("\n".join(ruts_ejemplo), language=None)

    if not consultar or not es_valido:
        return

    if df is None or df.empty:
        st.warning(
            "El sistema aun no tiene beneficiarios validados. "
            "Cargue al menos una fuente desde el panel lateral."
        )
        return

    coincidencias = df[df["RUT"].apply(lambda r: _mismo_rut(r, rut_input))]
    if coincidencias.empty:
        st.markdown(
            f"""
            <div style="
                background-color: #F4F6F9;
                border-left: 4px solid {COLOR_GRIS};
                padding: 16px;
                border-radius: 6px;
                margin-top: 8px;
            ">
                <div style="color: {COLOR_GRIS}; font-weight: 600; margin-bottom: 6px;">
                    Sin registro de validacion
                </div>
                <div style="color: #1A1A1A;">
                    Su RUT no registra validacion positiva en las fuentes
                    alternativas. Si considera que la suspension es un error,
                    contacte a la sucursal IPS mas cercana.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    fila = coincidencias.iloc[0]
    fuente = fila["Fuente"]
    fecha = fila["Fecha_Validacion"]
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
            border-left: 6px solid {COLOR_VERDE};
            padding: 18px 22px;
            border-radius: 8px;
            margin-top: 8px;
            font-family: 'Segoe UI', sans-serif;
            max-width: 540px;
        ">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 10px;">
                <span style="font-size: 1.2rem;">&#128241;</span>
                <span style="font-weight: 700; color: {COLOR_AZUL_IPS};">
                    SMS - Notificacion IPS
                </span>
            </div>
            <div style="background-color: #FFFFFF; padding: 14px; border-radius: 6px;
                        color: #1A1A1A; line-height: 1.5; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
                <strong>IPS Informa:</strong> Su PGU ha sido reactivada tras
                validar su presencialidad via <strong>{fuente}</strong>
                (Fecha del hito: {fecha}). Monto mensual protegido:
                CLP ${MONTO_PGU_MENSUAL:,}.
            </div>
            <div style="font-size: 0.75rem; color: {COLOR_GRIS}; margin-top: 8px;">
                ID Transaccion: {fila.get('ID de Transaccion', 'N/D')}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _mismo_rut(rut_base: str, rut_input: str) -> bool:
    """Compara dos RUTs ignorando formato (puntos, guion, mayusculas)."""
    def _norm(s: str) -> str:
        return s.replace(".", "").replace(" ", "").replace("-", "").upper().strip()
    return _norm(str(rut_base)) == _norm(rut_input)


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
        df_bancoestado=st.session_state.df_bancoestado,
        servel_cargado=st.session_state.servel_cargado,
        fonasa_cargado=st.session_state.fonasa_cargado,
        bancoestado_cargado=st.session_state.bancoestado_cargado,
        ruts_invalidos_pdi=len(st.session_state.df_invalidos),
    )
    metricas = calcular_metricas_sprint2(estado)

    tab_dash, tab_audit, tab_ciud = st.tabs(
        ["Dashboard", "Log de Auditoria", "Vision Ciudadana"]
    )
    with tab_dash:
        _render_tab_dashboard(estado, metricas)
    with tab_audit:
        _render_tab_auditoria(estado)
    with tab_ciud:
        _render_tab_ciudadana(estado)

    st.divider()
    st.caption(
        "Prototipo Sprint 2 | Datos simulados | "
        "RUTs generados con DV modulo 11 (100% ficticios)"
    )


if __name__ == "__main__":
    main()