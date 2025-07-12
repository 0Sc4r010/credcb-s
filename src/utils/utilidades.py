import logging
from lxml import etree

logger = logging.getLogger(__name__)

def truncar_con_regla_especial(valor, decimales, modo):
    try:
        valor = float(valor)
        if decimales == 0:
            valor_red = round(valor)
        elif decimales == 2:
            truncado = int(valor * 100) / 100
            valor_red = round(truncado + 0.01, 2) if round(truncado % 1, 2) == 0.99 else round(valor + 1e-10, 2)
        elif decimales == 3:
            truncado = int(valor * 1000) / 1000
            valor_red = round(truncado, 3)
        else:
            factor = 10 ** decimales
            valor_red = int(valor * factor) / factor

        return int(valor_red) if modo == 'T' else valor_red
    except (TypeError, ValueError):
        return None

def truncar_y_aproximar(valor):
    try:
        return round(float(valor) + 1e-10, 2)
    except (TypeError, ValueError):
        return None

def extraer_fac_cont(parametro, respuesta_xml):
    try:
        root = etree.fromstring(respuesta_xml)
        return int(root.find(parametro).text)
    except Exception:
        logger.error("Error al analizar el XML:", exc_info=True)
        return None
