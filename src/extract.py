import os
import pandas as pd
from logging_utils import get_process_logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_FILE = os.path.join(BASE_DIR, "..", "data", "raw", "ventas_raw.csv")

EXPECTED_COLUMNS = ["id", "fecha", "producto", "cantidad", "precio", "ciudad"]

logger = get_process_logger("extract", "extract.log")

def cargar_ventas(input_file=RAW_FILE):
    if not os.path.exists(input_file):
        logger.error("El archivo de origen no existe en la ruta: %s", input_file)
        raise FileNotFoundError(f"No se encontró el archivo crítico: {input_file}. Ejecuta primero generar_test_data.py")

    logger.info("Iniciando lectura de datos crudos desde: %s", input_file)
    df = pd.read_csv(input_file)
    
    columnas_faltantes = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if columnas_faltantes:
        logger.error("Fallo de esquema estructural. Columnas faltantes: %s", columnas_faltantes)
        raise ValueError(f"Faltan columnas requeridas en el archivo: {', '.join(columnas_faltantes)}")
        
    logger.info("Extracción exitosa. %s registros cargados a memoria.", len(df))
    return df[EXPECTED_COLUMNS].copy()

if __name__ == "__main__":
    try:
        df_test = cargar_ventas()
        print(f"Extracción verificada localmente de manera exitosa. Registros listos: {len(df_test)}")
    except Exception as e:
        print(f"Error en la verificación de extracción: {e}")