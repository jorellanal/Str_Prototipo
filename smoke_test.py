"""Smoke test ejecutable desde la raiz con .venv/Scripts/python.exe"""
from modules.data import (
    calcular_dv,
    formatear_rut,
    generar_base_pdi,
    generar_fonasa,
    generar_servel,
)
from modules.logic import calcular_estado_cascada, serializar_cascada


def main() -> None:
    print("=== Test DV modulo 11 ===")
    for n in [11111111, 12345678, 20000000, 10000000, 19000000]:
        print(f"  {n} -> {formatear_rut(n)}")

    df_pdi = generar_base_pdi(n=13000)
    df_servel = generar_servel(df_pdi, pct=0.40)
    df_fonasa = generar_fonasa(df_pdi, df_servel, pct=0.20)

    print("\n=== DataFrames generados ===")
    print(f"Universo PGU: 2.200.000 (referencia)")
    print(f"PDI rechazados: {len(df_pdi):,}")
    print(f"  Ejemplo: {df_pdi.iloc[0]['RUT']} | {df_pdi.iloc[0]['Nombre']}")
    print(f"  Dias fuera: {df_pdi.iloc[0]['Dias_Fuera']}")
    print(f"Servel recupera: {len(df_servel):,} (40% de rechazados)")
    print(f"  Ejemplo: {df_servel.iloc[0]['RUT']} | {df_servel.iloc[0]['Detalle']}")
    print(f"Fonasa recupera adicional: {len(df_fonasa):,} (20% adicional)")
    print(f"  Ejemplo: {df_fonasa.iloc[0]['RUT']} | {df_fonasa.iloc[0]['Detalle']}")

    overlap = set(df_servel["RUT"]) & set(df_fonasa["RUT"])
    print(f"\nOverlap Servel<->Fonasa: {len(overlap)} (esperado: 0)")

    print("\n=== Cascada de mitigacion ===")
    for sv, fn in [(False, False), (True, False), (True, True)]:
        e = calcular_estado_cascada(df_pdi, df_servel, df_fonasa, sv, fn)
        print(
            f"  Servel={sv}, Fonasa={fn} -> "
            f"total={e['total_pdi']} rec={e['rec_total']} pend={e['pendientes']}"
        )

    print("\n=== Cascada serializada (ambos cargados) ===")
    estado_full = calcular_estado_cascada(df_pdi, df_servel, df_fonasa, True, True)
    df_cascada = serializar_cascada(estado_full["pasos_cascada"])
    print(df_cascada.to_string(index=False))

    print("\n[OK] Smoke test completo")


if __name__ == "__main__":
    main()
