# 🗃️ Módulo 7: Modelado de Datos en Redis

*Autor: @mCárdenas 2025*

## 📋 Contenido

1. [Diferencias con Bases de Datos Relacionales](#-diferencias-con-bases-de-datos-relacionales)
2. [Convenciones de Nombrado de Claves](#-convenciones-de-nombrado-de-claves)
3. [Patrones de Diseño](#-patrones-de-diseño)
4. [Ejemplo Práctico: Blog](#-ejemplo-práctico-blog)
5. [Ejemplo Práctico: E-commerce](#-ejemplo-práctico-e-commerce)
6. [Hashes vs JSON](#-hashes-vs-json)

## 🔄 Diferencias con Bases de Datos Relacionales

### SQL vs Redis

| Aspecto       | SQL                     | Redis                          |
| ------------- | ----------------------- | ------------------------------ |
| Esquema       | Rígido, tablas          | Flexible, sin esquema          |
| Relaciones    | JOINs                   | Desnormalización o referencias |
| Índices       | Secundarios automáticos | Manuales (Sets/Sorted Sets)    |
| Consultas     | SQL complejo            | Por clave o índice manual      |
| Transacciones | ACID completo           | Básicas (MULTI/EXEC)           |

### Mentalidad de Redis

```
❌ SQL: "¿Cómo estructuro las tablas?"
✅ Redis: "¿Cómo voy a acceder a los datos?"
```

**Diseña pensando en las consultas**, no en la normalización.

## 🏷️ Convenciones de Nombrado de Claves

### Formato Recomendado

```
tipo:id:subcampo
```

### Ejemplos

| Clave                | Descripción               |
| -------------------- | ------------------------- |
| `user:1234`          | Usuario con ID 1234       |
| `user:1234:posts`    | Posts del usuario 1234    |
| `post:5678`          | Post con ID 5678          |
| `post:5678:comments` | Comentarios del post 5678 |
| `session:abc123`     | Sesión con token abc123   |
| `cache:producto:99`  | Caché del producto 99     |

### Reglas de Nombrado

| Regla                 | Bueno ✅               | Malo ❌                |
| --------------------- | --------------------- | --------------------- |
| Usar separadores      | `user:123:email`      | `user_123_email`      |
| Prefijos descriptivos | `cart:user:123`       | `c:u:123`             |
| Sin espacios          | `producto:laptop-pro` | `producto:laptop pro` |
| Minúsculas            | `user:profile`        | `User:Profile`        |
| IDs numéricos         | `order:12345`         | `order:pedido-nuevo`  |

### Jerarquía de Claves

```
┌─────────────────────────────────────────────────────────────┐
│                    JERARQUÍA DE CLAVES                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  user:1000                    → Hash (datos del usuario)    │
│  user:1000:followers          → Set (IDs de seguidores)     │
│  user:1000:following          → Set (IDs que sigue)         │
│  user:1000:posts              → List (IDs de posts)         │
│  user:1000:notifications      → List (notificaciones)       │
│  user:1000:settings           → Hash (configuración)        │
│                                                              │
│  post:5000                    → Hash (datos del post)       │
│  post:5000:likes              → Set (IDs que dieron like)   │
│  post:5000:comments           → List (IDs de comentarios)   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🎨 Patrones de Diseño

### 1. Desnormalización

En lugar de JOINs, duplicar datos para acceso rápido.

```python
# SQL: JOIN users, posts
# Redis: Incluir datos del autor en el post

HSET post:100 \
    id 100 \
    titulo "Mi primer post" \
    contenido "Hola mundo..." \
    autor_id 1 \
    autor_nombre "Juan García" \    # Dato duplicado
    autor_avatar "/img/juan.jpg"    # Dato duplicado
```

**Cuándo usar:**
- Datos que rara vez cambian (nombre, avatar)
- Lecturas mucho más frecuentes que escrituras

### 2. Referencias (IDs)

Almacenar solo IDs y resolver en la aplicación.

```python
# Post solo tiene autor_id
HSET post:100 titulo "Mi post" autor_id 1

# Resolver en la app
autor_id = HGET post:100 autor_id
autor = HGETALL user:{autor_id}
```

**Cuándo usar:**
- Datos que cambian frecuentemente
- Necesitas siempre datos actualizados

### 3. Índices Secundarios con Sets

Crear índices manuales para búsquedas.

```python
# Productos por categoría
SADD categoria:electronica producto:1 producto:2 producto:5

# Productos por precio (Sorted Set)
ZADD productos:por_precio 999.99 producto:1
ZADD productos:por_precio 499.99 producto:2

# Buscar productos de electrónica ordenados por precio
ids = SMEMBERS categoria:electronica
# Luego ordenar con ZRANGEBYSCORE o en la app
```

### 4. Listas para Ordenación Temporal

```python
# Timeline de un usuario (posts recientes primero)
LPUSH user:1:timeline post:100
LPUSH user:1:timeline post:101

# Obtener últimos 10
LRANGE user:1:timeline 0 9

# Mantener solo últimos 100
LTRIM user:1:timeline 0 99
```

## 📝 Ejemplo Práctico: Blog

### Modelo de Datos

```
┌─────────────────────────────────────────────────────────────┐
│                     MODELO: BLOG                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  USUARIOS                                                    │
│  ─────────                                                   │
│  user:{id}              → Hash  {nombre, email, bio}        │
│  user:{id}:posts        → List  [post_ids]                  │
│  user:{id}:followers    → Set   {user_ids}                  │
│  users:by_email         → Hash  {email → user_id}           │
│                                                              │
│  POSTS                                                       │
│  ─────                                                       │
│  post:{id}              → Hash  {titulo, contenido, autor}  │
│  post:{id}:likes        → Set   {user_ids}                  │
│  post:{id}:tags         → Set   {tags}                      │
│  posts:recientes        → List  [post_ids]                  │
│  posts:por_fecha        → ZSet  {post_id: timestamp}        │
│                                                              │
│  TAGS                                                        │
│  ────                                                        │
│  tag:{nombre}:posts     → Set   {post_ids}                  │
│                                                              │
│  COMENTARIOS                                                 │
│  ───────────                                                 │
│  comment:{id}           → Hash  {contenido, autor, post}    │
│  post:{id}:comments     → List  [comment_ids]               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Operaciones Comunes

```python
# Crear usuario
HSET user:1 nombre "Ana" email "ana@email.com"
HSET users:by_email ana@email.com 1

# Crear post
HSET post:100 titulo "Hola" contenido "..." autor_id 1
LPUSH user:1:posts 100
LPUSH posts:recientes 100
ZADD posts:por_fecha {timestamp} 100

# Añadir tags
SADD post:100:tags python redis tutorial
SADD tag:python:posts 100
SADD tag:redis:posts 100

# Dar like
SADD post:100:likes 2  # user:2 da like

# Obtener número de likes
SCARD post:100:likes

# Posts con tag "python"
SMEMBERS tag:python:posts
```

## 🛒 Ejemplo Práctico: E-commerce

### Modelo de Datos

```
┌─────────────────────────────────────────────────────────────┐
│                   MODELO: E-COMMERCE                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PRODUCTOS                                                   │
│  ─────────                                                   │
│  producto:{id}           → Hash/JSON {nombre, precio, ...}  │
│  producto:{id}:stock     → String (contador)                │
│  productos:categoria:{c} → Set {producto_ids}               │
│  productos:por_precio    → ZSet {producto_id: precio}       │
│  productos:por_ventas    → ZSet {producto_id: ventas}       │
│                                                              │
│  CARRITO                                                     │
│  ───────                                                     │
│  cart:{user_id}          → Hash {producto_id: cantidad}     │
│                                                              │
│  PEDIDOS                                                     │
│  ───────                                                     │
│  order:{id}              → Hash {estado, total, fecha}      │
│  order:{id}:items        → List [item JSON strings]         │
│  user:{id}:orders        → List [order_ids]                 │
│                                                              │
│  INVENTARIO                                                  │
│  ──────────                                                  │
│  stock:{producto_id}     → String (cantidad)                │
│  stock:bajo              → Set {producto_ids con stock < N} │
│                                                              │
│  SESIONES                                                    │
│  ────────                                                    │
│  session:{token}         → Hash {user_id, expira, ...}      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Operaciones Comunes

```python
# Añadir al carrito
HINCRBY cart:user123 producto:456 1

# Ver carrito
HGETALL cart:user123

# Decrementar stock (atómico)
nuevo_stock = DECRBY stock:producto:456 1
if nuevo_stock < 10:
    SADD stock:bajo producto:456

# Productos más vendidos
ZREVRANGE productos:por_ventas 0 9 WITHSCORES

# Buscar por rango de precio
ZRANGEBYSCORE productos:por_precio 100 500
```

## 🆚 Hashes vs JSON

### ¿Cuándo usar cada uno?

| Aspecto        | Hash            | JSON           |
| -------------- | --------------- | -------------- |
| Anidación      | ❌ Plano         | ✅ Ilimitada    |
| Acceso parcial | ✅ HGET campo    | ✅ $.path       |
| Memoria        | ⚡ Más eficiente | 📦 Más overhead |
| Índices        | Manual          | RediSearch     |
| Disponibilidad | Redis core      | RedisStack     |

### Ejemplo: Producto

**Con Hash (plano):**
```python
HSET producto:1 \
    nombre "Laptop" \
    precio 999.99 \
    stock 50 \
    categoria "electronica" \
    spec_cpu "i7" \
    spec_ram "16GB"  # Prefijo para "anidar"
```

**Con JSON (anidado):**
```python
JSON.SET producto:1 $ '{
    "nombre": "Laptop",
    "precio": 999.99,
    "stock": 50,
    "categoria": "electronica",
    "specs": {
        "cpu": "i7",
        "ram": "16GB"
    },
    "imagenes": ["img1.jpg", "img2.jpg"]
}'

# Acceso parcial
JSON.GET producto:1 $.specs.cpu
```

### Recomendación

- **Hash**: Datos simples sin anidación profunda
- **JSON**: Datos complejos, anidados, APIs REST

## 📊 Resumen

| Patrón            | Uso                                 |
| ----------------- | ----------------------------------- |
| Desnormalización  | Datos que no cambian frecuentemente |
| Referencias       | Datos que cambian mucho             |
| Sets como índices | Búsquedas por categoría/tag         |
| Sorted Sets       | Rankings, ordenación                |
| Listas            | Históricos, timelines               |

**Recuerda**: 
> Diseña para las consultas, no para la normalización.
