"""Logica de cascada de mitigacion del SVP-IPS.

Calcula metricas, recuperaciones y datos para visualizaciones segun
las fuentes alternativas que se hayan "cargado" en la sesion.

Sprint 2 incorpora:
  - Tercera fuente: BancoEstado (giros presenciales).
  - Modulo de mitigacion de Data Sucia (RUTs con DV invalido).
  - Metricas ejecutivas (% mitigacion, monto fiscal protegido).
  - Log de auditoria con ID de transaccion unico.
"""

import hashlib
import pandas as pd


UNIVERSO_PGU = 2_200_000
MONTO_PGU_MENSUAL = 224_000  # CLP por beneficiario reactivado.


def calcular_estado_cascada(
    df_pdi: pd.DataFrame,
    df_servel: pd.DataFrame,
    df_fonasa: pd.DataFrame,
    df_bancoestado: pd.DataFrame,
    servel_cargado: bool,
    fonasa_cargado: bool,
    bancoestado_cargado: bool,
    ruts_invalidos_pdi: int = 0,
) -> dict:
    """Calcula metricas y dataframes segun las fuentes cargadas."""
    total_pdi = len(df_pdi)

    df_servel_usado = df_servel if servel_cargado else df_servel.iloc[0:0]
    df_fonasa_usado = df_fonasa if fonasa_cargado else df_fonasa.iloc[0:0]
    df_be_usado = (
        df_bancoestado if bancoestado_cargado else df_bancoestado.iloc[0:0]
    )

    rec_servel = len(df_servel_usado)
    rec_fonasa = len(df_fonasa_usado)
    rec_bancoestado = len(df_be_usado)
    rec_total = rec_servel + rec_fonasa + rec_bancoestado
    pendientes = total_pdi - rec_total

    df_recuperados = pd.concat(
        [df_servel_usado, df_fonasa_usado, df_be_usado], ignore_index=True
    )

    pasos_cascada = [
        {
            "paso": "Casos PDI",
            "valor": total_pdi,
            "tipo": "inicio",
            "delta": 0,
        },
    ]

    acumulado = total_pdi
    if servel_cargado and rec_servel > 0:
        pasos_cascada.append(
            {
                "paso": "Recuperados x Servel",
                "valor": -rec_servel,
                "tipo": "reduccion",
                "delta": -rec_servel,
            }
        )
        acumulado -= rec_servel

    if fonasa_cargado and rec_fonasa > 0:
        pasos_cascada.append(
            {
                "paso": "Recuperados x Fonasa",
                "valor": -rec_fonasa,
                "tipo": "reduccion",
                "delta": -rec_fonasa,
            }
        )
        acumulado -= rec_fonasa

    if bancoestado_cargado and rec_bancoestado > 0:
        pasos_cascada.append(
            {
                "paso": "Recuperados x BancoEstado",
                "valor": -rec_bancoestado,
                "tipo": "reduccion",
                "delta": -rec_bancoestado,
            }
        )
        acumulado -= rec_bancoestado

    pasos_cascada.append(
        {
            "paso": "Aun suspendidos",
            "valor": max(acumulado, 0),
            "tipo": "pendiente",
            "delta": 0,
        }
    )

    return {
        "universo_pgu": UNIVERSO_PGU,
        "total_pdi": total_pdi,
        "rec_servel": rec_servel,
        "rec_fonasa": rec_fonasa,
        "rec_bancoestado": rec_bancoestado,
        "rec_total": rec_total,
        "pendientes": max(pendientes, 0),
        "df_recuperados": df_recuperados,
        "pasos_cascada": pasos_cascada,
        "ruts_invalidos_pdi": ruts_invalidos_pdi,
    }


def calcular_metricas_sprint2(estado: dict) -> dict:
    """Deriva las 4 metricas ejecutivas del Dashboard Sprint 2.

    - total_afectados: casos reportados por PDI (incluye Data Sucia).
    - recuperados: total validado por las 3 fuentes.
    - pct_mitigacion: recuperados / total_afectados (0-100).
    - monto_fiscal_protegido: recuperados * MONTO_PGU_MENSUAL (CLP).
    - ruts_invalidos_pdi: cantidad de RUTs con DV invalido detectados
      en la base de origen.
    """
    total = estado.get("total_pdi", 0)
    recuperados = estado.get("rec_total", 0)
    pct = (recuperados / total * 100) if total > 0 else 0.0
    monto = recuperados * MONTO_PGU_MENSUAL
    return {
        "total_afectados": total,
        "recuperados": recuperados,
        "pct_mitigacion": pct,
        "monto_fiscal_protegido": monto,
        "ruts_invalidos_pdi": estado.get("ruts_invalidos_pdi", 0),
    }


def _id_transaccion(rut: str, fuente: str, fecha: str) -> str:
    """Genera un ID de transaccion deterministico formato TX-XXXXXXXX.

    Hash truncated a 8 chars sobre (RUT|fuente|fecha) para garantizar
    reproducibilidad y unicidad por hito de validacion.
    """
    semilla = f"{rut}|{fuente}|{fecha}".encode("utf-8")
    return "TX-" + hashlib.sha256(semilla).hexdigest()[:8].upper()


def generar_log_auditoria(df_recuperados: pd.DataFrame) -> pd.DataFrame:
    """Construye el DataFrame de trazabilidad para la Contraloria.

    Columnas finales:
      - RUT
      - Nombre
      - Fuente de Validacion
      - Fecha del Hito
      - ID de Transaccion
    """
    if df_recuperados is None or df_recuperados.empty:
        return pd.DataFrame(
            columns=[
                "RUT",
                "Nombre",
                "Fuente de Validacion",
                "Fecha del Hito",
                "ID de Transaccion",
            ]
        )

    df = df_recuperados.copy()
    df["ID de Transaccion"] = df.apply(
        lambda r: _id_transaccion(
            str(r["RUT"]), str(r["Fuente"]), str(r["Fecha_Validacion"])
        ),
        axis=1,
    )
    return df.rename(
        columns={
            "RUT": "RUT",
            "Nombre": "Nombre",
            "Fuente": "Fuente de Validacion",
            "Fecha_Validacion": "Fecha del Hito",
        }
    )[
        [
            "RUT",
            "Nombre",
            "Fuente de Validacion",
            "Fecha del Hito",
            "ID de Transaccion",
        ]
    ].sort_values(["Fuente de Validacion", "Fecha del Hito"]).reset_index(drop=True)


def serializar_cascada(pasos: list[dict]) -> pd.DataFrame:
    """Convierte los pasos a un DataFrame apto para Altair waterfall.

    Columnas:
      - Paso, Tipo, Inicio, Fin, Etiqueta
      - Acumulado: total corriente al cierre del paso
      - DeltaLabel: texto del delta (+N, -N, =N)
    """
    rows = []
    acumulado = 0
    for p in pasos:
        if p["tipo"] == "inicio":
            base = 0
            top = p["valor"]
            delta_label = f"+{p['valor']:,}"
        elif p["tipo"] == "reduccion":
            top = acumulado + p["valor"]
            base = acumulado
            delta_label = f"{p['valor']:,}"
        else:
            base = 0
            top = p["valor"]
            delta_label = f"={p['valor']:,}"

        if p["tipo"] == "reduccion":
            nuevo_acumulado = acumulado + p["valor"]
        else:
            nuevo_acumulado = top

        rows.append(
            {
                "Paso": p["paso"],
                "Tipo": p["tipo"],
                "Inicio": base,
                "Fin": top,
                "Etiqueta": delta_label,
                "Acumulado": max(nuevo_acumulado, 0),
                "DeltaLabel": delta_label,
            }
        )
        acumulado = nuevo_acumulado

    return pd.DataFrame(rows)


def serializar_conectores(df_cascada: pd.DataFrame) -> pd.DataFrame:
    """Genera lineas conectoras horizontales entre barras consecutivas.

    Cada conector une el borde derecho de una barra con el izquierdo
    de la siguiente, a la altura donde termina la primera (Fin).
    """
    rows = []
    pasos = df_cascada["Paso"].tolist()
    fins = df_cascada["Fin"].tolist()
    for i in range(len(pasos) - 1):
        rows.append(
            {
                "x": pasos[i],
                "x2": pasos[i + 1],
                "y": fins[i],
            }
        )
    return pd.DataFrame(rows)


def serializar_stacked_bar(estado: dict) -> pd.DataFrame:
    """Devuelve un DataFrame para el grafico de barras apiladas por
    institucion. Cada fila = una fuente con su conteo de recuperados.
    """
    return pd.DataFrame(
        [
            {
                "Fuente": "Servel",
                "Casos": estado.get("rec_servel", 0),
                "Habilitada": bool(estado.get("rec_servel", 0) > 0),
            },
            {
                "Fuente": "Fonasa",
                "Casos": estado.get("rec_fonasa", 0),
                "Habilitada": bool(estado.get("rec_fonasa", 0) > 0),
            },
            {
                "Fuente": "BancoEstado",
                "Casos": estado.get("rec_bancoestado", 0),
                "Habilitada": bool(estado.get("rec_bancoestado", 0) > 0),
            },
        ]
    )