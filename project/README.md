# Sistema de Recomendacion de Restaurantes con Neo4j

Proyecto Python con Neo4j AuraDB para recomendar restaurantes segun gustos, usuarios similares, historial, rating, presupuesto y ubicacion.

## Estructura

```
project/
├── main.py
├── database.py
├── recommendation.py
├── seed_data.py
├── requirements.txt
└── README.md
```

## Instalacion

```bash
cd project
python -m venv venv
pip install -r requirements.txt
```

## Configuracion Neo4j

PowerShell:
```powershell
$env:NEO4J_URI="neo4j+s://xxxxxxxx.databases.neo4j.io"
$env:NEO4J_USER="neo4j"
$env:NEO4J_PASSWORD="tu_contrasena"
```

O edita URI, USER y PASSWORD en database.py.

## Ejecucion

```bash
python main.py
```

## Menu

1. Cargar datos
2. Ver usuarios
3. Recomendar restaurantes (ej: u1)
4. Ver restaurantes visitados
5. Salir

## Ejemplo

```
Selecciona una opcion: 1
Datos cargados correctamente en Neo4j.

Selecciona una opcion: 3
Ingresa el ID del usuario (ej: u1): u1
```

Para u1 se recomienda El Fogon (visitado por Carlos M., usuario similar).

## Instalacion rapida (recomendado)

Ejecuta el instalador que configura dependencias y conexion con AuraDB:

```bash
python instalar.py
```

El script:
1. Instala `neo4j` y `python-dotenv`
2. Te pide URI, usuario y contrasena de AuraDB
3. Guarda la configuracion en `.env`
4. Prueba la conexion con Neo4j
