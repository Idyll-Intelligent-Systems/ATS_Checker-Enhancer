"""
ZeX-ATS-AI Rate Limiter
Advanced rate limiting with user tiers and Redis backend.
"""

import time
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import json

import redis.asyncio as aioredis

from src.core.config import settings
from src.utils.system_logger import log_function


class RateLimiter:
    """Advanced rate limiter with tier-based limits."""
    
    def __init__(self):
        """Initialize rate limiter."""
        self.redis_client = None
        self.local_cache = {}  # Fallback for development
        
        # Rate limits by subscription tier
        self.tier_limits = {
            "free": {
                "daily_limit": 10,
                "hourly_limit": 5,
                "monthly_limit": 50,
                "burst_limit": 2,  # Requests per minute
                "concurrent_analyses": 1
            },
            "pro": {
                "daily_limit": 100,
                "hourly_limit": 25,
                "monthly_limit": 2000,
                "burst_limit": 10,
                "concurrent_analyses": 3
            },
            "enterprise": {
                "daily_limit": 1000,
                "hourly_limit": 200,
                "monthly_limit": 25000,
                "burst_limit": 50,
                "concurrent_analyses": 10
            }
        }
    
    @log_function("INFO", "RATE_LIMITER_INIT_OK")
    async def initialize(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = aioredis.from_url(
                settings.redis_url,
                decode_responses=True,
                retry_on_timeout=True
            )
            # Test connection
            await self.redis_client.ping()
            print("Rate limiter connected to Redis")
        except Exception as e:
            print(f"Redis connection failed, using local cache: {e}")
            self.redis_client = None
    
    @log_function("METRIC", "CHECK_LIMIT_OK")
    async def check_limit(self, user_id: str, tier: str) -> bool:
        """
        Check if user can make a request within rate limits.
        
        Args:
            user_id: User identifier
            tier: User subscription tier
            
        Returns:
            True if request is allowed, False if rate limited
        """
        limits = self.tier_limits.get(tier, self.tier_limits["free"])
        current_time = int(time.time())
        
        # Check all limit types
        checks = [
            ("burst", 60, limits["burst_limit"]),  # Per minute
            ("hourly", 3600, limits["hourly_limit"]),  # Per hour
            ("daily", 86400, limits["daily_limit"]),  # Per day
            ("monthly", 2592000, limits["monthly_limit"])  # Per month (30 days)
        ]
        
        for limit_type, window, limit in checks:
            if not await self._check_window_limit(user_id, limit_type, window, limit, current_time):
                return False
        
        # If all checks pass, increment counters
        for limit_type, window, limit in checks:
            await self._increment_counter(user_id, limit_type, window, current_time)
        
        return True
    
    @log_function("DEBUG", "WINDOW_LIMIT_OK")
    async def _check_window_limit(
        self, 
        user_id: str, 
        limit_type: str, 
        window: int, 
        limit: int, 
        current_time: int
    ) -> bool:
        """Check if user is within limits for a specific time window."""
        key = f"rate_limit:{user_id}:{limit_type}:{current_time // window}"
        
        if self.redis_client:
            try:
                current_count = await self.redis_client.get(key)
                current_count = int(current_count) if current_count else 0
                return current_count < limit
            except Exception:
                # Fallback to local cache
                pass
        
        # Local cache fallback
        current_count = self.local_cache.get(key, 0)
        return current_count < limit
    
    @log_function("DEBUG", "INCR_COUNTER_OK")
    async def _increment_counter(
        self, 
        user_id: str, 
        limit_type: str, 
        window: int, 
        current_time: int
    ):
        """Increment the counter for a specific time window."""
        key = f"rate_limit:{user_id}:{limit_type}:{current_time // window}"
        
        if self.redis_client:
            try:
                pipe = self.redis_client.pipeline()
                pipe.incr(key)
                pipe.expire(key, window)
                await pipe.execute()
                return
            except Exception:
                pass
        
        # Local cache fallback
        self.local_cache[key] = self.local_cache.get(key, 0) + 1
        
        # Clean up old entries periodically
        if len(self.local_cache) > 10000:
            cutoff_time = current_time - window
            keys_to_delete = [
                k for k in self.local_cache.keys() 
                if int(k.split(":")[-1]) < cutoff_time // window
            ]
            for k in keys_to_delete:
                del self.local_cache[k]
    
    @log_function("INFO", "GET_USAGE_OK")
    async def get_current_usage(self, user_id: str) -> Dict[str, int]:
        """Get current usage stats for a user."""
        current_time = int(time.time())
        usage = {}
        
        windows = [
            ("burst", 60),
            ("hourly", 3600),
            ("daily", 86400),
            ("monthly", 2592000)
        ]
        
        for limit_type, window in windows:
            key = f"rate_limit:{user_id}:{limit_type}:{current_time // window}"
            
            if self.redis_client:
                try:
                    count = await self.redis_client.get(key)
                    usage[limit_type] = int(count) if count else 0
                    continue
                except Exception:
                    pass
            
            # Fallback to local cache
            usage[limit_type] = self.local_cache.get(key, 0)
        
        return usage
    
    @log_function("ALERT", "RESET_LIMITS_OK")
    async def reset_user_limits(self, user_id: str) -> bool:
        """Reset all rate limits for a user (admin function)."""
        if self.redis_client:
            try:
                keys = await self.redis_client.keys(f"rate_limit:{user_id}:*")
                if keys:
                    await self.redis_client.delete(*keys)
                return True
            except Exception as e:
                print(f"Failed to reset Redis limits: {e}")
                return False
        
        # Local cache fallback
        keys_to_delete = [k for k in self.local_cache.keys() if k.startswith(f"rate_limit:{user_id}:")]
        for key in keys_to_delete:
            del self.local_cache[key]
        
        return True
    
    @log_function("DEBUG", "TIER_LIMITS_OK")
    def get_tier_limits(self, tier: str) -> Dict[str, int]:
        """Get rate limits for a specific tier."""
        return self.tier_limits.get(tier, self.tier_limits["free"]).copy()
    
    @log_function("METRIC", "CHK_CONC_OK")
    async def check_concurrent_analyses(self, user_id: str, tier: str) -> bool:
        """Check if user can start a new concurrent analysis."""
        limits = self.tier_limits.get(tier, self.tier_limits["free"])
        key = f"concurrent:{user_id}"
        
        if self.redis_client:
            try:
                current_count = await self.redis_client.get(key)
                current_count = int(current_count) if current_count else 0
                return current_count < limits["concurrent_analyses"]
            except Exception:
                pass
        
        # Local cache fallback
        current_count = self.local_cache.get(key, 0)
        return current_count < limits["concurrent_analyses"]
    
    @log_function("INFO", "START_ANALYSIS_OK")
    async def start_analysis(self, user_id: str) -> str:
        """Mark the start of an analysis and return analysis ID."""
        analysis_id = f"{user_id}:{int(time.time())}"
        key = f"concurrent:{user_id}"
        
        if self.redis_client:
            try:
                await self.redis_client.incr(key)
                await self.redis_client.expire(key, 3600)  # Expire after 1 hour
                
                # Store analysis start time
                analysis_key = f"analysis:{analysis_id}"
                await self.redis_client.set(analysis_key, int(time.time()), ex=3600)
                
                return analysis_id
            except Exception:
                pass
        
        # Local cache fallback
        self.local_cache[key] = self.local_cache.get(key, 0) + 1
        self.local_cache[f"analysis:{analysis_id}"] = int(time.time())
        
        return analysis_id
    
    @log_function("INFO", "FINISH_ANALYSIS_OK")
    async def finish_analysis(self, user_id: str, analysis_id: str):
        """Mark the completion of an analysis."""
        key = f"concurrent:{user_id}"
        
        if self.redis_client:
            try:
                current_count = await self.redis_client.get(key)
                if current_count and int(current_count) > 0:
                    await self.redis_client.decr(key)
                
                # Clean up analysis record
                analysis_key = f"analysis:{analysis_id}"
                await self.redis_client.delete(analysis_key)
                
                return
            except Exception:
                pass
        
        # Local cache fallback
        if key in self.local_cache and self.local_cache[key] > 0:
            self.local_cache[key] -= 1
        
        analysis_key = f"analysis:{analysis_id}"
        if analysis_key in self.local_cache:
            del self.local_cache[analysis_key]
    
    @log_function("ALERT", "CLEANUP_STALE_OK")
    async def cleanup_stale_analyses(self):
        """Clean up stale analysis records (should be run periodically)."""
        current_time = int(time.time())
        cutoff_time = current_time - 3600  # 1 hour ago
        
        if self.redis_client:
            try:
                # Get all analysis keys
                analysis_keys = await self.redis_client.keys("analysis:*")
                
                for key in analysis_keys:
                    start_time = await self.redis_client.get(key)
                    if start_time and int(start_time) < cutoff_time:
                        # Extract user_id from analysis key
                        analysis_id = key.replace("analysis:", "")
                        user_id = analysis_id.split(":")[0]
                        
                        # Decrement concurrent counter
                        concurrent_key = f"concurrent:{user_id}"
                        current_count = await self.redis_client.get(concurrent_key)
                        if current_count and int(current_count) > 0:
                            await self.redis_client.decr(concurrent_key)
                        
                        # Delete stale analysis record
                        await self.redis_client.delete(key)
                
                return
            except Exception as e:
                print(f"Failed to cleanup stale analyses in Redis: {e}")
        
        # Local cache cleanup
        keys_to_cleanup = []
        for key, start_time in self.local_cache.items():
            if key.startswith("analysis:") and isinstance(start_time, int) and start_time < cutoff_time:
                keys_to_cleanup.append(key)
        
        for key in keys_to_cleanup:
            analysis_id = key.replace("analysis:", "")
            user_id = analysis_id.split(":")[0]
            
            # Decrement concurrent counter
            concurrent_key = f"concurrent:{user_id}"
            if concurrent_key in self.local_cache and self.local_cache[concurrent_key] > 0:
                self.local_cache[concurrent_key] -= 1
            
            del self.local_cache[key]
    
    async def get_rate_limit_info(self, user_id: str, tier: str) -> Dict[str, any]:
        """Get comprehensive rate limit information for a user."""
        limits = self.get_tier_limits(tier)
        usage = await self.get_current_usage(user_id)
        
        # Calculate time until reset for each window
        current_time = int(time.time())
        reset_times = {}
        
        windows = [
            ("burst", 60),
            ("hourly", 3600),
            ("daily", 86400),
            ("monthly", 2592000)
        ]
        
        for limit_type, window in windows:
            next_reset = ((current_time // window) + 1) * window
            reset_times[f"{limit_type}_reset"] = datetime.fromtimestamp(next_reset)
        
        return {
            "tier": tier,
            "limits": limits,
            "current_usage": usage,
            "remaining": {
                limit_type: limits[f"{limit_type}_limit"] - usage.get(limit_type, 0)
                for limit_type in ["burst", "hourly", "daily", "monthly"]
            },
            "reset_times": reset_times,
            "is_rate_limited": any(
                usage.get(limit_type, 0) >= limits[f"{limit_type}_limit"]
                for limit_type in ["burst", "hourly", "daily", "monthly"]
            )
        }
