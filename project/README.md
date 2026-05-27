# Sistema de Recomendacion de Restaurantes (Neo4j AuraDB)

Proyecto Python con base de grafos en **Neo4j AuraDB** para recomendar restaurantes segun gustos, usuarios similares, historial, rating y presupuesto.

Incluye:
- **Consola** (`main.py`)
- **Interfaz grafica** (`gui.py`)
- **Visualizacion del grafo** en tiempo real

---

## Requisitos

- Python 3.8+
- Cuenta [Neo4j AuraDB](https://console.neo4j.io/)
- Archivo `.env` configurado (ver abajo)

---

## Instalacion

```powershell
cd c:\Users\Admin\Documents\restaurante\project
pip install -r requirements.txt
```

---

## Configuracion (.env)

Crea `project/.env` con tus credenciales de Aura:

```env
NEO4J_URI=neo4j+s://TU-INSTANCIA.databases.neo4j.io
NEO4J_USERNAME=TU-INSTANCIA
NEO4J_PASSWORD=tu_contrasena
NEO4J_DATABASE=TU-INSTANCIA
AURA_INSTANCEID=TU-INSTANCIA
AURA_INSTANCENAME=Restaurante
```

> En Aura el **usuario** y la **base de datos** suelen ser el ID de instancia, no `neo4j`.

---

## Ejecutables

Todos los comandos se ejecutan desde la carpeta `project/`:

```powershell
cd c:\Users\Admin\Documents\restaurante\project
```

### 1. Interfaz grafica (recomendado)

Aplicacion visual con Tkinter: agregar/editar usuarios, recomendaciones, historial y grafo en vivo.

```powershell
python gui.py
```

| Funcion | Descripcion |
|---------|-------------|
| Agregar usuario | Crea nodos User con LIVES_IN y LIKES_CUISINE |
| Editar usuario | Actualiza datos y relaciones |
| Recomendador | Top 5 restaurantes por similitud |
| Historial | Restaurantes visitados por usuario |
| Grafo | Panel derecho siempre visible (NetworkX + Matplotlib) |

---

### 2. Menu de consola

Menu interactivo en terminal (sin interfaz grafica).

```powershell
python main.py
```

| Opcion | Accion |
|--------|--------|
| 1 | Crear base de datos (limpia e inserta datos de ejemplo) |
| 2 | Ver usuarios |
| 3 | Recomendar restaurantes |
| 4 | Ver historial de usuario |
| 5 | Salir |

---

### 3. Probar conexion con AuraDB

Verifica que `.env`, usuario, password y base de datos sean correctos.

```powershell
python test_connection.py
```

Con debug detallado:

```powershell
python test_connection.py --debug
```

O:

```powershell
$env:DEBUG_NEO4J="1"
python test_connection.py
```

---

### 4. Instalador de dependencias y .env

Instala paquetes y guia la configuracion inicial de credenciales.

```powershell
python instalar.py
```

---

### 5. Crear base de datos (solo consola / script)

> **Usar solo la primera vez** o si quieres resetear datos de ejemplo.
> La GUI (`gui.py`) **no** ejecuta esto automaticamente.

```powershell
python seed_data.py
```

Tambien disponible desde `python main.py` -> opcion 1.

---

## Resumen rapido de comandos

| Comando | Para que sirve |
|---------|----------------|
| `python gui.py` | App visual completa |
| `python main.py` | Menu en consola |
| `python test_connection.py` | Probar conexion Neo4j |
| `python instalar.py` | Instalar deps + configurar .env |
| `python seed_data.py` | Poblar base de datos de ejemplo |

---

## Estructura del proyecto

```
project/
├── .env                 # Credenciales AuraDB (no subir a Git)
├── .env.example         # Plantilla
├── database.py          # Conexion Neo4j (Neo4jConnection)
├── recommendation.py    # Logica Cypher y CRUD usuarios
├── graph_view.py        # Visualizacion del grafo
├── gui.py               # Interfaz grafica Tkinter
├── main.py              # Menu consola
├── seed_data.py         # Datos de ejemplo
├── test_connection.py   # Test de conexion
├── instalar.py          # Instalador
└── requirements.txt     # Dependencias
```

---

## Dependencias

```
neo4j>=5.0.0
python-dotenv>=1.0.0
networkx>=3.0
matplotlib>=3.7
```

---

## Solucion de problemas

| Problema | Solucion |
|----------|----------|
| AuthError | Usa `NEO4J_USERNAME` = ID instancia (no `neo4j`) |
| DatabaseNotFound | `NEO4J_DATABASE` = ID instancia Aura |
| GUI no abre | `pip install networkx matplotlib` |
| Sin usuarios en GUI | La base ya debe estar creada (`seed_data.py` una vez) |

---

## Licencia

Proyecto educativo de demostracion con Neo4j y Python.
