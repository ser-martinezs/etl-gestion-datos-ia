import csv
import os

from logging_utils import get_process_logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(BASE_DIR, "..", "data", "raw")
output_file = os.path.join(output_dir, "ventas_raw.csv")

logger = get_process_logger("extract", "extract.log")

datos_ventas = [
    ["1", "2026-05-10", "Aceite CBD 5%", "2", "25000", "Santiago"],
    ["2", "2026-05-11", "Flores THC 10%", "5", "40000", "Valparaíso"],
    ["3", "2026-05-12", "Cápsulas CBN", "1", "15000", "Concepción"],
    ["4", "2026-05-13", "Aceite CBD 10%", "3", "30000", "La Serena"],
    ["5", "2026-05-14", "Flores THC 20%", "4", "45000", "Antofagasta"],
    ["6", "2026-05-15", "Cápsulas CBN 25%", "2", "18000", "Rancagua"],
    #Duplicados
    ["1", "2026-05-10", "Aceite CBD 5%", "2", "25000", "Santiago"],
    ["2", "2026-05-11", "Flores THC 10%", "5", "40000", "Valparaíso"],
    ["3", "2026-05-12", "Cápsulas CBN", "1", "15000", "Concepción"],
    # Nulos que deben eliminarse en limpieza
    ["7", "", "Aceite CBD 5%", "1", "25000", "La Serena"],
    ["8", "2026-05-17", "Cápsulas CBN", "2", "15000", ""]
]

headers = ["id", "fecha", "producto", "cantidad", "precio", "ciudad"]

def generar_csv_ventas():
    try:
        logger.info("Iniciando extracción de ventas.")
        os.makedirs(output_dir, exist_ok=True)
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(datos_ventas)
        logger.info("Archivo generado en %s con %s registros.", output_file, len(datos_ventas))
        print(f"Archivo '{output_file}' generado exitosamente con {len(datos_ventas)} registros.")
    except Exception as e:
        logger.exception("Error al generar el archivo de ventas.")
        print(f"Error al generar el archivo: {e}")

if __name__ == "__main__":
    generar_csv_ventas()