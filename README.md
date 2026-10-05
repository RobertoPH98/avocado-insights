# Avocado Insights · Equipo 4

Proyecto integrador TC5035.10, Tecnológico de Monterrey.

## Entrega actual

**[Avance 1. Análisis exploratorio de datos](notebooks/Avance1.Equipo4.ipynb)**

Diagnóstico de producción municipal de aguacate como base para planeación logística sustentable. La libreta documenta el cambio de enfoque descrito por el equipo y cubre los cinco criterios de la rúbrica con resultados calculados. Incluye 16 celdas de código ejecutadas secuencialmente, 12 figuras compuestas y tablas exportadas.

### Integrantes

- José Roberto Sánchez Rocha — A00903762
- Josué Águila Ramos — A01796400
- Roberto Perézcano Hernández — A01730502

Profesor del curso: Raúl Valente Ramírez Velarde. Sponsor: Dr. Jorge Antonio Ascencio Gutiérrez.

## Datos y alcance

Fuente original DGSIAP/SADER; bytes obtenidos de una copia pública de Montse, repositorio `lapanquecita/aguacate`, commit fijado en `data/proveniencia.json`. Se incluye atribución y licencia del distribuidor. La descarga directa del portal oficial falló; se verificaron cinco agregados de 2023 contra SEDARH, no todos los registros. No se presentan datos sintéticos como reales.

La copia contiene 15,474 registros (1980–2025). Se separan años previos a 2003 por no tener municipio y 2024 por claves administrativas ambiguas. El panel principal contiene 11,665 municipio–año de 2003–2023 y 2025. Los datos no incluyen rutas, acopios, consumo de combustible ni emisiones; estas limitaciones están explícitas.

## Estructura

- `notebooks/Avance1.Equipo4.ipynb`: entregable principal ejecutado con resultados.
- `data/raw/`: copia intacta de los datos y licencia del distribuidor.
- `data/proveniencia.json`: procedencia, versión, fecha y hash SHA-256.
- `data/processed/`: panel limpio, cuarentena 2024, rezagos y perfiles.
- `resultados/`: tablas completas, 12 figuras, conclusiones y resumen de comprobaciones.
- `documentacion/`: entregas previas, guía y versión HTML de lectura.
- `requirements.txt`: dependencias.

## Reproducir localmente

1. Descargar el repositorio/paquete y extraerlo conservando carpetas.
2. Desde la carpeta raíz, con Python 3.12:

```bash
python -m pip install -r requirements.txt
python -m jupyterlab
```

3. Abrir `notebooks/Avance1.Equipo4.ipynb`.
4. Usar **Kernel > Restart Kernel and Run All Cells** y guardar. La primera celda también acepta trabajar desde la raíz del paquete.

El EDA no requiere red ni credenciales; todas sus entradas están incluidas. La instalación inicial de dependencias sí requiere internet. La libreta verifica el hash y evita cargar una versión diferente sin advertirlo. Para cambiar la fuente se debe revisar y actualizar la procedencia y las comprobaciones, no saltarse la auditoría.

## Ejecución verificada en la preparación

Las 16 celdas se ejecutaron en orden en un proceso Python nuevo mediante IPython, con espacio de nombres limpio y captura de tablas/figuras. El entorno de preparación impidió abrir sockets de un kernel Jupyter, por lo que se utilizó ejecución IPython en proceso, sin modificar los cálculos. Se validó formato nbformat, ausencia de errores, 12 imágenes incrustadas, conservación de volumen y reglas de calendario. El notebook es compatible con un kernel Python 3 de Jupyter.

## Resultados principales

En 2025: 655 municipios registrados, 644 con producción positiva y 2,792,481.05 toneladas. Michoacán concentra 72.68%; 34 municipios reúnen al menos 80%. Son cifras de la copia histórica documentada, no mediciones de oferta diaria disponible ni resultados de optimización de rutas.

## Próximo avance

Aclarar 2024 con la fuente oficial e integrar rutas, centros de acopio, demanda, capacidades y consumo medido. El EDA no entrena ni evalúa modelos predictivos y no reporta ahorros no medidos.

## Entrega en Canvas

Entregar el enlace **directo al notebook en GitHub**, no solo la raíz del repositorio ni el ZIP. Instrucciones en `documentacion/COMO_SUBIR_Y_ENTREGAR.md`.
