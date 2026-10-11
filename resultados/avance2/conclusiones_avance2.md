**1. Unidad y calidad de los datos.** Se conserva la fuente de 15,474 registros. Los
981 registros estatales de 1980–2002 se separan y preservan: sus municipios
ausentes no se imputan. Se resguardan las 900 filas de 2024 en cuarentena.
Los registros elegibles originan 11,665 observaciones municipio-año con claves únicas.

**2. Construcción útil para el negocio.** Los 22 atributos numéricos, el indicador de
ausencia de cosecha, el estado, el perfil de riego y los tramos de producción describen escala,
capacidad y estabilidad de la oferta. Su medición más reciente es t−2. No se confunden con rutas,
exportaciones, emisiones o variables ambientales no observadas. El diccionario y las claves
permiten incorporarlos después a una red logística validada.

**3. Transformación y normalización.** La asimetría absoluta de producción t−2 pasa de
8.418 a 0.001 con
yeo-johnson. La reducción se verifica sobre entrenamiento; no prueba normalidad ni
mejor pronóstico. Las medias, escalas, medianas, cuantiles, categorías y parámetros se congelan
antes de transformar periodos posteriores. No se recortan extremos agrícolas legítimos.

**4. Selección y extracción.** La matriz inicial de 74 columnas queda en 51
al retirar 10 constantes, 3 atributos
numéricos redundantes y 10 indicadores idénticos. PCA comprime
18 atributos numéricos a 10 componentes y conserva
97.06% de su varianza. Sumando los indicadores
externos a PCA, la alternativa contiene 43 columnas; reduce 41.9%
los elementos de la matriz densa respecto de la versión completa. Esto reduce almacenamiento
numérico y dimensión, pero no asegura menor tiempo en toda implementación.

**5. Generalización y límites.** Se obtienen 3,930 filas de entrenamiento,
1,734 de validación, 637 de reserva interna y 647 de
aplicación retrospectiva. Las exclusiones por falta de historia se documentan por cohorte.
El menor MAE de la prueba instrumental corresponde a Persistencia t-2; el menor RMSLE, a
Ridge completo. Se conservan ambas representaciones; PCA no se adopta como mejora predictiva
automática. Para planear toneladas de capacidad logística debe priorizarse el costo de errores
en volumen, además de revisar el desempeño relativo y la cobertura territorial.

**6. Aceptación y siguiente fase.** Se aprueban 18 controles automatizados de fuente,
claves, fechas, particiones, ausencia de fuga por medición, matrices y serialización. Se exporta
la preparación reproducible y se habilita el Avance 3 para comparar persistencia, modelos
temporales y regresión con validación de origen móvil. Antes de uso operativo deben confirmarse
fechas de publicación, cambios en claves municipales, unidades y revisiones del proveedor;
resolver 2024; definir el manejo de municipios sin historia; y evaluar sesgos por estado,
tamaño productivo y disponibilidad de datos. Los precios nominales requieren deflactación si
se pretende interpretar evolución económica real. La falta de clima, agua y logística limita
la explicación causal y los alcances del sistema.