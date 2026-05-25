import csv
import os

output_dir = "../data/raw"
output_file = os.path.join(output_dir, "ventas_raw.csv")

datos_ventas = [
    ["1", "2026-05-10", "Aceite CBD 5%", "2", "25000", "Santiago"],
    ["2", "2026-05-11", "Flores THC 10%", "5", "40000", "Valparaíso"],
    ["3", "2026-05-12", "Cápsulas CBN", "1", "15000", "Concepción"],
    #Duplicados 
    ["1", "2026-05-10", "Aceite CBD 5%", "2", "25000", "Santiago"],
    ["2", "2026-05-11", "Flores THC 10%", "5", "40000", "Valparaíso"],
    ["3", "2026-05-12", "Cápsulas CBN", "1", "15000", "Concepción"],
    #Falta fecha, precio no numetico, etc.
    ["4", "", "Aceite CBD 5%", "1", "25000", "La Serena"],                 
    ["5", "2026-05-14", "Flores THC 10%", "0", "30000", "Antofagasta"],        
    ["6", "2026-05-15", "", "3", "15000", "Rancagua"],                        
    ["7", "2026-05-16", "Cápsulas CBN", "2", "15000", ""],                    
    ["8", "2026-05-17", "Aceite CBD 5%", "1", "abc", "Talca"]                 
]

headers = ["id", "fecha", "producto", "cantidad", "precio", "ciudad"]

def generar_csv_ventas():
    try:
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(datos_ventas)
        print(f"Archivo '{output_file}' generado exitosamente con {len(datos_ventas)} registros.")
    except Exception as e:
        print(f"Error al generar el archivo: {e}")

if __name__ == "__main__":
    generar_csv_ventas()