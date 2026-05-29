# Savory — Documentación completa del proyecto

**Sistema de recomendación gastronómica basado en grafos para Ciudad de Guatemala**

Versión del documento: 2026  
Stack principal: Python · Tkinter · Neo4j AuraDB · NetworkX · Matplotlib

---

## Índice

1. [Explicación general del proyecto](#parte-1--explicación-general-del-proyecto)
2. [Flujo completo del sistema](#parte-2--flujo-completo-del-sistema)
3. [Explicación del grafo](#parte-3--explicación-del-grafo)
4. [Algoritmos y recommendation engine](#parte-4--algoritmos-y-recommendation-engine)
5. [Por qué los restaurantes fake eran malos](#parte-5--por-qué-los-restaurantes-fake-eran-malos)
6. [Restaurantes reales y links externos](#parte-6--restaurantes-reales-y-links-externos)
7. [Interfaz y experiencia de usuario](#parte-7--interfaz-y-experiencia-de-usuario)
8. [Explicación de cada archivo](#parte-8--explicación-de-cada-archivo)
9. [Puntos para defender oralmente](#parte-9--puntos-para-defender-oralmente)
10. [Posibles preguntas del profesor](#parte-10--posibles-preguntas-del-profesor)
11. [Conclusión](#parte-11--conclusión)

---

# Parte 1 — Explicación general del proyecto

## ¿Qué es Savory?

**Savory** es una aplicación de recomendación gastronómica pensada para Ciudad de Guatemala. Su propósito no es mostrar una lista genérica de “los mejores restaurantes”, sino responder una pregunta más humana:

> *¿Qué restaurante encaja contigo, según cómo comes, qué buscas y cómo te sientes hoy?*

El usuario crea un **perfil gastronómico** mediante un cuestionario visual (onboarding), el sistema guarda sus preferencias en una base de datos en forma de **grafo**, y un **motor de recomendaciones** calcula compatibilidad con más de 200 restaurantes reales. Luego puede ver explicaciones, porcentajes de afinidad, un grafo interactivo y abrir links reales del restaurante en el navegador.

Savory se presenta como una **plataforma gastronómica moderna**, no como un demo técnico frío.

---

## ¿Cuál era el problema original?

Al inicio, muchos sistemas de recomendación cometen el mismo error: tratan todos los restaurantes como si fueran intercambiables y todos los usuarios como si quisieran lo mismo — normalmente “premium”, “gourmet” o “elegante”.

Eso produce recomendaciones absurdas:

- Un usuario que ama **fast food, comida americana y ambientes casuales** recibe un steakhouse fine dining con 35% de compatibilidad y un Burger King mal puntuado.
- Restaurantes ficticios o mal clasificados rompen la confianza del usuario.
- No hay explicación de *por qué* se recomienda algo.

El problema real no era “falta de datos”, sino **falta de contexto y coherencia semántica**.

---

## ¿Por qué un sistema de recomendación gastronómica?

Porque elegir dónde comer es una decisión **personal, emocional y contextual**:

- No es lo mismo cenar en pareja que salir con amigos.
- No es lo mismo buscar comida rápida que una experiencia gourmet.
- El presupuesto, la zona y el mood del día cambian la respuesta correcta.

Un motor de recomendación bien diseñado puede convertir preferencias dispersas (carne, casual, americana, comida rápida) en sugerencias que **se sienten humanas**.

---

## ¿Por qué usar grafos?

En la vida real, las relaciones gastronómicas no son tablas planas. Un usuario **vive en** una zona, **prefiere** ciertos sabores, **visita** restaurantes, y esos restaurantes **pertenecen a** cocinas y **coinciden con** preferencias.

Eso es naturalmente un **grafo**: nodos (usuario, restaurante, cocina, zona, preferencia) conectados por relaciones con significado.

**Analogía:** imagina un mapa de afinidades. No es una hoja de cálculo; es una red donde puedes “caminar” desde un usuario hacia restaurantes compatibles pasando por sus gustos.

---

## ¿Por qué Neo4j?

**Neo4j** es una base de datos diseñada para grafos. Savory la usa en la nube (**Neo4j AuraDB**).

### Ventajas frente a SQL tradicional para este proyecto


| Aspecto                                                       | SQL relacional                  | Neo4j (grafo)                           |
| ------------------------------------------------------------- | ------------------------------- | --------------------------------------- |
| Modelar “usuario → prefiere → X → coincide con → restaurante” | Varias tablas y JOINs complejos | Consultas directas sobre relaciones     |
| Agregar tipos de relación (VISITED, HAS_PREFERENCE, etc.)     | Migraciones y tablas puente     | Relaciones nativas con propiedades      |
| Visualizar conexiones                                         | Difícil de interpretar          | Natural para grafos y recomendaciones   |
| Preguntas del tipo “usuarios similares que visitaron…”        | Costoso de escribir y leer      | Expresivo con pattern matching (Cypher) |


**En resumen:** SQL sirve para inventarios y facturación; Neo4j encaja mejor cuando **las relaciones son el producto**.

---

## Evolución del proyecto

Savory evolucionó en etapas claras:

1. **Prototipo inicial** — consola, usuarios básicos, recomendaciones simples.
2. **Interfaz gráfica** — Tkinter, panel de grafo, gestión de usuarios.
3. **Onboarding inmersivo** — 15 pasos, perfil conductual acumulado.
4. **Catálogo real** — 220 restaurantes de Guatemala con clasificación semántica.
5. **Motor contextual** — perfiles dominantes, pesos dinámicos, explicaciones inteligentes.
6. **Experiencia premium** — cards interactivas, links reales, mood del día, analytics.

Cada etapa respondió a un problema concreto de coherencia o experiencia de usuario.

---

# Parte 2 — Flujo completo del sistema

A continuación se describe el recorrido completo, paso a paso, como si fuera la historia de un usuario real.

## 1. El usuario entra a Savory

Ejecuta `python gui.py`. La aplicación:

- Carga estilos y tema visual (`styles.py`).
- Conecta a Neo4j AuraDB (`database.py`).
- Importa el catálogo de restaurantes si aún no está en la base (`restaurant_importer.py`).
- Muestra la pantalla de inicio con el **hero banner** y dos caminos: crear perfil o explorar recomendaciones.

## 2. Crea su perfil gastronómico

Desde el hero o el menú lateral, entra al **onboarding**. Allí indica:

- Nombre
- Zona de residencia habitual
- Presupuesto aproximado por persona

Esto crea la base del nodo `User` en Neo4j.

## 3. Responde el cuestionario (15 pasos)

El wizard (`onboarding.py`) guía al usuario por preguntas como:

- ¿Qué base prefieres? (carne, mariscos, verduras)
- ¿Fast food o restaurante casual?
- ¿Qué cocinas del mundo te gustan?
- ¿Ambiente romántico, casual, trendy, familiar?
- ¿Presupuesto habitual?

Cada respuesta **suma pesos** a preferencias internas (`fast_food`, `comfort_food`, `pref_italiana`, `premium`, etc.). No es un simple “sí/no”: es un perfil acumulativo.

## 4. Se generan preferencias

Al finalizar, `OnboardingWizard.get_final_profile()` devuelve un diccionario de scores. Ejemplo simplificado:

```
fast_food: 11
comfort_food: 10
casual: 11
contundente: 8
premium: 3
```

Además, `map_food_to_cuisines()` infiere cocinas favoritas (Italiana, Japonesa, etc.) para la relación `LIKES_CUISINE`.

## 5. Se guardan nodos y relaciones en Neo4j

`user_manager.guardar_perfil_gastronomico()` persiste:

- Nodo **User** con id, nombre, presupuesto
- Relación **LIVES_IN** → **Zone**
- Relaciones **LIKES_CUISINE** → **Cuisine**
- Relaciones **HAS_PREFERENCE** → **Preference** (con propiedad `score`)

Cada preferencia es un nodo reutilizable en el grafo. Así dos usuarios que aman `comfort_food` comparten el mismo nodo de preferencia.

## 6. Se calcula el perfil conductual (arquetipo dominante)

No se usa solo una preferencia suelta. El motor detecta un **perfil dominante**, por ejemplo:

- `fast_food_user`
- `premium_user`
- `explorer_user`
- `romantic_user`
- `social_user`

Si alguien acumula mucho `fast_food`, `comida_rapida`, `casual` y `comfort_food`, el sistema entiende que no debe recomendar como si fuera un crítico gourmet.

## 7. El recommendation engine analiza afinidades

Cuando el usuario pide recomendaciones (`recomendar_restaurantes_inteligente()`):

1. Lee sus preferencias desde Neo4j.
2. Opcionalmente aplica un **mood del día** (comfort, premium, social…).
3. Compara contra el catálogo semántico de 220 restaurantes.
4. Calcula compatibilidad en capas (base, contexto, comportamiento).
5. Filtra por presupuesto y excluye restaurantes ya visitados.
6. Ordena y devuelve el top 8.

## 8. Se generan recomendaciones con explicación

Cada resultado incluye:

- **Porcentaje de compatibilidad**
- **Explicación en lenguaje humano** (“encaja contigo porque prefieres comida rápida y casual…”)
- **Tags** (#fastfood, #comfortfood, #americana)
- **Links** (web, Maps, Instagram)

## 9. El usuario puede abrir restaurantes reales

Al hacer clic en una card o en **Ver restaurante**, Savory abre el navegador con la mejor URL disponible (web oficial → Instagram → Google Maps → Facebook → búsqueda Google).

---

## Diagrama de flujo simplificado

```
Usuario → Onboarding → Perfil (prefs + cocinas + presupuesto)
                              ↓
                         Neo4j (grafo)
                              ↓
              Recommendation Engine (scoring contextual)
                              ↓
            Cards + explicaciones + tags + links
                              ↓
                    Navegador (restaurante real)
```

---

# Parte 3 — Explicación del grafo

## Nodos principales


| Nodo           | Qué representa                  | Ejemplo                                  |
| -------------- | ------------------------------- | ---------------------------------------- |
| **User**       | Persona con perfil gastronómico | `u1` — Ana G.                            |
| **Restaurant** | Restaurante del catálogo        | `gc_042` — Tre Fratelli                  |
| **Preference** | Dimensión de gusto o conducta   | `fast_food`, `romantic`, `pref_italiana` |
| **Cuisine**    | Tipo de cocina                  | Italiana, Japonesa, Guatemalteca         |
| **Zone**       | Zona de la ciudad               | Zona 10, Zona 14                         |


## Relaciones principales


| Relación                          | Significado                                      | Ejemplo                                                          |
| --------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------- |
| **HAS_PREFERENCE** `{score}`      | Cuánto valora el usuario esa preferencia         | `(Ana)-[:HAS_PREFERENCE {score: 9}]->(fast_food)`                |
| **MATCHES_PREFERENCE** `{weight}` | Cuánto encaja el restaurante con esa preferencia | `(Burger King)-[:MATCHES_PREFERENCE {weight: 1.0}]->(fast_food)` |
| **LIKES_CUISINE**                 | Cocinas favoritas del usuario                    | `(Ana)-[:LIKES_CUISINE]->(Italiana)`                             |
| **HAS_CUISINE**                   | Cocina principal del restaurante                 | `(Tre Fratelli)-[:HAS_CUISINE]->(Italiana)`                      |
| **LOCATED_IN**                    | Ubicación del restaurante                        | `(Tre Fratelli)-[:LOCATED_IN]->(Zona 10)`                        |
| **LIVES_IN**                      | Zona habitual del usuario                        | `(Ana)-[:LIVES_IN]->(Zona 10)`                                   |
| **VISITED**                       | Historial de visitas                             | `(Ana)-[:VISITED]->(Hacienda Real)`                              |


## Por qué el grafo modela mejor las afinidades gastronómicas

Porque la recomendación no depende de una sola columna. Depende de **caminos**:

- Usuario → prefiere → `comfort_food` ← coincide con ← Restaurante
- Usuario → vive en → Zona 10 ← ubicado en ← Restaurante
- Usuario → gusta → Italiana ← tiene cocina ← Restaurante

En SQL habría que unir muchas tablas. En Neo4j la pregunta se parece a la forma en que pensamos: *“este usuario está conectado a cosas que también conectan con este restaurante”*.

## Cómo se navega el grafo en Savory

1. **Recomendación principal:** consulta Cypher sobre restaurantes, presupuesto, zonas y preferencias; el scoring fino se hace en Python con el catálogo semántico.
2. **Usuarios similares:** usuarios que comparten cocinas y visitaron restaurantes que tú no has probado.
3. **Visualización:** `graph_view.py` dibuja el subgrafo alrededor del usuario activo con NetworkX y Matplotlib.

---

# Parte 4 — Algoritmos y recommendation engine

Esta es la parte central para defender el proyecto. Savory **no** usa un solo número mágico: combina varias ideas que juntas producen recomendaciones coherentes.

## Filosofía del motor

> No existe “el mejor restaurante universal”. Existe **el restaurante más compatible para ese tipo de usuario**.

Un steakhouse premium puede ser excelente, pero mala recomendación para alguien que hoy quiere fast food.

---

## 1. Similitud coseno (cosine similarity)

**Qué hace:** mide qué tan parecidos son dos vectores de preferencias.

**Intuición:** imagina que tus gustos y los de un restaurante son flechas en un espacio. Si apuntan en la misma dirección, hay alta similitud. Si van en direcciones opuestas (tú fast food, restaurante gourmet extremo), la similitud baja.

**En Savory:** compara el vector del usuario (normalizado 0–1) con el vector semántico del restaurante.

**Ejemplo humano:** si valoras mucho `casual`, `fast_food` y `comfort_food`, y el restaurante también tiene peso alto en esas dimensiones, la flecha coincide.

---

## 2. Weighted scoring (puntuación ponderada)

No todas las preferencias pesan igual para todos. Si el sistema detecta un **fast_food_user**, aumenta el peso de:

- `fast_food`, `comida_rapida`, `comfort_food`, `casual`

Y reduce el peso de:

- `premium`, `gourmet`, `exclusive`, `romantic`

**Analogía:** es como ajustar el volumen de ciertos instrumentos en una orquesta según el género musical que quieres escuchar.

---

## 3. Perfiles dominantes (user archetypes)

El sistema detecta automáticamente el “tipo principal” del usuario:


| Arquetipo        | Señales típicas                                |
| ---------------- | ---------------------------------------------- |
| `fast_food_user` | fast_food, comida_rapida, casual, comfort_food |
| `premium_user`   | premium, gourmet, exclusive, elegant           |
| `explorer_user`  | explorador, aventurero, trendy                 |
| `romantic_user`  | romantic, intimate, wine_focus                 |
| `social_user`    | social_grupo, lively, nightlife                |
| `comfort_user`   | comfort_food, family_friendly                  |
| `nightlife_user` | nightlife, craft_beer                          |
| `brunch_user`    | brunch, coffee_culture                         |


**Función clave:** `detect_user_archetype()`

**Ejemplo:** usuario con fast food alto → deja de castigar Burger King por “no ser premium”.

---

## 4. Perfiles conductuales (restaurant archetypes)

Cada restaurante tiene un **arquetipo semántico** definido en el catálogo:

- `fast_food`
- `italian_premium`
- `fusion_premium`
- `casual_dining`
- `steakhouse_premium`
- etc.

Estos arquetipos incluyen:

- Preferencias permitidas
- Preferencias **prohibidas** (ej.: fast food no puede ser `gourmet` + `romantic` alto)
- Scores de comportamiento (premium_score, comfort_score, etc.)

**Ejemplo:** Burger King = `fast_food`. Tre Fratelli = `italian_premium`. Mercado 24 = `fusion_premium`.

---

## 5. Recommendation context (puntuación contextual)

La compatibilidad final se divide en **tres capas**:

### Capa A — Base score

- Similitud ponderada entre preferencias
- Solapamiento de preferencias clave del arquetipo del usuario

### Capa B — Context score

- Bonus si el arquetipo del restaurante encaja con el del usuario (+ hasta ~22 puntos)
- Penalización si chocan (ej.: fast_food_user vs italian_premium)

### Capa C — Behavior score

- Alineación conductual: ¿el restaurante refuerza lo que el usuario busca y evita lo que no?

**Función central:** `compute_contextual_compatibility()`

**Resultado:** un porcentaje 0–100% más humano y defendible.

---

## 6. Dynamic preference weighting

Los pesos **no son fijos**. Cambian según:

1. Arquetipo dominante del usuario
2. Mood del día (opcional)
3. Preferencias activas (solo suben peso si el usuario realmente las tiene altas)

**Mood del día** (`mood_selector.py` + `apply_mood_boost()`):


| Mood      | Refuerza               |
| --------- | ---------------------- |
| Comfort   | comfort_food, casual   |
| Premium   | premium, gourmet       |
| Social    | social_grupo, lively   |
| Romántico | romantic, intimate     |
| Explorar  | explorador, aventurero |


El mood **no modifica** el perfil guardado en Neo4j; solo ajusta temporalmente la recomendación.

---

## 7. Explicabilidad (explainability)

Savory no solo dice “87% compatible”. Explica **por qué**:

- “Prefieres comida rápida y casual”
- “Disfrutas sabores americanos y comfort food”
- “Valoras la comodidad por encima de experiencias gourmet”

Además filtra tags incoherentes: Burger King no mostrará `#premium` ni `#gourmet`.

**Funciones:** `generar_explicacion()`, `validate_recommendation_semantics()`

---

## Ejemplo completo defendible

**Usuario:** ama fast food, americana, casual, carne, comfort food.

**Antes (motor ingenuo):** Burger King ~35% porque el sistema favorecía premium.

**Ahora (motor contextual):**

1. Detecta `fast_food_user`
2. Sube peso de fast food / casual / comfort
3. Baja peso de premium / gourmet
4. Burger King tiene arquetipo `fast_food`
5. Bonus de contexto + alta similitud base
6. **Resultado:** ~90–100% con explicación coherente

**Tre Fratelli** para ese mismo usuario baja correctamente, porque es `italian_premium`.

**Mercado 24** gana para un `explorer_user` con trendy y aventurero altos.

---

# Parte 5 — Por qué los restaurantes fake eran malos

## El problema

Los restaurantes ficticios o genéricos (`gt001`, datos inventados) generaban:

- Recomendaciones que **no existen en la vida real**
- Clasificaciones absurdas (Burger King con afinidad italiana)
- Cero confianza del usuario
- Imposibilidad de conectar con Google Maps o webs reales

## La solución

Se reemplazó el catálogo por **220 restaurantes reales** de Ciudad de Guatemala:

- Hacienda Real, Tre Fratelli, Kacao, Mercado 24, Saúl, Ambia, Tamarindos
- Cadenas reconocidas: Burger King, Wendy's, Chili's, Starbucks, etc.
- Distribuidos en Zona 10, 14, 15, 16, 11 y 5

## Coherencia semántica

Cada restaurante pasó por:

1. **Detección de arquetipo** según nombre, cocina, tipo, ambiente y precio
2. **Plantilla de preferencias** coherente con ese arquetipo
3. **Validación automática** (`validate_restaurant_catalog()`)

Reglas ejemplo:

- `fast_food` **prohibido:** gourmet, romantic, pref_italiana alto
- `italian_premium` **prohibido:** fast_food, street_food

## Corrección del caso Burger King

Antes: tags o prefs inconsistentes (italiano, premium).  
Ahora: arquetipo `fast_food`, prefs `fast_food`, `comida_rapida`, `casual`, `comfort_food`.

El motor dejó de castigar fast food y empezó a **premiar compatibilidad contextual**.

---

# Parte 6 — Restaurantes reales y links externos

## ¿Cómo se obtuvieron los restaurantes?

El catálogo (`restaurants_guatemala.py`) se construyó con:

- Conocimiento de la oferta gastronómica real de Ciudad de Guatemala
- Nombres, zonas, tipos de cocina, rangos de precio y descripciones representativas
- Clasificación semántica manual asistida por reglas automáticas

No es un scraper en tiempo real: es un **dataset curado** diseñado para ser estable, validable y coherente con el motor de recomendación.

## Información pública

Precios, ratings y descripciones son **referenciales** para el prototipo educativo. En un producto comercial se conectarían APIs de Google Places, TripAdvisor o datos propios del negocio.

## Links reales

Cada restaurante puede tener:


| Campo           | Uso                       |
| --------------- | ------------------------- |
| `website_url`   | Sitio oficial             |
| `instagram_url` | Perfil de Instagram       |
| `maps_url`      | Google Maps               |
| `facebook_url`  | Facebook                  |
| `search_url`    | Fallback: búsqueda Google |


Restaurantes destacados tienen URLs curadas (Tre Fratelli, Hacienda Real, Mercado 24, Burger King, etc.). El resto recibe al menos **Google Maps automático** por nombre + zona.

## Prioridad al abrir link

Implementada en `restaurant_links.py`:

1. Sitio web oficial
2. Instagram
3. Google Maps
4. Facebook
5. Búsqueda Google

## Interacción en la UI

- Clic en card, nombre o botón **Ver restaurante**
- Iconos 🌐 📍 📸 para web, Maps e Instagram
- Usa `webbrowser.open()` del sistema

---

# Parte 7 — Interfaz y experiencia de usuario

## Onboarding tipo app moderna

- 15 pasos con progreso visual
- Cards clickeables con emojis y grid responsive
- Avance automático al seleccionar
- Lenguaje cotidiano, no técnico

**Objetivo:** que crear el perfil se sienta como usar una app foodie, no llenar un formulario académico.

## Diseño premium foodie

Paleta cálida (rojos, naranjas, cremas), tipografía Segoe UI, cards con sombra suave, anillos de compatibilidad, barras de porcentaje con color semántico (verde = alta afinidad).

Definido en `styles.py`.

## Por qué importa la UX

Un motor perfecto con mala interfaz no genera confianza. Savory invierte en:

- **Hero emocional** — “Descubre tu próxima experiencia gastronómica”
- **Explicaciones legibles** — no “match_pref = 0.87”
- **Sin jerga de IA** — el usuario no necesita saber qué es cosine similarity
- **Acción real** — abrir el restaurante en el navegador

## Por qué se quitaron textos técnicos

Frases como “recomendación por IA” o “demo de grafo” alejan al usuario. Savory habla de **experiencias**, **mood**, **compatibilidad** y **descubrimiento**.

## Experiencia emocional

El **mood selector** pregunta “¿Qué mood tienes hoy?” antes de recomendar. Eso refleja cómo la gente realmente elige dónde comer: no solo por gustos permanentes, sino por el momento.

---

# Parte 8 — Explicación de cada archivo

## `database.py`


| Aspecto                   | Detalle                                                                                       |
| ------------------------- | --------------------------------------------------------------------------------------------- |
| **Qué hace**              | Conecta la aplicación con Neo4j AuraDB                                                        |
| **Problema que resuelve** | Centralizar credenciales, sesiones y manejo de errores de conexión                            |
| **Contiene**              | Carga de `.env`, clase `Neo4jConnection`, `get_session()`, validación de URI/usuario/password |
| **Clases**                | `Neo4jConnection`, `ConnectionError`                                                          |
| **Funciones clave**       | `load_environment()`, `read_neo4j_config()`, `get_connection()`, `get_session()`              |
| **Interacción**           | Usado por casi todos los módulos que leen o escriben datos                                    |
| **Por qué existe**        | Sin conexión fiable no hay grafo ni recomendaciones                                           |
| **Controla**              | Capa de persistencia — acceso a la base de datos                                              |


---

## `restaurants_guatemala.py`


| Aspecto                   | Detalle                                                                                     |
| ------------------------- | ------------------------------------------------------------------------------------------- |
| **Qué hace**              | Catálogo maestro de 220 restaurantes reales + semántica                                     |
| **Problema que resuelve** | Fuente de verdad para nombres, prefs, arquetipos y URLs                                     |
| **Contiene**              | `SEMANTIC_ARCHETYPES`, `build_catalog()`, validadores, links conocidos                      |
| **Funciones clave**       | `_detect_semantic_archetype()`, `build_restaurant_links()`, `validate_restaurant_catalog()` |
| **Interacción**           | Alimenta `restaurant_importer.py` y el índice usado por `recommendation.py`                 |
| **Por qué existe**        | Separar datos del catálogo de la lógica de recomendación                                    |
| **Controla**              | Identidad semántica de cada restaurante                                                     |


---

## `restaurant_importer.py`


| Aspecto                   | Detalle                                                                                          |
| ------------------------- | ------------------------------------------------------------------------------------------------ |
| **Qué hace**              | Importa el catálogo a Neo4j con MERGE por lotes                                                  |
| **Problema que resuelve** | Sincronizar Python → Neo4j sin duplicar ni perder visitas                                        |
| **Funciones clave**       | `import_guatemala_restaurants()`, `purge_legacy_restaurants()`, `_purge_restaurant_pref_edges()` |
| **Interacción**           | Lee `RESTAURANTS`, escribe nodos Restaurant, Zone, Cuisine, Preference y relaciones              |
| **Por qué existe**        | Neo4j debe reflejar el catálogo actualizado                                                      |
| **Controla**              | Población y actualización del grafo de restaurantes                                              |


---

## `restaurant_links.py`


| Aspecto                   | Detalle                                                                                      |
| ------------------------- | -------------------------------------------------------------------------------------------- |
| **Qué hace**              | Resuelve y abre URLs externas de restaurantes                                                |
| **Problema que resuelve** | Evitar import circular entre UI y recommendation                                             |
| **Funciones clave**       | `pick_primary_restaurant_url()`, `enrich_restaurant_links()`, `open_restaurant_in_browser()` |
| **Interacción**           | Usado por `recommendation.py` y `ui_widgets.py`                                              |
| **Controla**              | Navegación externa hacia restaurantes reales                                                 |


---

## `user_manager.py`


| Aspecto                   | Detalle                                                                                         |
| ------------------------- | ----------------------------------------------------------------------------------------------- |
| **Qué hace**              | CRUD de usuarios y persistencia del perfil gastronómico                                         |
| **Problema que resuelve** | Traducir onboarding → nodos y relaciones Neo4j                                                  |
| **Contiene**              | `PREFERENCE_CATALOG`, rangos de presupuesto                                                     |
| **Funciones clave**       | `guardar_perfil_gastronomico()`, `obtener_perfil_gastronomico()`, `ensure_preference_catalog()` |
| **Interacción**           | Onboarding → user_manager → Neo4j                                                               |
| **Controla**              | Identidad y perfil del usuario en el grafo                                                      |


---

## `onboarding.py`


| Aspecto                   | Detalle                                                  |
| ------------------------- | -------------------------------------------------------- |
| **Qué hace**              | Wizard de 15 pasos para construir el perfil              |
| **Problema que resuelve** | Capturar preferencias de forma guiada y amigable         |
| **Clases**                | `OnboardingWizard`                                       |
| **Funciones clave**       | `map_food_to_cuisines()`, `_sanitize_onboarding_steps()` |
| **Interacción**           | GUI lo embebe; al guardar llama a `user_manager`         |
| **Controla**              | Entrada principal de preferencias del usuario            |


---

## `recommendation.py`


| Aspecto                   | Detalle                                                                                                                                                    |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Qué hace**              | Motor de recomendaciones, scoring, explicaciones, consultas Cypher                                                                                         |
| **Problema que resuelve** | Calcular compatibilidad contextual y generar resultados defendibles                                                                                        |
| **Funciones clave**       | `recomendar_restaurantes_inteligente()`, `compute_contextual_compatibility()`, `detect_user_archetype()`, `generar_explicacion()`, `obtener_datos_grafo()` |
| **Interacción**           | Lee Neo4j + catálogo semántico; alimenta GUI, analytics y grafo                                                                                            |
| **Controla**              | Inteligencia central del sistema                                                                                                                           |


---

## `graph_view.py`


| Aspecto                   | Detalle                                                        |
| ------------------------- | -------------------------------------------------------------- |
| **Qué hace**              | Panel visual del grafo con NetworkX + Matplotlib               |
| **Problema que resuelve** | Hacer visible las conexiones usuario–restaurante–preferencias  |
| **Clases**                | `GraphPanel`                                                   |
| **Funciones clave**       | `render()`, `_subsample()` (limita nodos para rendimiento)     |
| **Interacción**           | Recibe datos de `obtener_datos_grafo()` en `recommendation.py` |
| **Controla**              | Visualización del grafo en la UI                               |


---

## `analytics_view.py`


| Aspecto             | Detalle                                                               |
| ------------------- | --------------------------------------------------------------------- |
| **Qué hace**        | Panel de insights: zona favorita, cocina top, heatmap de preferencias |
| **Clases**          | `AnalyticsPanel`                                                      |
| **Funciones clave** | `refresh()` usando `obtener_insights_usuario()`                       |
| **Controla**        | Analítica visual del perfil del usuario                               |


---

## `profile_visualizer.py`


| Aspecto      | Detalle                                                            |
| ------------ | ------------------------------------------------------------------ |
| **Qué hace** | Visualización del perfil gastronómico del usuario (radar/gráficos) |
| **Controla** | Representación gráfica de preferencias individuales                |


---

## `mood_selector.py`


| Aspecto      | Detalle                                                           |
| ------------ | ----------------------------------------------------------------- |
| **Qué hace** | Selector de mood del día (comfort, premium, social, etc.)         |
| **Clases**   | `MoodSelector`                                                    |
| **Controla** | Ajuste temporal de recomendaciones sin alterar el perfil guardado |


---

## `hero_banner.py`


| Aspecto      | Detalle                                              |
| ------------ | ---------------------------------------------------- |
| **Qué hace** | Banner principal de inicio con gradiente y CTAs      |
| **Clases**   | `HeroBanner`                                         |
| **Controla** | Primera impresión y acceso a crear perfil / explorar |


---

## `styles.py`


| Aspecto             | Detalle                                                       |
| ------------------- | ------------------------------------------------------------- |
| **Qué hace**        | Tema visual global: colores, fuentes, espaciados, estilos ttk |
| **Funciones clave** | `apply_theme()`, `compat_color()`                             |
| **Controla**        | Identidad visual coherente de Savory                          |


---

## `ui_widgets.py`


| Aspecto      | Detalle                                                                                                        |
| ------------ | -------------------------------------------------------------------------------------------------------------- |
| **Qué hace** | Componentes reutilizables de interfaz                                                                          |
| **Clases**   | `RestaurantCard`, `OnboardingOptionCard`, `ScrollableFrame`, `Sidebar`, `CompatRing`, `CompatibilityBar`, etc. |
| **Controla** | Cards de restaurantes interactivas, onboarding grid, layout reusable                                           |


---

## `ui_animations.py`


| Aspecto      | Detalle                                                    |
| ------------ | ---------------------------------------------------------- |
| **Qué hace** | Animaciones ligeras: fade in, hover glow, overlay de carga |
| **Controla** | Pulido visual y feedback al usuario                        |


---

## `gui.py`


| Aspecto                   | Detalle                                                          |
| ------------------------- | ---------------------------------------------------------------- |
| **Qué hace**              | Aplicación principal Tkinter — orquesta todo                     |
| **Clases**                | `RestaurantApp`                                                  |
| **Problema que resuelve** | Unificar pantallas, navegación, estado del usuario activo        |
| **Pantallas**             | Inicio, onboarding, recomendaciones, historial, grafo, analytics |
| **Interacción**           | Conecta todos los módulos anteriores                             |
| **Controla**              | Experiencia completa del usuario final                           |


---

## `main.py`


| Aspecto      | Detalle                                           |
| ------------ | ------------------------------------------------- |
| **Qué hace** | Menú de consola para pruebas sin interfaz gráfica |
| **Controla** | Modo alternativo de uso (terminal)                |


---

# Parte 9 — Puntos para defender oralmente

## Mensaje central (30 segundos)

> “Savory es un recomendador gastronómico para Ciudad de Guatemala que usa un grafo en Neo4j para modelar relaciones entre usuarios, preferencias y restaurantes reales. No busca el restaurante ‘mejor’ en abstracto, sino el más compatible con el perfil y el mood del usuario, con explicaciones claras y links para visitarlos.”

## Decisiones técnicas inteligentes

1. **Grafo en Neo4j** — porque las relaciones gastronómicas son el core del problema.
2. **Catálogo semántico local** — fuente de verdad para scoring; evita datos inconsistentes en Neo4j.
3. **Arquetipos de usuario y restaurante** — capturan contexto que un vector plano no explica.
4. **Pesos dinámicos** — el sistema se adapta al tipo de usuario, no impone premium universal.
5. **Onboarding acumulativo** — perfil rico sin pedir 100 sliders manualmente.
6. **Explicabilidad** — cada recomendación se puede justificar oralmente.
7. **Links reales** — convierte la app en herramienta de descubrimiento, no solo demo académica.

## Por qué no SQL tradicional

Porque el modelo mental es relacional en el sentido humano (conectado), no tabular. Las consultas de afinidad y usuarios similares son más naturales en Cypher.

## Por qué onboarding

Porque el cold start (“usuario nuevo sin historial”) se resuelve capturando preferencias conductuales desde el inicio.

## Por qué explainability

Porque un porcentaje sin contexto no genera confianza. En gastronomía, la decisión es emocional.

---

# Parte 10 — Posibles preguntas del profesor

### P: ¿Por qué Neo4j y no MySQL?

**R:** Porque Savory modela **relaciones con significado** (prefiere, visitó, coincide con, ubicado en). En Neo4j eso es nativo. En SQL requeriría muchas tablas puente y consultas largas difíciles de mantener para recomendaciones y visualización de grafo.

---

### P: ¿Cómo funciona cosine similarity en palabras simples?

**R:** Comparamos dos perfiles de preferencias como si fueran perfiles de intensidad. Si usuario y restaurante “apuntan” hacia los mismos gustos, la similitud es alta. Si el usuario busca fast food y el restaurante es fine dining premium, apuntan en direcciones distintas y la similitud baja.

---

### P: ¿Qué evita que Burger King salga mal recomendado?

**R:** Tres cosas: (1) clasificación semántica correcta como `fast_food`, (2) detección de arquetipo `fast_food_user`, (3) pesos dinámicos que priorizan comida rápida y reducen premium. Además hay bonus de contexto cuando arquetipos encajan.

---

### P: ¿El mood cambia el perfil permanentemente?

**R:** No. El mood aplica un boost temporal solo al momento de recomendar. El perfil en Neo4j permanece intacto.

---

### P: ¿De dónde salen los restaurantes?

**R:** De un catálogo curado en `restaurants_guatemala.py` con 220 establecimientos reales de Guatemala, validados semánticamente e importados a Neo4j.

---

### P: ¿Cómo validan coherencia semántica?

**R:** Con reglas por arquetipo: preferencias prohibidas, límites máximos y `validate_restaurant_catalog()` que detecta casos como fast food + gourmet.

---

### P: ¿Qué pasa si un restaurante no tiene página web?

**R:** Savory usa fallbacks: Instagram, Google Maps o búsqueda Google automática por nombre y zona.

---

### P: ¿Cómo encontrarían usuarios similares?

**R:** Mediante Cypher: usuarios que comparten cocinas (`LIKES_CUISINE`) y visitaron restaurantes que tú no has visitado. Eso alimenta un factor adicional en el score.

---

### P: ¿Cuál es la limitación principal del proyecto?

**R:** Es un prototipo educativo: ratings y precios son referenciales, no hay integración en tiempo real con APIs externas, y el scoring es heurístico semántico, no machine learning entrenado con millones de interacciones.

---

### P: ¿Qué mejorarían a futuro?

**R:** Integración con Google Places, aprendizaje de preferencias según visitas reales (`VISITED`), filtros por distancia GPS, y feedback explícito (“me gustó / no me gustó”).

---

# Parte 11 — Conclusión

## Qué logró Savory

- Transformó un ejercicio técnico en una **experiencia gastronómica creíble**
- Modeló usuarios y restaurantes como un **grafo explorable**
- Implementó un **motor de recomendación contextual** que corrige sesgos hacia lo premium
- Incorporó **220 restaurantes reales** de Ciudad de Guatemala
- Ofreció **explicaciones humanas**, visualización, analytics y **links accionables**

## Cómo evolucionó

De consola + datos fake → aplicación visual premium + grafo + onboarding + semántica + links reales.

## Qué lo hace diferente

No compite por “el algoritmo más complejo”, sino por **coherencia humana**: que la recomendación tenga sentido emocional y cultural para el usuario guatemalteco.

## Visión a futuro

Savory puede crecer hacia una plataforma completa de descubrimiento gastronómico: reservas, listas personalizadas, recomendaciones según hora del día, integración con redes sociales y aprendizaje continuo a partir de visitas reales.

---

## Comandos útiles para demostración

```powershell
cd restaurantes\project
python gui.py
```

Reimportar catálogo:

```powershell
python -c "from restaurant_importer import import_guatemala_restaurants; print(import_guatemala_restaurants())"
```

---

*Documento generado para estudio, exposición y defensa académica del proyecto Savory.*