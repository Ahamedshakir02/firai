"""
Cache Service
-------------
Redis-based caching layer for performance optimization.
Caches legal sections, embeddings, similarity results, and statistics.
"""

import json
import hashlib
from typing import Any, Optional, Callable
from datetime import timedelta
import aioredis
from logging_config import logger

# Global Redis client (initialized on startup)
redis_client: Optional[aioredis.Redis] = None


async def init_redis(redis_url: str = "redis://localhost:6379"):
    """Initialize Redis connection."""
    global redis_client
    try:
        redis_client = await aioredis.from_url(redis_url)
        await redis_client.ping()
        logger.info("Redis cache initialized")
        return redis_client
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
        return None


async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()


class CacheService:
    """Service for managing cache operations."""

    # Cache key prefixes
    PREFIX_LEGAL_SECTION = "legal_section:"
    PREFIX_EMBEDDING = "embedding:"
    PREFIX_SIMILARITY = "similarity:"
    PREFIX_STATS = "stats:"
    PREFIX_FIR = "fir:"

    # Default TTLs
    TTL_LEGAL_SECTION = timedelta(hours=24)  # 24 hours
    TTL_EMBEDDING = timedelta(days=7)  # 7 days
    TTL_SIMILARITY = timedelta(hours=1)  # 1 hour
    TTL_STATS = timedelta(hours=1)  # 1 hour
    TTL_FIR = timedelta(hours=6)  # 6 hours

    @staticmethod
    async def set(
        key: str,
        value: Any,
        ttl: timedelta = timedelta(hours=1),
    ) -> bool:
        """
        Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live

        Returns:
            True if successful, False otherwise
        """
        if not redis_client:
            return False

        try:
            # Serialize value
            if isinstance(value, (dict, list)):
                serialized = json.dumps(value)
            else:
                serialized = str(value)

            # Set in Redis with TTL
            await redis_client.setex(
                key,
                ttl,
                serialized,
            )
            return True
        except Exception as e:
            logger.error(f"Cache set failed for {key}: {e}")
            return False

    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """
        Get a value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if not redis_client:
            return None

        try:
            value = await redis_client.get(key)
            if value is None:
                return None

            # Try to deserialize as JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Cache get failed for {key}: {e}")
            return None

    @staticmethod
    async def delete(key: str) -> bool:
        """Delete a cache entry."""
        if not redis_client:
            return False

        try:
            await redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete failed for {key}: {e}")
            return False

    @staticmethod
    async def delete_pattern(pattern: str) -> int:
        """Delete all keys matching a pattern."""
        if not redis_client:
            return 0

        try:
            cursor = 0
            count = 0
            while True:
                cursor, keys = await redis_client.scan(cursor, match=pattern)
                if keys:
                    count += await redis_client.delete(*keys)
                if cursor == 0:
                    break
            return count
        except Exception as e:
            logger.error(f"Cache pattern delete failed for {pattern}: {e}")
            return 0

    @staticmethod
    async def clear_all() -> bool:
        """Clear all cache entries."""
        if not redis_client:
            return False

        try:
            await redis_client.flushdb()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return False

    @staticmethod
    async def get_stats() -> dict:
        """Get cache statistics."""
        if not redis_client:
            return {"status": "unavailable"}

        try:
            info = await redis_client.info()
            return {
                "status": "available",
                "used_memory_mb": info.get("used_memory", 0) / (1024 * 1024),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"status": "error", "error": str(e)}


# ──────────────────────── Specific Cache Operations ────────────────────────


class LegalSectionCache:
    """Cache for legal sections."""

    @staticmethod
    def _key(act: str, section: str) -> str:
        return f"{CacheService.PREFIX_LEGAL_SECTION}{act}:{section}"

    @staticmethod
    async def set(act: str, section: str, data: dict) -> bool:
        """Cache a legal section."""
        return await CacheService.set(
            LegalSectionCache._key(act, section),
            data,
            CacheService.TTL_LEGAL_SECTION,
        )

    @staticmethod
    async def get(act: str, section: str) -> Optional[dict]:
        """Get cached legal section."""
        return await CacheService.get(LegalSectionCache._key(act, section))

    @staticmethod
    async def invalidate_all() -> int:
        """Invalidate all legal section cache."""
        return await CacheService.delete_pattern(f"{CacheService.PREFIX_LEGAL_SECTION}*")


class EmbeddingCache:
    """Cache for narrative embeddings."""

    @staticmethod
    def _key(narrative_hash: str) -> str:
        return f"{CacheService.PREFIX_EMBEDDING}{narrative_hash}"

    @staticmethod
    def _hash_narrative(narrative: str) -> str:
        """Hash narrative to create cache key."""
        return hashlib.sha256(narrative.encode()).hexdigest()

    @staticmethod
    async def set(narrative: str, embedding: list) -> bool:
        """Cache a narrative embedding."""
        key = EmbeddingCache._key(EmbeddingCache._hash_narrative(narrative))
        return await CacheService.set(
            key,
            embedding,
            CacheService.TTL_EMBEDDING,
        )

    @staticmethod
    async def get(narrative: str) -> Optional[list]:
        """Get cached embedding."""
        key = EmbeddingCache._key(EmbeddingCache._hash_narrative(narrative))
        return await CacheService.get(key)


class SimilarityCache:
    """Cache for similarity search results."""

    @staticmethod
    def _key(query_hash: str, limit: int) -> str:
        return f"{CacheService.PREFIX_SIMILARITY}{query_hash}:{limit}"

    @staticmethod
    def _hash_query(query: dict) -> str:
        """Hash query parameters to create cache key."""
        query_str = json.dumps(query, sort_keys=True)
        return hashlib.sha256(query_str.encode()).hexdigest()

    @staticmethod
    async def set(query: dict, limit: int, results: list) -> bool:
        """Cache similarity search results."""
        key = SimilarityCache._key(SimilarityCache._hash_query(query), limit)
        return await CacheService.set(
            key,
            results,
            CacheService.TTL_SIMILARITY,
        )

    @staticmethod
    async def get(query: dict, limit: int) -> Optional[list]:
        """Get cached similarity results."""
        key = SimilarityCache._key(SimilarityCache._hash_query(query), limit)
        return await CacheService.get(key)

    @staticmethod
    async def invalidate_all() -> int:
        """Invalidate all similarity cache when new FIR is added."""
        return await CacheService.delete_pattern(f"{CacheService.PREFIX_SIMILARITY}*")


class StatisticsCache:
    """Cache for dashboard statistics."""

    @staticmethod
    def _key(stat_type: str) -> str:
        return f"{CacheService.PREFIX_STATS}{stat_type}"

    @staticmethod
    async def set(stat_type: str, data: dict) -> bool:
        """Cache statistics."""
        return await CacheService.set(
            StatisticsCache._key(stat_type),
            data,
            CacheService.TTL_STATS,
        )

    @staticmethod
    async def get(stat_type: str) -> Optional[dict]:
        """Get cached statistics."""
        return await CacheService.get(StatisticsCache._key(stat_type))

    @staticmethod
    async def invalidate_all() -> int:
        """Invalidate all stats cache."""
        return await CacheService.delete_pattern(f"{CacheService.PREFIX_STATS}*")


class FIRCache:
    """Cache for FIR data."""

    @staticmethod
    def _key(fir_id: int) -> str:
        return f"{CacheService.PREFIX_FIR}{fir_id}"

    @staticmethod
    async def set(fir_id: int, data: dict) -> bool:
        """Cache a FIR."""
        return await CacheService.set(
            FIRCache._key(fir_id),
            data,
            CacheService.TTL_FIR,
        )

    @staticmethod
    async def get(fir_id: int) -> Optional[dict]:
        """Get cached FIR."""
        return await CacheService.get(FIRCache._key(fir_id))

    @staticmethod
    async def invalidate(fir_id: int) -> bool:
        """Invalidate cache for a specific FIR."""
        return await CacheService.delete(FIRCache._key(fir_id))

    @staticmethod
    async def invalidate_related() -> int:
        """Invalidate related caches when FIR changes."""
        # Invalidate similarity and stats caches
        count = await SimilarityCache.invalidate_all()
        count += await StatisticsCache.invalidate_all()
        return count


# ──────────────────────── Cache Decorator ────────────────────────


def cached(cache_func: Callable, ttl: timedelta = timedelta(hours=1)):
    """
    Decorator to cache async function results.

    Usage:
        @cached(LegalSectionCache.set, ttl=timedelta(hours=24))
        async def get_legal_section(act: str, section: str):
            # Fetch and return section
            ...
    """

    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # Try cache first
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached_result = await CacheService.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Cache miss - call function
            result = await func(*args, **kwargs)

            # Cache result
            if result is not None:
                await CacheService.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator
