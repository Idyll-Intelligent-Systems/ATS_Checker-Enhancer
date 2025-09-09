"""
ZeX-ATS-AI JWT Authentication Handler
Secure JWT token management for user authentication.
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets

from src.core.config import settings


class JWTHandler:
    """JWT token management for authentication."""
    
    def __init__(self):
        """Initialize JWT handler with configuration."""
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Payload data to encode in the token
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT refresh token with longer expiration.
        
        Args:
            data: Payload data to encode in the token
            
        Returns:
            Encoded JWT refresh token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=30)  # 30 days for refresh tokens
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Decoded payload
            
        Raises:
            jwt.ExpiredSignatureError: Token has expired
            jwt.InvalidTokenError: Token is invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid token")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token
            
        Raises:
            jwt.InvalidTokenError: Invalid or expired refresh token
        """
        try:
            payload = self.verify_token(refresh_token)
            
            # Verify it's a refresh token
            if payload.get("type") != "refresh":
                raise jwt.InvalidTokenError("Not a refresh token")
            
            # Extract user info and create new access token
            user_data = {
                "sub": payload.get("sub"),
                "email": payload.get("email")
            }
            
            return self.create_access_token(user_data)
        
        except jwt.ExpiredSignatureError:
            raise jwt.InvalidTokenError("Refresh token expired")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid refresh token")
    
    def get_token_claims(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get token claims without verification (for debugging).
        
        Args:
            token: JWT token
            
        Returns:
            Decoded claims or None if invalid
        """
        try:
            # Decode without verification
            return jwt.decode(token, options={"verify_signature": False})
        except Exception:
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """
        Check if token is expired without raising exception.
        
        Args:
            token: JWT token to check
            
        Returns:
            True if expired, False otherwise
        """
        try:
            claims = self.get_token_claims(token)
            if not claims:
                return True
            
            exp = claims.get("exp")
            if not exp:
                return True
            
            return datetime.utcnow().timestamp() > exp
        except Exception:
            return True
    
    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """
        Get token expiration datetime.
        
        Args:
            token: JWT token
            
        Returns:
            Expiration datetime or None
        """
        try:
            claims = self.get_token_claims(token)
            if not claims:
                return None
            
            exp = claims.get("exp")
            if not exp:
                return None
            
            return datetime.fromtimestamp(exp)
        except Exception:
            return None
    
    def create_api_token(self, user_id: str, api_key_id: str) -> str:
        """
        Create a JWT token for API access.
        
        Args:
            user_id: User ID
            api_key_id: API key ID
            
        Returns:
            API JWT token
        """
        data = {
            "sub": user_id,
            "api_key_id": api_key_id,
            "type": "api"
        }
        
        # API tokens have longer expiration (1 year)
        expire_delta = timedelta(days=365)
        return self.create_access_token(data, expire_delta)
    
    def verify_api_token(self, token: str) -> Dict[str, Any]:
        """
        Verify API token and return claims.
        
        Args:
            token: API JWT token
            
        Returns:
            Token claims
            
        Raises:
            jwt.InvalidTokenError: Invalid API token
        """
        try:
            payload = self.verify_token(token)
            
            # Verify it's an API token
            if payload.get("type") != "api":
                raise jwt.InvalidTokenError("Not an API token")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.InvalidTokenError("API token expired")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid API token")


class SessionManager:
    """Manage user sessions and token blacklisting."""
    
    def __init__(self):
        """Initialize session manager."""
        self.blacklisted_tokens = set()  # In production, use Redis
        self.active_sessions = {}  # In production, use Redis
    
    def add_to_blacklist(self, token: str) -> None:
        """Add token to blacklist (logout)."""
        self.blacklisted_tokens.add(token)
    
    def is_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted."""
        return token in self.blacklisted_tokens
    
    def create_session(self, user_id: str, token: str) -> str:
        """Create a new user session."""
        session_id = secrets.token_urlsafe(32)
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "token": token,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate and update session."""
        session = self.active_sessions.get(session_id)
        if session:
            # Update last activity
            session["last_activity"] = datetime.utcnow()
            return session
        return None
    
    def invalidate_session(self, session_id: str) -> None:
        """Invalidate a specific session."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            # Blacklist associated token
            self.add_to_blacklist(session["token"])
            # Remove session
            del self.active_sessions[session_id]
    
    def invalidate_user_sessions(self, user_id: str) -> None:
        """Invalidate all sessions for a user."""
        sessions_to_remove = []
        
        for session_id, session_data in self.active_sessions.items():
            if session_data["user_id"] == user_id:
                # Blacklist token
                self.add_to_blacklist(session_data["token"])
                sessions_to_remove.append(session_id)
        
        # Remove sessions
        for session_id in sessions_to_remove:
            del self.active_sessions[session_id]
    
    def cleanup_expired_sessions(self) -> None:
        """Remove expired sessions."""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            # Sessions expire after 24 hours of inactivity
            if current_time - session_data["last_activity"] > timedelta(hours=24):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.invalidate_session(session_id)


class PasswordManager:
    """Password security utilities."""
    
    @staticmethod
    def generate_secure_password(length: int = 16) -> str:
        """Generate a cryptographically secure password."""
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def check_password_strength(password: str) -> Dict[str, Any]:
        """
        Check password strength and return analysis.
        
        Args:
            password: Password to analyze
            
        Returns:
            Dictionary with strength analysis
        """
        score = 0
        feedback = []
        requirements = {
            "length": len(password) >= 8,
            "uppercase": any(c.isupper() for c in password),
            "lowercase": any(c.islower() for c in password),
            "digit": any(c.isdigit() for c in password),
            "special": any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        }
        
        # Calculate score
        for req, met in requirements.items():
            if met:
                score += 20
            else:
                if req == "length":
                    feedback.append("Password must be at least 8 characters long")
                elif req == "uppercase":
                    feedback.append("Include at least one uppercase letter")
                elif req == "lowercase":
                    feedback.append("Include at least one lowercase letter")
                elif req == "digit":
                    feedback.append("Include at least one number")
                elif req == "special":
                    feedback.append("Include at least one special character")
        
        # Bonus points for length
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 10
        
        # Determine strength level
        if score >= 90:
            strength = "Very Strong"
        elif score >= 70:
            strength = "Strong"
        elif score >= 50:
            strength = "Medium"
        elif score >= 30:
            strength = "Weak"
        else:
            strength = "Very Weak"
        
        return {
            "score": min(score, 100),
            "strength": strength,
            "requirements": requirements,
            "feedback": feedback,
            "is_acceptable": score >= 70
        }
    
    @staticmethod
    def generate_reset_token() -> str:
        """Generate secure password reset token."""
        return secrets.token_urlsafe(32)


# Global instances
jwt_handler = JWTHandler()
session_manager = SessionManager()
password_manager = PasswordManager()
