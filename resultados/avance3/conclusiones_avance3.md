**Algoritmo y viabilidad.** Se seleccionó **Ridge nivel** por MAE temporal de **539.95 t** en
2018–2020. La elección se congeló antes de la prueba interna. El modelo final se ajustó con
6,707 observaciones de 2007–2020 y se evaluó en 637 municipios de 2023.
Una relación simple y regularizada ofrece un punto de comparación interpretable sin exigir un
modelo independiente con muy pocos años por municipio.

**Características importantes.** La variante seleccionada utiliza 1 entrada(s):
produccion_lag2. La selección de representaciones y la ablación respaldan la
importancia de escala/capacidad y cuantifican qué grupos aportan información en las variantes
multivariadas. Quitar clima del modelo externo cambia su MAE en +12.49 t; quitar
macroeconomía lo cambia en -8.56 t. Es evidencia condicional, no prueba de causalidad.
El trabajo de ingeniería previo sigue disponible aunque el baseline elegido sea más pequeño.

**Sub/sobreajuste.** El MAE es 555.60 t en ajuste y
743.82 t en prueba; el RMSE es 3,117.64 t y
6,081.88 t, respectivamente. La prueba tiene mayor MAE que el ajuste: existe una brecha de generalización, compatible con cambio temporal y/o limitaciones de ajuste; el diseño no permite atribuirla solamente a sobreajuste. La curva histórica y los residuos
complementan la comparación: al ampliar la historia, el MAE de validación fija 2020 baja
7.80%. No aparece deterioro histórico al aumentar datos; junto con un único coeficiente
en la variante de nivel, esto no respalda una explicación de memorización por exceso de complejidad.
La brecha de 2023 y el sesgo negativo sí señalan generalización temporal insuficiente para
considerar resuelto el problema. Una referencia proporcional tiene limitaciones estructurales ante
municipios que pasan de cero a producción, cambios agronómicos y shocks no observados; no se
concluye subajuste solo por usar un modelo sencillo.

**Métrica y mínimo.** Se prioriza MAE en toneladas por el contexto de oferta y capacidad territorial.
En prueba, el WAPE es 15.94% y el sesgo agregado es
-13.79%. El MAE de persistencia es 852.30 t;
el baseline lo cambia en +12.73% de mejora relativa. El criterio mínimo técnico
**se cumple** y la meta adicional del 5%
**se alcanza**. Estos umbrales son propuestas técnicas,
pendientes de validación económica por el sponsor. El intervalo descriptivo por estados es
[-6.89%, +13.88%]. La sensibilidad por estados incluye cero; la mejora puntual no acredita superioridad robusta para toda composición territorial ni para años futuros.

**Respuesta a fuentes externas y calidad.** Se integraron inflación estadounidense, tipo de cambio
y temperatura estatal con mediciones t−2 o anteriores. Las fuentes y sus versiones quedan
preservadas; el conflicto de año del PDF climático 2013 se aisló. No se inventaron aranceles ni
registros de criminalidad. El conjunto no permite concluir que esos factores carecen de efecto:
faltan observaciones temporales independientes, datos locales y una disponibilidad histórica
verificada. Se aprobaron 21 controles de integridad y reproducción.

**Continuidad en CRISP-ML(Q).** Queda una referencia congelada para Avance 4: todo candidato
deberá compararse con persistencia y este baseline sobre el mismo horizonte y cobertura, con
preparación dentro de cada ventana. Deben revisarse residuos por región y tamaño, función de
costos, fechas reales de publicación y opciones para municipios sin historia. La mejora futura
requiere comprobar información climática/local, agua y calendario económico antes de incrementar
complejidad. Los resultados actuales sustentan una evaluación retrospectiva; no acreditan un
pronóstico prospectivo ni una solución logística desplegada.