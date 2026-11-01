**Ensambles.** Se construyeron siete modelos: cuatro homogéneos y tres heterogéneos. Voting,
stacking y blending usaron Huber y cuantílica ajustados del Avance 4. La auditoría de los
metamodelos comprueba etiquetas internas hasta s−3; las filas de calibración no entrenan sus bases.
Los siete algoritmos individuales anteriores y dos referencias también se evaluaron sobre iguales cohortes.

**Optimización.** Se ajustaron Bagging Huber, Voting H-Q, HistGradientBoosting mediante 72 configuraciones distintas y
216 evaluaciones por ventana. Las mejoras sobre la configuración inicial, usando los mismos
orígenes 2018–2020, fueron Bagging Huber: +0.94%; Voting H-Q: +0.03%; HistGradientBoosting: +2.89%. La búsqueda conserva convergencia, parámetros y tiempos.
La confirmación posterior y la reserva de predicción de esta fase permanecieron fuera de la búsqueda.

**Selección.** El mejor ensamble de confirmación fue Voting H-Q, con MAE
283.39 t; el mejor individual de A4 fue Huber, con
283.39 t. La mejora relativa del ensamble sobre ese individual fue
-0.00%. La regla de negocio provisional eligió **Ridge A3**, con MAE
279.21 t, costo total medido de 0.01 s
en los dos orígenes y complejidad registrada 1. Se prefirió simplicidad cuando
la diferencia quedó dentro de 1%; se permitió conservar una referencia individual si la evidencia
no justificaba sustituirla. La tolerancia requiere validación económica del sponsor.

**Evaluación.** El predictor final se reajustó con 7,963 observaciones de 2007–2022
y se evaluó en 647 municipios de 2025. MAE **755.34 t**, RMSE
6,478.33 t, WAPE 17.52%, R² 0.9094,
RMSLE 0.6094 y sesgo +11.50%. La mejora de MAE frente
a Huber A4 es -30.34%. La sensibilidad espacial es [-40.79%, +11.57%].
El MAE de prueba cambia +47.47% respecto de entrenamiento; esa diferencia entre periodos
no prueba por sí sola sobreajuste. No se cambió la elección al observar los resultados finales.

**Interpretación y límites.** Cuatro gráficos principales separan magnitud, dirección,
calibración y tamaños; tendencia sobre cohorte fija, estados y sensibilidad complementan la lectura.
Los residuos Huber–Cuantil tuvieron correlación 1.0000; combinar predictores muy similares
limita diversidad. Los errores grandes y los ceros requieren revisión local. El crecimiento
temporal de una cohorte no equivale al nacional ni a una relación causal. Las pruebas 2023/2025
ya se habían examinado en fases previas: no hay una evaluación global ciega nueva ni validación prospectiva.

**Producto de la fase.** Se conserva un predictor final con datos originales, fuentes,
parámetros, predicciones, matrices y 37 controles aprobados. La siguiente etapa debe
comunicar tanto el valor como la incertidumbre territorial, validar disponibilidad de datos
y costos de error, y obtener una evaluación futura independiente antes de adopción operativa.