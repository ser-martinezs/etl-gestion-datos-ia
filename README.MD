## Flujo ETL

1. Generar los datos crudos con `python src/extract.py`.
2. Limpiar y validar con `python src/transform.py`.
3. Cargar en Supabase con `python src/load.py`.

O

Ejecutar todo en conjunto con `python src/pipeline.py`.

## Variables de entorno

### Opción A: URL de Conexión Directa (Recomendada)

```env
SUPABASE_DATABASE_URL=postgresql://postgres.[TU_ID_DE_PROYECTO]:[TU_CONTRASEÑA]@aws-1-us-east-2.pooler.supabase.com:6543/postgres
```

## Opción B: Componentes
```env
DB_HOST=aws-0-[REGINA].supabase.co
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=TU_CONTRASEÑA_SECRETA
DB_PORT=5432
```

## Docker

Construye la imagen desde la raíz del proyecto:

```bash
docker build -t etl-ventas:latest .
```

Prueba el ETL en local con SQLite:

### Linux Estándar (Ubuntu, Debian, Mint)

```bash
docker run --rm \
  -e DATABASE_URL=sqlite:////app/data/etl.db \
  -v "$(pwd)/logs:/app/logs" \
  -v "$(pwd)/data:/app/data" \
  etl-ventas:latest
```

### Ejecucion en Linux (SELinux)

```bash
docker run --rm \
  -e DATABASE_URL=sqlite:////app/data/etl.db \
  -v "$(pwd)/logs":/app/logs:Z \
  -v "$(pwd)/data":/app/data:Z \
  etl-ventas:latest
```
### Ejecución en Windows (PowerShell)

```powershell
docker run --rm `
  -e DATABASE_URL=sqlite:////app/data/etl.db `
  -v "${PWD}/logs:/app/logs" `
  -v "${PWD}/data:/app/data" `
  etl-ventas:latest
```

### CMD

```cmd
docker run --rm ^
  -e DATABASE_URL=sqlite:////app/data/etl.db ^
  -v "%cd%/logs:/app/logs" ^
  -v "%cd%/data:/app/data" ^
  etl-ventas:latest
