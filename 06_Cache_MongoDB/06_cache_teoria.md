# 💾 Módulo 6: Redis como Caché con MongoDB

*Autor: @mCárdenas 2025*

## 📋 Contenido

1. [¿Por qué usar Caché?](#-por-qué-usar-caché)
2. [Patrones de Caché](#-patrones-de-caché)
3. [Arquitectura](#-arquitectura)
4. [Implementación](#-implementación)
5. [Invalidación de Caché](#-invalidación-de-caché)
6. [Métricas](#-métricas)

---

## 🤔 ¿Por qué usar Caché?

### El Problema

```
Usuario ──► API ──► MongoDB ──► Disco
                    ⏱️ 10-100ms
```

### La Solución

```
Usuario ──► API ──► Redis (caché) ──► Respuesta rápida
                    ⏱️ <1ms ✅
                    
                    ↓ (si no está en caché)
                    
                    MongoDB ──► Guardar en Redis ──► Respuesta
```

### Comparación de Latencias

| Fuente        | Latencia  | Operaciones/seg |
| ------------- | --------- | --------------- |
| Redis (RAM)   | ~0.1ms    | 100,000+        |
| MongoDB (SSD) | ~5-50ms   | 1,000-10,000    |
| MongoDB (HDD) | ~10-100ms | 100-1,000       |

---

## 🔄 Patrones de Caché

### 1. Cache-Aside (Lazy Loading)

El más común. La aplicación gestiona el caché manualmente.

```python
def obtener_producto(id):
    # 1. Buscar en caché
    producto = redis.get(f"producto:{id}")
    
    if producto:
        return producto  # Cache HIT
    
    # 2. Cache MISS: buscar en MongoDB
    producto = mongodb.productos.find_one({"_id": id})
    
    # 3. Guardar en caché
    redis.setex(f"producto:{id}", 3600, producto)
    
    return producto
```

**Ventajas:**
- Simple de implementar
- Solo cachea datos que se usan

**Desventajas:**
- Primera petición siempre lenta
- Datos pueden quedar desactualizados

---

### 2. Write-Through

Escribe en caché Y en base de datos simultáneamente.

```python
def guardar_producto(id, producto):
    # Escribir en MongoDB
    mongodb.productos.update_one({"_id": id}, producto)
    
    # Escribir en caché
    redis.setex(f"producto:{id}", 3600, producto)
```

**Ventajas:**
- Caché siempre actualizado
- Lecturas siempre rápidas

**Desventajas:**
- Escrituras más lentas
- Puede cachear datos que nunca se leen

---

### 3. Write-Behind (Write-Back)

Escribe primero en caché, luego en base de datos de forma asíncrona.

```python
def guardar_producto(id, producto):
    # Escribir en caché inmediatamente
    redis.setex(f"producto:{id}", 3600, producto)
    
    # Encolar para escritura en DB
    redis.lpush("cola:escrituras", json.dumps({"id": id, "data": producto}))

# Worker en background
def worker():
    while True:
        item = redis.brpop("cola:escrituras")
        mongodb.productos.update_one(...)
```

**Ventajas:**
- Escrituras muy rápidas
- Reduce carga en DB

**Desventajas:**
- Riesgo de pérdida de datos
- Más complejo

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                        ARQUITECTURA                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────┐                                                  │
│   │ Cliente  │                                                  │
│   └────┬─────┘                                                  │
│        │                                                        │
│        ▼                                                        │
│   ┌──────────┐     ┌─────────┐                                 │
│   │   API    │────►│  Redis  │ ◄── Cache HIT (rápido)          │
│   │  Flask   │     │  Cache  │                                 │
│   └────┬─────┘     └────┬────┘                                 │
│        │                │                                       │
│        │           Cache MISS                                   │
│        │                │                                       │
│        ▼                ▼                                       │
│   ┌─────────────────────────┐                                  │
│   │        MongoDB          │ ◄── Base de datos principal      │
│   └─────────────────────────┘                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementación

Ver los archivos:
- [app.py](./app.py) - Aplicación Flask con caché
- [models.py](./models.py) - Modelos y conexiones
- [06_cache_demo.ipynb](./06_cache_demo.ipynb) - Demo interactiva

### Estructura de la Mini-Aplicación

```
06_Cache_MongoDB/
├── app.py          # API REST con Flask
├── models.py       # Conexión a MongoDB y Redis
└── 06_cache_demo.ipynb  # Demo y pruebas
```

---

## 🗑️ Invalidación de Caché

> "Solo hay dos problemas difíciles en informática: invalidación de caché y nombrar cosas."
> — Phil Karlton

### Estrategias

#### 1. TTL (Time To Live)
```python
redis.setex("producto:123", 3600, datos)  # Expira en 1 hora
```

#### 2. Invalidación Manual
```python
def actualizar_producto(id, datos):
    mongodb.update(id, datos)
    redis.delete(f"producto:{id}")  # Invalidar caché
```

#### 3. Pub/Sub para Invalidación
```python
# Al actualizar
redis.publish("cache:invalidar", f"producto:{id}")

# Servidores escuchan
for mensaje in pubsub.listen():
    redis.delete(mensaje['data'])
```

---

## 📊 Métricas

### Cache Hit Ratio

```python
hits = redis.get("stats:cache:hits")
misses = redis.get("stats:cache:misses")
ratio = hits / (hits + misses) * 100
print(f"Hit ratio: {ratio}%")
```

### Métricas Importantes

| Métrica        | Descripción                          | Objetivo |
| -------------- | ------------------------------------ | -------- |
| Hit Ratio      | % de peticiones servidas desde caché | > 80%    |
| Miss Ratio     | % de peticiones que van a DB         | < 20%    |
| Latencia media | Tiempo de respuesta                  | < 10ms   |
| Memoria usada  | RAM consumida por caché              | < límite |

---

## ⚠️ Consideraciones

### ¿Qué cachear?

✅ **Cachear:**
- Datos que se leen frecuentemente
- Datos que cambian poco
- Resultados de consultas costosas
- Datos de configuración

❌ **No cachear:**
- Datos que cambian constantemente
- Datos sensibles/personales
- Datos de tamaño muy grande
- Datos únicos por request

### TTL Recomendados

| Tipo de Dato          | TTL Sugerido        |
| --------------------- | ------------------- |
| Sesiones              | 30 min - 24 horas   |
| Datos de usuario      | 5 - 60 minutos      |
| Catálogo de productos | 1 - 24 horas        |
| Configuración         | 5 - 60 minutos      |
| Datos estáticos       | 24 horas - 1 semana |
