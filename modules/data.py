"""Generacion de datos simulados para SVP-IPS.

Crea RUTs chilenos validos (DV modulo 11) y DataFrames que representan
los registros originales de PDI y las fuentes alternativas de cruce
(Servel y Fonasa).
"""

from datetime import date, timedelta

import numpy as np
import pandas as pd


NOMBRES = [
    "Maria", "Juan", "Carlos", "Ana", "Pedro", "Luis", "Jose", "Camila",
    "Francisca", "Diego", "Sebastian", "Valentina", "Catalina", "Matias",
    "Florencia", "Ignacio", "Isidora", "Tomas", "Antonia", "Felipe",
    "Constanza", "Andres", "Josefa", "Maximiliano", "Renata", "Vicente",
    "Martina", "Benjamin", "Sofia", "Agustin", "Emilia", "Nicolas",
    "Trinidad", "Joaquin", "Amanda", "Cristobal", "Paula", "Gabriel",
    "Elena", "Rodrigo", "Macarena", "Hernan", "Daniela", "Ricardo",
    "Lorena", "Patricio", "Ximena", "Marcelo", "Veronica", "Eduardo",
    "Patricia", "Gustavo", "Claudia", "Raul", "Alejandra", "Sergio",
    "Romina", "Pablo", "Cecilia", "Fernando", "Carolina", "Roberto",
    "Isabel", "Manuel", "Adriana", "Hector", "Soledad", "Alfredo",
    "Pilar", "Esteban", "Margarita", "Julio", "Beatriz", "Mauricio",
    "Consuelo", "Osvaldo", "Yasna", "Dario", "Monica", "Claudio",
    "Paulina", "Alberto", "Sandra", "Gonzalo", "Ruth", "Hugo",
    "Eliana", "Mario", "Ines", "Luis", "Rosa", "Ivan", "Gladys",
    "Ramon", "Miriam", "Christian", "Olga", "Felipe", "Iris",
    "Hernan", "Luz", "Victor", "Susana", "Eduardo", "Carmen",
    "Alfonso", "Gladys", "Omar", "Marta", "Tito", "Julia",
    "Dominga", "Camilo", "Aida", "Segundo", "Elba", "Nestor",
    "Nelly", "Erick", "Elsa", "Boris", "Petronila", "Erik",
    "Regina", "Yolanda", "Fabian", "Lidia", "Elias", "Teresa",
    "Simon", "Eva", "Lorenzo", "Magdalena", "Ariel", "Sara",
    "Dagoberto", "Rosario", "Genaro", "Aurora", "Edmundo", "Laura",
    "Octavio", "Cristina", "Wilfredo", "Alicia", "Eleuterio", "Ester",
    "Rigoberto", "Pabla", "Hermogenes", "Edita", "Froilan", "Fidelia",
    "Remigio", "Dorita", "Eulogio", "Nuria", "Hilario", "Amalia",
    "Bonifacio", "Encarnacion", "Aniceto", "Rosalia", "Epifanio", "Presentacion",
]

APELLIDOS = [
    "Gonzalez", "Munoz", "Rojas", "Diaz", "Perez", "Soto", "Contreras",
    "Silva", "Martinez", "Sepulveda", "Morales", "Rodriguez", "Lopez",
    "Fuentes", "Hernandez", "Torres", "Araya", "Flores", "Espinoza",
    "Valenzuela", "Castillo", "Ramirez", "Reyes", "Gutierrez", "Castro",
    "Vargas", "Alvarez", "Vasquez", "Fernandez", "Carrasco", "Orellana",
    "Jara", "Bravo", "Vergara", "Maldonado", "Parra", "Romero",
    "Salazar", "Cruz", "Aguilera", "Riquelme", "Gallardo", "Henriquez",
    "Navarro", "Saavedra", "Tapia", "Pizarro", "Palma", "Salgado",
    "Mendoza", "Lara", "Escobar", "Donoso", "Arancibia", "Pino",
    "Carrillo", "Garrido", "Cordova", "Acevedo", "Poblete", "Bustamante",
    "Olivares", "Toledo", "Cifuentes", "Marin", "Sandoval", "Nunez",
    "Caceres", "Leiva", "Quezada", "Valdes", "Vera", "Tobar",
    "Urbina", "Paredes", "Acuña", "Cofré", "Godoy", "Rubio",
]

LOCALES_SERVEL = [
    "Liceo A-1 Republica Argentina", "Escuela D-92 Brasilia", "Liceo B-30 Maipu",
    "Colegio San Ignacio", "Escuela E-78 Bicentenario", "Liceo Industrial",
    "Gimnasio Municipal", "Centro Cultural Estacion Mapocho", "Liceo C-33",
    "Colegio Santa Maria", "Escuela F-25 Alborada", "Liceo A-32",
]

PRESTADORES_FONASA = [
    "Hospital Sotero del Rio", "Cesfam Carol Urzua", "Hospital del Trabajador",
    "Cesfam Dr. Salvador Allende", "Hospital Barros Luco", "Cesfam Cristo Vive",
    "Hospital Roberto del Rio", "Cesfam Padre Vicente Irarrazaval",
    "Cesfam Quinta Bella", "Hospital San Borja Arriaran", "Cesfam Santa Julia",
    "Integra Medica Plaza Norte",
]

ESPECIALIDADES_FONASA = [
    "Consulta general", "Control cardiovascular", "Kinesiologia",
    "Examenes de laboratorio", "Consulta traumatologica", "Atencion dental",
    "Control diabetologico", "Consulta geriatrica", "Vacunacion",
    "Control oftalmologico",
]

SUCURSALES_BANCOESTADO = [
    "Sucursal Ahumada", "Sucursal Plaza Norte", "Sucursal Maipu",
    "Sucursal La Florida", "Sucursal Puente Alto", "Sucursal San Bernardo",
    "Sucursal Maipu Express", "Cajero Auto Servicio Plaza Oeste",
    "Sucursal Quilicura", "Sucursal Estacion Central", "Sucursal Quinta Normal",
    "Sucursal San Miguel",
]

CANALES_BANCOESTADO = [
    "Cajero automatico", "Ventanilla", "Caja Vecina", "App BancoEstado",
]

DIGITOS_DV_VALIDOS = "0123456789K"


def _normalizar_rut(rut: str) -> str:
    """Quita puntos, espacios y guion; devuelve mayusculas."""
    return rut.replace(".", "").replace(" ", "").replace("-", "").strip().upper()


def validar_rut(rut: str) -> bool:
    """Valida que el digito verificador de un RUT chileno sea correcto.

    Acepta formatos:
      - 12345678-9
      - 12.345.678-9
      - 12345678K
      - 123456789 (9 digitos, DV al final)

    Regla: modulo 11 sobre el cuerpo numerico, comparando contra el DV
    reportado. Si el cuerpo no es numerico o el DV no esta en
    {0-9, K}, retorna False.
    """
    limpio = _normalizar_rut(rut)
    if len(limpio) < 2:
        return False
    dv_reportado = limpio[-1]
    cuerpo = limpio[:-1]
    if dv_reportado not in DIGITOS_DV_VALIDOS:
        return False
    if not cuerpo.isdigit():
        return False
    try:
        numero = int(cuerpo)
    except ValueError:
        return False
    return calcular_dv(numero) == dv_reportado


def inyectar_ruts_invalidos(
    df_pdi: pd.DataFrame,
    pct: float = 0.05,
    seed: int = 99,
) -> pd.DataFrame:
    """Devuelve una copia del DataFrame con un % de RUTs modificados
    para tener DV incorrecto. Simula 'Data Sucia' en el origen PDI.
    """
    df = df_pdi.copy()
    rng = np.random.default_rng(seed)
    n = int(round(len(df) * pct))
    n = min(n, len(df))
    if n == 0:
        return df
    indices = rng.choice(len(df), size=n, replace=False)
    for idx in indices:
        rut_actual = df.at[idx, "RUT"]
        cuerpo, _, dv_actual = rut_actual.partition("-")
        dv_correcto = calcular_dv(int(cuerpo.replace(".", "")))
        candidatos = [d for d in DIGITOS_DV_VALIDOS if d != dv_correcto]
        dv_invalido = candidatos[int(rng.integers(0, len(candidatos)))]
        numero = int(cuerpo.replace(".", ""))
        df.at[idx, "RUT"] = formatear_rut(numero)[:-1] + dv_invalido
    return df


def detectar_ruts_invalidos(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna un sub-DataFrame con los RUTs cuyo DV no valida."""
    mascara = ~df["RUT"].apply(validar_rut)
    return df[mascara].copy()


def generar_bancoestado(
    df_pdi: pd.DataFrame,
    df_servel: pd.DataFrame,
    df_fonasa: pd.DataFrame,
    pct: float = 0.15,
    seed: int = 43,
) -> pd.DataFrame:
    """Selecciona un % ADICIONAL de RUTs del PDI (excluyendo Servel y
    Fonasa) con giro presencial en BancoEstado posterior al reporte PDI.

    Esquema alineado a generar_servel/generar_fonasa para que la cascada
    pueda concatenarlos sin transformaciones.
    """
    rng = np.random.default_rng(seed)
    ruts_ya_validados = set(df_servel["RUT"].tolist()) | set(df_fonasa["RUT"].tolist())
    df_disponibles = df_pdi[~df_pdi["RUT"].isin(ruts_ya_validados)].reset_index(drop=True)

    n = int(round(len(df_pdi) * pct))
    n = min(n, len(df_disponibles))
    if n == 0:
        return pd.DataFrame(
            columns=["RUT", "Nombre", "Fuente", "Fecha_Validacion", "Detalle"]
        )

    indices = rng.choice(len(df_disponibles), size=n, replace=False)
    base = df_disponibles.iloc[indices][["RUT", "Nombre"]].reset_index(drop=True)
    sucursales = rng.choice(SUCURSALES_BANCOESTADO, size=n)
    canales = rng.choice(CANALES_BANCOESTADO, size=n)
    montos = rng.integers(low=50_000, high=350_000, size=n)
    fechas_giro = [
        (date(2026, 1, 20) - timedelta(days=int(rng.integers(0, 120)))).isoformat()
        for _ in range(n)
    ]

    return pd.DataFrame(
        {
            "RUT": base["RUT"],
            "Nombre": base["Nombre"],
            "Fuente": "BancoEstado",
            "Fecha_Validacion": fechas_giro,
            "Detalle": [
                f"Giro ${int(m):,} - {suc} ({can})"
                for m, suc, can in zip(montos, sucursales, canales)
            ],
        }
    )


def calcular_dv(numero: int) -> str:
    """Calcula el digito verificador de un RUT chileno (modulo 11)."""
    reversed_digits = [int(d) for d in str(numero)][::-1]
    factors = [2, 3, 4, 5, 6, 7, 2, 3, 4]
    s = sum(d * factors[i % len(factors)] for i, d in enumerate(reversed_digits))
    remainder = 11 - (s % 11)
    if remainder == 11:
        return "0"
    if remainder == 10:
        return "K"
    return str(remainder)


def formatear_rut(numero: int) -> str:
    """Formatea un numero de RUT con puntos y guion + DV."""
    cuerpo = f"{numero:,}".replace(",", ".")
    return f"{cuerpo}-{calcular_dv(numero)}"


def generar_base_pdi(
    n: int = 13000,
    seed: int = 42,
    fecha_base: date | None = None,
) -> pd.DataFrame:
    """Genera el DataFrame inicial de casos PDI (todos fuera > 180 dias)."""
    rng = np.random.default_rng(seed)
    fecha_base = fecha_base or date(2026, 1, 20)

    numeros = rng.integers(low=10_000_000, high=19_999_999, size=n)
    ruts = [formatear_rut(int(num)) for num in numeros]

    nombres = rng.choice(NOMBRES, size=n)
    apellidos1 = rng.choice(APELLIDOS, size=n)
    apellidos2 = rng.choice(APELLIDOS, size=n)
    nombres_completos = [
        f"{n} {a1} {a2}" for n, a1, a2 in zip(nombres, apellidos1, apellidos2)
    ]

    dias_fuera = rng.integers(low=181, high=460, size=n)
    fechas_registro = [
        fecha_base - timedelta(days=int(d) - 180) for d in dias_fuera
    ]

    return pd.DataFrame(
        {
            "RUT": ruts,
            "Nombre": nombres_completos,
            "Dias_Fuera": dias_fuera,
            "Fecha_Registro_PDI": [f.isoformat() for f in fechas_registro],
        }
    )


def generar_servel(
    df_pdi: pd.DataFrame,
    pct: float = 0.40,
    seed: int = 42,
) -> pd.DataFrame:
    """Selecciona un % de RUTs del PDI que aparecen con voto en Servel."""
    rng = np.random.default_rng(seed + 1)
    n = int(round(len(df_pdi) * pct))
    n = min(n, len(df_pdi))
    indices = rng.choice(len(df_pdi), size=n, replace=False)

    base = df_pdi.iloc[indices][["RUT", "Nombre"]].reset_index(drop=True)
    locales = rng.choice(LOCALES_SERVEL, size=n)
    fechas_voto = [
        (date(2026, 1, 12) - timedelta(days=int(rng.integers(0, 90)))).isoformat()
        for _ in range(n)
    ]

    return pd.DataFrame(
        {
            "RUT": base["RUT"],
            "Nombre": base["Nombre"],
            "Fuente": "Servel",
            "Fecha_Validacion": fechas_voto,
            "Detalle": locales,
        }
    )


def generar_fonasa(
    df_pdi: pd.DataFrame,
    df_servel: pd.DataFrame,
    pct: float = 0.20,
    seed: int = 42,
) -> pd.DataFrame:
    """Selecciona un % ADICIONAL de RUTs del PDI (excluyendo Servel) con atencion Fonasa."""
    rng = np.random.default_rng(seed + 2)
    ruts_ya_validados = set(df_servel["RUT"].tolist())
    df_disponibles = df_pdi[~df_pdi["RUT"].isin(ruts_ya_validados)].reset_index(drop=True)

    n = int(round(len(df_pdi) * pct))
    n = min(n, len(df_disponibles))
    indices = rng.choice(len(df_disponibles), size=n, replace=False)

    base = df_disponibles.iloc[indices][["RUT", "Nombre"]].reset_index(drop=True)
    prestadores = rng.choice(PRESTADORES_FONASA, size=n)
    especialidades = rng.choice(ESPECIALIDADES_FONASA, size=n)
    fechas_atencion = [
        (date(2026, 1, 20) - timedelta(days=int(rng.integers(0, 120)))).isoformat()
        for _ in range(n)
    ]

    return pd.DataFrame(
        {
            "RUT": base["RUT"],
            "Nombre": base["Nombre"],
            "Fuente": "Fonasa",
            "Fecha_Validacion": fechas_atencion,
            "Detalle": [f"{esp} - {pre}" for esp, pre in zip(especialidades, prestadores)],
        }
    )
