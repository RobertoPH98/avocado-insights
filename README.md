# Avocado Insights · Equipo 4

Proyecto integrador TC5035.10, Tecnológico de Monterrey.

**[Avance 5. Modelo final — libreta ejecutada](notebooks/Avance5.Equipo4.ipynb)**

Se comparan siete ensambles y los modelos individuales del Avance 4 para estimar producción anual municipal de aguacate en toneladas. El análisis documenta ajuste de hiperparámetros, elección temporal, costos y límites de generalización.

## Desarrollo del proyecto

| Fase | Material |
|---|---|
| Exploración | [Avance 1](notebooks/Avance1.Equipo4.ipynb) |
| Ingeniería de características | [Avance 2](notebooks/Avance2.Equipo4.ipynb) |
| Baseline | [Avance 3](notebooks/Avance3.Equipo4.ipynb) |
| Modelos individuales alternativos | [Avance 4](notebooks/Avance4.Equipo4.ipynb) |
| Ensambles y elección final | [Avance 5](notebooks/Avance5.Equipo4.ipynb) |

Los enlaces a avances anteriores corresponden al repositorio completo; el paquete actual incluye las entradas y módulos necesarios para reproducir A5 independientemente.

## Ensambles y optimización

- **Homogéneos:** Bagging de Huber, Random Forest, Extra Trees y HistGradientBoosting.
- **Heterogéneos:** Voting H-Q, stacking temporal y blending temporal.
- **Bases heterogéneas:** Huber y cuantílica con las configuraciones ajustadas de A4, preservadas.
- **Comparación:** siete algoritmos individuales anteriores y dos referencias adicionales; 16 modelos en las tablas comunes.
- **Optimización:** Bagging Huber, Voting H-Q, HistGradientBoosting; 24 configuraciones por familia, 72 candidatos y 216 evaluaciones por ventana.

El stacking utiliza predicciones OOF temporales: una etiqueta interna s recibe predicciones de bases ajustadas solo hasta s−3. El blending mantiene las bases entrenadas antes de su bloque de calibración. Todas las preparaciones se aprenden en entrenamiento. Los costos de las comparativas incluyen preparación y metamodelos, sin reutilización de caché; las búsquedas sí reutilizan bases calculadas exclusivamente con entrenamiento.

## Selección y resultados

El desarrollo y ajuste usan 2018–2020; la elección utiliza 2021–2022. Se minimiza MAE y, dentro de 1% del mínimo, se favorece menor complejidad registrada. Las referencias también pueden ganar. La elección se congela antes de puntuar las pruebas de esta fase.

**Modelo final: Ridge A3.** En confirmación obtuvo 279.21 t de MAE. El mejor ensamble fue Voting H-Q, con 283.39 t; el mejor individual de A4 fue Huber, con 283.39 t. La ventaja relativa del ensamble sobre ese individual fue -0.00%.

| Indicador · 2025, 647 municipios | Modelo final | Huber A4 reajustado |
|---|---:|---:|
| MAE · t por municipio | 755.34 | 579.50 |
| RMSE · t | 6,478.33 | 4,678.20 |
| WAPE | 17.52% | 13.44% |
| R² | 0.9094 | 0.9528 |
| RMSLE | 0.6094 | 0.8703 |
| Sesgo agregado | +11.50% | +6.72% |

La mejora puntual de MAE frente a Huber en 2025 es -30.34%. La sensibilidad espacial por estados tiene percentiles [-40.79%, +11.57%]. La comparativa posterior no modifica la elección previa.

En la prueba concatenada 2023/2025, Bagging Huber obtuvo el menor MAE (690.30 t), frente a 749.63 t del seleccionado, una reducción puntual de 7.91%. Es un hallazgo posterior a la selección. El deterioro de Ridge frente a Huber en 2025 limita una recomendación operativa: se requiere un periodo nuevo para comparar estos candidatos antes de adopción.

**Límite de independencia:** 2023 se evaluó en A3 y 2025 en A4. En A5 se excluyen de entrenamiento y de selección, pero se declaran pruebas retrospectivas reutilizadas; no son nuevos tests ciegos. Falta una evaluación prospectiva independiente. No se garantiza que un ensamble supere a un individual ni que una ventaja agregada se repita en todo territorio.

## Datos y horizonte

Se conservan los 15,474 registros agrícolas originales atribuidos a DGSIAP/SADER, obtenidos de la copia secundaria documentada en `data/proveniencia.json`. La historia estatal 1980–2002 permanece separada y agricultura 2024 sigue en cuarentena por claves ambiguas.

Las series oficiales del Banco Mundial (inflación de Estados Unidos y tipo de cambio de México) y los PDFs del SMN/CONAGUA mantienen las instantáneas y hashes de los avances anteriores. El PDF nominal 2013 muestra 2012 y no se integra. El horizonte utiliza mediciones t−2 o anteriores y etiquetas de entrenamiento hasta t−3. Los datos son revisados y carecen de un archivo integral de fechas de publicación.

La cohorte requiere objetivo observado e historia t−2; los ceros reportados se preservan y no se imputan objetivos. No se miden ventas, rutas o emisiones. El modelo no sustituye validación de costos de error y disponibilidad real con el sponsor.

## Estructura

- `notebooks/Avance5.Equipo4.ipynb`: 15 celdas de código ejecutadas, 12 figuras, tablas, interpretaciones y declaración final.
- `src/ensambles_avance5.py`: ensambles, metamodelos temporales, búsqueda y decisión.
- `src/modelos_avance4.py`, `src/baseline_avance3.py`, `src/fe_avance2.py`: módulos heredados sin cambios.
- `data/raw/` y `data/externos/`: fuentes originales, licencia y procedencia.
- `data/avance5/`: predictor, matrices antes de preparación, panel y ficha estructurada.
- `resultados/avance5/`: comparativas, predicciones, figuras y diarios de búsqueda.
- `documentacion/avance5/`: protocolo, selección, ficha técnica, versión de lectura y controles de entrega.
- `scripts/ejecutar_avance5.py`: ejecución secuencial real desde un proceso limpio.

## Reproducción analítica

Entorno verificado: Python 3.12.14. Dependencias en `requirements_avance5.txt`.

```bash
python -m pip install -r requirements_avance5.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 python scripts/ejecutar_avance5.py
```

La ejecución vuelve a entrenar todos los modelos y evalúa sus predicciones; no simula salidas leyendo métricas guardadas. También puede usarse Jupyter con un kernel limpio y ejecución de todas las celdas en orden. Después de instalar dependencias no se necesita red. Los tiempos dependen de la máquina.

Se aprobaron 37 controles analíticos. La declaración de IA y las aportaciones individuales mantienen literalmente las dos tablas de la versión final del Avance 4; las decisiones finales corresponden a esta fase. La revisión académica final corresponde al equipo.

Versión de lectura: [Avance5.Equipo4_lectura.html](documentacion/avance5/Avance5.Equipo4_lectura.html). Ficha técnica: [ficha_modelo.md](documentacion/avance5/ficha_modelo.md).

## Integrantes

- José Roberto Sánchez Rocha — A00903762
- Josué Águila Ramos — A01796400
- Roberto Perézcano Hernández — A01730502

Profesor: Dr. Raúl Valente Ramírez Velarde. Sponsor: Dr. Jorge Antonio Ascencio Gutiérrez.
