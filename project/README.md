# Sistema de Recomendacion de Restaurantes (Neo4j AuraDB)

Proyecto Python que crea automaticamente una base de grafos en **Neo4j AuraDB** y recomienda restaurantes segun gustos, usuarios similares, historial, rating y presupuesto.

## Estructura

```
project/
├── .env
├── database.py
├── seed_data.py
├── recommendation.py
├── main.py
├── requirements.txt
└── README.md
```

## Paso 1: Instalar dependencias

Abre PowerShell o CMD en la carpeta `project`:

```powershell
cd c:\Users\Admin\Documents\restaurante\project
pip install -r requirements.txt
```

## Paso 2: Crear archivo `.env`

Crea `project/.env` con tus credenciales de AuraDB (desde https://console.neo4j.io/):

```env
NEO4J_URI=neo4j+s://TU-INSTANCIA.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=tu_contrasena
```

> **Importante:** Nunca subas `.env` a GitHub. Ya esta en `.gitignore`.

## Paso 3: Ejecutar el proyecto

```powershell
python main.py
```

## Paso 4: Crear la base de datos

En el menu elige **opcion 1** (Crear base de datos).

El script:
1. Conecta a AuraDB
2. Ejecuta `MATCH (n) DETACH DELETE n`
3. Crea zonas, cocinas, restaurantes, usuarios y visitas
4. Muestra mensajes en consola

## Paso 5: Probar recomendaciones

1. Opcion **2** -> ver usuarios (u1, u2, u3)
2. Opcion **3** -> ingresa `u1`
3. Veras recomendaciones basadas en usuarios similares

### Ejemplo esperado para u1 (Ana G.)

- Ya visito: Sushi Ito (r1), La Trattoria (r2)
- Usuario similar Carlos M. visito El Fogón (r3)
- Recomendacion principal: **El Fogón**

## Menu completo

| Opcion | Accion |
|--------|--------|
| 1 | Crear base de datos |
| 2 | Ver usuarios |
| 3 | Recomendar restaurantes |
| 4 | Ver historial de usuario |
| 5 | Salir |

## Crear base sin menu (opcional)

```powershell
python seed_data.py
```

## Solucion de problemas

| Error | Solucion |
|-------|----------|
| Faltan variables en .env | Crea `project/.env` con URI, USER y PASSWORD |
| Autenticacion fallida | Verifica contrasena en Aura Console |
| Usuario no existe | Ejecuta opcion 1 para crear la base |
