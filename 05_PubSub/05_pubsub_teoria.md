# 📨 Módulo 5: Patrón Publicador/Suscriptor (Pub/Sub)

*Autor: @mCárdenas 2025*

## 📋 Contenido

1. [¿Qué es Pub/Sub?](#-qué-es-pubsub)
2. [Arquitectura](#-arquitectura)
3. [Comandos Principales](#-comandos-principales)
4. [Casos de Uso](#-casos-de-uso)
5. [Limitaciones](#-limitaciones)

---

## 🤔 ¿Qué es Pub/Sub?

**Pub/Sub** (Publicador/Suscriptor) es un patrón de mensajería donde:

- **Publicadores** envían mensajes a **canales**
- **Suscriptores** escuchan en canales específicos
- Los publicadores no saben quién recibe los mensajes
- Los suscriptores no saben quién los envía

```
┌──────────────┐                           ┌──────────────┐
│ Publicador 1 │──┐                   ┌───►│ Suscriptor 1 │
└──────────────┘  │   ┌───────────┐   │    └──────────────┘
                  ├──►│  Canal A  │───┤
┌──────────────┐  │   └───────────┘   │    ┌──────────────┐
│ Publicador 2 │──┘                   └───►│ Suscriptor 2 │
└──────────────┘                           └──────────────┘
```

### Características

| Característica       | Descripción                               |
| -------------------- | ----------------------------------------- |
| **Desacoplamiento**  | Publicadores y suscriptores no se conocen |
| **Tiempo real**      | Mensajes entregados instantáneamente      |
| **Fire and forget**  | No hay confirmación de entrega            |
| **Sin persistencia** | Mensajes no se almacenan                  |

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        REDIS SERVER                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                      CANALES                         │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │    │
│  │  │ noticias    │  │ chat:sala1  │  │ alerts:*    │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Publishers ───► PUBLISH canal mensaje                       │
│                                                              │
│  Subscribers ◄── SUBSCRIBE canal / PSUBSCRIBE patrón        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Comandos Principales

| Comando           | Descripción            | Ejemplo                   |
| ----------------- | ---------------------- | ------------------------- |
| `SUBSCRIBE`       | Suscribirse a canales  | `SUBSCRIBE canal1 canal2` |
| `PSUBSCRIBE`      | Suscribirse a patrones | `PSUBSCRIBE noticias:*`   |
| `PUBLISH`         | Publicar mensaje       | `PUBLISH canal "mensaje"` |
| `UNSUBSCRIBE`     | Cancelar suscripción   | `UNSUBSCRIBE canal`       |
| `PUNSUBSCRIBE`    | Cancelar patrón        | `PUNSUBSCRIBE patrón`     |
| `PUBSUB CHANNELS` | Listar canales activos | `PUBSUB CHANNELS`         |
| `PUBSUB NUMSUB`   | Suscriptores por canal | `PUBSUB NUMSUB canal`     |

---

## 💼 Casos de Uso

### 1. Notificaciones en Tiempo Real

```python
# Publicador
PUBLISH notificaciones:user123 "Tienes un nuevo mensaje"

# Suscriptor
SUBSCRIBE notificaciones:user123
```

### 2. Chat en Vivo

```python
# Publicador (usuario envía mensaje)
PUBLISH chat:sala_general '{"user": "Ana", "msg": "Hola!"}'

# Suscriptores (otros usuarios)
SUBSCRIBE chat:sala_general
```

### 3. Invalidación de Caché

```python
# Cuando cambia un producto
PUBLISH cache:invalidar "producto:123"

# Servidores de caché escuchan
PSUBSCRIBE cache:*
```

### 4. Eventos del Sistema

```python
# Sistema publica eventos
PUBLISH eventos:sistema "servidor_reiniciado"
PUBLISH eventos:errores "error_critico:db_timeout"

# Monitores suscritos
PSUBSCRIBE eventos:*
```

---

## ⚠️ Limitaciones

| Limitación           | Descripción                              | Alternativa             |
| -------------------- | ---------------------------------------- | ----------------------- |
| **Sin persistencia** | Mensajes perdidos si no hay suscriptores | Usar Streams            |
| **Sin ACK**          | No hay confirmación de entrega           | Usar Streams con grupos |
| **Sin historial**    | No se pueden ver mensajes anteriores     | Usar Streams            |
| **Solo texto**       | Mensajes son strings                     | Serializar con JSON     |

### ¿Cuándo NO usar Pub/Sub?

- ❌ Necesitas garantía de entrega
- ❌ Necesitas historial de mensajes
- ❌ Los suscriptores pueden estar offline
- ❌ Necesitas procesamiento exactly-once

### ¿Cuándo SÍ usar Pub/Sub?

- ✅ Notificaciones en tiempo real
- ✅ Chat donde perder mensajes es aceptable
- ✅ Invalidación de caché
- ✅ Eventos efímeros del sistema

---

## ➡️ Práctica

- [publisher.py](./publisher.py) - Script de publicador
- [subscriber.py](./subscriber.py) - Script de suscriptor
- [05_pubsub.ipynb](./05_pubsub.ipynb) - Notebook interactivo
