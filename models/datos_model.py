"""Consultas y persistencia de los reportes del conjunto seleccionado."""

import json
import os

import pyodbc
from dotenv import load_dotenv

load_dotenv()


def obtener_conexion():
    """Abre una conexión a SQL Server usando configuración del entorno."""
    servidor = os.getenv("DB_SERVER", "localhost")
    base_datos = os.getenv("DB_NAME", "DatosAbiertosDB")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
    trusted = os.getenv("DB_TRUSTED", "yes").strip().lower() in {"yes", "true", "1", "si", "sí"}

    if trusted:
        cadena = (
            f"DRIVER={{{driver}}};SERVER={servidor};DATABASE={base_datos};"
            "Trusted_Connection=yes;TrustServerCertificate=yes;"
        )
    else:
        usuario = os.getenv("DB_USER", "")
        clave = os.getenv("DB_PASSWORD", "")
        if not usuario or not clave:
            raise ValueError("Configura DB_USER y DB_PASSWORD para autenticación SQL.")
        cadena = (
            f"DRIVER={{{driver}}};SERVER={servidor};DATABASE={base_datos};"
            f"UID={usuario};PWD={clave};TrustServerCertificate=yes;"
        )
    return pyodbc.connect(cadena, timeout=10)


def _texto(valor, maximo):
    if valor is None:
        return None
    return str(valor)[:maximo]


def _entero(valor):
    if valor in (None, ""):
        return None
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def guardar_registros(registros):
    """Inserta filas nuevas y conserva la unicidad de id_api."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    insertados = 0
    sql = """
        SET NOCOUNT ON;
        DECLARE @insertados TABLE (id_api NVARCHAR(40));
        IF NOT EXISTS (
            SELECT 1 FROM dbo.RegistrosAPI WITH (UPDLOCK, HOLDLOCK) WHERE id_api = ?
        )
        BEGIN
            INSERT INTO dbo.RegistrosAPI (
                id_api, fecha_reporte_web, fecha_notificacion, departamento,
                departamento_nombre, municipio, municipio_nombre, edad,
                unidad_medida, sexo, tipo_contagio, ubicacion, estado,
                recuperado, json_original
            )
            OUTPUT INSERTED.id_api INTO @insertados
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        END
        SELECT COUNT(1) FROM @insertados;
    """

    try:
        for registro in registros:
            if not isinstance(registro, dict):
                continue
            identificador = _texto(registro.get("id_de_caso"), 40)
            if not identificador:
                continue

            cursor.execute(
                sql,
                identificador,
                identificador,
                registro.get("fecha_reporte_web"),
                registro.get("fecha_de_notificaci_n"),
                _texto(registro.get("departamento"), 12),
                _texto(registro.get("departamento_nom"), 120),
                _texto(registro.get("ciudad_municipio"), 12),
                _texto(registro.get("ciudad_municipio_nom"), 160),
                _entero(registro.get("edad")),
                _texto(registro.get("unidad_medida"), 12),
                _texto(registro.get("sexo"), 12),
                _texto(registro.get("fuente_tipo_contagio"), 80),
                _texto(registro.get("ubicacion"), 80),
                _texto(registro.get("estado"), 80),
                _texto(registro.get("recuperado"), 80),
                json.dumps(registro, ensure_ascii=False),
            )
            resultado = cursor.fetchone()
            insertados += int(resultado[0])

        conexion.commit()
        return insertados
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def consultar_registros(filtro="", limite=100):
    """Devuelve las filas más recientes, con búsqueda territorial opcional."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    limite = max(1, min(int(limite), 500))
    try:
        if filtro:
            patron = f"%{filtro}%"
            cursor.execute(
                f"""
                SELECT TOP ({limite}) id_api, fecha_reporte_web, departamento_nombre,
                       municipio_nombre, edad, sexo, tipo_contagio, estado
                FROM dbo.RegistrosAPI
                WHERE departamento_nombre LIKE ?
                   OR municipio_nombre LIKE ?
                   OR tipo_contagio LIKE ?
                   OR estado LIKE ?
                ORDER BY fecha_reporte_web DESC, TRY_CONVERT(BIGINT, id_api) DESC
                """,
                patron,
                patron,
                patron,
                patron,
            )
        else:
            cursor.execute(
                f"""
                SELECT TOP ({limite}) id_api, fecha_reporte_web, departamento_nombre,
                       municipio_nombre, edad, sexo, tipo_contagio, estado
                FROM dbo.RegistrosAPI
                ORDER BY fecha_reporte_web DESC, TRY_CONVERT(BIGINT, id_api) DESC
                """
            )
        columnas = [columna[0] for columna in cursor.description]
        return [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
    finally:
        cursor.close()
        conexion.close()


def obtener_resumen():
    """Calcula indicadores sencillos sobre los registros guardados."""
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            """
            SELECT COUNT_BIG(*) AS total,
                   COUNT(DISTINCT departamento_nombre) AS departamentos,
                   COUNT(DISTINCT municipio_nombre) AS municipios,
                   MAX(fecha_reporte_web) AS fecha_mas_reciente
            FROM dbo.RegistrosAPI;
            """
        )
        fila = cursor.fetchone()
        return {
            "total": int(fila[0] or 0),
            "departamentos": int(fila[1] or 0),
            "municipios": int(fila[2] or 0),
            "fecha_mas_reciente": fila[3],
        }
    finally:
        cursor.close()
        conexion.close()
