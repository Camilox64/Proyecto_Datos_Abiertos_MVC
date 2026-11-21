"""Cliente HTTP para el recurso SODA de datos.gov.co."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()


class DatosGovClient:
    """Consulta registros públicos en formato JSON."""

    BASE_URL = "https://www.datos.gov.co/resource"

    def __init__(self, resource_id=None):
        self.resource_id = resource_id or os.getenv("API_RESOURCE_ID", "gt2j-8ykr")
        if not self.resource_id or self.resource_id == "ID_DEL_RECURSO":
            raise ValueError("Configura API_RESOURCE_ID en el archivo .env.")
        self.url = f"{self.BASE_URL}/{self.resource_id}.json"

    def obtener_registros(self, limite=100):
        """Trae los reportes más recientes publicados en el recurso."""
        limite = max(1, min(int(limite), 1000))
        respuesta = requests.get(
            self.url,
            params={"$limit": limite, "$order": "fecha_reporte_web DESC"},
            headers={"User-Agent": "ProyectoDatosAbiertosMVC/1.0"},
            timeout=30,
        )
        respuesta.raise_for_status()
        datos = respuesta.json()
        if not isinstance(datos, list):
            raise ValueError("La API respondió con un formato JSON distinto al esperado.")
        return datos
