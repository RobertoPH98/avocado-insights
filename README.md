# Avocado Insights · Equipo 4

Proyecto integrador TC5035.10, Tecnológico de Monterrey.

**[Avance 3. Baseline — libreta ejecutada](notebooks/Avance3.Equipo4.ipynb)**

Referencia predictiva de producción anual municipal de aguacate para el componente de oferta territorial del proyecto. El baseline permite comparar precisión y complejidad antes de desarrollar modelos más avanzados.

## Desarrollo del proyecto

| Fase | Material |
|---|---|
| Análisis exploratorio | [Avance 1](notebooks/Avance1.Equipo4.ipynb) |
| Ingeniería de características | [Avance 2](notebooks/Avance2.Equipo4.ipynb) |
| Modelo de referencia | [Avance 3](notebooks/Avance3.Equipo4.ipynb) |

Los avances anteriores permanecen como antecedentes del proyecto; este paquete incorpora los archivos necesarios para reproducir el Avance 3 de manera independiente.

## Baseline actual

Se compararon mediana global, persistencia y cuatro variantes de regresión Ridge mediante validación de origen móvil en 2018–2020. La variante elegida fue **Ridge nivel**, con producción municipal t−2 como entrada y un multiplicador global aprendido. Después de congelar esa elección, se reajustó con 6,707 observaciones de 2007–2020 y se evaluó en 637 municipios de 2023.

| Indicador en prueba interna 2023 | Baseline | Persistencia t−2 |
|---|---:|---:|
| MAE · toneladas por municipio | 743.82 | 852.30 |
| RMSE · toneladas | 6,081.88 | 6,863.64 |
| WAPE | 15.94% | 18.27% |

La mejora puntual del MAE es **12.73%**. El modelo subestima 13.79% del volumen agregado de la cohorte y la sensibilidad del resultado cambia según la composición estatal: el rango central del remuestreo por estados cruza cero. La prueba interna no demuestra operación prospectiva ni sustituye una función de costos validada por el sponsor.

## Datos y alcance

La fuente agrícola es atribuida a DGSIAP/SADER. Los bytes provienen de la copia pública de Montse (`lapanquecita/aguacate`), fijada y documentada en `data/proveniencia.json`. La validación oficial del Avance 1 fue parcial; no se afirma certificación de todos los registros. Se conservan 15,474 registros originales, se separa la historia estatal de 1980–2002 y se mantiene 2024 en cuarentena por claves administrativas ambiguas.

El Avance 3 integra además dos series oficiales del Banco Mundial —inflación de Estados Unidos y tipo de cambio de México— y tablas de temperatura estatal del SMN/CONAGUA. Se preservan respuestas originales, 21 PDFs climáticos, URLs y hashes. El PDF nominal de 2013 tiene encabezado 2012 y se conserva sin usar sus valores en la unión temporal. La comparación externa muestra aportes condicionales, sin justificar por sí sola un baseline más complejo.

La variable objetivo es producción anual en toneladas. Estos datos no miden ventas, exportaciones, rutas, combustible ni emisiones. Las fuentes son instantáneas revisadas sin un archivo completo de fechas de publicación; el escenario usa mediciones t−2 o anteriores y etiquetas de entrenamiento hasta t−3 para cada origen.

## Estructura

- `notebooks/Avance3.Equipo4.ipynb`: análisis principal, 14 celdas de código ejecutadas, 8 figuras y conclusiones.
- `src/baseline_avance3.py`: integración externa, regresión, validación y pruebas de relevancia.
- `src/fe_avance2.py`: reconstrucción del panel y atributos históricos, idéntica al avance anterior.
- `data/raw/`: fuente agrícola original y licencia del distribuidor.
- `data/externos/`: respuestas JSON, tablas climáticas, PDFs originales en ZIP y procedencia.
- `data/avance3/`: panel integrado, modelo serializado, matrices y ficha del modelo.
- `resultados/avance3/`: métricas, predicciones, análisis por segmentos y figuras.
- `documentacion/avance3/`: protocolo de evaluación, elección congelada y versión de lectura.
- `scripts/ejecutar_avance3.py`: ejecución secuencial reproducible.

## Reproducción analítica

Entorno verificado: Python 3.12.14. Dependencias en `requirements_avance3.txt`.

```bash
python -m pip install -r requirements_avance3.txt
python scripts/ejecutar_avance3.py
```

También se puede abrir el notebook con Jupyter y ejecutar todas las celdas desde un kernel limpio. El análisis utiliza las entradas incluidas y funciona sin red después de instalar las dependencias. La ejecución entregada se verificó en un proceso nuevo mediante IPython, con captura de salidas y figuras. Se aprobaron 21 controles de calidad y restauración del modelo.

La versión autosuficiente de lectura se encuentra en [Avance3.Equipo4_lectura.html](documentacion/avance3/Avance3.Equipo4_lectura.html). La ficha técnica está en [ficha_modelo.md](documentacion/avance3/ficha_modelo.md).

## Integrantes

- José Roberto Sánchez Rocha — A00903762
- Josué Águila Ramos — A01796400
- Roberto Perézcano Hernández — A01730502

Profesor: Dr. Raúl Valente Ramírez Velarde. Sponsor: Dr. Jorge Antonio Ascencio Gutiérrez.

## Continuidad

El siguiente modelado deberá conservar comparaciones de horizonte y cobertura equivalentes, revisar disponibilidad histórica y errores territoriales, integrar factores locales con trazabilidad y resolver las fuentes en cuarentena. Los criterios de aceptación de negocio y la evaluación prospectiva quedan pendientes.
