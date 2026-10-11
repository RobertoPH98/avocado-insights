# Cómo subir y entregar el Avance 2

## 1. Descargar y extraer el paquete

Descarga `Entrega_Avance2_Equipo4.zip`. En Windows, usa clic derecho → **Extraer todo**. Abre la carpeta extraída `entrega_avance2` hasta ver `README_AVANCE2.md`, `requirements_avance2.txt` y las carpetas `notebooks`, `src`, `data`, `resultados`, `documentacion` y `scripts`.

**No arrastres archivos directamente desde la vista del ZIP/RAR.** Primero extráelos a una carpeta normal.

## 2. Subir a la raíz del repositorio

1. Abre https://github.com/RobertoPH98/avocado-insights e inicia sesión con una cuenta que tenga permiso de escritura.
2. Selecciona la rama `main` y la pestaña **Code**. Debes estar en la raíz, donde ves las carpetas existentes, no dentro de `notebooks`.
3. Pulsa **Add file → Upload files**.
4. Arrastra **todo el contenido interior** de `entrega_avance2`. No arrastres el ZIP ni la carpeta exterior `entrega_avance2`.
5. Espera a que termine la carga. Comprueba en la lista al menos estas rutas:

| Ruta | Por qué importa |
|---|---|
| `notebooks/Avance2.Equipo4.ipynb` | Archivo que revisará el profesor |
| `src/fe_avance2.py` | Código requerido para ejecutar la libreta |
| `data/raw/siap_produccion.csv` | Datos de entrada; ya estaban en el repositorio, se incluyen idénticos |
| `data/avance2/manifest_avance2.json` | Evidencia y descripción de las matrices exportadas |
| `requirements_avance2.txt` | Dependencias para reproducir |

6. Escribe como mensaje de commit: `Agrega Avance 2: ingeniería de características y validación reproducible`.
7. Pulsa **Commit changes**. Si GitHub crea una rama o una propuesta de cambio, integra esa rama en `main` antes de usar la liga de abajo.
8. Abre `notebooks` → `Avance2.Equipo4.ipynb`. Confirma que se ven los integrantes, las tablas, las 9 figuras y las conclusiones.

La cantidad de carpetas visibles no equivale a la cantidad de archivos subidos. Comprueba las rutas, no solo que aparezcan “dos elementos”. Si una carga falla, repite por carpetas desde la raíz y verifica sus contenidos. No borres Avance 1 ni las entregas anteriores.

Si aparece un mensaje de permisos, debe subirlo el propietario o una cuenta colaboradora con permiso de escritura. No se necesitan contraseñas ni tokens dentro de ningún archivo del proyecto.

Guía oficial de GitHub: https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository

## 3. Entregar en Canvas

**Después de que el archivo esté publicado en `main`**, abre esta liga y comprueba que muestra la libreta:

https://github.com/RobertoPH98/avocado-insights/blob/main/notebooks/Avance2.Equipo4.ipynb

En Canvas entra a **TC5035.10 → Avance 2. Ingeniería de características → Ingresar URL web**. Pega la liga anterior y pulsa el botón de envío que muestre la actividad. Comprueba que el intento quedó registrado.

No entregues el enlace al ZIP, la página de carga o únicamente la raíz del repositorio. No basta subir a GitHub: también debes confirmar el envío en Canvas.

## 4. Revisar sin instalar Python

Abre `documentacion/avance2/Avance2.Equipo4_lectura.html` con Chrome o Edge. Contiene los resultados y las gráficas incrustadas; el código se puede desplegar. Esta versión facilita la lectura, pero el entregable solicitado sigue siendo el notebook en GitHub.

## 5. Última revisión

- Nombre: `Avance2.Equipo4.ipynb`.
- Celdas de código numeradas 1–14, con resultados y sin traceback.
- 9 figuras y conclusión general de Preparación de datos en CRISP-ML(Q).
- Explicación explícita sobre los 981 registros estatales de 1980–2002.
- Datos originales, módulo `src` y dependencias accesibles para el profesor.
- Liga directa abierta y comprobada antes de pegarla en Canvas.

La libreta ya está ejecutada. Si modificas código o datos, vuelve a ejecutarla completa y guarda antes de subirla.
