# Avocado Insights · Equipo 4

Proyecto integrador TC5035.10, Tecnológico de Monterrey.

**[Avance 4. Modelos alternativos — libreta ejecutada](notebooks/Avance4.Equipo4.ipynb)**

Comparación de siete algoritmos individuales para estimar la producción anual municipal de aguacate, ajuste de los dos mejores y elección de un modelo para la siguiente etapa. Se conserva el objetivo, la fuente agrícola y el escenario temporal del baseline.

## Desarrollo del proyecto

| Fase | Material |
|---|---|
| Análisis exploratorio | [Avance 1](notebooks/Avance1.Equipo4.ipynb) |
| Ingeniería de características | [Avance 2](notebooks/Avance2.Equipo4.ipynb) |
| Modelo de referencia | [Avance 3](notebooks/Avance3.Equipo4.ipynb) |
| Modelos alternativos | [Avance 4](notebooks/Avance4.Equipo4.ipynb) |

Los avances 1–3 permanecen en el repositorio como antecedentes. Los archivos de este paquete permiten reproducir el Avance 4 de forma independiente; sus enlaces a avances anteriores corresponden al repositorio completo.

## Comparación y ajuste

Se entrenaron **ElasticNet, Huber, regresión cuantílica, CART, KNN, SVR y MLP**. Todos son individuales: un árbol, una red o un regresor según el caso. Ridge A3 y persistencia son referencias adicionales.

| Fase temporal | Años objetivo | Uso |
|---|---|---|
| Ranking | 2015–2017 | Comparar siete modelos sobre las mismas 17 entradas |
| Ajuste fino | 2018–2020 | 48 configuraciones para cuantílica y 48 para Huber |
| Confirmación | 2021–2022 | Elegir entre los dos modelos ajustados |
| Prueba interna | 2025 | Evaluar la elección congelada y las referencias |

Se registraron **96 configuraciones y 288 ajustes por ventana**, todos convergentes. La selección utiliza MAE en toneladas; también se reportan RMSE, WAPE, R², RMSLE, sesgo y tiempos. El ajuste redujo el MAE en 5.63% para cuantílica y 0.31% para Huber en 2018–2020. Las ganancias de búsqueda no se presuponen válidas en otros años.

## Modelo individual elegido

**HuberRegressor**, con `epsilon=1.01`, `alpha=1.264998997e-06` y conjunto completo de 17 entradas. La preparación, incluida la estandarización lineal del objetivo, se aprende dentro del entrenamiento. Tras imputar X, agregar indicadores y retirar constantes, el ajuste final utiliza 24 columnas efectivas. No se imputan etiquetas ni se promedian predicciones de distintos modelos.

En confirmación, Huber ajustado obtuvo 283.39 t y cuantílica ajustada 283.45 t de MAE. Los dos son lineales y usan igual número de entradas; la regla determinista favoreció el menor MAE. Cuantílica tuvo ligeramente menor RMSE y Huber menor tiempo de ajuste medido. **Ridge A3 obtuvo 279.21 t y superó a los dos ajustados en esa fase**. La elección corresponde al mejor entre los dos finalistas ajustados, sin declarar una superioridad uniforme sobre la referencia.

| Indicador · prueba interna 2025 | Huber elegido | Ridge A3 reajustado |
|---|---:|---:|
| MAE · toneladas por municipio | 579.50 | 755.34 |
| RMSE · toneladas | 4,678.20 | 6,478.33 |
| WAPE | 13.44% | 17.52% |
| RMSLE | 0.870 | 0.609 |
| Sesgo de volumen | +6.72% | +11.50% |

El ajuste final usa 7,963 municipio-año de 2007–2022 y se evalúa en 647 municipios de 2025. La mejora puntual del MAE frente a Ridge es **23.28%**; el RMSLE es mayor. El rango estatal de sensibilidad de la mejora es [-13.08%, +28.97%] y cruza cero. Son resultados retrospectivos, sin garantía de desempeño uniforme ni prospectivo.

## Datos y alcance

Se preservan los 15,474 registros agrícolas originales atribuidos a DGSIAP/SADER, obtenidos de la copia pública de Montse (`lapanquecita/aguacate`). Origen, licencia y hash fijo se documentan en `data/proveniencia.json`. La historia estatal 1980–2002 se separa del panel municipal. El año agrícola 2024 permanece en cuarentena por claves ambiguas.

Las fuentes externas conservan la instantánea del Avance 3: inflación de Estados Unidos y tipo de cambio de México del Banco Mundial, y temperatura estatal del SMN/CONAGUA. Se incluyen respuestas originales y 21 PDFs climáticos en ZIP. El archivo nominal 2013 muestra 2012 en su encabezado y no se integra. No se reasignan sus valores.

El horizonte utiliza mediciones t−2 o anteriores y etiquetas de entrenamiento hasta t−3. No hay particiones aleatorias de filas. 2023 ya fue evaluado en el Avance 3; 2025 fue explorado descriptivamente y constituye una reserva interna de modelado, sin ajuste con sus errores. Las fuentes revisadas carecen de un archivo completo de fechas de publicación. Los datos no miden ventas, exportaciones, rutas, combustible o emisiones.

## Estructura

- `notebooks/Avance4.Equipo4.ipynb`: análisis principal, 15 celdas de código ejecutadas y 8 figuras.
- `src/modelos_avance4.py`: siete algoritmos, preparación, comparación temporal y búsqueda.
- `src/baseline_avance3.py` y `src/fe_avance2.py`: módulos heredados, idénticos al commit de continuidad.
- `data/raw/` y `data/externos/`: entradas originales y procedencia.
- `data/avance4/`: panel, matrices, modelo serializado y ficha estructurada.
- `resultados/avance4/`: métricas, predicciones, diagnósticos, figuras y diarios de las dos búsquedas.
- `documentacion/avance4/`: protocolo, decisiones, ficha técnica, versión de lectura y verificación.
- `scripts/ejecutar_avance4.py`: ejecución secuencial de todas las celdas reales.

## Reproducción analítica

Entorno verificado: Python 3.12.14. Dependencias en `requirements_avance4.txt`.

```bash
python -m pip install -r requirements_avance4.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python scripts/ejecutar_avance4.py
```

También puede ejecutarse la libreta completa desde un kernel limpio de Jupyter. Después de instalar dependencias, no necesita red. Las fuentes incluidas permiten reconstruir las variables y volver a entrenar los modelos. El análisis realiza los ajustes reales; no recupera métricas precalculadas para simular ejecución. Los tiempos dependen de la máquina.

La ejecución entregada aprobó 33 controles y no presentó errores ni advertencias de convergencia. La declaración obligatoria de IA y contribuciones está en la última celda de texto. La revisión académica final corresponde al equipo.

Versión autosuficiente de lectura: [Avance4.Equipo4_lectura.html](documentacion/avance4/Avance4.Equipo4_lectura.html). Ficha técnica: [ficha_modelo.md](documentacion/avance4/ficha_modelo.md).

## Integrantes

- José Roberto Sánchez Rocha — A00903762
- Josué Águila Ramos — A01796400
- Roberto Perézcano Hernández — A01730502

Profesor: Dr. Raúl Valente Ramírez Velarde. Sponsor: Dr. Jorge Antonio Ascencio Gutiérrez.

## Continuidad

Conservar este modelo individual y su protocolo para la siguiente fase. La frontera de epsilon, el sesgo, los errores territoriales y el desempeño de municipios pequeños requieren nuevos experimentos con evaluación posterior independiente. La aceptación operativa, los costos de error y la disponibilidad real de las fuentes quedan pendientes de validación con el sponsor.
