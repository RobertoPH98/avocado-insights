# Ficha técnica · Modelo final

**Avocado Insights · Equipo 4 · TC5035.10 · 1 de noviembre de 2026**

## Propósito y población

Estimar producción anual municipal de aguacate en toneladas para anticipar oferta territorial. La población evaluable tiene objetivo observado e historia de producción t−2. Un cero reportado es válido. Un municipio sin historia queda fuera de la cohorte y requiere otro mecanismo de estimación.

## Predictor elegido

- Modelo: **Ridge A3**.
- Estrategia: Individual / referencia.
- Configuración efectiva: Ridge alpha=1, solver SVD, sin intercepto; escala de X de entrenamiento sin centrar. Regla en unidades originales: ŷ = max(0, 1.046145842 × producción t−2).
- Ajuste final: 7,963 observaciones de 2007–2022.
- Prueba retrospectiva principal: 647 municipios, 2025.
- Horizonte: mediciones hasta t−2; etiquetas de entrenamiento hasta t−3 por origen.
- Salida: toneladas no negativas; la limitación inferior de predicciones se contabiliza.
- Entradas finales: produccion_lag2.

La preparación de cada predictor se aprende dentro del entrenamiento. Incluye mediana e indicadores de ausencia, filtrado de constantes y escalamiento cuando aplica. Las transformaciones lineales del objetivo se invierten a toneladas. Las variantes residuales suman el nivel histórico disponible a su estimación de cambio.

## Evidencia de ensambles

Se construyeron cuatro familias homogéneas —Bagging Huber, Random Forest, Extra Trees y HistGradientBoosting— y tres heterogéneas —Voting H-Q, stacking temporal y blending temporal—. Los heterogéneos usan Huber y cuantílica ajustados en A4.

El stacking aprende de predicciones internas para años s, generadas con bases ajustadas hasta s−3. El metamodelo no recibe predicciones ajustadas sobre sus propias etiquetas. Luego se reajustan las bases con la historia completa permitida del origen externo. El blending conserva las bases entrenadas antes de calibración, sin un reajuste posterior que cambie su distribución. Voting promedia los dos predictores con pesos positivos. La diversidad se analiza mediante correlación de residuos de desarrollo.

Las búsquedas seleccionaron tres familias por regla registrada: mejor homogénea, mejor heterogénea y mejor restante. Se evaluaron 24 configuraciones por familia, 72 candidatos y 216 evaluaciones temporales. La inicial se incluyó siempre. Los espacios de búsqueda, resultados por ventana y convergencia acompañan la libreta.

## Elección y compromisos

El ajuste usa 2018–2020 y la elección 2021–2022. Se minimiza MAE; dentro de 1% del mínimo se favorece la menor complejidad registrada, después MAE y nombre. La tolerancia es metodológica y provisional. Las referencias también pueden ganar: no se fuerza una sustitución sin valor medido.

Ridge A3 obtuvo 279.2133 t en confirmación, con 0.010 segundos de ajuste completo en los dos orígenes. El mejor ensamble fue Voting H-Q (283.3903 t) y el mejor individual de A4 fue Huber (283.3891 t): mejora relativa del ensamble -0.000%. Las tablas también incluyen los otros individuales y Ridge/persistencia. La comparación posterior de prueba no modifica esa decisión.

## Evaluación de 2025

| Métrica | Modelo elegido | Huber A4 reajustado |
|---|---:|---:|
| MAE · t | 755.3440 | 579.4988 |
| RMSE · t | 6478.3275 | 4678.1986 |
| WAPE | 17.5190% | 13.4405% |
| R² | 0.909437 | 0.952774 |
| RMSLE | 0.609365 | 0.870316 |
| Sesgo agregado | +11.5046% | +6.7171% |

La mejora puntual frente a Huber es -30.3443%. Los 1,500 remuestreos emparejados de estados dieron percentiles de mejora [-40.79%, +11.57%]. Describen sensibilidad espacial condicionada a 2025, sin incorporar variación de entrenamiento o de años futuros.

La superioridad de confirmación no se sostuvo frente a Huber en 2025. En las dos pruebas concatenadas, Bagging Huber logró 690.30 t frente a 749.63 t del modelo elegido (7.91% de reducción). Ese resultado se informa como diagnóstico posterior, sin cambiar la elección ni denominarlo selección independiente. La adopción operativa queda pendiente de un periodo nuevo; Bagging y Huber son comparadores prioritarios.

Se entregan cuatro figuras principales del rendimiento: observado frente a estimado, residuos por escala histórica, calibración de magnitudes y MAE por cuartil productivo. Cada una tiene una interpretación calculada. La trayectoria usa una cohorte fija de municipios; el hueco 2024 se muestra sin interpolar. Los resultados por estado, antecedentes cero y municipios con mayor error identifican límites operativos.

## Calidad y restricciones

Se aprobaron 37 controles de integridad, temporalidad y reproducción. Las fuentes originales y los módulos heredados conservan sus hashes. El predictor no consulta el objetivo al inferir, no cambia de estado durante predicción y reproduce exactamente los resultados al guardar/restaurar.

2023 y 2025 ya fueron evaluados en fases previas. Aunque sus etiquetas se excluyen del ajuste y de la elección de A5, no constituyen una prueba global nueva e independiente. Los hiperparámetros individuales también se heredaron de un proceso anterior. La evaluación es retrospectiva con fuentes revisadas y sin reconstrucción completa de fechas de publicación.

La historia estatal 1980–2002 permanece separada; agricultura 2024 y clima nominal 2013 permanecen aislados. Las variables climáticas son estatales y las macroeconómicas anuales, sin miles de observaciones independientes por la repetición en municipios. Los datos no miden ventas, rutas ni emisiones. La función de costos y la aceptación prospectiva requieren validación con el sponsor.

## Artefactos y reproducción

`modelo_final.joblib` requiere `src/ensambles_avance5.py`, los módulos heredados y las versiones de `requirements_avance5.txt`. Las matrices `X_*.npz` contienen entradas **antes de preparación**, con nombres y posibles NaN; siguen el orden de `claves_objetivo_*.csv`. Las claves `cvegeo` y `estado` deben leerse como texto. La inferencia exige conservar los nombres y las unidades de entrada.

La libreta tiene 15 celdas de código ejecutadas y 12 figuras incrustadas. El código, los datos, las predicciones, los parámetros y los diarios permiten repetir el análisis sin red después de instalar dependencias. Las referencias completas y la declaración obligatoria de IA están en la libreta. El modelo se entrega como resultado de investigación reproducible para la siguiente fase; su disponibilidad no acredita despliegue operativo.
