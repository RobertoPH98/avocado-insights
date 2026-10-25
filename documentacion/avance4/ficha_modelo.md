# Ficha técnica · Modelo individual del Avance 4

**Avocado Insights · Equipo 4 · TC5035.10 · 24 de octubre de 2026**

## Propósito y población

Predecir producción anual municipal de aguacate en toneladas para el componente de oferta territorial. Se evalúan municipios con objetivo observado e historia de producción t−2. Un cero reportado permanece; un municipio sin esa historia no recibe una etiqueta cero artificial. No se estiman ventas, rutas o emisiones.

## Modelo y preparación

- **Algoritmo:** HuberRegressor, un único regresor lineal robusto.
- **Parámetros elegidos:** epsilon=1.01; alpha=1.26499899704e-06; conjunto completo.
- **Parámetros numéricos:** max_iter=6,000 y tol=10⁻⁶; aumento de presupuesto solo ante advertencia numérica, sin consultar validación.
- **Entradas:** 17 variables originales; historia de escala, capacidad, productividad, crecimiento, dispersión, macroeconomía, clima e interacciones, más logaritmos de magnitudes históricas.
- **Preparación de X:** mediana por columna, indicadores de ausencia, filtro de constantes y StandardScaler, aprendidos en cada entrenamiento.
- **Preparación de y:** StandardScaler lineal dentro de entrenamiento, invertido antes de predecir toneladas. No se usa logaritmo del objetivo.
- **Salida:** predicción en toneladas, limitada inferiormente a cero; las negativas previas al límite se contabilizan.
- **Ajuste final:** 7,963 municipio-año de 2007–2022; 24 columnas efectivas; convergente, sin reintento, 908 iteraciones.

Los coeficientes restaurados en unidades originales y el intercepto figuran en `data/avance4/ficha_modelo_avance4.json` y `resultados/avance4/24_coeficientes_modelo_individual.csv`. Sus signos son condicionales a las demás entradas; no son efectos causales ni una clasificación de importancia independiente de la colinealidad.

La escala robusta aprendida fue 0.749 t y 97.16% de las filas quedó en la región lineal de la pérdida. Con epsilon próximo a 1, el ajuste se aproxima al comportamiento de error absoluto. La bandera interna `outliers_` señala una región de pérdida; no identifica errores de fuente y no se usó para eliminar observaciones.

## Experimentos y decisión

Se compararon siete algoritmos individuales —ElasticNet, Huber, cuantílica, CART, KNN, SVR y MLP— sobre las mismas 17 entradas iniciales. Ridge A3 y persistencia se conservaron como referencias. Cada origen usa mediciones hasta t−2 y etiquetas de entrenamiento hasta t−3.

1. Ranking 2015–2017: selección de cuantílica y Huber por MAE concatenado.
2. Ajuste 2018–2020: 48 configuraciones por familia; 96 candidatos y 288 ajustes por ventana, todos convergentes. Se exploraron regularización, epsilon cuando aplica y cuatro conjuntos de variables.
3. Confirmación 2021–2022: comparación de versiones iniciales, ajustadas y referencias, con decisión restringida a los dos finalistas ajustados.
4. Prueba interna 2025: evaluación del único modelo elegido, sin reabrir la selección.

La mejora MAE en búsqueda fue 5.63% para cuantílica y 0.31% para Huber. Huber ajustado obtuvo 283.3891 t frente a 283.4502 t de cuantílica en confirmación. La tolerancia de 1% permitió considerar familia y número de entradas; ambos finalistas eran lineales con 17 entradas, por lo que resolvió el menor MAE. Huber tuvo menor tiempo medido de ajuste; cuantílica tuvo menor RMSE (1108.65 frente a 1112.37 t). El tiempo no intervino en el desempate determinista.

Ridge A3 logró 279.2133 t en confirmación y superó a los dos ajustados. Además, Huber inicial tuvo menor MAE que Huber ajustado en esa fase. La mejora del ajuste no se sostuvo en todo periodo. El modelo final es el mejor entre los dos ajustados según el protocolo, sin atribuirle superioridad general sobre toda referencia.

El epsilon ganador está en el límite inferior del refinamiento (1.01). Se conserva el resultado como mejor configuración explorada; no se afirma óptimo global ni se amplía la búsqueda después de ver la prueba.

## Desempeño final

| Indicador · 647 municipios, año 2025 | Huber | Ridge A3 reajustado |
|---|---:|---:|
| MAE · t | 579.4988 | 755.3440 |
| RMSE · t | 4678.1986 | 6478.3275 |
| WAPE | 13.4405% | 17.5190% |
| R² | 0.952774 | 0.909437 |
| RMSLE | 0.870316 | 0.609365 |
| Sesgo de volumen | +6.7171% | +11.5046% |

La reducción puntual de MAE es 23.2801%. La ventaja en toneladas convive con mayor RMSLE y sobreestimación agregada. Los gráficos de residuos, cuartiles, estados y antecedentes de cero permiten localizar límites. El mayor error de prueba que de entrenamiento no demuestra por sí solo sobreajuste; cambian el periodo y la distribución.

La sensibilidad espacial mediante 1,500 remuestreos emparejados de estados produjo percentiles de mejora [-13.08%, +28.97%]. El rango cruza cero; no representa incertidumbre de años futuros ni garantiza superioridad en todo territorio.

## Fuentes y límites

Se preservó el commit base `71c97b1d245c0304df1f28a4a62be6c69143f243` y el hash agrícola `f195190c043409188741ea4a6a2bbb44343aaeaa1f2e02dc17b6bd5f394f9dd3`. El archivo original contiene 15,474 registros. Historia estatal 1980–2002 y agricultura 2024 permanecen separadas. El PDF climático nominal 2013 muestra 2012 y no se integra. Las fuentes macroeconómicas del Banco Mundial y las tablas estatales del SMN/CONAGUA conservan la instantánea del Avance 3 y sus hashes.

2023 ya fue evaluado en el Avance 3. 2025 había sido explorado descriptivamente: esta es una reserva de modelado interna, no una prueba completamente desconocida. Las fuentes son instantáneas revisadas y no existe una reconstrucción integral de publicaciones históricas. Los efectos climáticos son estatales y los macroeconómicos anuales; no equivalen a observaciones locales independientes.

## Artefactos y reproducción

La libreta contiene 15 celdas de código ejecutadas secuencialmente, 8 figuras y la declaración de IA en la última celda Markdown. Se aprobaron 33 controles. Datos, módulos, protocolo, configuraciones, registros por ventana, predicciones, matrices y objeto serializado acompañan el análisis. Las referencias bibliográficas completas están en la libreta.

El objeto `modelo_individual_final.joblib` requiere los módulos de `src/` y el entorno documentado en `requirements_avance4.txt`. Su restauración reproduce exactamente las predicciones guardadas. Las matrices incluyen los nombres de columnas y siguen el orden de `claves_objetivo_*.csv`; `cvegeo` y `estado` deben leerse como texto. La operación real y los costos de error quedan pendientes de validación con el sponsor.
