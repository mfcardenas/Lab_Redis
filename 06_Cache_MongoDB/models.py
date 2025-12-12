"""
🗄️ Modelos y conexiones para Redis + MongoDB

Este módulo proporciona las conexiones a Redis y MongoDB,
así como funciones auxiliares para el caché.
"""

import redis
from pymongo import MongoClient
import json
from datetime import datetime
from functools import wraps


# =============================================================================
# CONEXIONES
# =============================================================================

def get_redis():
    """Obtener conexión a Redis."""
    return redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )


def get_mongodb():
    """Obtener conexión a MongoDB."""
    client = MongoClient('mongodb://localhost:27017/')
    return client['tienda_db']


# Conexiones globales
redis_client = get_redis()
mongo_db = get_mongodb()


# =============================================================================
# ESTADÍSTICAS DE CACHÉ
# =============================================================================

class CacheStats:
    """Estadísticas del caché."""
    
    def __init__(self, redis_client):
        self.r = redis_client
    
    def registrar_hit(self):
        self.r.incr("stats:cache:hits")
    
    def registrar_miss(self):
        self.r.incr("stats:cache:misses")
    
    def obtener_estadisticas(self):
        hits = int(self.r.get("stats:cache:hits") or 0)
        misses = int(self.r.get("stats:cache:misses") or 0)
        total = hits + misses
        
        return {
            "hits": hits,
            "misses": misses,
            "total": total,
            "hit_ratio": round(hits / total * 100, 2) if total > 0 else 0
        }
    
    def reset(self):
        self.r.delete("stats:cache:hits", "stats:cache:misses")


cache_stats = CacheStats(redis_client)


# =============================================================================
# DECORADOR DE CACHÉ
# =============================================================================

def cached(ttl=3600, prefix="cache"):
    """
    Decorador para cachear resultados de funciones.
    
    Uso:
        @cached(ttl=300, prefix="productos")
        def obtener_producto(id):
            return db.productos.find_one({"_id": id})
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave de caché
            key_args = "_".join(str(a) for a in args)
            key_kwargs = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = f"{prefix}:{func.__name__}:{key_args}:{key_kwargs}".rstrip(":")
            
            # Intentar obtener de caché
            cached_result = redis_client.get(cache_key)
            
            if cached_result:
                cache_stats.registrar_hit()
                return json.loads(cached_result)
            
            # Cache miss: ejecutar función
            cache_stats.registrar_miss()
            result = func(*args, **kwargs)
            
            # Guardar en caché
            if result is not None:
                redis_client.setex(cache_key, ttl, json.dumps(result, default=str))
            
            return result
        
        return wrapper
    return decorator


# =============================================================================
# REPOSITORIO DE PRODUCTOS
# =============================================================================

class ProductoRepository:
    """Repositorio de productos con caché."""
    
    def __init__(self):
        self.r = redis_client
        self.db = mongo_db
        self.collection = self.db['productos']
        self.cache_ttl = 3600  # 1 hora
    
    def _cache_key(self, producto_id):
        return f"producto:{producto_id}"
    
    def obtener(self, producto_id: str):
        """Obtiene un producto (primero caché, luego DB)."""
        cache_key = self._cache_key(producto_id)
        
        # 1. Buscar en caché
        cached = self.r.get(cache_key)
        if cached:
            cache_stats.registrar_hit()
            return json.loads(cached)
        
        # 2. Cache miss: buscar en MongoDB
        cache_stats.registrar_miss()
        producto = self.collection.find_one({"_id": producto_id})
        
        if producto:
            # Convertir ObjectId a string si existe
            if '_id' in producto:
                producto['_id'] = str(producto['_id'])
            
            # 3. Guardar en caché
            self.r.setex(cache_key, self.cache_ttl, json.dumps(producto))
        
        return producto
    
    def obtener_todos(self, limit=100):
        """Obtiene todos los productos."""
        cache_key = f"productos:all:{limit}"
        
        cached = self.r.get(cache_key)
        if cached:
            cache_stats.registrar_hit()
            return json.loads(cached)
        
        cache_stats.registrar_miss()
        productos = list(self.collection.find().limit(limit))
        
        for p in productos:
            p['_id'] = str(p['_id'])
        
        self.r.setex(cache_key, 300, json.dumps(productos))  # TTL corto
        
        return productos
    
    def crear(self, producto: dict):
        """Crea un nuevo producto."""
        producto['created_at'] = datetime.now().isoformat()
        result = self.collection.insert_one(producto)
        producto['_id'] = str(result.inserted_id)
        
        # Invalidar caché de lista
        self.r.delete("productos:all:100")
        
        return producto
    
    def actualizar(self, producto_id: str, datos: dict):
        """Actualiza un producto e invalida caché."""
        datos['updated_at'] = datetime.now().isoformat()
        
        self.collection.update_one(
            {"_id": producto_id},
            {"$set": datos}
        )
        
        # Invalidar caché
        self.r.delete(self._cache_key(producto_id))
        self.r.delete("productos:all:100")
        
        return self.obtener(producto_id)
    
    def eliminar(self, producto_id: str):
        """Elimina un producto e invalida caché."""
        result = self.collection.delete_one({"_id": producto_id})
        
        # Invalidar caché
        self.r.delete(self._cache_key(producto_id))
        self.r.delete("productos:all:100")
        
        return result.deleted_count > 0
    
    def buscar(self, query: str):
        """Busca productos por nombre."""
        cache_key = f"productos:buscar:{query}"
        
        cached = self.r.get(cache_key)
        if cached:
            cache_stats.registrar_hit()
            return json.loads(cached)
        
        cache_stats.registrar_miss()
        productos = list(self.collection.find({
            "nombre": {"$regex": query, "$options": "i"}
        }).limit(50))
        
        for p in productos:
            p['_id'] = str(p['_id'])
        
        self.r.setex(cache_key, 60, json.dumps(productos))  # TTL muy corto para búsquedas
        
        return productos


# Instancia global
producto_repo = ProductoRepository()
