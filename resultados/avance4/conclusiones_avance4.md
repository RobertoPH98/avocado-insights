**Comparativa.** Se construyeron **7 algoritmos distintos, individuales y no ensambles**,
evaluados con las mismas entradas iniciales y cortes. La tabla se ordenó por MAE e incluyó RMSE,
WAPE, R², RMSLE, sesgo y tiempos de entrenamiento/predicción. Las referencias Ridge A3 y
persistencia aportan el contexto histórico sin contarse como alternativas adicionales.

**Ajuste fino.** El ranking 2015–2017 seleccionó **Cuantil, Huber**. Se exploraron
96 configuraciones distintas y se registraron
288 ajustes por ventana, con exploración y refinamiento.
Las mejoras de MAE frente a la configuración inicial sobre 2018–2020 fueron: Cuantil: +5.63%; Huber: +0.31%.
Son resultados de selección y se contrastaron posteriormente; la búsqueda no prueba un óptimo global.

**Elección individual.** Se eligió **Huber**, configuración `{"alpha":1.2649989970392911e-06,"epsilon":1.01,"features":"completo"}`,
con MAE de confirmación **283.39 t**. La regla consideró tolerancia de 1%,
interpretabilidad de familia y cantidad de entradas antes del desempate por MAE. El estimador final
es **HuberRegressor**, con 17 entradas originales y
24 columnas efectivas. Los costos medidos y las limitaciones de explicación
se documentaron junto con las métricas. No se combinaron sus predicciones con otro modelo.
Ridge A3 obtuvo 279.21 t en confirmación y superó a los dos finalistas ajustados;
la elección de esta fase corresponde al mejor entre esos dos. El Huber inicial también tuvo menor
MAE de confirmación que el ajustado. Cuantílica ajustada logró menor RMSE que Huber ajustado;
Huber tuvo menor MAE y menor tiempo de ajuste medido. No se asume una ventaja concluyente ante
diferencias pequeñas. El epsilon ganador está en la frontera inferior del espacio refinado.

**Prueba interna.** El ajuste final usa 7,963 municipio-año de 2007–2022 y la
prueba contiene 647 municipios de 2025. El MAE final es **579.50 t**,
frente a **755.34 t** del baseline reajustado; mejora relativa **+23.28%**.
El WAPE es 13.44%, el RMSE 4,678.20 t y el sesgo agregado
+6.72%. La referencia Ridge puntual **se alcanza o supera**.
El resultado se conserva sin modificar la elección. El rango de sensibilidad estatal de mejora es
[-13.08%, +28.97%]. El rango estatal cruza cero; la ventaja puntual no es robusta a toda composición territorial.
El RMSLE de 0.870 es mayor que el de Ridge
(0.609):
la ventaja en toneladas convive con peores errores en escala logarítmica, relevante para municipios
pequeños y con producción cero. La métrica principal sigue siendo el error de oferta en toneladas.

**Generalización y límites.** El MAE de prueba cambia +29.83% respecto del ajuste final.
La comparación temporal, residuos y segmentos aportan evidencia; una diferencia entre periodos
no permite atribuir por sí sola el resultado a sobreajuste o a una causa externa. Hay concentración
de volumen, cambios de distribución y casos con historia cero. La temperatura es estatal,
los factores macro varían por año y la disponibilidad histórica de publicación no está reconstruida.
2025 es una reserva de modelado interna ya explorada descriptivamente, no una prueba prospectiva.

**Continuidad.** Se entrega un único modelo reproducible para la siguiente etapa, con parámetros,
fuentes, matrices, predicciones y 33 controles aprobados. Antes de uso operativo deben
validarse costos de error, horizonte, cobertura de municipios sin historia y disponibilidad real
de datos. La declaración final identifica el apoyo real de IA y no sustituye la revisión académica
que corresponde al equipo.