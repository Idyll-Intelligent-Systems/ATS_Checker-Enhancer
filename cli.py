#!/usr/bin/env python3
"""
ZeX-ATS-AI Command Line Interface
Advanced CLI for system administration and operations.
"""

import asyncio
import sys
import argparse
from pathlib import Path
import json
from typing import Dict, List, Optional
import time
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.database import DatabaseManager
from src.core.config import settings
from src.utils.rate_limiter import RateLimiter
from src.services.user_service import UserService
from src.services.analytics_service import AnalyticsService
from src.models.user import User, UserRole, SubscriptionTier


class ZeXCLI:
    """Advanced CLI for ZeX-ATS-AI administration."""
    
    def __init__(self):
        """Initialize CLI."""
        self.db_manager = None
        self.rate_limiter = None
        self.user_service = None
        self.analytics_service = None
    
    async def initialize(self):
        """Initialize all services."""
        print("Initializing ZeX-ATS-AI CLI...")
        
        # Initialize database
        self.db_manager = DatabaseManager()
        await self.db_manager.initialize()
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter()
        await self.rate_limiter.initialize()
        
        # Initialize services
        self.user_service = UserService(self.db_manager)
        self.analytics_service = AnalyticsService()
        
        print("✅ CLI initialized successfully")
    
    async def create_user(self, email: str, password: str, role: str = "user", tier: str = "free") -> Dict:
        """Create a new user."""
        try:
            user_role = UserRole(role)
            subscription_tier = SubscriptionTier(tier)
            
            user = await self.user_service.create_user(
                email=email,
                password=password,
                role=user_role,
                subscription_tier=subscription_tier
            )
            
            return {
                "status": "success",
                "message": f"User created successfully: {user.email}",
                "user_id": str(user.id)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create user: {str(e)}"
            }
    
    async def list_users(self, limit: int = 50, offset: int = 0) -> Dict:
        """List all users with pagination."""
        try:
            users = await self.user_service.get_users_paginated(limit=limit, offset=offset)
            
            user_list = []
            for user in users:
                user_list.append({
                    "id": str(user.id),
                    "email": user.email,
                    "role": user.role.value,
                    "tier": user.subscription_tier.value,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "last_login": user.last_login.isoformat() if user.last_login else None
                })
            
            return {
                "status": "success",
                "users": user_list,
                "count": len(user_list)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to list users: {str(e)}"
            }
    
    async def update_user_tier(self, email: str, tier: str) -> Dict:
        """Update user subscription tier."""
        try:
            subscription_tier = SubscriptionTier(tier)
            user = await self.user_service.get_user_by_email(email)
            
            if not user:
                return {
                    "status": "error",
                    "message": f"User not found: {email}"
                }
            
            await self.user_service.update_subscription_tier(user.id, subscription_tier)
            
            return {
                "status": "success",
                "message": f"Updated {email} to {tier} tier"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to update user tier: {str(e)}"
            }
    
    async def get_user_analytics(self, days: int = 30) -> Dict:
        """Get user analytics for the specified period."""
        try:
            analytics = await self.analytics_service.get_user_analytics(days)
            
            return {
                "status": "success",
                "analytics": analytics
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get analytics: {str(e)}"
            }
    
    async def reset_rate_limits(self, email: str) -> Dict:
        """Reset rate limits for a user."""
        try:
            user = await self.user_service.get_user_by_email(email)
            
            if not user:
                return {
                    "status": "error",
                    "message": f"User not found: {email}"
                }
            
            success = await self.rate_limiter.reset_user_limits(str(user.id))
            
            if success:
                return {
                    "status": "success",
                    "message": f"Rate limits reset for {email}"
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to reset rate limits"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to reset rate limits: {str(e)}"
            }
    
    async def get_rate_limit_status(self, email: str) -> Dict:
        """Get current rate limit status for a user."""
        try:
            user = await self.user_service.get_user_by_email(email)
            
            if not user:
                return {
                    "status": "error",
                    "message": f"User not found: {email}"
                }
            
            rate_info = await self.rate_limiter.get_rate_limit_info(
                str(user.id), 
                user.subscription_tier.value
            )
            
            return {
                "status": "success",
                "rate_limit_info": rate_info
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get rate limit status: {str(e)}"
            }
    
    async def cleanup_system(self) -> Dict:
        """Run system cleanup tasks."""
        try:
            # Clean up stale analyses
            await self.rate_limiter.cleanup_stale_analyses()
            
            # Clean up expired sessions (if implemented)
            # await self.user_service.cleanup_expired_sessions()
            
            # Clean up old analytics data (if needed)
            # await self.analytics_service.cleanup_old_data()
            
            return {
                "status": "success",
                "message": "System cleanup completed successfully"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"System cleanup failed: {str(e)}"
            }
    
    async def get_system_status(self) -> Dict:
        """Get overall system status."""
        try:
            # Database status
            try:
                await self.db_manager.database.fetch_one("SELECT 1")
                db_status = "healthy"
            except Exception:
                db_status = "unhealthy"
            
            # Redis status
            try:
                if self.rate_limiter.redis_client:
                    await self.rate_limiter.redis_client.ping()
                    redis_status = "healthy"
                else:
                    redis_status = "using_fallback"
            except Exception:
                redis_status = "unhealthy"
            
            # User count
            total_users = await self.user_service.get_user_count()
            active_users = await self.user_service.get_active_user_count()
            
            return {
                "status": "success",
                "system_status": {
                    "database": db_status,
                    "redis": redis_status,
                    "total_users": total_users,
                    "active_users": active_users,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get system status: {str(e)}"
            }
    
    async def backup_database(self, output_path: str) -> Dict:
        """Create a database backup."""
        try:
            # This would typically use pg_dump or similar
            # For now, just return success message
            return {
                "status": "success",
                "message": f"Database backup would be created at {output_path}",
                "note": "Backup functionality needs to be implemented with pg_dump"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Backup failed: {str(e)}"
            }
    
    def print_result(self, result: Dict):
        """Print CLI command result in a formatted way."""
        if result["status"] == "success":
            print(f"✅ {result.get('message', 'Success')}")
            
            # Print additional data if present
            for key, value in result.items():
                if key not in ["status", "message"]:
                    if isinstance(value, (dict, list)):
                        print(f"\n{key.title()}:")
                        print(json.dumps(value, indent=2, default=str))
                    else:
                        print(f"{key.title()}: {value}")
        else:
            print(f"❌ {result.get('message', 'Error occurred')}")


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="ZeX-ATS-AI CLI Administration Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # User management commands
    user_parser = subparsers.add_parser("user", help="User management commands")
    user_subparsers = user_parser.add_subparsers(dest="user_action")
    
    # Create user
    create_user_parser = user_subparsers.add_parser("create", help="Create a new user")
    create_user_parser.add_argument("email", help="User email")
    create_user_parser.add_argument("password", help="User password")
    create_user_parser.add_argument("--role", default="user", help="User role (user, admin)")
    create_user_parser.add_argument("--tier", default="free", help="Subscription tier (free, pro, enterprise)")
    
    # List users
    list_users_parser = user_subparsers.add_parser("list", help="List users")
    list_users_parser.add_argument("--limit", type=int, default=50, help="Number of users to list")
    list_users_parser.add_argument("--offset", type=int, default=0, help="Offset for pagination")
    
    # Update user tier
    update_tier_parser = user_subparsers.add_parser("update-tier", help="Update user subscription tier")
    update_tier_parser.add_argument("email", help="User email")
    update_tier_parser.add_argument("tier", help="New subscription tier")
    
    # Rate limiting commands
    rate_parser = subparsers.add_parser("rate", help="Rate limiting commands")
    rate_subparsers = rate_parser.add_subparsers(dest="rate_action")
    
    # Reset rate limits
    reset_parser = rate_subparsers.add_parser("reset", help="Reset user rate limits")
    reset_parser.add_argument("email", help="User email")
    
    # Get rate limit status
    status_parser = rate_subparsers.add_parser("status", help="Get user rate limit status")
    status_parser.add_argument("email", help="User email")
    
    # System commands
    system_parser = subparsers.add_parser("system", help="System management commands")
    system_subparsers = system_parser.add_subparsers(dest="system_action")
    
    # System status
    system_subparsers.add_parser("status", help="Get system status")
    
    # System cleanup
    system_subparsers.add_parser("cleanup", help="Run system cleanup")
    
    # Analytics commands
    analytics_parser = subparsers.add_parser("analytics", help="Analytics commands")
    analytics_parser.add_argument("--days", type=int, default=30, help="Number of days for analytics")
    
    # Backup commands
    backup_parser = subparsers.add_parser("backup", help="Create database backup")
    backup_parser.add_argument("output", help="Output path for backup file")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    cli = ZeXCLI()
    await cli.initialize()
    
    try:
        # Execute command
        if args.command == "user":
            if args.user_action == "create":
                result = await cli.create_user(args.email, args.password, args.role, args.tier)
            elif args.user_action == "list":
                result = await cli.list_users(args.limit, args.offset)
            elif args.user_action == "update-tier":
                result = await cli.update_user_tier(args.email, args.tier)
            else:
                print("Unknown user action")
                return
        
        elif args.command == "rate":
            if args.rate_action == "reset":
                result = await cli.reset_rate_limits(args.email)
            elif args.rate_action == "status":
                result = await cli.get_rate_limit_status(args.email)
            else:
                print("Unknown rate action")
                return
        
        elif args.command == "system":
            if args.system_action == "status":
                result = await cli.get_system_status()
            elif args.system_action == "cleanup":
                result = await cli.cleanup_system()
            else:
                print("Unknown system action")
                return
        
        elif args.command == "analytics":
            result = await cli.get_user_analytics(args.days)
        
        elif args.command == "backup":
            result = await cli.backup_database(args.output)
        
        else:
            print("Unknown command")
            return
        
        # Print result
        cli.print_result(result)
        
    except Exception as e:
        print(f"❌ Command failed: {str(e)}")
        sys.exit(1)
    
    finally:
        # Cleanup
        if cli.db_manager:
            await cli.db_manager.close()


if __name__ == "__main__":
    asyncio.run(main())
