"""
📤 Publicador Redis Pub/Sub

*Autor: @mCárdenas 2025*

Este script publica mensajes en canales de Redis.
Ejecutar en una terminal mientras subscriber.py corre en otra.

Uso:
    python publisher.py
"""

import redis
import json
import time
from datetime import datetime


def crear_conexion():
    """Crear conexión a Redis."""
    return redis.Redis(host='localhost', port=6379, decode_responses=True)


def publicar_notificacion(r, canal: str, mensaje: dict):
    """Publica una notificación en un canal."""
    mensaje['timestamp'] = datetime.now().isoformat()
    datos = json.dumps(mensaje, ensure_ascii=False)
    num_suscriptores = r.publish(canal, datos)
    print(f"📤 Publicado en '{canal}' → {num_suscriptores} suscriptor(es)")
    return num_suscriptores


def demo_chat():
    """Demo de chat: envía mensajes a una sala."""
    r = crear_conexion()
    canal = "chat:sala_general"
    
    print("=" * 50)
    print("💬 DEMO: Chat en tiempo real")
    print(f"   Canal: {canal}")
    print("   Escribe mensajes (Ctrl+C para salir)")
    print("=" * 50)
    
    usuario = input("Tu nombre: ").strip() or "Anónimo"
    
    try:
        while True:
            mensaje = input(f"[{usuario}] > ").strip()
            if mensaje:
                publicar_notificacion(r, canal, {
                    "usuario": usuario,
                    "mensaje": mensaje
                })
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")


def demo_notificaciones():
    """Demo de notificaciones: envía a usuarios específicos."""
    r = crear_conexion()
    
    print("=" * 50)
    print("🔔 DEMO: Sistema de notificaciones")
    print("=" * 50)
    
    # Simular notificaciones a diferentes usuarios
    notificaciones = [
        ("notificaciones:user1", {"tipo": "mensaje", "contenido": "Tienes un nuevo mensaje"}),
        ("notificaciones:user2", {"tipo": "alerta", "contenido": "Tu pedido ha sido enviado"}),
        ("notificaciones:user1", {"tipo": "sistema", "contenido": "Mantenimiento programado"}),
        ("notificaciones:all", {"tipo": "broadcast", "contenido": "¡Nueva actualización disponible!"}),
    ]
    
    for canal, mensaje in notificaciones:
        publicar_notificacion(r, canal, mensaje)
        time.sleep(1)
    
    print("✅ Demo completada")


def demo_eventos_sistema():
    """Demo de eventos del sistema."""
    r = crear_conexion()
    
    print("=" * 50)
    print("⚙️ DEMO: Eventos del sistema")
    print("=" * 50)
    
    eventos = [
        ("eventos:servidor", {"accion": "inicio", "servidor": "web-01"}),
        ("eventos:base_datos", {"accion": "backup_completado", "tamaño_mb": 150}),
        ("eventos:error", {"nivel": "warning", "mensaje": "Alta latencia detectada"}),
        ("eventos:cache", {"accion": "invalidar", "claves": ["user:123", "producto:456"]}),
        ("eventos:despliegue", {"version": "2.1.0", "estado": "completado"}),
    ]
    
    for canal, evento in eventos:
        publicar_notificacion(r, canal, evento)
        time.sleep(0.5)
    
    print("✅ Demo completada")


def main():
    print("" + "=" * 50)
    print("     📤 REDIS PUB/SUB - PUBLICADOR")
    print("=" * 50)
    print("Selecciona una demo:")
    print("  1. Chat interactivo")
    print("  2. Notificaciones automáticas")
    print("  3. Eventos del sistema")
    print("  0. Salir")
    
    opcion = input("Opción: ").strip()
    
    if opcion == "1":
        demo_chat()
    elif opcion == "2":
        demo_notificaciones()
    elif opcion == "3":
        demo_eventos_sistema()
    elif opcion == "0":
        print("👋 ¡Hasta luego!")
    else:
        print("❌ Opción no válida")


if __name__ == "__main__":
    main()
