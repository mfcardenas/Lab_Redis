# 📦 Módulo 2: Instalación de RedisStack con Docker

*Autor: @mCárdenas 2025*

<div align="center">

![Docker + Redis](https://img.shields.io/badge/Docker-Redis_Stack-blue?style=for-the-badge&logo=docker)

*"La forma más rápida de tener Redis funcionando en minutos"*

</div>

## 📋 Contenido de este módulo

1. [¿Por qué Docker?](#-por-qué-docker)
2. [Requisitos Previos](#-requisitos-previos)
3. [Instalación Paso a Paso](#-instalación-paso-a-paso)
4. [Verificación de la Instalación](#-verificación-de-la-instalación)
5. [RedisInsight: Interfaz Gráfica](#-redisinsight-interfaz-gráfica)
6. [Conexión desde Python](#-conexión-desde-python)
7. [Comandos Docker Útiles](#-comandos-docker-útiles)
8. [Solución de Problemas](#-solución-de-problemas)

## 🐳 ¿Por qué Docker?

Docker nos permite:

| Ventaja                  | Descripción                              |
| ------------------------ | ---------------------------------------- |
| **Consistencia**         | El mismo entorno en cualquier máquina    |
| **Aislamiento**          | Redis no interfiere con tu sistema       |
| **Facilidad**            | Un comando para instalar todo            |
| **Limpieza**             | Fácil de eliminar sin residuos           |
| **Redis Stack completo** | Incluye todos los módulos + RedisInsight |

```
┌─────────────────────────────────────────────────────────────┐
│                    TU ORDENADOR                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌───────────────────────────────────────────────────┐     │
│   │              CONTENEDOR DOCKER                     │     │
│   │  ┌─────────────────────────────────────────────┐  │     │
│   │  │              REDIS STACK                     │  │     │
│   │  │  • Redis Server (puerto 6379)               │  │     │
│   │  │  • RedisJSON                                │  │     │
│   │  │  • RediSearch                               │  │     │
│   │  │  • RedisGraph                               │  │     │
│   │  │  • RedisTimeSeries                          │  │     │
│   │  │  • RedisBloom                               │  │     │
│   │  │  • RedisInsight (puerto 8001)               │  │     │
│   │  └─────────────────────────────────────────────┘  │     │
│   └───────────────────────────────────────────────────┘     │
│                           │                                  │
│   ┌───────────────────────┴───────────────────────────┐     │
│   │  Volumen: redis-data (datos persistentes)         │     │
│   └───────────────────────────────────────────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Requisitos Previos

### 1. Docker Desktop

**Windows:**
1. Descargar de [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
2. Ejecutar el instalador
3. Reiniciar si es necesario
4. Verificar instalación:

```powershell
docker --version
# Docker version 24.x.x, build xxxxxxx

docker compose version
# Docker Compose version v2.x.x
```

**Requisitos de Windows:**
- Windows 10/11 64-bit
- WSL2 habilitado (Docker Desktop lo configura automáticamente)
- Virtualización habilitada en BIOS

### 2. Verificar que Docker está corriendo

```powershell
docker info
```

Si ves información del sistema Docker, ¡está listo!

## 🚀 Instalación Paso a Paso

### Paso 1: Navegar al directorio del taller

```powershell
cd C:\Users\tu-usuario\Documents\GitHub\RedisLab
```

### Paso 2: Revisar el archivo docker-compose.yml

El archivo ya está creado con esta configuración:

```yaml
version: '3.8'

services:
  redis-stack:
    image: redis/redis-stack:latest
    container_name: redis-stack-lab
    ports:
      - "6379:6379"   # Puerto Redis
      - "8001:8001"   # Puerto RedisInsight (interfaz gráfica)
    volumes:
      - redis-data:/data
    environment:
      - REDIS_ARGS=--appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  redis-data:
    driver: local
```

#### Explicación de la configuración:

| Parámetro            | Valor                    | Descripción                          |
| -------------------- | ------------------------ | ------------------------------------ |
| `image`              | redis/redis-stack:latest | Imagen oficial con todos los módulos |
| `container_name`     | redis-stack-lab          | Nombre del contenedor                |
| `ports: 6379`        | 6379:6379                | Puerto de Redis                      |
| `ports: 8001`        | 8001:8001                | Puerto de RedisInsight               |
| `volumes`            | redis-data:/data         | Datos persistentes                   |
| `--appendonly yes`   | AOF activo               | Persistencia en cada escritura       |
| `--maxmemory 256mb`  | Límite RAM               | Máximo de memoria a usar             |
| `--maxmemory-policy` | allkeys-lru              | Elimina claves menos usadas          |

### Paso 3: Iniciar Redis Stack

```powershell
docker compose up -d
```

**Salida esperada:**
```
[+] Running 2/2
 ✔ Network redislab_default  Created
 ✔ Container redis-stack-lab Started
```

### Paso 4: Verificar que está corriendo

```powershell
docker ps
```

**Salida esperada:**
```
CONTAINER ID   IMAGE                    PORTS                                            NAMES
xxxxxxxxxxxx   redis/redis-stack:latest 0.0.0.0:6379->6379/tcp, 0.0.0.0:8001->8001/tcp   redis-stack-lab
```

## ✅ Verificación de la Instalación

### Test 1: Ping desde Docker

```powershell
docker exec -it redis-stack-lab redis-cli ping
```

**Respuesta esperada:** `PONG`

### Test 2: Información del servidor

```powershell
docker exec -it redis-stack-lab redis-cli INFO server
```

**Respuesta esperada:** Información del servidor Redis

### Test 3: Probar comandos básicos

```powershell
# Entrar a la consola de Redis
docker exec -it redis-stack-lab redis-cli

# Dentro de redis-cli:
127.0.0.1:6379> SET saludo "Hola Redis!"
OK

127.0.0.1:6379> GET saludo
"Hola Redis!"

127.0.0.1:6379> DEL saludo
(integer) 1

127.0.0.1:6379> exit
```

### Test 4: Verificar módulos de Redis Stack

```powershell
docker exec -it redis-stack-lab redis-cli MODULE LIST
```

**Respuesta esperada:**
```
1) 1) "name"
   2) "search"
   3) "ver"
   4) (integer) ...
2) 1) "name"
   2) "ReJSON"
   ...
```

## 🖥️ RedisInsight: Interfaz Gráfica

RedisInsight es una **interfaz gráfica** incluida en Redis Stack que permite:

- 📊 Visualizar datos
- 🔍 Buscar claves
- ✏️ Editar valores
- 📈 Monitorear rendimiento
- 💻 Ejecutar comandos

### Acceder a RedisInsight

1. Abre tu navegador
2. Ve a: **http://localhost:8001**
3. Acepta los términos de uso
4. Haz clic en **"Add Redis Database"**
5. Usa la configuración automática o manual:

**Configuración manual:**
| Campo    | Valor     |
| -------- | --------- |
| Host     | localhost |
| Port     | 6379      |
| Name     | Redis Lab |
| Username | (vacío)   |
| Password | (vacío)   |

6. Haz clic en **"Add Redis Database"**

### Características principales de RedisInsight

```
┌─────────────────────────────────────────────────────────────┐
│                      REDIS INSIGHT                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Browser   │  │  Workbench  │  │   Slowlog   │         │
│  │             │  │             │  │             │         │
│  │ Ver y editar│  │  Ejecutar   │  │  Comandos   │         │
│  │   claves    │  │  comandos   │  │   lentos    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Memory    │  │    CLI      │  │   Pub/Sub   │         │
│  │  Analysis   │  │             │  │             │         │
│  │  Análisis   │  │  Terminal   │  │  Mensajes   │         │
│  │  de memoria │  │  integrado  │  │  en vivo    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## 🐍 Conexión desde Python

### Instalar el cliente Redis para Python

```powershell
# Activar entorno virtual (si lo usas)
venv\Scripts\activate

# Instalar redis-py
pip install redis
```

### Probar la conexión

Crea un archivo `test_connection.py`:

```python
import redis

# Conectar a Redis
r = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True  # Para obtener strings en lugar de bytes
)

# Probar conexión
try:
    # Ping
    response = r.ping()
    print(f"✅ Conexión exitosa! PING: {response}")
    
    # Info del servidor
    info = r.info('server')
    print(f"📊 Versión de Redis: {info['redis_version']}")
    
    # Prueba básica
    r.set('test:python', '¡Funciona desde Python!')
    valor = r.get('test:python')
    print(f"💾 Valor guardado y recuperado: {valor}")
    
    # Limpiar
    r.delete('test:python')
    print("🧹 Clave de prueba eliminada")
    
except redis.ConnectionError as e:
    print(f"❌ Error de conexión: {e}")
```

**Ejecutar:**
```powershell
python test_connection.py
```

**Salida esperada:**
```
✅ Conexión exitosa! PING: True
📊 Versión de Redis: 7.2.x
💾 Valor guardado y recuperado: ¡Funciona desde Python!
🧹 Clave de prueba eliminada
```

### Patrón de conexión recomendado

```python
import redis
from contextlib import contextmanager

def get_redis_connection():
    """Crear una conexión a Redis."""
    return redis.Redis(
        host='localhost',
        port=6379,
        db=0,  # Base de datos 0-15
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5
    )

# Uso
r = get_redis_connection()
```

### Usando Connection Pool (recomendado para aplicaciones)

```python
import redis

# Crear pool de conexiones (reutilizable)
pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True,
    max_connections=10
)

# Obtener conexión del pool
r = redis.Redis(connection_pool=pool)

# Usar normalmente
r.set('clave', 'valor')
```

## 🛠️ Comandos Docker Útiles

### Gestión del contenedor

```powershell
# Iniciar Redis
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f

# Detener Redis
docker compose down

# Detener y eliminar TODOS los datos
docker compose down -v

# Reiniciar Redis
docker compose restart
```

### Acceso a Redis CLI

```powershell
# Entrar a la consola de Redis
docker exec -it redis-stack-lab redis-cli

# Ejecutar un comando directamente
docker exec -it redis-stack-lab redis-cli GET mi_clave

# Conectar a una base de datos específica (0-15)
docker exec -it redis-stack-lab redis-cli -n 1
```

### Comandos Redis útiles

```bash
# Dentro de redis-cli:

# Ver todas las claves (¡NO usar en producción!)
KEYS *

# Contar claves
DBSIZE

# Ver tipo de una clave
TYPE mi_clave

# Ver TTL de una clave
TTL mi_clave

# Eliminar todas las claves de la DB actual
FLUSHDB

# Eliminar todas las claves de todas las DBs
FLUSHALL

# Información del servidor
INFO

# Monitorear comandos en tiempo real
MONITOR

# Guardar snapshot a disco
BGSAVE
```

## 🔧 Solución de Problemas

### Problema 1: Puerto 6379 ya en uso

**Error:**
```
Bind for 0.0.0.0:6379 failed: port is already allocated
```

**Solución:**
```powershell
# Ver qué proceso usa el puerto
netstat -ano | findstr :6379

# Matar el proceso (reemplaza PID)
taskkill /PID <PID> /F

# O cambiar el puerto en docker-compose.yml
ports:
  - "6380:6379"  # Usar puerto 6380 en tu máquina
```

### Problema 2: Docker no está corriendo

**Error:**
```
Cannot connect to the Docker daemon
```

**Solución:**
1. Abrir Docker Desktop
2. Esperar a que inicie completamente
3. Reintentar el comando

### Problema 3: Contenedor no inicia

**Diagnóstico:**
```powershell
# Ver logs del contenedor
docker compose logs

# Ver estado detallado
docker inspect redis-stack-lab
```

### Problema 4: No puedo acceder a RedisInsight

**Verificar:**
1. ¿El contenedor está corriendo? `docker ps`
2. ¿El puerto está correcto? http://localhost:8001
3. ¿Hay firewall bloqueando?

**Solución alternativa:**
```powershell
# Verificar puertos del contenedor
docker port redis-stack-lab
```

### Problema 5: Datos no persisten

**Verificar volumen:**
```powershell
docker volume ls
docker volume inspect redislab_redis-data
```

## 📊 Resumen del Módulo

| Acción        | Comando                                          |
| ------------- | ------------------------------------------------ |
| Iniciar Redis | `docker compose up -d`                           |
| Verificar     | `docker exec -it redis-stack-lab redis-cli ping` |
| RedisInsight  | http://localhost:8001                            |
| Redis CLI     | `docker exec -it redis-stack-lab redis-cli`      |
| Detener       | `docker compose down`                            |
| Ver logs      | `docker compose logs -f`                         |

## ✅ Checklist de Verificación

Antes de continuar, asegúrate de que:

- [ ] Docker Desktop está instalado y corriendo
- [ ] `docker compose up -d` ejecuta sin errores
- [ ] `redis-cli ping` responde `PONG`
- [ ] RedisInsight es accesible en http://localhost:8001
- [ ] Python puede conectarse a Redis

## ➡️ Siguiente Módulo

[📊 Módulo 3: Tipos de Datos en Redis](../03_Tipos_de_Datos/03_tipos_datos_overview.md)

<div align="center">

**¿Todo funcionando?** ¡Excelente! 🎉

</div>
