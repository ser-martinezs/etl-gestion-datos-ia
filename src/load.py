import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import OperationalError

from logging_utils import get_process_logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VALID_FILE = os.path.join(BASE_DIR, "..", "data", "processed", "ventas_validas.csv")
INVALID_FILE = os.path.join(BASE_DIR, "..", "data", "processed", "ventas_invalidas.csv")

CLEAN_TABLE = "ventas_clean"
ERROR_TABLE = "ventas_error"
TARGET_COLUMNS = [
    "id",
    "fecha",
    "producto",
    "cantidad",
    "precio",
    "ciudad",
    "total",
    "estado_calidad",
    "fuente",
]

logger = get_process_logger("load", "load.log")
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))


def obtener_database_url():
    database_url = os.getenv("SUPABASE_DATABASE_URL") or os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    host = os.getenv("SUPABASE_HOST")
    port = os.getenv("SUPABASE_PORT", "5432")
    database = os.getenv("SUPABASE_DB", "postgres")
    user = os.getenv("SUPABASE_USER")
    password = os.getenv("SUPABASE_PASSWORD")

    if not all([host, user, password]):
        raise RuntimeError(
            "Falta SUPABASE_DATABASE_URL, DATABASE_URL o las variables SUPABASE_HOST, SUPABASE_USER y SUPABASE_PASSWORD."
        )

    return str(
        URL.create(
            "postgresql+psycopg2",
            username=user,
            password=password,
            host=host,
            port=int(port),
            database=database,
            query={"sslmode": "require"},
        )
    )


def obtener_engine():
    database_url = obtener_database_url()
    return create_engine(database_url, pool_pre_ping=True)


def leer_csv_seguro(file_path):
    if not os.path.exists(file_path):
        logger.warning("No existe el archivo esperado: %s", file_path)
        return pd.DataFrame()
    return pd.read_csv(file_path)


def normalizar_id(df):
    df = df.copy()
    if "id" in df.columns:
        df["id"] = pd.to_numeric(df["id"], errors="coerce").astype("Int64")
    return df


def normalizar_fecha(df):
    df = df.copy()
    if "fecha" in df.columns:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce").dt.date
    return df


def normalizar_numericos(df):
    df = df.copy()
    for column in ["cantidad", "precio", "total"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
    return df


def asegurar_columnas_base(df):
    df = df.copy()
    for column in TARGET_COLUMNS:
        if column not in df.columns:
            df[column] = pd.NA
    return df[TARGET_COLUMNS].copy()


def preparar_ventas_clean(df):
    df = asegurar_columnas_base(df)
    df = normalizar_id(df)
    df = normalizar_fecha(df)
    df = normalizar_numericos(df)
    df["estado_calidad"] = df["estado_calidad"].fillna("clean")
    df["fuente"] = df["fuente"].fillna("transformacion")
    return df


def preparar_ventas_error(df):
    df = df.copy()
    observacion_origen = df["observacion"] if "observacion" in df.columns else pd.Series([pd.NA] * len(df))
    motivo_origen = (
        df["motivo_invalidacion"] if "motivo_invalidacion" in df.columns else pd.Series([pd.NA] * len(df))
    )
    for column in TARGET_COLUMNS + ["observacion"]:
        if column not in df.columns:
            df[column] = pd.NA
    df = df[[*TARGET_COLUMNS, "observacion"]].copy()
    df = normalizar_id(df)
    df = normalizar_fecha(df)
    df = normalizar_numericos(df)
    df["observacion"] = observacion_origen.fillna(motivo_origen).fillna("error_en_proceso")
    df["estado_calidad"] = df["estado_calidad"].fillna("error")
    df["fuente"] = df["fuente"].fillna("transformacion")
    return df


def cargar_tabla(df, table_name, engine, schema="public"):
    if df.empty:
        logger.info("No hay registros para cargar en %s.", table_name)
        return 0

    registros = len(df)
    schema_sql = None if engine.dialect.name == "sqlite" else schema
    schema_log = schema_sql or "default"
    logger.info("Cargando %s registros en %s.%s", registros, schema_log, table_name)
    with engine.begin() as connection:
        df.to_sql(
            name=table_name,
            con=connection,
            schema=schema_sql,
            if_exists="append",
            index=False,
            method="multi",
        )
    logger.info("Carga completada en %s.%s", schema_log, table_name)
    return registros


def cargar_datos():
    logger.info("Inicio del proceso de carga.")
    engine = obtener_engine()

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except OperationalError:
        logger.exception(
            "No fue posible conectar a Supabase. Revisa SUPABASE_HOST, SUPABASE_PORT y las credenciales del .env."
        )
        raise

    ventas_validas = leer_csv_seguro(VALID_FILE)
    ventas_invalidas = leer_csv_seguro(INVALID_FILE)

    ventas_clean = preparar_ventas_clean(ventas_validas)
    ventas_error = preparar_ventas_error(ventas_invalidas)

    registros_clean = cargar_tabla(ventas_clean, CLEAN_TABLE, engine)
    registros_error = cargar_tabla(ventas_error, ERROR_TABLE, engine)

    logger.info("Registros cargados en ventas_clean: %s", registros_clean)
    logger.info("Registros cargados en ventas_error: %s", registros_error)
    logger.info("Proceso de carga finalizado.")

    return registros_clean, registros_error


if __name__ == "__main__":
    try:
        clean, error = cargar_datos()
        print(f"Carga completada. ventas_clean: {clean}, ventas_error: {error}")
    except Exception:
        logger.exception("Falló el proceso de carga.")
        raise
