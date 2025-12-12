# 💾 Módulo 9: Persistencia - Volcado de RAM (RDB y AOF)

*Autor: @mCárdenas 2025*

## 📋 Contenido

1. [¿Por qué Persistencia?](#-por-qué-persistencia)
2. [RDB: Snapshots](#-rdb-snapshots)
3. [AOF: Append Only File](#-aof-append-only-file)
4. [RDB vs AOF](#-rdb-vs-aof)
5. [Configuración Combinada](#-configuración-combinada)
6. [Backup y Restauración](#-backup-y-restauración)
7. [Ejemplo Práctico](#-ejemplo-práctico)

## 🤔 ¿Por qué Persistencia?

Redis almacena todo en RAM, pero **RAM es volátil**:

```
┌─────────────────────────────────────────┐
│           SIN PERSISTENCIA              │
├─────────────────────────────────────────┤
│                                         │
│  Redis corriendo → 10GB de datos        │
│           ↓                             │
│  Reinicio/Crash                         │
│           ↓                             │
│  Redis reinicia → 0 datos  ❌           │
│                                         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│           CON PERSISTENCIA              │
├─────────────────────────────────────────┤
│                                         │
│  Redis corriendo → 10GB de datos        │
│           ↓      → dump.rdb / appendonly│
│  Reinicio/Crash                         │
│           ↓                             │
│  Redis reinicia → 10GB restaurados ✅   │
│                                         │
└─────────────────────────────────────────┘
```

Redis ofrece **dos mecanismos** de persistencia:
- **RDB**: Snapshots (fotos del estado)
- **AOF**: Log de operaciones

## 📸 RDB: Snapshots

### ¿Qué es?

RDB (Redis Database) crea **snapshots** del dataset en momentos específicos.

```
┌─────────────────────────────────────────────────────────────┐
│                    RDB - SNAPSHOTS                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  T=0        T=5min      T=10min     T=15min                 │
│   │           │           │           │                     │
│   ▼           ▼           ▼           ▼                     │
│  [📸]────────[📸]────────[📸]────────[📸]                   │
│  dump.rdb                                                    │
│                                                              │
│  Ventaja: Archivo compacto, rápido de cargar                │
│  Desventaja: Pérdida de datos entre snapshots               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Configuración

```bash
# redis.conf

# Guardar snapshot si:
# - 900 segundos (15 min) y al menos 1 cambio
# - 300 segundos (5 min) y al menos 10 cambios  
# - 60 segundos (1 min) y al menos 10000 cambios
save 900 1
save 300 10
save 60 10000

# Nombre del archivo
dbfilename dump.rdb

# Directorio donde guardar
dir /var/lib/redis/

# Compresión (recomendado)
rdbcompression yes

# Verificar integridad
rdbchecksum yes

# Detener escrituras si falla el snapshot
stop-writes-on-bgsave-error yes
```

### Comandos

```bash
# Crear snapshot manualmente (bloqueante - NO usar en producción)
SAVE

# Crear snapshot en background (recomendado)
BGSAVE

# Ver estado del último backup
LASTSAVE

# Ver información de persistencia
INFO persistence
```

### Pros y Contras

| ✅ Ventajas       | ❌ Desventajas                      |
| ---------------- | ---------------------------------- |
| Archivo compacto | Pérdida de datos entre snapshots   |
| Rápido de cargar | BGSAVE usa RAM adicional (fork)    |
| Backups simples  | No recomendado para pérdida mínima |
| Bajo overhead    |                                    |

## 📝 AOF: Append Only File

### ¿Qué es?

AOF registra **cada operación** de escritura en un log.

```
┌─────────────────────────────────────────────────────────────┐
│                    AOF - LOG DE OPERACIONES                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Comando           appendonly.aof                            │
│  ─────────────     ──────────────────────                   │
│  SET foo bar   →   *3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n...      │
│  INCR counter  →   *2\r\n$4\r\nINCR\r\n$7\r\ncounter...     │
│  LPUSH list a  →   *3\r\n$5\r\nLPUSH\r\n$4\r\nlist...       │
│                                                              │
│  Recuperación: Re-ejecutar todos los comandos               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Configuración

```bash
# redis.conf

# Habilitar AOF
appendonly yes

# Nombre del archivo
appendfilename "appendonly.aof"

# Frecuencia de sincronización
# - always: más seguro, más lento
# - everysec: balance (recomendado)
# - no: más rápido, menos seguro
appendfsync everysec

# Reescribir AOF cuando crece mucho
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# No sincronizar durante rewrite (mejora rendimiento)
no-appendfsync-on-rewrite no
```

### Modos de Sincronización

| Modo       | Descripción        | Pérdida Máxima | Rendimiento |
| ---------- | ------------------ | -------------- | ----------- |
| `always`   | Sync cada comando  | 0 datos        | Lento       |
| `everysec` | Sync cada segundo  | 1 segundo      | Equilibrado |
| `no`       | Deja al SO decidir | 30+ segundos   | Rápido      |

### Comandos

```bash
# Reescribir AOF manualmente (compactar)
BGREWRITEAOF

# Ver información
INFO persistence
```

### Pros y Contras

| ✅ Ventajas               | ❌ Desventajas              |
| ------------------------ | -------------------------- |
| Pérdida mínima de datos  | Archivo más grande que RDB |
| Legible (comandos Redis) | Carga más lenta            |
| Recuperación granular    | Más I/O de disco           |

## 🆚 RDB vs AOF

### Comparación

| Aspecto            | RDB              | AOF                     |
| ------------------ | ---------------- | ----------------------- |
| Formato            | Binario compacto | Texto (comandos)        |
| Pérdida de datos   | Entre snapshots  | Configurable (hasta 1s) |
| Tamaño archivo     | Pequeño          | Grande                  |
| Velocidad carga    | Rápida           | Lenta                   |
| Uso de disco       | Bajo             | Alto                    |
| CPU durante backup | Alto (fork)      | Bajo                    |
| Legibilidad        | No               | Sí (comandos Redis)     |

### ¿Cuál elegir?

```
┌─────────────────────────────────────────────────────────────┐
│                   GUÍA DE DECISIÓN                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ¿Puedes perder algunos minutos de datos?                   │
│       ↓ SÍ                    ↓ NO                          │
│    Usa RDB               Usa AOF + RDB                      │
│                                                              │
│  ¿Prioridad es restauración rápida?                         │
│       ↓ SÍ                    ↓ NO                          │
│    Usa RDB                Usa AOF                           │
│                                                              │
│  ¿Necesitas ambas ventajas?                                 │
│       ↓                                                      │
│    Usa RDB + AOF (recomendado para producción)              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Configuración Combinada

### Configuración Recomendada para Producción

```bash
# redis.conf

# === RDB ===
save 900 1
save 300 10
save 60 10000
dbfilename dump.rdb
dir /var/lib/redis/
rdbcompression yes
rdbchecksum yes

# === AOF ===
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# === AMBOS ===
# Si AOF está habilitado, Redis carga AOF (más completo)
# RDB sirve como backup adicional
```

### Comportamiento al Iniciar

```
┌─────────────────────────────────────────────────────────────┐
│                 ORDEN DE CARGA AL INICIAR                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. ¿Existe AOF habilitado?                                 │
│       ↓ SÍ                    ↓ NO                          │
│     Cargar AOF            Cargar RDB                        │
│                                                              │
│  AOF tiene prioridad porque es más completo                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 💾 Backup y Restauración

### Crear Backup

```bash
# 1. Forzar snapshot RDB
docker exec redis-stack-lab redis-cli BGSAVE

# 2. Esperar a que termine
docker exec redis-stack-lab redis-cli LASTSAVE

# 3. Copiar el archivo
docker cp redis-stack-lab:/data/dump.rdb ./backups/dump_$(date +%Y%m%d).rdb
```

### Script de Backup Automático

```bash
#!/bin/bash
# backup_redis.sh

BACKUP_DIR="/backups/redis"
DATE=$(date +%Y%m%d_%H%M%S)
CONTAINER="redis-stack-lab"

# Crear backup
docker exec $CONTAINER redis-cli BGSAVE
sleep 5  # Esperar a que termine

# Copiar archivo
docker cp $CONTAINER:/data/dump.rdb $BACKUP_DIR/dump_$DATE.rdb

# Mantener solo últimos 7 días
find $BACKUP_DIR -name "dump_*.rdb" -mtime +7 -delete

echo "Backup completado: dump_$DATE.rdb"
```

### Restaurar Backup

```bash
# 1. Detener Redis
docker compose down

# 2. Copiar backup al volumen
docker cp ./backups/dump_20240115.rdb redis-stack-lab:/data/dump.rdb

# 3. Reiniciar Redis
docker compose up -d

# 4. Verificar
docker exec redis-stack-lab redis-cli DBSIZE
```

## 🧪 Ejemplo Práctico

### Verificar Configuración Actual

```bash
# Conectar a Redis
docker exec -it redis-stack-lab redis-cli

# Ver configuración de persistencia
CONFIG GET save
CONFIG GET appendonly
CONFIG GET appendfsync

# Ver información de persistencia
INFO persistence
```

### Forzar Snapshot Manual

```bash
# Crear snapshot en background
BGSAVE

# Ver cuándo fue el último save
LASTSAVE

# Ver si hay backup en progreso
INFO persistence
# rdb_bgsave_in_progress:0
```

### Simular Recuperación

```python
# test_persistencia.py
import redis
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# 1. Crear datos
print("1. Creando datos de prueba...")
r.set("test:persistencia", "dato_importante")
r.hset("user:test", mapping={"nombre": "Test", "email": "test@email.com"})
r.lpush("lista:test", "a", "b", "c")

print(f"   Claves creadas: {r.dbsize()}")

# 2. Forzar snapshot
print("\n2. Creando snapshot...")
r.bgsave()
time.sleep(2)

print(f"   Último save: {r.lastsave()}")

# 3. Verificar datos
print("\n3. Datos guardados:")
print(f"   test:persistencia = {r.get('test:persistencia')}")
print(f"   user:test = {r.hgetall('user:test')}")
print(f"   lista:test = {r.lrange('lista:test', 0, -1)}")

print("\n✅ Ahora puedes reiniciar Redis y verificar que los datos persisten")
```

### Verificar Archivos de Persistencia

```bash
# Ver archivos en el contenedor
docker exec redis-stack-lab ls -la /data/

# Resultado esperado:
# -rw-r--r-- 1 redis redis  1234 Dec 15 10:00 dump.rdb
# -rw-r--r-- 1 redis redis  5678 Dec 15 10:01 appendonly.aof
```

## 📊 Resumen

### Configuración Mínima Recomendada

```bash
# Para desarrollo
appendonly no
save 900 1

# Para producción (caché)
appendonly no
save 300 10
save 60 10000

# Para producción (datos importantes)
appendonly yes
appendfsync everysec
save 900 1
save 300 10
```

### Tabla de Decisión

| Escenario         | RDB | AOF        | Razón              |
| ----------------- | --- | ---------- | ------------------ |
| Solo caché        | ✅   | ❌          | Pérdida aceptable  |
| Datos importantes | ✅   | ✅          | Máxima protección  |
| Disco limitado    | ✅   | ❌          | RDB es más pequeño |
| Pérdida = 0       | ❌   | ✅ always   | AOF registra todo  |
| Balance           | ✅   | ✅ everysec | Mejor de ambos     |

## 🎓 Conclusión

> **RDB** = Fotos periódicas, rápido de cargar, puede perder datos
>
> **AOF** = Cada operación, más seguro, archivos grandes
>
> **Ambos** = Mejor protección, recomendado para producción

```bash
# Configuración "dorada" para producción
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
```
