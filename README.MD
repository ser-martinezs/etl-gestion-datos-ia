## Flujo ETL

1. Generar los datos crudos con `python src/extract.py`.
2. Limpiar y validar con `python src/transform.py`.
3. Cargar en Supabase con `python src/load.py`.
4. Ejecutar todo junto con `python src/pipeline.py`.

## Variables de entorno

Usa `.env` con las variables de Supabase o define `SUPABASE_DATABASE_URL`.