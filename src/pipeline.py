import extract
import load
import transform


def ejecutar_pipeline():
	extract.generar_csv_ventas()
	transform.transformar_ventas()
	return load.cargar_datos()


if __name__ == "__main__":
	clean, error = ejecutar_pipeline()
	print(f"Pipeline completado. ventas_clean: {clean}, ventas_error: {error}")
