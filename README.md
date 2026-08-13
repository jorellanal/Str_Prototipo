# SVP-IPS - Sistema de Validacion de Presencialidad

Prototipo **Streamlit** que demuestra como el cruce masivo de datos reduce
los errores de suspension de pensiones (PGU) en el IPS, Chile.

## Contexto

La PDI entrego datos que indicaban que ~13.000 pensionados estaban fuera
de Chile por mas de 180 dias, provocando la suspension indebida de la
**PGU** (Pension Garantizada Universal). Este dashboard simula el flujo
de mitigacion cruzando la PDI con fuentes alternativas:

- **Servel** - registro de votacion (40% de los casos validados).
- **Fonasa** - atenciones medicas presenciales (20% adicional).
- **BancoEstado** - giros presenciales en sucursal/cajero (15% adicional).

Resultado: el sistema reduce las supuestas suspensiones de **13.000** a
**3.250** casos (75% de mitigacion). Ademas detecta ~650 RUTs con DV
invalido en la base de origen ("Data Sucia").

## Stack

- Python 3.12 (3.13 / 3.14 soportados)
- Streamlit >=1.52
- Pandas >=2.3.3 / NumPy >=2.3.4
- Altair >=6.0 (waterfall + stacked bar)

## Instalacion

### Windows / PowerShell

```powershell
# 1. Clonar
git clone https://github.com/jorellanal/Str_Prototipo.git
cd Str_Prototipo

# 2. Bootstrap del entorno virtual + dependencias
.\setup.ps1

# 3. Activar entorno y ejecutar
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```

### Windows / cmd

```cmd
git clone https://github.com/jorellanal/Str_Prototipo.git
cd Str_Prototipo
setup.bat
.venv\Scripts\activate.bat
streamlit run app.py
```

> **No instales dependencias en el Python global.** Todo va dentro de `.venv/`.

> **PowerShell:** si tenes Pester (u otro modulo) cargado, no escribas
> solo `setup` — colisiona con el cmdlet `Setup` de Pester y obtendras
> "The Setup command may only be used inside a Describe block". Usa
> siempre `.\setup.ps1` con extension explicita.

## Estructura

```
Str_Prototipo/
├── app.py                 # Dashboard Streamlit (3 tabs)
├── smoke_test.py          # Asserts reproducibles (validacion de logica)
├── requirements.txt       # Dependencias pinneadas por minimo
├── setup.ps1              # Bootstrap automatico del entorno (PowerShell)
├── setup.bat              # Bootstrap automatico del entorno (cmd)
├── .streamlit/
│   └── config.toml        # Tema institucional (primaryColor, base, etc.)
└── modules/
    ├── __init__.py
    ├── data.py            # Generador RUTs (DV mod 11), 3 fuentes, inyeccion
    │                      # de Data Sucia, validador DV
    ├── logic.py           # Cascada 3-fuentes, metricas Sprint 2,
    │                      # log de auditoria con ID de transaccion
    └── style.py           # CSS institucional (azul #003366 / verde)
```

## Uso

1. Abrir la app (`streamlit run app.py`).
2. En el sidebar, pulsar **Cargar Archivo Servel**.
   - Metricas: 13.000 / 5.200 / 40% / CLP $1.164.800.000
   - Cascada: -5.200 en verde
   - Tabla: 5.200 beneficiarios validados
3. Pulsar **Cargar Archivo Fonasa**.
   - Metricas: 13.000 / 7.800 / 60% / CLP $1.747.200.000
   - Cascada: -2.600 verde adicional
   - Tabla: 7.800 beneficiarios validados
4. Pulsar **Cargar Archivo BancoEstado**.
   - Metricas: 13.000 / 9.750 / 75% / CLP $2.184.000.000
   - Cascada: -1.950 verde adicional
   - Tabla: 9.750 beneficiarios validados

El tab **Log de Auditoria** muestra la tabla completa con
`RUT | Nombre | Fuente de Validacion | Fecha del Hito | ID de Transaccion`
y permite descargar el CSV `Reporte_Trazabilidad_Contraloria.csv`.

El tab **Vision Ciudadana** simula la consulta que haria un pensionado
ingresando su RUT. Si fue validado, muestra un mensaje tipo SMS con la
fuente y el monto reactivado.

## Datos

- **100% simulados.** RUTs con DV modulo 11 valido, nombres ficticios
  chilenos, fechas relativas al 20/01/2026.
- `np.random.seed(42)` asegura que la demo es reproducible.
- El 5% de la base PDI se inyecta con DV corrupto para probar el modulo
  de mitigacion de "Data Sucia".

## Despliegue en Streamlit Cloud

La version de Python se fija en **Settings > Advanced settings > Python version**
del panel de Streamlit Cloud (no usar `runtime.txt`, el archivo es ignorado).
El stack declarado en `requirements.txt` es compatible con 3.12, 3.13 y 3.14.

## Sprint

- **Sprint 1**: Maqueta visual y logica de cascada (2 fuentes).
- **Sprint 2**: Incremento funcional — tercera fuente (BancoEstado),
  validacion DV de RUTs, 4 metricas ejecutivas (% mitigacion, monto
  fiscal protegido), tab de auditoria con exporte CSV, tab de vision
  ciudadana con SMS.
- Proximos: conexion a APIs reales, automatizacion de reversion
  masiva de PGU, dashboard operativo para IPS.