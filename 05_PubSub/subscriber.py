"""
📥 Suscriptor Redis Pub/Sub

*Autor: @mCárdenas 2025*

Este script se suscribe a canales de Redis y muestra los mensajes recibidos.
Ejecutar en una terminal mientras publisher.py corre en otra.

Uso:
    python subscriber.py
"""

import redis
import json
from datetime import datetime


def formatear_mensaje(canal: str, datos: str) -> str:
    """Formatea un mensaje para mostrarlo."""
    try:
        mensaje = json.loads(datos)
        timestamp = mensaje.get('timestamp', datetime.now().isoformat())
        
        # Formatear según el tipo de canal
        if 'chat' in canal:
            usuario = mensaje.get('usuario', 'Anónimo')
            texto = mensaje.get('mensaje', '')
            return f"💬 [{usuario}]: {texto}"
        
        elif 'notificaciones' in canal:
            tipo = mensaje.get('tipo', 'info')
            contenido = mensaje.get('contenido', '')
            iconos = {'mensaje': '✉️', 'alerta': '🔔', 'sistema': '⚙️', 'broadcast': '📢'}
            icono = iconos.get(tipo, 'ℹ️')
            return f"{icono} {contenido}"
        
        elif 'eventos' in canal:
            return f"⚡ Evento: {json.dumps(mensaje, ensure_ascii=False)}"
        
        else:
            return f"📨 {datos}"
    
    except json.JSONDecodeError:
        return f"📨 {datos}"


def suscriptor_simple(canales: list):
    """Suscriptor a canales específicos."""
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    pubsub = r.pubsub()
    
    print(f"📥 Suscrito a: {', '.join(canales)}")
    print("   Esperando mensajes... (Ctrl+C para salir)\n")
    
    pubsub.subscribe(*canales)
    
    try:
        for mensaje in pubsub.listen():
            if mensaje['type'] == 'message':
                canal = mensaje['channel']
                datos = mensaje['data']
                texto = formatear_mensaje(canal, datos)
                print(f"[{canal}] {texto}")
    except KeyboardInterrupt:
        print("\n👋 Desconectado")
    finally:
        pubsub.unsubscribe()


def suscriptor_patron(patrones: list):
    """Suscriptor a patrones de canales."""
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    pubsub = r.pubsub()
    
    print(f"📥 Suscrito a patrones: {', '.join(patrones)}")
    print("   Esperando mensajes... (Ctrl+C para salir)\n")
    
    pubsub.psubscribe(*patrones)
    
    try:
        for mensaje in pubsub.listen():
            if mensaje['type'] == 'pmessage':
                patron = mensaje['pattern']
                canal = mensaje['channel']
                datos = mensaje['data']
                texto = formatear_mensaje(canal, datos)
                print(f"[{patron} → {canal}] {texto}")
    except KeyboardInterrupt:
        print("\n👋 Desconectado")
    finally:
        pubsub.punsubscribe()


def demo_chat():
    """Demo: suscriptor de chat."""
    suscriptor_simple(["chat:sala_general"])


def demo_notificaciones():
    """Demo: suscriptor de notificaciones para un usuario."""
    usuario = input("ID de usuario (ej: user1): ").strip() or "user1"
    canales = [f"notificaciones:{usuario}", "notificaciones:all"]
    suscriptor_simple(canales)


def demo_todos_eventos():
    """Demo: suscriptor a todos los eventos del sistema."""
    suscriptor_patron(["eventos:*"])


def demo_todo():
    """Demo: suscriptor a TODO."""
    suscriptor_patron(["*"])


def main():
    print("" + "=" * 50)
    print("     📥 REDIS PUB/SUB - SUSCRIPTOR")
    print("=" * 50)
    print("Selecciona qué escuchar:")
    print("  1. Chat (sala general)")
    print("  2. Notificaciones (usuario específico)")
    print("  3. Eventos del sistema (todos)")
    print("  4. TODO (todos los canales)")
    print("  0. Salir")
    
    opcion = input("\nOpción: ").strip()
    
    if opcion == "1":
        demo_chat()
    elif opcion == "2":
        demo_notificaciones()
    elif opcion == "3":
        demo_todos_eventos()
    elif opcion == "4":
        demo_todo()
    elif opcion == "0":
        print("👋 ¡Hasta luego!")
    else:
        print("❌ Opción no válida")


if __name__ == "__main__":
    main()
