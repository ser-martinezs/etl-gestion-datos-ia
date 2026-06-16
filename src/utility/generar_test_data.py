import csv
import os
import random
from datetime import datetime, timedelta

from matplotlib.pylab import rint

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROYECTO_RAIZ = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
OUTPUT_DIR = os.path.join(PROYECTO_RAIZ, "data", "raw")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "ventas_raw.csv")

def generar_datos_prueba(output_file="ventas_raw.csv", total_registros=1000):
    headers = ["id", "fecha", "producto", "cantidad", "precio", "ciudad"]
    
    productos_validos = ["Aceite CBD 5%", "Flores THC 10%", "Cápsulas CBN"]
    ciudades_validas = ["Santiago", "Viña del Mar", "Concepción"]
    
    datos = []
    mitad = total_registros // 2

    for i in range(1, mitad + 1):
        fecha = (datetime(2026, 1, 1) + timedelta(days=random.randint(0, 100))).strftime("%Y-%m-%d")
        row = [
            i,                                      
            fecha,                                  
            random.choice(productos_validos),       
            random.randint(1, 10),                  
            random.randint(5000, 80000),            
            random.choice(ciudades_validas)         
        ]
        datos.append(row)

    tipos_de_error = [
        "duplicado", 
        "nulo_vacio", 
        "precio_no_numerico", 
        "cantidad_invalida", 
        "producto_invalido", 
        "ciudad_invalida"
    ]
    
    current_id = mitad + 1
    while len(datos) < total_registros:
        error = random.choice(tipos_de_error)
        fecha = (datetime(2026, 1, 1) + timedelta(days=random.randint(0, 100))).strftime("%Y-%m-%d")
        
        if error == "duplicado" and len(datos) > 0:
            registro_duplicado = list(random.choice(datos[:mitad]))
            datos.append(registro_duplicado)
            
        elif error == "nulo_vacio":
            campo_vacio = random.choice(["fecha", "cantidad", "precio"])
            row = [
                current_id,
                "" if campo_vacio == "fecha" else fecha,
                random.choice(productos_validos),
                "" if campo_vacio == "cantidad" else random.randint(1, 5),
                "" if campo_vacio == "precio" else random.randint(10000, 30000),
                random.choice(ciudades_validas)
            ]
            datos.append(row)
            current_id += 1
            
        elif error == "precio_no_numerico":
            row = [current_id, fecha, random.choice(productos_validos), random.randint(1, 5), "abc", random.choice(ciudades_validas)]
            datos.append(row)
            current_id += 1
            
        elif error == "cantidad_invalida":
            row = [current_id, fecha, random.choice(productos_validos), random.choice([0, -1, -5]), random.randint(10000, 30000), random.choice(ciudades_validas)]
            datos.append(row)
            current_id += 1
            
        elif error == "producto_invalido":
            row = [current_id, fecha, "Gomitas THC Ultra", random.randint(1, 5), random.randint(10000, 30000), random.choice(ciudades_validas)]
            datos.append(row)
            current_id += 1
            
        elif error == "ciudad_invalida":
            row = [current_id, fecha, random.choice(productos_validos), random.randint(1, 5), random.randint(10000, 30000), "Antofagasta"]
            datos.append(row)
            current_id += 1

    random.shuffle(datos)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(datos)
        
    print(f" Archivo '{output_file}' generado con {len(datos)} registros de prueba.")

if __name__ == "__main__":
    generar_datos_prueba(output_file=OUTPUT_FILE)