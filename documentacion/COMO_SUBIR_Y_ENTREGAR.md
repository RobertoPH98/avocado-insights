# Cómo subir y entregar · Equipo 4

## Primero: tu captura muestra un bloqueo de permisos

El mensaje observado es **Uploads are disabled. File uploads require push access to this repository.** No es un problema del archivo. La cuenta abierta no puede publicar cambios en ese repositorio.

La opción más rápida es que Roberto, propietario de `RobertoPH98/avocado-insights`, descargue el ZIP y siga el paso 2 desde su cuenta. También puede invitar tu usuario de GitHub como colaborador con permiso de escritura; debes aceptar la invitación antes de volver a la página de carga. No basta con poder ver el repositorio.

## 1. Descargar y extraer

Descarga `Entrega_Avance1_Equipo4.zip`. En Windows: clic derecho → **Extraer todo**. Abre la carpeta `avocado-insights-entrega` hasta ver `README.md`, `requirements.txt`, `data`, `notebooks`, `documentacion` y `resultados`.

## 2. Subir a GitHub

1. Inicia sesión en la cuenta que tenga permiso de escritura en https://github.com/RobertoPH98/avocado-insights .
2. Desde la raíz del repositorio, confirma la rama `main` y pulsa **Add file → Upload files**.
3. Arrastra **el contenido** de `avocado-insights-entrega`: los archivos y las carpetas de su interior. No arrastres el ZIP ni agregues una carpeta exterior extra.
4. Espera a que termine la carga. Revisa que aparezca `notebooks/Avance1.Equipo4.ipynb`, además de `data/raw/siap_produccion.csv` y `data/proveniencia.json`.
5. Como mensaje de commit escribe: `Completa Avance 1: EDA ejecutado, datos y conclusiones`.
6. Pulsa **Commit changes**. Si GitHub ofrece crear una rama/PR en lugar de escribir en `main`, el propietario deberá revisar e integrar el cambio antes de usar la URL de `main`.
7. Abre `notebooks` → `Avance1.Equipo4.ipynb`. Comprueba que aparecen tablas, gráficas y conclusiones. Si GitHub tarda en renderizar, recarga y espera; los resultados ya están guardados.

Si no puedes subir: confirma con Roberto que tu cuenta sea colaboradora o pásale el paquete para que lo suba. No se requieren contraseñas ni tokens en los archivos.

Documentación oficial de carga: https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository?platform=windows

El paquete tiene menos de 100 archivos y cada uno está por debajo de 25 MiB, compatibles con carga web. El README actual del paquete sustituye el README mínimo del repositorio con la documentación del avance. Conserva archivos adicionales que ya existan y no estén relacionados con esta entrega.

## 3. Verificación antes de entregar

- El enlace abre la libreta exacta, no una página de subida ni el listado de carpetas.
- Se ven los integrantes, alcance y los cinco criterios de la rúbrica.
- Hay 12 figuras compuestas y conclusiones con cifras.
- La libreta tiene 16 celdas de código con ejecuciones 1–16 y sin salidas de error.
- El profesor puede acceder al repositorio. Si es privado, requiere acceso autorizado.
- Conserva el ZIP como respaldo.

## 4. Entregar en Canvas

Después de subir correctamente a `main`, el enlace esperado es:

https://github.com/RobertoPH98/avocado-insights/blob/main/notebooks/Avance1.Equipo4.ipynb

**Este enlace solo funcionará después de la carga.** Ábrelo y copia la URL de la barra del navegador.

En Canvas: TC5035.10 → Avance 1. Análisis exploratorio de datos → **Entregar tarea** o **Nuevo intento**, según lo que muestre tu cuenta. Selecciona la opción de URL/enlace, pega la liga directa y confirma el envío. Revisa que el intento quede registrado. La publicación de GitHub no realiza automáticamente la entrega en Canvas.

Si la actividad ya cerró, las opciones dependen de la configuración del docente. El material queda preparado, pero no se garantiza que Canvas permita un nuevo envío fuera de plazo.

## 5. Revisar sin ejecutar

Abre `documentacion/Avance1.Equipo4_lectura.html` con Edge o Chrome. Es una versión local autosuficiente con las tablas y figuras incrustadas. La entrega pedida por la actividad sigue siendo la libreta en GitHub.

## 6. Qué debes poder explicar

- El enfoque actual es producción territorial como base de logística sustentable.
- La fuente original es SIAP, pero los bytes provienen de una copia pública identificada y contrastada parcialmente.
- 2024 se separó por claves ambiguas; no se imputó un año entero ni se borraron filas arbitrariamente.
- Sin cosecha, rendimiento/precio no se inventan mediante medianas.
- Atípico no significa error; los municipios grandes se conservan.
- Log1p reduce el sesgo y los rezagos respetan el calendario.
- La correlación producción/superficie no demuestra causalidad y algunas variables tienen relaciones aritméticas.
- No se afirma optimización de rutas, combustible o emisiones porque faltan esos datos.

No es posible prometer una calificación. La libreta aporta evidencia para cada criterio; el docente determina el puntaje.
