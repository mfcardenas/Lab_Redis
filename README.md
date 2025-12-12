# 🚀 Taller de Redis - Guía Completa

<div align="center">

![Redis Logo](https://redis.io/images/redis-white.png)

**Un taller completo y pedagógico para dominar Redis**

[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com/)
[![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)](https://jupyter.org/)

</div>

---

## 📋 Tabla de Contenidos

1. [🎯 Objetivos del Taller](#-objetivos-del-taller)
2. [🛠️ Requisitos Previos](#️-requisitos-previos)
3. [🚀 Inicio Rápido](#-inicio-rápido)
4. [📚 Módulos del Taller](#-módulos-del-taller)
5. [📁 Estructura del Proyecto](#-estructura-del-proyecto)

---

## 🎯 Objetivos del Taller

Al finalizar este taller, serás capaz de:

- ✅ Comprender qué es Redis y cuándo utilizarlo
- ✅ Instalar y configurar Redis Stack con Docker
- ✅ Dominar todos los tipos de datos de Redis
- ✅ Implementar patrones de uso reales con Python
- ✅ Utilizar el patrón Publicador/Suscriptor
- ✅ Implementar Redis como caché entre una aplicación y MongoDB
- ✅ Modelar datos correctamente en Redis
- ✅ Aplicar buenas prácticas y evitar errores comunes
- ✅ Configurar la persistencia de datos

---

## 🛠️ Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

| Herramienta        | Versión Mínima | Verificar                |
| ------------------ | -------------- | ------------------------ |
| **Docker**         | 20.10+         | `docker --version`       |
| **Docker Compose** | 2.0+           | `docker compose version` |
| **Python**         | 3.10+          | `python --version`       |
| **pip**            | 21.0+          | `pip --version`          |
| **MongoDB**        | 6.0+           | `mongod --version`       |

---

## 🚀 Inicio Rápido

### 1️⃣ Clonar o descargar el repositorio

```bash
cd RedisLab
```

### 2️⃣ Iniciar Redis Stack con Docker

```bash
docker compose up -d
```

### 3️⃣ Verificar que Redis está funcionando

```bash
docker exec -it redis-stack-lab redis-cli ping
# Respuesta esperada: PONG
```

### 4️⃣ Acceder a RedisInsight (Interfaz Gráfica)

Abre tu navegador en: **http://localhost:8001**

### 5️⃣ Instalar dependencias de Python

```bash
# Crear entorno virtual (recomendado)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

### 6️⃣ Iniciar Jupyter Notebook

```bash
jupyter notebook
```

---

## 📚 Módulos del Taller

| #   | Módulo                                                                  | Tipo       | Descripción                            |
| --- | ----------------------------------------------------------------------- | ---------- | -------------------------------------- |
| 1   | [Introducción a Redis](./01_Introduccion/01_introduccion_redis.md)      | 📖 Teoría   | ¿Qué es Redis? Historia y arquitectura |
| 2   | [Instalación con Docker](./02_Instalacion/02_instalacion_redisstack.md) | 📖 Teoría   | Guía completa de instalación           |
| 3   | [Tipos de Datos](./03_Tipos_de_Datos/)                                  | 📖 + 💻      | Todos los tipos con ejemplos           |
| 4   | [Casos de Uso Reales](./04_Casos_de_Uso/04_casos_uso_reales.ipynb)      | 💻 Práctica | 2 casos por cada tipo de dato          |
| 5   | [Pub/Sub](./05_PubSub/)                                                 | 📖 + 💻      | Patrón Publicador/Suscriptor           |
| 6   | [Caché con MongoDB](./06_Cache_MongoDB/)                                | 📖 + 💻      | Redis como capa de caché               |
| 7   | [Modelado de Datos](./07_Modelado_Datos/07_modelado_datos.md)           | 📖 Teoría   | Patrones de diseño en Redis            |
| 8   | [Buenas Prácticas](./08_Buenas_Practicas/08_buenas_practicas.md)        | 📖 Teoría   | Qué hacer y qué no hacer               |
| 9   | [Persistencia](./09_Persistencia/09_persistencia_rdb_aof.md)            | 📖 Teoría   | Volcado de RAM: RDB y AOF              |

> 📖 = Material teórico (Markdown) | 💻 = Ejercicios prácticos (Jupyter Notebook)

---

## 📁 Estructura del Proyecto

```
RedisLab/
├── 📄 README.md                           # Este archivo
├── 🐳 docker-compose.yml                  # Configuración de RedisStack
├── 📦 requirements.txt                    # Dependencias de Python
│
├── 📁 01_Introduccion/
│   └── 📖 01_introduccion_redis.md
│
├── 📁 02_Instalacion/
│   └── 📖 02_instalacion_redisstack.md
│
├── 📁 03_Tipos_de_Datos/
│   ├── 📖 03_tipos_datos_overview.md
│   └── 💻 03_tipos_datos.ipynb
│
├── 📁 04_Casos_de_Uso/
│   └── 💻 04_casos_uso_reales.ipynb
│
├── 📁 05_PubSub/
│   ├── 📖 05_pubsub_teoria.md
│   ├── 🐍 publisher.py
│   ├── 🐍 subscriber.py
│   └── 💻 05_pubsub.ipynb
│
├── 📁 06_Cache_MongoDB/
│   ├── 📖 06_cache_teoria.md
│   ├── 🐍 app.py
│   ├── 🐍 models.py
│   └── 💻 06_cache_demo.ipynb
│
├── 📁 07_Modelado_Datos/
│   └── 📖 07_modelado_datos.md
│
├── 📁 08_Buenas_Practicas/
│   └── 📖 08_buenas_practicas.md
│
└── 📁 09_Persistencia/
    └── 📖 09_persistencia_rdb_aof.md
```

---

## 🔧 Comandos Útiles

### Docker

```bash
# Iniciar Redis
docker compose up -d

# Ver logs
docker compose logs -f

# Detener Redis
docker compose down

# Detener y eliminar datos
docker compose down -v
```

### Redis CLI

```bash
# Conectar a Redis
docker exec -it redis-stack-lab redis-cli

# Comandos básicos
PING                    # Verificar conexión
INFO                    # Información del servidor
DBSIZE                  # Número de claves
FLUSHDB                 # Borrar base de datos actual
FLUSHALL                # Borrar todas las bases de datos
```

---

## 📞 Recursos Adicionales

- 📚 [Documentación Oficial de Redis](https://redis.io/docs/)
- 📚 [Redis University (Cursos Gratuitos)](https://university.redis.com/)
- 📚 [Redis Python Client](https://redis-py.readthedocs.io/)
- 📚 [Redis Stack](https://redis.io/docs/stack/)

---

<div align="center">

**¡Feliz aprendizaje! 🎉**

</div>
