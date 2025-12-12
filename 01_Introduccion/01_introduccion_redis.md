# 📚 Módulo 1: Introducción a Redis

*Autor: @mCárdenas 2025*

<div align="center">

![Redis](https://redis.io/images/redis-white.png)

*"Redis es como tener una memoria fotográfica para tu aplicación"*

</div>


## 📋 Contenido de este módulo

1. [¿Qué es Redis?](#-qué-es-redis)
2. [Historia y Evolución](#-historia-y-evolución)
3. [Arquitectura de Redis](#-arquitectura-de-redis)
4. [Redis vs Otras Bases de Datos](#-redis-vs-otras-bases-de-datos)
5. [Redis vs Redis Stack](#-redis-vs-redis-stack)
6. [Casos de Uso Generales](#-casos-de-uso-generales)
7. [Cuándo Usar y Cuándo NO Usar Redis](#-cuándo-usar-y-cuándo-no-usar-redis)



## 🤔 ¿Qué es Redis?

**Redis** (Remote Dictionary Server) es una base de datos **en memoria** de código abierto que se utiliza como:

- 🗄️ **Base de datos**: Almacenamiento de datos persistente
- 💾 **Caché**: Almacenamiento temporal de alta velocidad
- 📨 **Message Broker**: Sistema de mensajería pub/sub
- 📊 **Motor de streaming**: Procesamiento de datos en tiempo real

### Características Principales

| Característica                 | Descripción                                                                        |
| ------------------------------ | ---------------------------------------------------------------------------------- |
| **In-Memory**                  | Todos los datos se almacenan en RAM, lo que proporciona latencias de microsegundos |
| **Estructuras de datos ricas** | Soporta strings, listas, sets, hashes, streams y más                               |
| **Persistencia opcional**      | Puede guardar datos en disco (RDB/AOF)                                             |
| **Replicación**                | Arquitectura maestro-réplica para alta disponibilidad                              |
| **Clustering**                 | Distribución automática de datos entre nodos                                       |
| **Lua Scripting**              | Ejecución de scripts atómicos en el servidor                                       |
| **Pub/Sub**                    | Sistema de mensajería publicador/suscriptor                                        |

### ¿Por qué "In-Memory"?

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPARACIÓN DE LATENCIAS                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  RAM (Redis)      ████  ~100 nanosegundos                       │
│                                                                  │
│  SSD              ████████████████  ~100 microsegundos          │
│                                                                  │
│  HDD              ████████████████████████████  ~10 milisegundos│
│                                                                  │
│  Red (DB remota)  ████████████████████████████████  ~100+ ms    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

> 💡 **Dato clave**: Redis puede procesar **más de 100,000 operaciones por segundo** en un solo núcleo.


## 📜 Historia y Evolución

### Línea del Tiempo

```
2009 ─────► Salvatore Sanfilippo (antirez) crea Redis en Italia
            Necesitaba mejorar el rendimiento de su startup LLOOGG

2010 ─────► VMware patrocina el desarrollo de Redis
            Primera versión estable (1.0)

2013 ─────► Pivotal toma el patrocinio
            Redis 2.6 introduce Lua scripting

2015 ─────► Redis Labs (ahora Redis Inc.) se convierte en el patrocinador principal
            Redis 3.0 introduce Redis Cluster

2018 ─────► Redis 5.0 introduce Streams
            Nuevo tipo de dato para event sourcing

2020 ─────► Redis 6.0 introduce ACLs y SSL/TLS
            Mejoras de seguridad significativas

2022 ─────► Redis 7.0 con funciones serverless
            Redis Stack se lanza oficialmente

2024 ─────► Redis cambia a licencia dual (RSALv2/SSPL)
            Continúa siendo open source con restricciones comerciales
```

### El Creador: Salvatore Sanfilippo

Conocido como **antirez**, es un programador italiano que creó Redis para resolver problemas de rendimiento en su startup de análisis web. Su filosofía de diseño:

> *"Simplicidad es la complejidad resuelta"*

## 🏗️ Arquitectura de Redis

### Modelo Single-Threaded

```
┌─────────────────────────────────────────────────────────────┐
│                     ARQUITECTURA REDIS                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   Cliente 1 ──┐                                              │
│               │      ┌─────────────────┐                    │
│   Cliente 2 ──┼─────►│   Event Loop    │◄────► RAM          │
│               │      │  (Single Thread) │                    │
│   Cliente 3 ──┘      └─────────────────┘                    │
│                              │                               │
│                              ▼                               │
│                      ┌───────────────┐                       │
│                      │ Disco (RDB/AOF)│                      │
│                      │  (Persistencia)│                      │
│                      └───────────────┘                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### ¿Por qué Single-Threaded?

| Ventaja          | Explicación                                     |
| ---------------- | ----------------------------------------------- |
| **Sin bloqueos** | No hay contención por recursos compartidos      |
| **Simplicidad**  | Código más simple y menos bugs                  |
| **Atomicidad**   | Cada comando es atómico por naturaleza          |
| **Predecible**   | Comportamiento consistente y fácil de debuggear |

> ⚠️ **Nota**: A partir de Redis 6.0, algunas operaciones de I/O se ejecutan en threads separados, pero el procesamiento de comandos sigue siendo single-threaded.

### Modelo de Memoria

```
┌─────────────────────────────────────────────────────────────┐
│                      MEMORIA REDIS                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    KEYSPACE                          │    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐             │    │
│  │  │ DB 0    │  │ DB 1    │  │ DB 15   │  (16 DBs)   │    │
│  │  ├─────────┤  ├─────────┤  ├─────────┤             │    │
│  │  │ key1:val│  │ key1:val│  │ key1:val│             │    │
│  │  │ key2:val│  │ key2:val│  │ key2:val│             │    │
│  │  │ ...     │  │ ...     │  │ ...     │             │    │
│  │  └─────────┘  └─────────┘  └─────────┘             │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              METADATOS Y ESTRUCTURAS                 │    │
│  │  • Expiraciones (TTL)                                │    │
│  │  • Información de replicación                        │    │
│  │  • Estadísticas                                      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Redis vs Otras Bases de Datos

### Comparación General

| Característica     | Redis       | MongoDB    | PostgreSQL    | Memcached    |
| ------------------ | ----------- | ---------- | ------------- | ------------ |
| **Tipo**           | Key-Value + | Documentos | Relacional    | Key-Value    |
| **Almacenamiento** | RAM         | Disco      | Disco         | RAM          |
| **Persistencia**   | Opcional    | Sí         | Sí            | No           |
| **Estructuras**    | Múltiples   | JSON/BSON  | Tablas        | Solo strings |
| **Transacciones**  | Básicas     | Sí         | ACID completo | No           |
| **Velocidad**      | ⚡⚡⚡⚡⚡       | ⚡⚡⚡        | ⚡⚡            | ⚡⚡⚡⚡⚡        |
| **Consultas**      | Por clave   | Flexibles  | SQL completo  | Por clave    |

### ¿Cuándo elegir cada uno?

```
Redis       → Caché, sesiones, colas, tiempo real, leaderboards
MongoDB     → Documentos flexibles, catálogos, CMS
PostgreSQL  → Transacciones ACID, datos relacionales complejos
Memcached   → Caché simple, sin persistencia necesaria
```

## 🧩 Redis vs Redis Stack

### Redis "Core" (OSS)

La versión básica de Redis incluye:
- Todos los tipos de datos básicos (strings, lists, sets, hashes, etc.)
- Pub/Sub
- Lua scripting
- Clustering y replicación
- Persistencia RDB/AOF

### Redis Stack

Redis Stack añade **módulos adicionales** que extienden las capacidades:

| Módulo              | Funcionalidad                            | Casos de Uso                    |
| ------------------- | ---------------------------------------- | ------------------------------- |
| **RedisJSON**       | Almacenamiento nativo de JSON            | APIs REST, documentos anidados  |
| **RediSearch**      | Búsqueda full-text e índices secundarios | Buscadores, autocompletado      |
| **RedisGraph**      | Base de datos de grafos                  | Redes sociales, recomendaciones |
| **RedisTimeSeries** | Series temporales                        | IoT, métricas, monitoreo        |
| **RedisBloom**      | Estructuras probabilísticas              | Filtros de spam, deduplicación  |

```
┌─────────────────────────────────────────────────────────────┐
│                       REDIS STACK                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                    REDIS CORE                        │    │
│  │  Strings │ Lists │ Sets │ Hashes │ Streams │ ...    │    │
│  └─────────────────────────────────────────────────────┘    │
│                           +                                  │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐   │
│  │ RedisJSON │ │RediSearch │ │RedisGraph │ │TimeSeries │   │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘   │
│                           +                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                   REDIS INSIGHT                      │    │
│  │            (Interfaz gráfica de administración)      │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

> 💡 **En este taller usaremos Redis Stack** para aprovechar todas las funcionalidades, especialmente RedisJSON y RediSearch.

## 💼 Casos de Uso Generales

### 1. 💾 Caché de Aplicación

```
Usuario ──► Aplicación ──► ¿Está en Redis? ──► Sí ──► Respuesta rápida
                                │
                                └──► No ──► Consultar DB ──► Guardar en Redis
```

**Ejemplos**: Resultados de consultas SQL, respuestas de APIs, páginas renderizadas.

### 2. 🎮 Sesiones de Usuario

```python
# Almacenar sesión con expiración automática
SET session:user123 "{user_data}" EX 3600  # Expira en 1 hora
```

**Ventajas**: Compartir sesiones entre servidores, expiración automática.

### 3. 🏆 Leaderboards y Rankings

```python
# Añadir puntuación
ZADD leaderboard 1500 "player1"
ZADD leaderboard 2000 "player2"

# Top 10 jugadores
ZREVRANGE leaderboard 0 9 WITHSCORES
```

### 4. 📊 Rate Limiting

```python
# Limitar a 100 requests por minuto
INCR rate:user123
EXPIRE rate:user123 60

# Verificar límite
if GET rate:user123 > 100:
    return "Too Many Requests"
```

### 5. 📨 Colas de Mensajes

```python
# Productor
LPUSH queue:emails "email_data"

# Consumidor
BRPOP queue:emails 0  # Espera bloqueante
```

### 6. 🔔 Notificaciones en Tiempo Real

```python
# Publicar notificación
PUBLISH notifications:user123 "Nuevo mensaje"

# Suscribirse
SUBSCRIBE notifications:user123
```

## ⚖️ Cuándo Usar y Cuándo NO Usar Redis

### ✅ USA Redis cuando necesites:

| Escenario                             | Por qué Redis                      |
| ------------------------------------- | ---------------------------------- |
| **Baja latencia**                     | Operaciones en microsegundos       |
| **Alto throughput**                   | 100K+ ops/segundo                  |
| **Datos temporales**                  | TTL nativo para expiración         |
| **Estructuras de datos complejas**    | Sets, sorted sets, streams nativos |
| **Compartir estado entre servidores** | Almacenamiento centralizado        |
| **Datos que caben en memoria**        | Optimizado para RAM                |

### ❌ NO uses Redis cuando:

| Escenario                                  | Alternativa                  |
| ------------------------------------------ | ---------------------------- |
| **Datos más grandes que la RAM**           | MongoDB, PostgreSQL          |
| **Consultas SQL complejas**                | PostgreSQL, MySQL            |
| **Transacciones ACID estrictas**           | PostgreSQL                   |
| **Almacenamiento a largo plazo sin caché** | Bases de datos tradicionales |
| **Datos altamente relacionales**           | Bases de datos relacionales  |
| **Presupuesto limitado para RAM**          | Bases de datos en disco      |

### 🎯 Regla de Oro

> *"Usa Redis como complemento, no como reemplazo de tu base de datos principal"*
>
> La combinación más común es: **Redis + MongoDB** o **Redis + PostgreSQL**

## 📊 Resumen del Módulo

| Concepto         | Valor Clave                                              |
| ---------------- | -------------------------------------------------------- |
| **¿Qué es?**     | Base de datos in-memory, key-value con estructuras ricas |
| **Velocidad**    | ~100,000 ops/segundo, latencia en microsegundos          |
| **Arquitectura** | Single-threaded, event loop, opcional persistencia       |
| **Redis Stack**  | Redis + módulos (JSON, Search, Graph, TimeSeries)        |
| **Mejor uso**    | Caché, sesiones, colas, tiempo real, leaderboards        |

## ➡️ Siguiente Módulo

[📦 Módulo 2: Instalación con RedisStack](../02_Instalacion/02_instalacion_redisstack.md)

<div align="center">

**¿Preguntas sobre los conceptos?** 🤔

</div>
