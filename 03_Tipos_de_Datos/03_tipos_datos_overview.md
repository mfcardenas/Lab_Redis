# 📊 Módulo 3: Tipos de Datos en Redis - Visión General

*Autor: @mCárdenas 2025*

<div align="center">

![Redis Data Types](https://img.shields.io/badge/Redis-Data_Types-red?style=for-the-badge&logo=redis)

*"Redis no es solo key-value, es una navaja suiza de estructuras de datos"*

</div>

## 📋 Contenido de este módulo

1. [Visión General de los Tipos](#-visión-general-de-los-tipos)
2. [Strings](#-strings)
3. [Lists](#-lists)
4. [Sets](#-sets)
5. [Sorted Sets (ZSets)](#-sorted-sets-zsets)
6. [Hashes](#-hashes)
7. [Streams](#-streams)
8. [Bitmaps](#-bitmaps)
9. [HyperLogLog](#-hyperloglog)
10. [Geospatial](#-geospatial)
11. [JSON (RedisStack)](#-json-redisstack)
12. [Search (RedisStack)](#-search-redisstack)

## 🗺️ Visión General de los Tipos

Redis ofrece una rica variedad de estructuras de datos, cada una optimizada para casos de uso específicos:

```
┌─────────────────────────────────────────────────────────────────┐
│                   TIPOS DE DATOS EN REDIS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   STRINGS   │  │    LISTS    │  │    SETS     │              │
│  │  "Hola"     │  │ [a,b,c,d]   │  │ {a,b,c}     │              │
│  │  Básico     │  │  Ordenadas  │  │   Únicos    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ SORTED SETS │  │   HASHES    │  │   STREAMS   │              │
│  │ {a:1,b:2}   │  │ {k1:v1,...} │  │  [evento]→  │              │
│  │  Con score  │  │   Campos    │  │    Logs     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   BITMAPS   │  │ HYPERLOGLOG │  │ GEOSPATIAL  │              │
│  │  01100110   │  │   ~count    │  │  📍 lat/lng │              │
│  │    Bits     │  │ Aproximado  │  │ Geográfico  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                  │
│  ═══════════════ REDIS STACK MODULES ═══════════════           │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐                               │
│  │    JSON     │  │   SEARCH    │                               │
│  │ {"a":1,...} │  │  FT.SEARCH  │                               │
│  │ Documentos  │  │  Full-text  │                               │
│  └─────────────┘  └─────────────┘                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Tabla Comparativa

| Tipo            | Descripción                           | Complejidad                | Mejor Para                   |
| --------------- | ------------------------------------- | -------------------------- | ---------------------------- |
| **Strings**     | Valor simple (texto, número, binario) | O(1)                       | Caché, contadores, flags     |
| **Lists**       | Lista ordenada de strings             | O(1) push/pop, O(n) acceso | Colas, historial, logs       |
| **Sets**        | Conjunto de strings únicos            | O(1) add/remove            | Tags, relaciones, unicidad   |
| **Sorted Sets** | Set con score numérico                | O(log n)                   | Rankings, feeds, scheduling  |
| **Hashes**      | Mapa clave-valor                      | O(1) por campo             | Objetos, perfiles, entidades |
| **Streams**     | Log append-only                       | O(1) append                | Event sourcing, mensajería   |
| **Bitmaps**     | Operaciones a nivel de bits           | O(1)                       | Flags, presencia, estados    |
| **HyperLogLog** | Conteo probabilístico                 | O(1)                       | Conteo de únicos aproximado  |
| **Geospatial**  | Coordenadas geográficas               | O(log n)                   | Ubicaciones, proximidad      |
| **JSON**        | Documentos JSON nativos               | O(path)                    | APIs, documentos complejos   |
| **Search**      | Índices y búsqueda                    | O(n) query                 | Full-text, filtros           |

## 📝 Strings

El tipo más básico y versátil de Redis.

### ¿Qué puede almacenar?

- Texto: `"Hola mundo"`
- Números: `42`, `3.14`
- JSON serializado: `"{\"nombre\":\"Juan\"}"`
- Binarios: imágenes, archivos (hasta 512MB)

### Comandos Principales

| Comando  | Descripción         | Ejemplo                  |
| -------- | ------------------- | ------------------------ |
| `SET`    | Establecer valor    | `SET clave "valor"`      |
| `GET`    | Obtener valor       | `GET clave`              |
| `INCR`   | Incrementar (+1)    | `INCR contador`          |
| `INCRBY` | Incrementar por N   | `INCRBY contador 5`      |
| `DECR`   | Decrementar (-1)    | `DECR contador`          |
| `APPEND` | Añadir al final     | `APPEND clave " más"`    |
| `STRLEN` | Longitud del string | `STRLEN clave`           |
| `SETEX`  | Set con expiración  | `SETEX clave 60 "valor"` |
| `SETNX`  | Set si no existe    | `SETNX clave "valor"`    |
| `MSET`   | Set múltiple        | `MSET k1 v1 k2 v2`       |
| `MGET`   | Get múltiple        | `MGET k1 k2`             |

### Ejemplo en Shell

```bash
# Básico
SET nombre "María García"
GET nombre
# "María García"

# Con expiración (TTL)
SETEX sesion:123 3600 "datos_sesion"  # Expira en 1 hora
TTL sesion:123
# (integer) 3599

# Contadores
SET visitas 0
INCR visitas
INCR visitas
GET visitas
# "2"

# Múltiples operaciones
MSET usuario:1:nombre "Juan" usuario:1:email "juan@email.com"
MGET usuario:1:nombre usuario:1:email
# 1) "Juan"
# 2) "juan@email.com"
```

## 📋 Lists

Listas ordenadas de strings, implementadas como listas doblemente enlazadas.

### Características

- Orden de inserción preservado
- Acceso O(1) a cabeza y cola
- Pueden tener duplicados
- Máximo ~4 mil millones de elementos

### Comandos Principales

| Comando  | Descripción          | Ejemplo                    |
| -------- | -------------------- | -------------------------- |
| `LPUSH`  | Insertar al inicio   | `LPUSH lista "a"`          |
| `RPUSH`  | Insertar al final    | `RPUSH lista "z"`          |
| `LPOP`   | Extraer del inicio   | `LPOP lista`               |
| `RPOP`   | Extraer del final    | `RPOP lista`               |
| `LRANGE` | Obtener rango        | `LRANGE lista 0 -1`        |
| `LLEN`   | Longitud             | `LLEN lista`               |
| `LINDEX` | Elemento por índice  | `LINDEX lista 0`           |
| `LSET`   | Modificar por índice | `LSET lista 0 "nuevo"`     |
| `BRPOP`  | Pop bloqueante       | `BRPOP lista 30`           |
| `LMOVE`  | Mover entre listas   | `LMOVE src dst LEFT RIGHT` |

### Ejemplo en Shell

```bash
# Crear cola de tareas
RPUSH tareas "tarea1" "tarea2" "tarea3"
# (integer) 3

# Ver todas las tareas
LRANGE tareas 0 -1
# 1) "tarea1"
# 2) "tarea2"
# 3) "tarea3"

# Procesar tarea (FIFO)
LPOP tareas
# "tarea1"

# Añadir nueva tarea
RPUSH tareas "tarea4"

# Longitud de la cola
LLEN tareas
# (integer) 3
```

## 🔵 Sets

Conjuntos de strings únicos, sin orden.

### Características

- Elementos únicos (no duplicados)
- Sin orden garantizado
- Operaciones de conjuntos (unión, intersección, diferencia)
- Verificación de pertenencia O(1)

### Comandos Principales

| Comando       | Descripción         | Ejemplo             |
| ------------- | ------------------- | ------------------- |
| `SADD`        | Añadir elementos    | `SADD set "a" "b"`  |
| `SREM`        | Eliminar elementos  | `SREM set "a"`      |
| `SMEMBERS`    | Todos los elementos | `SMEMBERS set`      |
| `SISMEMBER`   | ¿Pertenece?         | `SISMEMBER set "a"` |
| `SCARD`       | Cardinalidad        | `SCARD set`         |
| `SINTER`      | Intersección        | `SINTER set1 set2`  |
| `SUNION`      | Unión               | `SUNION set1 set2`  |
| `SDIFF`       | Diferencia          | `SDIFF set1 set2`   |
| `SRANDMEMBER` | Elemento aleatorio  | `SRANDMEMBER set`   |
| `SPOP`        | Extraer aleatorio   | `SPOP set`          |

### Ejemplo en Shell

```bash
# Tags de productos
SADD producto:1:tags "electrónica" "oferta" "nuevo"
SADD producto:2:tags "electrónica" "premium"

# Ver tags de un producto
SMEMBERS producto:1:tags
# 1) "electrónica"
# 2) "oferta"
# 3) "nuevo"

# Tags en común
SINTER producto:1:tags producto:2:tags
# 1) "electrónica"

# ¿Tiene el tag "oferta"?
SISMEMBER producto:1:tags "oferta"
# (integer) 1  (true)
```

## 🏆 Sorted Sets (ZSets)

Sets con un score numérico asociado a cada elemento.

### Características

- Elementos únicos con score
- Ordenados por score (ascendente)
- Score puede ser flotante
- Ideal para rankings y ordenación

### Comandos Principales

| Comando         | Descripción       | Ejemplo                    |
| --------------- | ----------------- | -------------------------- |
| `ZADD`          | Añadir con score  | `ZADD zset 100 "a"`        |
| `ZREM`          | Eliminar          | `ZREM zset "a"`            |
| `ZSCORE`        | Obtener score     | `ZSCORE zset "a"`          |
| `ZRANK`         | Posición (asc)    | `ZRANK zset "a"`           |
| `ZREVRANK`      | Posición (desc)   | `ZREVRANK zset "a"`        |
| `ZRANGE`        | Por posición      | `ZRANGE zset 0 9`          |
| `ZRANGEBYSCORE` | Por score         | `ZRANGEBYSCORE zset 0 100` |
| `ZINCRBY`       | Incrementar score | `ZINCRBY zset 10 "a"`      |
| `ZCARD`         | Cardinalidad      | `ZCARD zset`               |
| `ZCOUNT`        | Contar por rango  | `ZCOUNT zset 0 100`        |

### Ejemplo en Shell

```bash
# Leaderboard de videojuego
ZADD leaderboard 1500 "player1" 2000 "player2" 1800 "player3"

# Top 3 (mayor a menor)
ZREVRANGE leaderboard 0 2 WITHSCORES
# 1) "player2"
# 2) "2000"
# 3) "player3"
# 4) "1800"
# 5) "player1"
# 6) "1500"

# Posición de un jugador (0-indexed)
ZREVRANK leaderboard "player1"
# (integer) 2  (tercer puesto)

# Actualizar puntuación
ZINCRBY leaderboard 600 "player1"
# "2100"

# Nuevo ranking
ZREVRANGE leaderboard 0 2 WITHSCORES
# 1) "player1"  ← ¡Ahora es #1!
# 2) "2100"
# ...
```

## 🗂️ Hashes

Mapas de campo-valor, ideales para representar objetos.

### Características

- Similar a un diccionario/objeto
- Cada hash puede tener millones de campos
- Más eficiente en memoria que strings JSON
- Operaciones individuales por campo

### Comandos Principales

| Comando   | Descripción       | Ejemplo                  |
| --------- | ----------------- | ------------------------ |
| `HSET`    | Establecer campo  | `HSET hash campo valor`  |
| `HGET`    | Obtener campo     | `HGET hash campo`        |
| `HMSET`   | Múltiples campos  | `HMSET hash c1 v1 c2 v2` |
| `HMGET`   | Múltiples gets    | `HMGET hash c1 c2`       |
| `HGETALL` | Todos los campos  | `HGETALL hash`           |
| `HDEL`    | Eliminar campo    | `HDEL hash campo`        |
| `HEXISTS` | ¿Existe campo?    | `HEXISTS hash campo`     |
| `HINCRBY` | Incrementar campo | `HINCRBY hash campo 1`   |
| `HKEYS`   | Todas las claves  | `HKEYS hash`             |
| `HVALS`   | Todos los valores | `HVALS hash`             |
| `HLEN`    | Número de campos  | `HLEN hash`              |

### Ejemplo en Shell

```bash
# Perfil de usuario
HSET usuario:1 nombre "Ana López" email "ana@email.com" edad 28

# Obtener un campo
HGET usuario:1 nombre
# "Ana López"

# Obtener todo el perfil
HGETALL usuario:1
# 1) "nombre"
# 2) "Ana López"
# 3) "email"
# 4) "ana@email.com"
# 5) "edad"
# 6) "28"

# Actualizar edad
HINCRBY usuario:1 edad 1
# (integer) 29

# Añadir campo
HSET usuario:1 ciudad "Madrid"
```

## 🌊 Streams

Estructura de datos tipo log, append-only, para event sourcing.

### Características

- Mensajes ordenados por tiempo
- ID único generado automáticamente
- Grupos de consumidores
- Persistente (no se pierden mensajes)

### Comandos Principales

| Comando         | Descripción       | Ejemplo                                 |
| --------------- | ----------------- | --------------------------------------- |
| `XADD`          | Añadir mensaje    | `XADD stream * campo valor`             |
| `XREAD`         | Leer mensajes     | `XREAD STREAMS stream 0`                |
| `XRANGE`        | Rango de mensajes | `XRANGE stream - +`                     |
| `XLEN`          | Longitud          | `XLEN stream`                           |
| `XGROUP CREATE` | Crear grupo       | `XGROUP CREATE stream grupo $ MKSTREAM` |
| `XREADGROUP`    | Leer con grupo    | `XREADGROUP GROUP grupo consumer ...`   |
| `XACK`          | Confirmar mensaje | `XACK stream grupo id`                  |

### Ejemplo en Shell

```bash
# Log de eventos
XADD eventos * tipo "login" usuario "user123" ip "192.168.1.1"
# "1702345678901-0"  (ID automático)

XADD eventos * tipo "compra" usuario "user123" producto "ABC"
# "1702345678902-0"

# Leer todos los eventos
XRANGE eventos - +
# 1) 1) "1702345678901-0"
#    2) 1) "tipo"
#       2) "login"
#       3) "usuario"
#       4) "user123"
#       5) "ip"
#       6) "192.168.1.1"
# 2) ...

# Longitud del stream
XLEN eventos
# (integer) 2
```

## 🔢 Bitmaps

Operaciones a nivel de bits sobre strings.

### Características

- Extremadamente eficiente en memoria
- Operaciones bit a bit
- Ideal para flags y estados booleanos
- 1 bit por estado = millones de estados en pocos MB

### Comandos Principales

| Comando    | Descripción             | Ejemplo                |
| ---------- | ----------------------- | ---------------------- |
| `SETBIT`   | Establecer bit          | `SETBIT key offset 1`  |
| `GETBIT`   | Obtener bit             | `GETBIT key offset`    |
| `BITCOUNT` | Contar bits en 1        | `BITCOUNT key`         |
| `BITOP`    | Operación lógica        | `BITOP AND dest k1 k2` |
| `BITPOS`   | Posición del primer 1/0 | `BITPOS key 1`         |

### Ejemplo en Shell

```bash
# Asistencia de usuarios (día 15 del mes)
# Usuario 100 asistió
SETBIT asistencia:2024:01 100 1

# Usuario 101 asistió
SETBIT asistencia:2024:01 101 1

# Usuario 102 NO asistió (por defecto es 0)

# ¿Asistió usuario 100?
GETBIT asistencia:2024:01 100
# (integer) 1

# ¿Cuántos asistieron?
BITCOUNT asistencia:2024:01
# (integer) 2
```

## 🎲 HyperLogLog

Estructura probabilística para contar elementos únicos.

### Características

- Error estándar < 1%
- Memoria fija: 12KB máximo
- Ideal para conteos aproximados de millones de elementos
- No almacena los elementos, solo el conteo

### Comandos Principales

| Comando   | Descripción     | Ejemplo                  |
| --------- | --------------- | ------------------------ |
| `PFADD`   | Añadir elemento | `PFADD hll "elem"`       |
| `PFCOUNT` | Contar únicos   | `PFCOUNT hll`            |
| `PFMERGE` | Unir HLLs       | `PFMERGE dest hll1 hll2` |

### Ejemplo en Shell

```bash
# Visitantes únicos por día
PFADD visitantes:2024:01:15 "user1" "user2" "user3"
# (integer) 1

PFADD visitantes:2024:01:15 "user1" "user4"  # user1 ya existe
# (integer) 1

# ¿Cuántos únicos?
PFCOUNT visitantes:2024:01:15
# (integer) 4  (aproximado)

# Unir varios días
PFMERGE visitantes:2024:01:semana1 visitantes:2024:01:15 visitantes:2024:01:16
```

## 📍 Geospatial

Almacenamiento y consulta de coordenadas geográficas.

### Características

- Basado internamente en Sorted Sets
- Consultas por radio
- Cálculo de distancias
- Ideal para ubicaciones y proximidad

### Comandos Principales

| Comando     | Descripción         | Ejemplo                       |
| ----------- | ------------------- | ----------------------------- |
| `GEOADD`    | Añadir ubicación    | `GEOADD key lng lat nombre`   |
| `GEOPOS`    | Obtener coordenadas | `GEOPOS key nombre`           |
| `GEODIST`   | Distancia entre 2   | `GEODIST key n1 n2 km`        |
| `GEORADIUS` | Buscar por radio    | `GEORADIUS key lng lat 10 km` |
| `GEOSEARCH` | Búsqueda flexible   | `GEOSEARCH key FROMMEMBER...` |

### Ejemplo en Shell

```bash
# Restaurantes en una ciudad
GEOADD restaurantes -3.7038 40.4168 "Restaurante Centro"
GEOADD restaurantes -3.6883 40.4530 "Restaurante Norte"
GEOADD restaurantes -3.7495 40.4633 "Restaurante Oeste"

# Distancia entre dos restaurantes
GEODIST restaurantes "Restaurante Centro" "Restaurante Norte" km
# "4.1234"

# Buscar restaurantes en radio de 5km desde el centro
GEOSEARCH restaurantes FROMMEMBER "Restaurante Centro" BYRADIUS 5 km WITHDIST
# 1) 1) "Restaurante Centro"
#    2) "0.0000"
# 2) 1) "Restaurante Norte"
#    2) "4.1234"
```

## 📄 JSON (RedisStack)

Almacenamiento nativo de documentos JSON.

### Características

- Acceso parcial a documentos
- Modificación de campos específicos
- Indexable con RediSearch
- Más flexible que Hashes para datos anidados

### Comandos Principales

| Comando          | Descripción        | Ejemplo                          |
| ---------------- | ------------------ | -------------------------------- |
| `JSON.SET`       | Establecer JSON    | `JSON.SET key $ '{"a":1}'`       |
| `JSON.GET`       | Obtener JSON/path  | `JSON.GET key $.a`               |
| `JSON.NUMINCRBY` | Incrementar número | `JSON.NUMINCRBY key $.a 1`       |
| `JSON.ARRAPPEND` | Añadir a array     | `JSON.ARRAPPEND key $.arr '"x"'` |
| `JSON.DEL`       | Eliminar path      | `JSON.DEL key $.a`               |

### Ejemplo en Shell

```bash
# Producto con estructura compleja
JSON.SET producto:1 $ '{"nombre":"Laptop","precio":999.99,"specs":{"ram":"16GB","cpu":"i7"},"tags":["electrónica","oferta"]}'

# Obtener todo
JSON.GET producto:1
# {"nombre":"Laptop","precio":999.99,...}

# Obtener solo el precio
JSON.GET producto:1 $.precio
# [999.99]

# Obtener specs.ram
JSON.GET producto:1 $.specs.ram
# ["16GB"]

# Actualizar precio
JSON.SET producto:1 $.precio 899.99

# Añadir tag
JSON.ARRAPPEND producto:1 $.tags '"nuevo"'
```

## 🔍 Search (RedisStack)

Motor de búsqueda full-text e índices secundarios.

### Características

- Búsqueda full-text
- Filtros numéricos y de texto
- Agregaciones
- Autocompletado
- Búsqueda geográfica

### Comandos Principales

| Comando        | Descripción         | Ejemplo                     |
| -------------- | ------------------- | --------------------------- |
| `FT.CREATE`    | Crear índice        | `FT.CREATE idx ON HASH ...` |
| `FT.SEARCH`    | Buscar              | `FT.SEARCH idx "query"`     |
| `FT.AGGREGATE` | Agregar             | `FT.AGGREGATE idx ...`      |
| `FT.SUGADD`    | Autocompletado      | `FT.SUGADD sug "texto" 1`   |
| `FT.SUGGET`    | Obtener sugerencias | `FT.SUGGET sug "tex"`       |

### Ejemplo en Shell

```bash
# Crear índice sobre productos (Hashes)
FT.CREATE idx:productos ON HASH PREFIX 1 producto: SCHEMA nombre TEXT SORTABLE precio NUMERIC SORTABLE categoria TAG

# Crear productos
HSET producto:1 nombre "Laptop Gaming" precio 1200 categoria "electrónica"
HSET producto:2 nombre "Laptop Oficina" precio 800 categoria "electrónica"
HSET producto:3 nombre "Silla Oficina" precio 200 categoria "muebles"

# Buscar por texto
FT.SEARCH idx:productos "Laptop"
# Devuelve producto:1 y producto:2

# Buscar con filtro
FT.SEARCH idx:productos "@categoria:{electrónica} @precio:[0 1000]"
# Devuelve producto:2 (Laptop Oficina, precio 800)
```

## 📊 Resumen: ¿Cuándo usar cada tipo?

| Necesidad               | Tipo Recomendado    |
| ----------------------- | ------------------- |
| Valor simple, contador  | **String**          |
| Cola FIFO/LIFO          | **List**            |
| Tags, relaciones únicas | **Set**             |
| Rankings, ordenación    | **Sorted Set**      |
| Objeto con campos       | **Hash** o **JSON** |
| Event sourcing, logs    | **Stream**          |
| Flags booleanos masivos | **Bitmap**          |
| Conteo aproximado único | **HyperLogLog**     |
| Ubicaciones, proximidad | **Geospatial**      |
| Documentos anidados     | **JSON**            |
| Búsqueda full-text      | **Search**          |

## ➡️ Práctica

Ahora que conoces la teoría, es momento de practicar:

[💻 Notebook: Tipos de Datos en Práctica](./03_tipos_datos.ipynb)


<div align="center">

**¡A programar!** 🚀

</div>
