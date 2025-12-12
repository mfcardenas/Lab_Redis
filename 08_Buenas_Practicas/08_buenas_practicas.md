# ✅ Módulo 8: Buenas Prácticas y Recomendaciones

*Autor: @mCárdenas 2025*

## 📋 Contenido

1. [Qué Hacer (DO)](#-qué-hacer-do)
2. [Qué NO Hacer (DON'T)](#-qué-no-hacer-dont)
3. [Seguridad](#-seguridad)
4. [Rendimiento](#-rendimiento)
5. [Monitoreo](#-monitoreo)
6. [Producción](#-producción)

---

## ✅ Qué Hacer (DO)

### 1. Usar TTL para Datos Temporales

```python
# ✅ BIEN: Sesiones con expiración
SETEX session:abc123 3600 "datos_sesion"  # 1 hora

# ✅ BIEN: Caché con TTL
SETEX cache:producto:123 1800 "{...}"  # 30 minutos
```

**Beneficios:**
- Limpieza automática de memoria
- Datos siempre frescos
- Sin acumulación de basura

---

### 2. Convenciones de Nombrado Consistentes

```python
# ✅ BIEN: Formato consistente tipo:id:subcampo
user:1234
user:1234:posts
user:1234:settings
post:5678
post:5678:likes

# ❌ MAL: Inconsistente
User_1234
1234_user
posts-user-1234
```

---

### 3. Usar SCAN en Lugar de KEYS

```python
# ❌ MAL: Bloquea Redis
claves = KEYS "user:*"  # ¡NO en producción!

# ✅ BIEN: Iteración no bloqueante
cursor = 0
while True:
    cursor, claves = SCAN cursor MATCH "user:*" COUNT 100
    for clave in claves:
        # procesar
    if cursor == 0:
        break
```

---

### 4. Usar Pipelines para Múltiples Comandos

```python
# ❌ MAL: Una petición por comando
for id in ids:
    r.get(f"user:{id}")  # N roundtrips

# ✅ BIEN: Un pipeline
pipe = r.pipeline()
for id in ids:
    pipe.get(f"user:{id}")
resultados = pipe.execute()  # 1 roundtrip
```

**Mejora**: De N roundtrips a 1

---

### 5. Configurar maxmemory y Política de Evicción

```bash
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

| Política         | Descripción                                   |
| ---------------- | --------------------------------------------- |
| `noeviction`     | Error si no hay memoria                       |
| `allkeys-lru`    | Elimina menos usadas (recomendado para caché) |
| `volatile-lru`   | Elimina menos usadas CON TTL                  |
| `allkeys-random` | Elimina aleatoriamente                        |
| `volatile-ttl`   | Elimina las que expiran pronto                |

---

### 6. Usar Connection Pools

```python
# ✅ BIEN: Pool de conexiones
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    max_connections=10
)

r = redis.Redis(connection_pool=pool)
```

---

### 7. Documentar tus Claves

```
# docs/redis-keys.md

## Claves en Redis

| Patrón            | Tipo   | TTL  | Descripción       |
| ----------------- | ------ | ---- | ----------------- |
| `user:{id}`       | Hash   | -    | Datos del usuario |
| `session:{token}` | String | 3600 | Token de sesión   |
| `cache:*`         | String | 1800 | Caché de datos    |
```

---

## ❌ Qué NO Hacer (DON'T)

### 1. NO Usar KEYS en Producción

```python
# ❌ NUNCA en producción
KEYS *
KEYS user:*

# Bloquea Redis completamente
# En una DB con millones de claves = desastre
```

---

### 2. NO Almacenar Datos Muy Grandes

```python
# ❌ MAL: Clave de 100MB
SET archivo:grande {100MB de datos}

# ✅ BIEN: Fragmentar o usar otro almacenamiento
# Límite recomendado: < 100KB por clave
# Máximo absoluto: 512MB
```

---

### 3. NO Usar Redis como Única Base de Datos (sin persistencia)

```python
# ❌ RIESGO: Solo en memoria
# Si Redis se reinicia = pérdida de datos

# ✅ BIEN: Habilitar persistencia
# appendonly yes
# save 900 1
# save 300 10
```

---

### 4. NO Ignorar el Uso de Memoria

```python
# Comandos para monitorear
INFO memory
MEMORY USAGE clave
MEMORY DOCTOR

# Alertar si uso > 80% de maxmemory
```

---

### 5. NO Usar Claves Muy Largas

```python
# ❌ MAL
SET "esto:es:una:clave:extremadamente:larga:con:muchos:niveles:que:desperdicia:memoria" valor

# ✅ BIEN: Claves cortas pero descriptivas
SET "u:1234:email" valor
SET "user:1234:em" valor  # Abreviaturas consistentes
```

---

### 6. NO Almacenar Contraseñas en Texto Plano

```python
# ❌ NUNCA
HSET user:1 password "mi_contraseña"

# ✅ BIEN: Solo hashes
import bcrypt
hash = bcrypt.hashpw(password, bcrypt.gensalt())
HSET user:1 password_hash hash
```

---

### 7. NO Usar Redis Expuesto a Internet sin AUTH

```bash
# ❌ PELIGROSO
bind 0.0.0.0
# protected-mode no

# ✅ SEGURO
bind 127.0.0.1  # Solo local
requirepass "contraseña_fuerte"
```

---

## 🔐 Seguridad

### Checklist de Seguridad

| Item       | Configuración                                  |
| ---------- | ---------------------------------------------- |
| Contraseña | `requirepass tu_contraseña_fuerte`             |
| Bind       | `bind 127.0.0.1` o IP específica               |
| Puerto     | Cambiar de 6379 si es necesario                |
| Firewall   | Bloquear puerto Redis del exterior             |
| TLS        | Habilitar en producción                        |
| ACLs       | Crear usuarios con permisos mínimos (Redis 6+) |

### Crear Usuario con Permisos Limitados (Redis 6+)

```bash
# Usuario solo lectura para caché
ACL SETUSER cache_readonly on >password ~cache:* +get +mget

# Usuario para la app
ACL SETUSER app on >app_password ~* +@all -@dangerous
```

---

## ⚡ Rendimiento

### Optimizaciones Clave

| Técnica          | Impacto             |
| ---------------- | ------------------- |
| Pipelines        | 10-100x más rápido  |
| Connection pools | Menos overhead      |
| Evitar KEYS      | No bloquea servidor |
| Claves cortas    | Menos memoria       |
| TTL apropiados   | Menos memoria       |

### Comandos a Evitar en Producción

| Comando    | Problema   | Alternativa               |
| ---------- | ---------- | ------------------------- |
| `KEYS *`   | Bloquea    | `SCAN`                    |
| `FLUSHALL` | Borra todo | Automatización controlada |
| `DEBUG`    | Peligroso  | Solo desarrollo           |
| `SAVE`     | Bloquea    | `BGSAVE`                  |

---

## 📊 Monitoreo

### Métricas Importantes

```bash
# Información general
INFO

# Memoria
INFO memory
# used_memory: 1.5GB
# maxmemory: 2GB

# Clientes conectados
INFO clients
# connected_clients: 42

# Estadísticas de comandos
INFO commandstats

# Tiempo de actividad
INFO server
# uptime_in_days: 30
```

### Comandos de Diagnóstico

```bash
# ¿Qué está pasando ahora?
MONITOR  # Ver comandos en tiempo real (solo debug)

# Comandos lentos
SLOWLOG GET 10

# Memoria por tipo
MEMORY STATS

# Latencia
redis-cli --latency
```

---

## 🏭 Producción

### Checklist de Producción

| ✅   | Item                                           |
| --- | ---------------------------------------------- |
| ☐   | Persistencia habilitada (RDB o AOF)            |
| ☐   | maxmemory configurado                          |
| ☐   | Política de evicción apropiada                 |
| ☐   | Contraseña fuerte (requirepass)                |
| ☐   | Bind a IP específica                           |
| ☐   | Firewall configurado                           |
| ☐   | Monitoreo activo                               |
| ☐   | Backups automáticos                            |
| ☐   | Plan de recuperación probado                   |
| ☐   | Réplicas configuradas (si alta disponibilidad) |

### Configuración de Producción Básica

```bash
# /etc/redis/redis.conf

# Memoria
maxmemory 4gb
maxmemory-policy allkeys-lru

# Persistencia
appendonly yes
appendfsync everysec
save 900 1
save 300 10
save 60 10000

# Seguridad  
requirepass "contraseña_muy_fuerte_y_larga"
bind 127.0.0.1

# Rendimiento
tcp-keepalive 300
timeout 0
```

---

## 📋 Resumen Rápido

### ✅ HACER

1. Usar TTL para datos temporales
2. Nombrado consistente de claves
3. SCAN en lugar de KEYS
4. Pipelines para múltiples comandos
5. Configurar maxmemory
6. Connection pools
7. Monitorear memoria y rendimiento

### ❌ NO HACER

1. KEYS en producción
2. Datos > 100KB por clave
3. Redis sin persistencia como DB principal
4. Ignorar uso de memoria
5. Claves extremadamente largas
6. Contraseñas en texto plano
7. Redis expuesto sin AUTH

---

## 🎓 Reglas de Oro

> **1.** "Redis es rápido, pero no almacena más de lo que cabe en RAM"

> **2.** "Diseña pensando en las consultas, no en la normalización"

> **3.** "Un TTL olvidado es una fuga de memoria esperando"

> **4.** "Si usas KEYS *, mereces lo que te pase"

> **5.** "Probar en desarrollo ≠ funcional en producción"
