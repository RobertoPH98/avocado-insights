# Ficha técnica del baseline · Avocado Insights

**Equipo 4 · TC5035.10 · 18 de octubre de 2026**

## Propósito y contrato

Estimar producción anual municipal de aguacate, en toneladas, como referencia del componente de oferta territorial. El modelo utiliza mediciones t−2 o anteriores. Cada entrenamiento emplea etiquetas hasta t−3; no se imputan objetivos.

La cohorte contiene municipios con una observación de producción dos años antes. Un cero reportado es una observación válida. Los municipios sin historia t−2 requieren otro mecanismo y no se les asigna producción cero artificialmente.

## Modelo elegido y preparación

- Familia: **Ridge nivel**, regresión Ridge.
- Parámetros: `alpha=1`, ajuste por SVD, sin intercepto.
- Entrada: `produccion_lag2`.
- Escalamiento: desviación estándar de entrenamiento, sin centrar; se conserva el origen cero.
- Regla restaurada en unidades originales: **ŷ = 1.048680322 × producción municipal t−2**, con límite inferior cero.
- La magnitud 1.048680322 es un multiplicador aprendido para este horizonte y conjunto; no una tasa anual ni una elasticidad causal.

Se compararon cuatro variantes de Ridge, una referencia de mediana global y persistencia. La elección se hizo por MAE en validación de origen móvil 2018–2020. Todos los parámetros de preparación se ajustaron por ventana. El registro de selección se guardó antes de puntuar 2023.

## Resultados

| Indicador | Entrenamiento final / prueba |
|---|---|
| Entrenamiento final | 6,707 municipio-año, 2007–2020 |
| Prueba interna | 637 municipios, 2023 |
| MAE de prueba | 743.8233 t por municipio |
| RMSE de prueba | 6,081.8800 t |
| WAPE de prueba | 15.9447% |
| Sesgo de volumen agregado | -13.7890% |
| R² | 0.943833 |
| RMSLE | 0.762396 |
| Mejora MAE frente a persistencia | +12.7273% |
| Mínimo técnico frente a persistencia y mediana | Cumple |
| Meta adicional propuesta del 5% | Cumple |

El mínimo técnico y la meta adicional son criterios provisionales, pendientes de validación del sponsor. No se facilitó un historial de errores de un sistema empresarial vigente. La referencia histórica utiliza la producción t−2 realmente observada.

## Relevancia y generalización

La selección reducida ganó por MAE global. La ablación con reajuste cuantifica aportes de escala, productividad, dinámica, macroeconomía y clima en la variante ampliada. La información climática tuvo un aporte condicional; la combinación completa de externos no superó al baseline reducido en la métrica principal. Esto no prueba que los factores externos carezcan de efecto.

La prueba tiene mayor error absoluto que el entrenamiento y mantiene subestimación sistemática. La curva histórica mejora al ampliar datos. El patrón no respalda una explicación simple de memorización por exceso de parámetros; sí evidencia límites de especificación y generalización temporal. Los residuos por municipio y estado identifican casos que requieren mayor atención.

El intervalo de sensibilidad espacial por estados es [-6.89%, +13.88%] de mejora del MAE. Cruza cero: la ventaja puntual de 2023 no demuestra superioridad robusta para toda composición estatal. Los 1,500 remuestreos emparejados no representan incertidumbre de años futuros.

## Fuentes y calidad

1. Agricultura: instantánea SIAP/DGSIAP obtenida de la copia secundaria documentada en `data/proveniencia.json`, con hash SHA-256 fijo. La historia estatal 1980–2002 se separa y el año agrícola 2024 permanece en cuarentena.
2. Banco Mundial: inflación USA (`FP.CPI.TOTL.ZG`) y tipo de cambio MEX (`PA.NUS.FCRF`), 2000–2023, respuestas originales y hashes preservados.
3. SMN/CONAGUA: tablas de temperatura estatal, 2003–2023. Se conservan 21 PDFs. Se integran 20 años: el archivo nominal 2013 muestra 2012 en su encabezado y no se reasigna.

La temperatura es estatal, no de parcela. Los datos macro tienen variación anual compartida; no se tratan como miles de observaciones independientes. Las ausencias climáticas derivadas de la cuarentena se imputan únicamente dentro del entrenamiento de las variantes que las utilizan, con indicadores.

## Restricciones de uso

- Evaluación retrospectiva con instantáneas revisadas; no se dispone del archivo completo de fechas de publicación.
- Reserva 2023 previamente explorada de forma descriptiva en el EDA, sin ajuste con sus etiquetas en esta fase.
- Producción de municipios con historia; limitaciones ante aparición de oferta después de un cero y ante cambios de clave territorial.
- Aranceles y criminalidad aún requieren cobertura y armonización; no se fabricaron series.
- Las cifras no son pronósticos de ventas, rutas óptimas, ahorro logístico ni emisiones.
- Aceptación operativa y costos de error pendientes de validación por el sponsor.

## Reproducibilidad

La libreta contiene 14 celdas de código ejecutadas en orden y 8 figuras incrustadas; se aprobaron 21 controles. La ejecución se hizo en un proceso Python nuevo mediante IPython, con captura de salidas, espacio de nombres limpio y sin servidor de kernel. Las versiones exactas, el protocolo, las fuentes y el objeto serializado acompañan el análisis.

Las matrices `X_*.npz` incluyen sus nombres de columnas y mantienen el mismo orden que `claves_objetivo_*.csv`. Al leer las claves, `cvegeo` y `estado` deben conservarse como texto. El objeto guardado requiere que `src/baseline_avance3.py` esté disponible para importar.
