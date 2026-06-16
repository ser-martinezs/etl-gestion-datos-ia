import os
import pandas as pd
from logging_utils import get_process_logger
import extract

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_FILE = os.path.join(BASE_DIR, "..", "data", "raw", "ventas_raw.csv")
PROCESSED_FILE = os.path.join(BASE_DIR, "..", "data", "processed", "ventas_procesadas.csv")
VALID_FILE = os.path.join(BASE_DIR, "..", "data", "processed", "ventas_validas.csv")
INVALID_FILE = os.path.join(BASE_DIR, "..", "data", "processed", "ventas_invalidas.csv")

EXPECTED_COLUMNS = ["id", "fecha", "producto", "cantidad", "precio", "ciudad"]
REQUIRED_CLEAN_COLUMNS = ["fecha", "producto", "cantidad", "precio", "ciudad"]

PRODUCTOS_VALIDOS = {"Aceite CBD 5%", "Flores THC 10%", "Cápsulas CBN"}
CIUDADES_VALIDAS  = {"Santiago", "Viña del Mar", "Concepción"}

logger_transform = get_process_logger("transform", "transform.log")
logger_validation = get_process_logger("validation", "validation.log")

def eliminar_duplicados(df):
	return df.drop_duplicates()


def eliminar_nulos(df):
	return df.dropna(subset=REQUIRED_CLEAN_COLUMNS)


def obtener_duplicados(df):
	return df[df.duplicated(keep="first")].copy()


def obtener_nulos(df):
	return df[df[REQUIRED_CLEAN_COLUMNS].isna().any(axis=1)].copy()


def limpiar_ventas(df):
	registros_iniciales = len(df)
	df_sin_duplicados = eliminar_duplicados(df)
	duplicados_rechazados = obtener_duplicados(df)
	if not duplicados_rechazados.empty:
		duplicados_rechazados = duplicados_rechazados.assign(
			motivo_invalidacion="duplicado",
			estado_calidad="error",
			fuente="limpieza",
		)
	duplicados_eliminados = registros_iniciales - len(df_sin_duplicados)
	df_limpio = eliminar_nulos(df_sin_duplicados)
	nulos_rechazados = obtener_nulos(df_sin_duplicados)
	if not nulos_rechazados.empty:
		nulos_rechazados = nulos_rechazados.assign(
			motivo_invalidacion="nulo_en_campos_obligatorios",
			estado_calidad="error",
			fuente="limpieza",
		)
	nulos_eliminados = len(df_sin_duplicados) - len(df_limpio)
	df_rechazados = pd.concat([duplicados_rechazados, nulos_rechazados], ignore_index=True)

	logger_transform.info("Registros iniciales: %s", registros_iniciales)
	logger_transform.info("Duplicados eliminados: %s", duplicados_eliminados)
	logger_transform.info("Nulos eliminados: %s", nulos_eliminados)
	logger_transform.info("Registros después limpieza: %s", len(df_limpio))

	return df_limpio, df_rechazados


def estandarizar_fechas(df):
	df = df.copy()
	df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
	df["fecha"] = df["fecha"].dt.strftime("%Y-%m-%d")
	return df


def convertir_numericos(df):
	df = df.copy()
	df["cantidad"] = pd.to_numeric(df["cantidad"], errors="coerce")
	df["precio"] = pd.to_numeric(df["precio"], errors="coerce")
	return df


def crear_total(df):
	df = df.copy()
	df["total"] = df["cantidad"] * df["precio"]
	return df


def _fecha_dt(df):
	return pd.to_datetime(df["fecha"], errors="coerce")


def validar_fecha(df):
	fecha_dt = _fecha_dt(df)
	return fecha_dt.between("2020-01-01", "2030-12-31")

def validar_producto(df):
    return df["producto"].isin(PRODUCTOS_VALIDOS)

def validar_ciudad(df):
    return df["ciudad"].isin(CIUDADES_VALIDAS)

def validar_cantidad(df):
	return df["cantidad"].between(1, 1000)


def validar_precio(df):
	return df["precio"].between(1000, 200000)

def validar_total(df):
	return df["total"].gt(0)


def aplicar_validaciones(df):
	df = df.copy()
	df["valid_fecha"] = validar_fecha(df)
	df["valid_cantidad"] = validar_cantidad(df)
	df["valid_precio"] = validar_precio(df)
	df["valid_producto"] = validar_producto(df)
	df["valid_ciudad"] = validar_ciudad(df)
	df["valid_total"] = validar_total(df)
	df["es_valido"] = df[
		[
			"valid_fecha",
			"valid_cantidad",
			"valid_precio",
			"valid_producto",
			"valid_ciudad",
			"valid_total",
		]
	].all(axis=1)
	df["motivo_invalidacion"] = df.apply(_motivo_invalidacion, axis=1)
	logger_validation.info("Registros validados: %s", len(df))
	logger_validation.info("Registros válidos: %s", int(df["es_valido"].sum()))
	logger_validation.info("Registros inválidos: %s", int((~df["es_valido"]).sum()))
	return df


def registrar_rechazados_por_validacion(df):
	rechazados = df[~df["es_valido"]].copy()
	if rechazados.empty:
		return rechazados
	rechazados["estado_calidad"] = "error"
	rechazados["fuente"] = "transformacion"
	rechazados["observacion"] = rechazados["motivo_invalidacion"]
	return rechazados


def _motivo_invalidacion(fila):
    motivos = []
    if not fila["valid_fecha"]:
        motivos.append("fecha_fuera_de_rango_o_invalida")
    if not fila["valid_cantidad"]:
        motivos.append("cantidad_fuera_de_rango_o_invalida")
    if not fila["valid_precio"]:
        motivos.append("precio_fuera_de_rango_o_invalido")
    if not fila["valid_producto"]:
        motivos.append("producto_no_en_catalogo")  
    if not fila["valid_ciudad"]:
        motivos.append("ciudad_no_en_catalogo")     
    if not fila["valid_total"]:
        motivos.append("total_menor_o_igual_a_cero")
    return "; ".join(motivos) if motivos else pd.NA


def exportar_registros(validos, invalidos, valid_file=VALID_FILE, invalid_file=INVALID_FILE):
	validos = validos.copy()
	invalidos = invalidos.copy()

	if valid_file:
		os.makedirs(os.path.dirname(valid_file), exist_ok=True)
		validos.to_csv(valid_file, index=False)

	if invalid_file:
		os.makedirs(os.path.dirname(invalid_file), exist_ok=True)
		invalidos.to_csv(invalid_file, index=False)

	return validos, invalidos


def transformar_ventas(df, output_file=PROCESSED_FILE):

	df, rechazados_limpieza = limpiar_ventas(df)
	df = estandarizar_fechas(df)
	df = convertir_numericos(df)
	df = crear_total(df)
	df = df.assign(
		fecha=df["fecha"].where(_fecha_dt(df).notna(), pd.NA),
		producto=df["producto"].astype("string").str.strip(),
		ciudad=df["ciudad"].astype("string").str.strip(),
	)
	df = aplicar_validaciones(df)
	df["estado_calidad"] = "clean"
	df["fuente"] = "transformacion"
	rechazados_validacion = registrar_rechazados_por_validacion(df)
	df_rechazados = pd.concat([rechazados_limpieza, rechazados_validacion], ignore_index=True)

	if not df_rechazados.empty:
		if "estado_calidad" not in df_rechazados.columns:
			df_rechazados["estado_calidad"] = "error"
		if "fuente" not in df_rechazados.columns:
			df_rechazados["fuente"] = "transformacion"
		if "observacion" not in df_rechazados.columns:
			df_rechazados["observacion"] = df_rechazados.get("motivo_invalidacion", "error_en_proceso")

	if output_file:
		os.makedirs(os.path.dirname(output_file), exist_ok=True)
		df.to_csv(output_file, index=False)

	df_verdaderos_validos = df[df["es_valido"]].copy()
	exportar_registros(df_verdaderos_validos, df_rechazados)

	logger_transform.info("Transformación finalizada con %s registros.", len(df))

	return df


if __name__ == "__main__":
    df_original = extract.cargar_ventas()
    total_ingresado = len(df_original)
    
    resultado_df = transformar_ventas(df_original)
    
    df_validos_reales = pd.read_csv(VALID_FILE)
    df_invalidos_reales = pd.read_csv(INVALID_FILE)
    
    total_validos = len(df_validos_reales)
    total_invalidos_absolutos = len(df_invalidos_reales)
    
    total_descartados_limpieza = len(df_invalidos_reales[df_invalidos_reales["fuente"] == "limpieza"])
    total_descartados_negocio = len(df_invalidos_reales[df_invalidos_reales["fuente"] == "transformacion"])
    
    logger_transform.info("Ejecución completada desde línea de comandos.")
    
    print("\n" + "="*55)
    print("   REPORTE DE CALIDAD DE DATOS (MÉTRICAS DEL PIPELINE)")
    print("="*55)
    print(f"Total registros recibidos de la ingesta : {total_ingresado}")
    print(f"Registros guardados en ventas_validas   : {total_validos}")
    print(f"Registros guardados en ventas_invalidas : {total_invalidos_absolutos}")
    print("-"*55)
    print(" DETALLE DE DESCARTES COMPROBADOS EN ARCHIVO:")
    print(f"  [x] Por Limpieza Inicial (Duplicados/Nulos) : {total_descartados_limpieza}")
    print(f"  [x] Por Reglas de Negocio (Rangos/Catálogo) : {total_descartados_negocio}")
    print("="*55 + "\n")




