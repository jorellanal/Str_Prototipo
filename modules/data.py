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
    n: int = 1000,
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
