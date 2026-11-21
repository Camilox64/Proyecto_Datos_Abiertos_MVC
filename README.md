# Sistema web de consulta y análisis de datos abiertos

Aplicación académica en Flask que consulta el recurso público **Casos positivos de COVID-19 en Colombia**, conserva una muestra en SQL Server y permite buscarla desde el navegador.

## Repositorio

El código fuente y las evidencias del proyecto están publicados en [GitHub](https://github.com/Camilox64/Proyecto_Datos_Abiertos_MVC).

## Conjunto de datos

- **Nombre:** Casos positivos de COVID-19 en Colombia.
- **Entidad:** Instituto Nacional de Salud (INS).
- **Propósito:** practicar el consumo de una API REST, la persistencia de registros en SQL Server y una consulta web organizada con Modelo–Vista–Controlador.
- **Ficha:** https://www.datos.gov.co/Salud-y-Protecci-n-Social/Casos-positivos-de-COVID-19-en-Colombia-/gt2j-8ykr
- **Recurso SODA:** `gt2j-8ykr`
- **Endpoint:** https://www.datos.gov.co/resource/gt2j-8ykr.json
- **Corte de la fuente:** los datos llegan hasta el 18 de enero de 2024. La ficha de datos.gov.co registra metadatos actualizados el 18 de mayo de 2026. La aplicación presenta el conjunto como información histórica.
- **Campos usados:** `id_de_caso`, `fecha_reporte_web`, `fecha_de_notificaci_n`, `departamento`, `departamento_nom`, `ciudad_municipio`, `ciudad_municipio_nom`, `edad`, `unidad_medida`, `sexo`, `fuente_tipo_contagio`, `ubicacion`, `estado` y `recuperado`.

La aplicación trae hasta 100 reportes por sincronización, ordenados por fecha de reporte descendente. La API acepta límites de hasta 1.000 filas en esta implementación. La restricción única de `id_api` evita duplicados. El JSON original queda guardado para conservar los campos de la fuente.

## Requisitos

- Python 3.10 o superior
- SQL Server (instancia local o remota)
- Microsoft ODBC Driver 17 o 18 for SQL Server
- Acceso a Internet para consultar datos.gov.co

## Instalación en Windows

Abre PowerShell en esta carpeta y ejecuta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` para indicar servidor, base de datos, controlador e identificador del recurso. Para autenticación integrada de Windows usa `DB_TRUSTED=yes`. Para autenticación SQL usa `DB_TRUSTED=no` y completa `DB_USER` y `DB_PASSWORD`. No publiques `.env`.

Genera una clave Flask local y reemplaza `FLASK_SECRET_KEY` en `.env`:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

## Preparar SQL Server

En SQL Server Management Studio abre y ejecuta `database/crear_base_datos.sql`. El script crea `DatosAbiertosDB` y `dbo.RegistrosAPI` si no existen. La tabla incluye un índice único sobre `id_api`.

Para la instancia predeterminada local, la configuración inicial de `.env.example` usa `DB_SERVER=localhost`. Ajusta ese valor si tienes una instancia con nombre, por ejemplo `localhost\SQLEXPRESS`.

## Ejecutar

```powershell
python app.py
```

Abre http://127.0.0.1:5000. Pulsa **Consultar API y guardar** para obtener el lote configurado. La búsqueda filtra departamento, municipio, tipo de contagio o estado sobre los registros almacenados.

## Estructura MVC

```text
app.py                         Controlador Flask y rutas
api/api_client.py              Servicio HTTP para datos.gov.co
models/datos_model.py          Modelo y acceso a SQL Server con pyodbc
templates/index.html           Vista HTML con Jinja2
static/estilos.css             Presentación adaptable a móvil
database/crear_base_datos.sql  Base y esquema SQL Server
evidence/                      Respuesta de API y evidencia de carga
```

- **Modelo:** `models/datos_model.py` abre la conexión, inserta registros sin duplicar, consulta filas y calcula el resumen.
- **Vista:** `templates/index.html` presenta los indicadores, el formulario y la tabla. No contiene SQL ni conexiones.
- **Controlador:** `app.py` recibe las rutas, coordina el cliente API y el modelo, y envía datos a la plantilla.
- **Servicio API:** `api/api_client.py` separa las peticiones HTTP del acceso a datos.

## Evidencias incluidas

- `evidence/api_response_sample.json`: muestra de cinco respuestas del endpoint consultado el 20 de noviembre de 2026.
- `evidence/carga_sql.txt`: cantidad insertada y consulta de verificación en SQL Server.
- `evidence/sync_repeat.txt`: segunda sincronización de 100 filas, con cero duplicados nuevos.
- `evidence/web_validation.txt`: resultado de la revisión de la página principal y del filtro por Medellín.
- `evidence/capturas/`: capturas de la sincronización, la vista principal y el filtro por Envigado.

La sincronización de esta muestra histórica no representa una actualización epidemiológica actual. Los datos conservan el corte publicado por el INS.

## Presentación

La presentación breve del proyecto está en `presentacion/Presentacion_Proyecto_Datos_Abiertos.pptx`.
