"""
🚀 API REST con Flask + Redis Cache + MongoDB

Mini-aplicación de demostración de Redis como caché.

Ejecutar:
    python app.py

Endpoints:
    GET  /api/productos          - Listar productos
    GET  /api/productos/<id>     - Obtener producto
    POST /api/productos          - Crear producto
    PUT  /api/productos/<id>     - Actualizar producto
    DELETE /api/productos/<id>   - Eliminar producto
    GET  /api/stats              - Estadísticas de caché
"""

from flask import Flask, jsonify, request
from models import producto_repo, cache_stats, redis_client
import time

app = Flask(__name__)


# =============================================================================
# MIDDLEWARE
# =============================================================================

@app.before_request
def before_request():
    """Registrar tiempo de inicio."""
    request.start_time = time.time()


@app.after_request
def after_request(response):
    """Añadir tiempo de respuesta a headers."""
    if hasattr(request, 'start_time'):
        elapsed = (time.time() - request.start_time) * 1000
        response.headers['X-Response-Time'] = f"{elapsed:.2f}ms"
    return response


# =============================================================================
# ENDPOINTS DE PRODUCTOS
# =============================================================================

@app.route('/api/productos', methods=['GET'])
def listar_productos():
    """Listar todos los productos."""
    try:
        productos = producto_repo.obtener_todos()
        return jsonify({
            "success": True,
            "count": len(productos),
            "data": productos
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/productos/<producto_id>', methods=['GET'])
def obtener_producto(producto_id):
    """Obtener un producto por ID."""
    try:
        producto = producto_repo.obtener(producto_id)
        
        if not producto:
            return jsonify({
                "success": False,
                "error": "Producto no encontrado"
            }), 404
        
        return jsonify({
            "success": True,
            "data": producto
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/productos', methods=['POST'])
def crear_producto():
    """Crear un nuevo producto."""
    try:
        datos = request.get_json()
        
        if not datos or 'nombre' not in datos:
            return jsonify({
                "success": False,
                "error": "El campo 'nombre' es requerido"
            }), 400
        
        producto = producto_repo.crear(datos)
        
        return jsonify({
            "success": True,
            "message": "Producto creado",
            "data": producto
        }), 201
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/productos/<producto_id>', methods=['PUT'])
def actualizar_producto(producto_id):
    """Actualizar un producto."""
    try:
        datos = request.get_json()
        
        if not datos:
            return jsonify({
                "success": False,
                "error": "Se requieren datos para actualizar"
            }), 400
        
        producto = producto_repo.actualizar(producto_id, datos)
        
        if not producto:
            return jsonify({
                "success": False,
                "error": "Producto no encontrado"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "Producto actualizado",
            "data": producto
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/productos/<producto_id>', methods=['DELETE'])
def eliminar_producto(producto_id):
    """Eliminar un producto."""
    try:
        eliminado = producto_repo.eliminar(producto_id)
        
        if not eliminado:
            return jsonify({
                "success": False,
                "error": "Producto no encontrado"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "Producto eliminado"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/productos/buscar', methods=['GET'])
def buscar_productos():
    """Buscar productos por nombre."""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({
                "success": False,
                "error": "Se requiere parámetro 'q'"
            }), 400
        
        productos = producto_repo.buscar(query)
        
        return jsonify({
            "success": True,
            "query": query,
            "count": len(productos),
            "data": productos
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =============================================================================
# ENDPOINTS DE ESTADÍSTICAS
# =============================================================================

@app.route('/api/stats', methods=['GET'])
def estadisticas():
    """Obtener estadísticas del caché."""
    try:
        stats = cache_stats.obtener_estadisticas()
        
        # Añadir info de Redis
        info = redis_client.info('memory')
        stats['redis_memory_used'] = info.get('used_memory_human', 'N/A')
        stats['redis_keys'] = redis_client.dbsize()
        
        return jsonify({
            "success": True,
            "data": stats
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/stats/reset', methods=['POST'])
def reset_estadisticas():
    """Resetear estadísticas del caché."""
    try:
        cache_stats.reset()
        return jsonify({
            "success": True,
            "message": "Estadísticas reseteadas"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/cache/clear', methods=['POST'])
def limpiar_cache():
    """Limpiar todo el caché."""
    try:
        # Solo eliminar claves de productos
        claves = redis_client.keys("producto:*") + redis_client.keys("productos:*")
        if claves:
            redis_client.delete(*claves)
        
        return jsonify({
            "success": True,
            "message": f"Caché limpiado ({len(claves)} claves eliminadas)"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check del servicio."""
    try:
        # Verificar Redis
        redis_ok = redis_client.ping()
        
        # Verificar MongoDB
        from models import mongo_db
        mongo_ok = mongo_db.command('ping').get('ok', 0) == 1
        
        return jsonify({
            "status": "healthy" if redis_ok and mongo_ok else "unhealthy",
            "redis": "ok" if redis_ok else "error",
            "mongodb": "ok" if mongo_ok else "error"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 API de Productos con Redis Cache")
    print("=" * 50)
    print("\nEndpoints disponibles:")
    print("  GET    /api/productos")
    print("  GET    /api/productos/<id>")
    print("  POST   /api/productos")
    print("  PUT    /api/productos/<id>")
    print("  DELETE /api/productos/<id>")
    print("  GET    /api/productos/buscar?q=<query>")
    print("  GET    /api/stats")
    print("  POST   /api/stats/reset")
    print("  POST   /api/cache/clear")
    print("  GET    /health")
    print("\n" + "=" * 50)
    
    app.run(debug=True, port=5000)
