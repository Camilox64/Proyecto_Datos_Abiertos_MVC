"""Controlador Flask del sistema de consulta de datos abiertos."""

import os
import secrets

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from api.api_client import DatosGovClient
from models.datos_model import consultar_registros, guardar_registros, obtener_resumen

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32)


@app.get("/")
def inicio():
    filtro = request.args.get("q", "").strip()[:100]
    try:
        registros = consultar_registros(filtro)
        resumen = obtener_resumen()
        error_bd = None
    except Exception:
        app.logger.exception("No fue posible consultar SQL Server")
        registros = []
        resumen = {"total": 0, "departamentos": 0, "municipios": 0, "fecha_mas_reciente": None}
        error_bd = "No fue posible consultar SQL Server. Revisa la conexión y ejecuta database/crear_base_datos.sql."

    return render_template(
        "index.html",
        registros=registros,
        filtro=filtro,
        resumen=resumen,
        error_bd=error_bd,
    )


@app.post("/sincronizar")
def sincronizar():
    try:
        limite = int(os.getenv("API_LIMIT", "100"))
        limite = max(1, min(limite, 1000))
        datos = DatosGovClient().obtener_registros(limite)
        cantidad = guardar_registros(datos)
        flash(
            f"La API respondió con {len(datos)} registros. Se guardaron {cantidad} nuevos; los repetidos se omitieron.",
            "success",
        )
    except Exception as error:
        app.logger.exception("Falló la sincronización")
        flash(f"No fue posible completar la sincronización: {error}", "error")
    return redirect(url_for("inicio"))


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "0").strip().lower() in {"1", "true", "yes", "si", "sí"}
    app.run(host="127.0.0.1", port=5000, debug=debug)
