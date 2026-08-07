"""Logica de cascada de mitigacion del SVP-IPS.

Calcula metricas, recuperaciones y datos para visualizaciones segun
las fuentes alternativas que se hayan "cargado" en la sesion.
"""

import pandas as pd


def calcular_estado_cascada(
    df_pdi: pd.DataFrame,
    df_servel: pd.DataFrame,
    df_fonasa: pd.DataFrame,
    servel_cargado: bool,
    fonasa_cargado: bool,
) -> dict:
    """Calcula metricas y dataframes segun las fuentes cargadas."""
    total_pdi = len(df_pdi)

    df_servel_usado = df_servel if servel_cargado else df_servel.iloc[0:0]
    df_fonasa_usado = df_fonasa if fonasa_cargado else df_fonasa.iloc[0:0]

    rec_servel = len(df_servel_usado)
    rec_fonasa = len(df_fonasa_usado)
    rec_total = rec_servel + rec_fonasa
    pendientes = total_pdi - rec_total

    df_recuperados = pd.concat([df_servel_usado, df_fonasa_usado], ignore_index=True)

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

    pasos_cascada.append(
        {
            "paso": "Aun suspendidos",
            "valor": max(acumulado, 0),
            "tipo": "pendiente",
            "delta": 0,
        }
    )

    return {
        "total_pdi": total_pdi,
        "rec_servel": rec_servel,
        "rec_fonasa": rec_fonasa,
        "rec_total": rec_total,
        "pendientes": max(pendientes, 0),
        "df_recuperados": df_recuperados,
        "pasos_cascada": pasos_cascada,
    }


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
