import os
import time
import asyncio
import numpy as np
from typing import Optional, Dict, Any, List, Tuple

class SemanticCacheService:
    """
    Production-Conscious In-Memory Semantic Caching Service.
    Guarantees strict patient and report isolation, configurable cosine similarity,
    TTL expiration, and non-blocking thread-safety.
    """

    def __init__(self):
        # Cache storage structure:
        # { namespace_key: [ { "query_text": str, "embedding": np.ndarray, "response": dict, "timestamp": float } ] }
        self._cache: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = asyncio.Lock()
        
        # Configurable similarity threshold via env var (Default: 0.97 for clinical safety)
        self.threshold = float(os.getenv("SEMANTIC_CACHE_THRESHOLD", "0.97"))
        
        # Configurable Time-To-Live in seconds (Default: 3600 seconds = 1 hour)
        self.ttl_seconds = float(os.getenv("SEMANTIC_CACHE_TTL_SEC", "3600"))

        # Performance & telemetry metrics
        self.total_lookups = 0
        self.cache_hits = 0
        self.cache_misses = 0

    def _build_namespace(self, user_id: str, mode: str, report_ids: Optional[List[str]]) -> str:
        """
        Builds strict multi-tenant namespace key to prevent cross-patient data leakage.
        """
        sorted_reports = ",".join(sorted(report_ids)) if report_ids else "none"
        return f"user:{user_id}:mode:{mode}:reports:{sorted_reports}"

    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Computes normalized cosine similarity between two 1D vectors."""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (norm1 * norm2))

    async def get(
        self,
        query_embedding: List[float],
        user_id: str,
        mode: str,
        report_ids: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Performs semantic lookup in the user's isolated namespace.
        Returns cached response if similarity >= threshold, else None.
        """
        async with self._lock:
            self.total_lookups += 1
            namespace = self._build_namespace(user_id, mode, report_ids)
            
            if namespace not in self._cache:
                self.cache_misses += 1
                return None

            entries = self._cache[namespace]
            current_time = time.time()
            query_vec = np.array(query_embedding, dtype=np.float32)

            best_entry = None
            best_score = -1.0

            # Find closest semantic match within this isolated namespace
            for entry in entries:
                # Check TTL expiration
                if current_time - entry["timestamp"] > self.ttl_seconds:
                    continue

                sim = self._cosine_similarity(query_vec, entry["embedding"])
                if sim > best_score:
                    best_score = sim
                    best_entry = entry

            if best_entry is not None and best_score >= self.threshold:
                self.cache_hits += 1
                response = dict(best_entry["response"])
                response["cache_hit"] = True
                response["similarity_score"] = round(best_score, 4)
                return response

            self.cache_misses += 1
            return None

    async def put(
        self,
        query_text: str,
        query_embedding: List[float],
        response: Dict[str, Any],
        user_id: str,
        mode: str,
        report_ids: Optional[List[str]] = None
    ) -> None:
        """
        Stores successfully completed query and verified response in user's isolated namespace.
        """
        if not response or not response.get("answer"):
            return

        async with self._lock:
            namespace = self._build_namespace(user_id, mode, report_ids)
            if namespace not in self._cache:
                self._cache[namespace] = []

            entry = {
                "query_text": query_text,
                "embedding": np.array(query_embedding, dtype=np.float32),
                "response": {
                    "answer": response.get("answer"),
                    "sources": response.get("sources", "Semantic Cache")
                },
                "timestamp": time.time()
            }
            self._cache[namespace].append(entry)

    def invalidate_user(self, user_id: str) -> int:
        """Invalidates all cached entries for a specific user upon document update/deletion."""
        prefix = f"user:{user_id}:"
        keys_to_delete = [k for k in self._cache.keys() if k.startswith(prefix)]
        count = sum(len(self._cache[k]) for k in keys_to_delete)
        for k in keys_to_delete:
            del self._cache[k]
        return count

    def get_metrics(self) -> Dict[str, Any]:
        """Returns real telemetry on cache efficiency."""
        hit_rate = (self.cache_hits / self.total_lookups * 100) if self.total_lookups > 0 else 0.0
        return {
            "total_lookups": self.total_lookups,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate_pct": round(hit_rate, 2),
            "similarity_threshold": self.threshold,
            "ttl_seconds": self.ttl_seconds
        }

# Global singleton instance
semantic_cache = SemanticCacheService()
