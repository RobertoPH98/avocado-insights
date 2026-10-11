# Avocado Insights · Avance 2 · Equipo 4

**[Abrir la libreta ejecutada](notebooks/Avance2.Equipo4.ipynb)**

Ingeniería de características para el componente de oferta municipal de aguacate como base de planeación logística. Continúa el Avance 1 con los mismos bytes de datos y responde al comentario del doctor sobre los faltantes de 1980–2002.

## Contenido verificado

- 14 celdas de código ejecutadas en orden, sin errores ni advertencias capturadas.
- 9 figuras compuestas y 25 tablas CSV, además de conclusiones calculadas.
- 18 controles automatizados de calidad, calendario, separación de objetivos, esquemas y serialización.
- 74 columnas iniciales; 51 después de selección; alternativa con 43 columnas al aplicar PCA al bloque numérico.
- 10 componentes retienen 97.06% de la varianza de las 18 variables numéricas seleccionadas. Los indicadores permanecen fuera de PCA.

## Decisiones que deben poder explicarse

1. Los 981 registros de 1980–2002 son estatales: se conservan aparte, sin imputar municipios.
2. Se preservan las 900 filas de 2024 en cuarentena por claves ambiguas, sin deduplicación arbitraria.
3. El escenario utiliza mediciones de t−2 o anteriores. Una ausencia anual no se sustituye por cero ni se confunde con el año anterior disponible.
4. El objetivo es producción municipal anual en toneladas. Solo X se imputa para el algoritmo, con medianas de entrenamiento e indicadores de ausencia; y nunca se imputa.
5. Imputación, cuantiles, Yeo–Johnson, one-hot, escalamiento, filtros y PCA se ajustan en 2007–2015. La validación 2018–2020 no reajusta parámetros.
6. La menor asimetría y la compresión no prueban mejores predicciones. En la prueba instrumental, persistencia obtiene menor MAE/RMSE en toneladas; Ridge completo obtiene menor RMSLE. Se conserva esa evidencia, sin prometer mejoras no observadas.
7. El archivo es una instantánea sin fechas de publicación por registro. La aplicación de 2025 es retrospectiva y la reserva 2023 ya se exploró en el EDA. No se presenta como una prueba prospectiva.
8. Estos datos no miden rutas, acopios, combustible ni emisiones. El componente de oferta necesita una integración logística posterior.

## Estructura añadida

| Ruta | Función |
|---|---|
| `notebooks/Avance2.Equipo4.ipynb` | Entregable principal, con salidas incrustadas |
| `src/fe_avance2.py` | Implementación auditable de preparación, filtros y extracción |
| `data/raw/` | Fuente intacta y licencia del distribuidor, iguales al Avance 1 |
| `data/proveniencia.json` | Origen, commit del distribuidor y hash de los datos |
| `data/avance2/` | Panel, conjuntos separados, atributos, matrices NPZ, claves/objetivo CSV, diccionario y parámetros |
| `resultados/avance2/` | Tablas completas, figuras y conclusiones |
| `documentacion/avance2/` | Versión de lectura, guía de entrega y verificación |
| `scripts/ejecutar_avance2.py` | Ejecución secuencial en proceso nuevo, sin servidor de notebooks |
| `requirements_avance2.txt` | Dependencias de esta fase |

El paquete añade el Avance 2. Los archivos compartidos de `data/raw/` y `data/proveniencia.json` conservan los mismos bytes del repositorio verificado. No sustituye el README principal ni las entregas previas.

## Reproducción

Se verificó con Python 3.12.14. Desde la raíz del repositorio:

```bash
python -m pip install -r requirements_avance2.txt
python -m jupyterlab
```

Abrir `notebooks/Avance2.Equipo4.ipynb`, ejecutar **Restart Kernel and Run All Cells** y guardar. No se necesitan red ni credenciales para los cálculos; la instalación inicial sí descarga dependencias.

También se puede ejecutar en un proceso nuevo:

```bash
python scripts/ejecutar_avance2.py
```

La ejecución incluida se realizó mediante IPython en un proceso Python nuevo, con espacio de nombres limpio, en el orden de las 14 celdas y capturando todas sus salidas. No se simularon contadores ni resultados. El método no requiere sockets de kernel. Se comprobó el formato nbformat y la ausencia de salidas de error. El notebook es compatible con un kernel Python de Jupyter.

## Reutilizar matrices en Avance 3

```python
import numpy as np
import pandas as pd

with np.load('data/avance2/matrices_train.npz', allow_pickle=False) as data:
    X = data['X_seleccionada']
    columnas = data['columnas_seleccionada']
claves = pd.read_csv('data/avance2/claves_objetivo_train.csv', dtype={'cvegeo': str})
y = claves['produccion_t'].to_numpy()
assert len(X) == len(y)
```

Cada archivo NPZ contiene `X_seleccionada`, `columnas_seleccionada`, `X_pca` y `columnas_pca`. El CSV de claves de la misma partición conserva exactamente el mismo orden. Cargar la clave territorial como texto preserva ceros iniciales. Las métricas predictivas de reserva/aplicación no se calculan en esta entrega.

El objeto `preprocesador_avance2.joblib` conserva los parámetros y necesita `src/fe_avance2.py` importable y las versiones documentadas. Para validación con origen móvil, se debe reconstruir y ajustar un preprocesador dentro de cada ventana de entrenamiento; no reutilizar el objeto global como si hubiera sido ajustado en cada ventana.

## Equipo

José Roberto Sánchez Rocha — A00903762 · Josué Águila Ramos — A01796400 · Roberto Perézcano Hernández — A01730502.

Profesor: Dr. Raúl Valente Ramírez Velarde. Sponsor: Dr. Jorge Antonio Ascencio Gutiérrez.

## Entrega

Seguir [COMO_SUBIR_Y_ENTREGAR.md](documentacion/avance2/COMO_SUBIR_Y_ENTREGAR.md). En Canvas se entrega la liga directa al notebook en GitHub. La publicación y el envío en Canvas son pasos distintos.
