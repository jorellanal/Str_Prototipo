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

Resultado: el sistema reduce las supuestas suspensiones de **13.000** a
**5.200** casos (60% de mitigacion).

## Stack

- Python 3.12 (3.13 / 3.14 soportados)
- Streamlit >=1.52
- Pandas >=2.3.3 / NumPy >=2.3.4
- Altair >=6.0 (waterfall chart)

## Instalacion (Windows / PowerShell)

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

> **No instales dependencias en el Python global.** Todo va dentro de `.venv/`.

## Estructura

```
Str_Prototipo/
├── app.py                 # Dashboard Streamlit (UI)
├── requirements.txt       # Dependencias pinneadas por minimo
├── setup.ps1              # Bootstrap automatico del entorno
├── .gitignore
└── modules/
    ├── __init__.py
    ├── data.py            # Generador RUTs (DV modulo 11) + DataFrames
    ├── logic.py           # Cascada de mitigacion y metricas
    └── style.py           # CSS institucional (azul #0033A0 / gris)
```

## Uso

1. Abrir la app (`streamlit run app.py`).
2. En el sidebar, pulsar **Cargar Archivo Servel**.
   - Metricas: 13.000 / 5.200 / 7.800
   - Cascada: -5.200 en verde
   - Tabla: 5.200 beneficiarios validados
3. Pulsar **Cargar Archivo Fonasa**.
   - Metricas: 13.000 / 7.800 / 5.200
   - Cascada: -2.600 verde adicional
   - Tabla: 7.800 beneficiarios validados

## Datos

- **100% simulados.** RUTs con DV modulo 11 valido, nombres ficticios
  chilenos, fechas relativas al 20/01/2026.
- `np.random.seed(42)` asegura que la demo es reproducible.

## Despliegue en Streamlit Cloud

La version de Python se fija en **Settings > Advanced settings > Python version**
del panel de Streamlit Cloud (no usar `runtime.txt`, el archivo es ignorado).
El stack declarado en `requirements.txt` es compatible con 3.12, 3.13 y 3.14.

## Sprint

- **Sprint 1**: Maqueta visual y logica de cascada.
- Proximos: conexion a APIs reales, automatizacion de reversion
  masiva de PGU, dashboard operativo para IPS.
