"""Smoke test ejecutable desde la raiz con .venv/Scripts/python.exe

Sprint 2: incluye asserts para BancoEstado, validacion DV, inyeccion
de Data Sucia, metricas ejecutivas y log de auditoria.
"""
from modules.data import (
    calcular_dv,
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
    serializar_stacked_bar,
)


N_PDI = 13_000
PCT_SERVEL = 0.40
PCT_FONASA = 0.20
PCT_BANCOESTADO = 0.15
PCT_RUTS_INVALIDOS = 0.05


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)
    print(f"  [OK] {msg}")


def main() -> None:
    print("=== Test DV modulo 11 ===")
    for n in [11111111, 12345678, 20000000, 10000000, 19000000]:
        print(f"  {n} -> {formatear_rut(n)}")

    print("\n=== Test validar_rut (formatos multiples) ===")
    _check(validar_rut("11.111.111-1"), "11.111.111-1 valido")
    _check(validar_rut("11111111-1"), "11111111-1 valido (sin puntos)")
    _check(validar_rut("12.345.678-5"), "12.345.678-5 valido")
    _check(not validar_rut("11.111.111-2"), "11.111.111-2 invalido")
    _check(not validar_rut("ABC123"), "ABC123 invalido")
    _check(not validar_rut(""), "vacio invalido")

    print("\n=== DataFrames generados ===")
    df_pdi_limpio = generar_base_pdi(n=N_PDI)
    df_pdi = inyectar_ruts_invalidos(df_pdi_limpio, pct=PCT_RUTS_INVALIDOS)
    df_servel = generar_servel(df_pdi, pct=PCT_SERVEL)
    df_fonasa = generar_fonasa(df_pdi, df_servel, pct=PCT_FONASA)
    df_bancoestado = generar_bancoestado(df_pdi, df_servel, df_fonasa, pct=PCT_BANCOESTADO)

    print(f"  Universo PGU: {UNIVERSO_PGU:,} (referencia)")
    print(f"  PDI rechazados: {len(df_pdi):,}")
    print(f"    Ejemplo: {df_pdi.iloc[0]['RUT']} | {df_pdi.iloc[0]['Nombre']}")
    print(f"  Servel recupera: {len(df_servel):,} ({PCT_SERVEL * 100:.0f}%)")
    print(f"    Ejemplo: {df_servel.iloc[0]['RUT']} | {df_servel.iloc[0]['Detalle']}")
    print(f"  Fonasa recupera: {len(df_fonasa):,} (+{PCT_FONASA * 100:.0f}%)")
    print(f"    Ejemplo: {df_fonasa.iloc[0]['RUT']} | {df_fonasa.iloc[0]['Detalle']}")
    print(f"  BancoEstado recupera: {len(df_bancoestado):,} (+{PCT_BANCOESTADO * 100:.0f}%)")
    print(f"    Ejemplo: {df_bancoestado.iloc[0]['RUT']} | {df_bancoestado.iloc[0]['Detalle']}")

    df_invalidos = detectar_ruts_invalidos(df_pdi)
    print(f"\n=== Data Sucia ===")
    print(f"  RUTs invalidos detectados: {len(df_invalidos):,} "
          f"({len(df_invalidos) / N_PDI * 100:.1f}%)")
    if len(df_invalidos) > 0:
        print(f"    Ejemplo: {df_invalidos.iloc[0]['RUT']} | {df_invalidos.iloc[0]['Nombre']}")
    _check(len(df_invalidos) > 0, "Inyeccion de Data Sucia produjo invalidos")

    print("\n=== Overlaps entre fuentes ===")
    ruts_sv = set(df_servel["RUT"])
    ruts_fn = set(df_fonasa["RUT"])
    ruts_be = set(df_bancoestado["RUT"])
    print(f"  Servel <-> Fonasa: {len(ruts_sv & ruts_fn)} (esperado: 0)")
    print(f"  Servel <-> BancoEstado: {len(ruts_sv & ruts_be)} (esperado: 0)")
    print(f"  Fonasa <-> BancoEstado: {len(ruts_fn & ruts_be)} (esperado: 0)")
    _check(len(ruts_sv & ruts_fn) == 0, "Sin overlap Servel-Fonasa")
    _check(len(ruts_sv & ruts_be) == 0, "Sin overlap Servel-BancoEstado")
    _check(len(ruts_fn & ruts_be) == 0, "Sin overlap Fonasa-BancoEstado")

    print("\n=== Cascada de mitigacion ===")
    escenarios = [
        (False, False, False),
        (True, False, False),
        (True, True, False),
        (True, True, True),
    ]
    for sv, fn, be in escenarios:
        e = calcular_estado_cascada(
            df_pdi, df_servel, df_fonasa, df_bancoestado,
            sv, fn, be,
            ruts_invalidos_pdi=len(df_invalidos),
        )
        print(
            f"  Servel={sv}, Fonasa={fn}, BE={be} -> "
            f"total={e['total_pdi']:,} rec={e['rec_total']:,} pend={e['pendientes']:,}"
        )

    print("\n=== Metricas Sprint 2 (estado completo) ===")
    estado = calcular_estado_cascada(
        df_pdi, df_servel, df_fonasa, df_bancoestado,
        True, True, True,
        ruts_invalidos_pdi=len(df_invalidos),
    )
    metricas = calcular_metricas_sprint2(estado)
    for k, v in metricas.items():
        if k == "monto_fiscal_protegido":
            print(f"  {k}: CLP ${v:,}")
        elif k == "pct_mitigacion":
            print(f"  {k}: {v:.2f}%")
        else:
            print(f"  {k}: {v:,}")

    esperado_rec = int(round(N_PDI * (PCT_SERVEL + PCT_FONASA + PCT_BANCOESTADO)))
    _check(metricas["recuperados"] == esperado_rec,
           f"Recuperados {metricas['recuperados']} == esperado {esperado_rec}")
    _check(metricas["monto_fiscal_protegido"] == esperado_rec * MONTO_PGU_MENSUAL,
           "Monto fiscal == recuperados * PGU mensual")
    _check(abs(metricas["pct_mitigacion"] - (PCT_SERVEL + PCT_FONASA + PCT_BANCOESTADO) * 100) < 0.01,
           "% mitigacion == suma de porcentajes")
    _check(metricas["ruts_invalidos_pdi"] == len(df_invalidos),
           "ruts_invalidos_pdi se propaga al estado")

    print("\n=== Cascada serializada (todos los cargados) ===")
    df_cascada = serializar_cascada(estado["pasos_cascada"])
    print(df_cascada.to_string(index=False))

    print("\n=== Stacked bar serializada ===")
    df_stacked = serializar_stacked_bar(estado)
    print(df_stacked.to_string(index=False))

    print("\n=== Log de auditoria ===")
    log = generar_log_auditoria(estado["df_recuperados"])
    print(f"  Filas: {len(log):,}")
    print(f"  Columnas: {list(log.columns)}")
    print("  Primeras filas:")
    print(log.head(3).to_string(index=False))
    _check("ID de Transaccion" in log.columns, "Log incluye ID de Transaccion")
    _check(log["ID de Transaccion"].is_unique, "IDs de transaccion unicos")

    print("\n[OK] Smoke test Sprint 2 completo")


if __name__ == "__main__":
    main()