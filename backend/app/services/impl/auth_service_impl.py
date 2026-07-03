import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.exceptions.base import AuthenticationError, NotFoundError, ValidationError
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.password_reset_token import PasswordResetToken
from app.models.auth_log import AuthLog
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    GoogleLoginRequest,
    TokenRefreshRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserProfileUpdateRequest,
    AuthResponseData,
    TokenRefreshResponseData,
    UserProfileResponse
)
from app.services.interfaces.auth_service import IAuthService

class AuthServiceImpl(IAuthService):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _write_auth_log(
        self, 
        event_type: str, 
        success: bool, 
        user_id: uuid.UUID | None = None, 
        ip_address: str | None = None, 
        user_agent: str | None = None, 
        error_message: str | None = None
    ) -> None:
        """Ghi nhận sự kiện xác thực vào nhật ký hệ thống."""
        auth_log = AuthLog(
            user_id=user_id,
            event_type=event_type,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            error_message=error_message
        )
        self.db.add(auth_log)
        await self.db.flush()

    async def register_user(
        self, 
        payload: UserRegisterRequest, 
        ip_address: str | None = None, 
        user_agent: str | None = None
    ) -> AuthResponseData:
        # Check if email exists
        stmt = select(User).where(User.email == payload.email)
        result = await self.db.execute(stmt)
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            await self._write_auth_log(
                event_type="register",
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message="Email already exists"
            )
            raise ValidationError(message="Email này đã được sử dụng")

        # Create user
        hashed_password = get_password_hash(payload.password)
        new_user = User(
            email=payload.email,
            password_hash=hashed_password,
            full_name=payload.full_name,
            role="candidate",
            email_verified=True,  # Default to True for hackathon convenience
            is_active=True
        )
        self.db.add(new_user)
        await self.db.flush()

        # Generate tokens
        access_token = create_access_token(
            user_id=new_user.id,
            role=new_user.role,
            email=new_user.email,
            full_name=new_user.full_name
        )
        refresh_token_val = create_refresh_token(user_id=new_user.id)
        
        # Save refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        db_refresh_token = RefreshToken(
            user_id=new_user.id,
            token_hash=refresh_token_val,
            expires_at=expires_at,
            device_info=user_agent,
            ip_address=ip_address
        )
        self.db.add(db_refresh_token)

        # Log event
        await self._write_auth_log(
            event_type="register",
            success=True,
            user_id=new_user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return AuthResponseData(
            user=UserProfileResponse.model_validate(new_user),
            access_token=access_token,
            refresh_token=refresh_token_val,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    async def login_user(
        self, 
        payload: UserLoginRequest, 
        ip_address: str | None = None, 
        user_agent: str | None = None
    ) -> AuthResponseData:
        stmt = select(User).where(User.email == payload.email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            await self._write_auth_log(
                event_type="login",
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message="User not found"
            )
            raise AuthenticationError("Email hoặc mật khẩu không chính xác.")

        # Check account lock status
        now_utc = datetime.now(timezone.utc)
        if user.locked_until and user.locked_until > now_utc:
            remaining_mins = int((user.locked_until - now_utc).total_seconds() / 60) + 1
            await self._write_auth_log(
                event_type="login",
                success=False,
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message="Account locked"
            )
            raise AuthenticationError(f"Tài khoản của bạn đã bị khóa tạm thời do nhập sai quá nhiều lần. Vui lòng thử lại sau {remaining_mins} phút.")

        # Verify password
        if not user.password_hash or not verify_password(payload.password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = now_utc + timedelta(minutes=15)
                error_msg = "Tài khoản bị khóa 15 phút do nhập sai 5 lần."
            else:
                error_msg = f"Sai mật khẩu. Lần thử {user.failed_login_attempts}/5."

            await self.db.flush()
            await self._write_auth_log(
                event_type="login",
                success=False,
                user_id=user.id,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message=error_msg
            )
            await self.db.commit()  # Lưu lại số lần đăng nhập sai và log
            raise AuthenticationError("Email hoặc mật khẩu không chính xác.")

        # Reset failed attempts
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = now_utc
        await self.db.flush()

        # Generate tokens
        access_token = create_access_token(
            user_id=user.id,
            role=user.role,
            email=user.email,
            full_name=user.full_name
        )
        refresh_token_val = create_refresh_token(user_id=user.id)
        
        # Save refresh token
        expires_at = now_utc + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        db_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=refresh_token_val,
            expires_at=expires_at,
            device_info=user_agent,
            ip_address=ip_address
        )
        self.db.add(db_refresh_token)

        # Log event
        await self._write_auth_log(
            event_type="login",
            success=True,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return AuthResponseData(
            user=UserProfileResponse.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token_val,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    async def google_oauth_login(
        self, 
        code: str, 
        ip_address: str | None = None, 
        user_agent: str | None = None
    ) -> AuthResponseData:
        # Default or mock sign in fallback
        email = None
        name = None
        google_id = None
        avatar_url = None

        if code.startswith("mock_") or not settings.GOOGLE_CLIENT_ID:
            # Under dev/mock mode
            email = code.replace("mock_", "")
            if "@" not in email:
                email = f"{email}@gmail.com"
            name = email.split("@")[0].capitalize()
            google_id = f"g_{code}"
        else:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    # 1. Exchange code for tokens
                    token_data = {
                        "code": code,
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                        "grant_type": "authorization_code"
                    }
                    token_resp = await client.post("https://oauth2.googleapis.com/token", data=token_data)
                    if token_resp.status_code != 200:
                        raise AuthenticationError("Lỗi khi trao đổi Authorization Code với Google")
                    
                    token_json = token_resp.json()
                    access_token = token_json.get("access_token")
                    
                    # 2. Get user info
                    user_resp = await client.get(
                        "https://www.googleapis.com/oauth2/v3/userinfo",
                        headers={"Authorization": f"Bearer {access_token}"}
                    )
                    if user_resp.status_code != 200:
                        raise AuthenticationError("Không thể lấy thông tin người dùng từ Google")
                        
                    user_info = user_resp.json()
                    email = user_info.get("email")
                    name = user_info.get("name", email.split("@")[0] if email else None)
                    google_id = user_info.get("sub")
                    avatar_url = user_info.get("picture")
                    
            except Exception as e:
                await self._write_auth_log(
                    event_type="google_login",
                    success=False,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    error_message=f"Google code exchange exception: {str(e)}"
                )
                raise AuthenticationError("Xác thực qua tài khoản Google thất bại")

        if not email or not google_id:
            raise AuthenticationError("Không tìm thấy thông tin email trong tài khoản Google")

        # Find or create user
        stmt = select(User).where((User.google_id == google_id) | (User.email == email))
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        is_new_user = False

        if not user:
            # Create user automatically
            user = User(
                email=email,
                google_id=google_id,
                full_name=name,
                avatar_url=avatar_url,
                role="candidate",
                email_verified=True,
                is_active=True
            )
            self.db.add(user)
            await self.db.flush()
            is_new_user = True
        else:
            # Link Google account if not linked
            if not user.google_id:
                user.google_id = google_id
            if avatar_url:
                user.avatar_url = avatar_url
            await self.db.flush()

        # Update last login
        user.last_login = datetime.now(timezone.utc)
        await self.db.flush()

        # Generate tokens
        access_token = create_access_token(
            user_id=user.id,
            role=user.role,
            email=user.email,
            full_name=user.full_name
        )
        refresh_token_val = create_refresh_token(user_id=user.id)
        
        # Save refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        db_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=refresh_token_val,
            expires_at=expires_at,
            device_info=user_agent,
            ip_address=ip_address
        )
        self.db.add(db_refresh_token)

        # Log event
        await self._write_auth_log(
            event_type="google_login",
            success=True,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return AuthResponseData(
            user=UserProfileResponse.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token_val,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            is_new_user=is_new_user
        )

    async def refresh_token_session(
        self, 
        payload: TokenRefreshRequest, 
        ip_address: str | None = None, 
        user_agent: str | None = None
    ) -> TokenRefreshResponseData:
        # Decode & Verify token values
        try:
            token_claims = decode_token(payload.refresh_token)
            if token_claims.get("type") != "refresh":
                raise AuthenticationError("Token không hợp lệ")
        except Exception:
            raise AuthenticationError("Refresh token không hợp lệ hoặc đã hết hạn")

        # Find in database
        stmt = select(RefreshToken).where(
            (RefreshToken.token_hash == payload.refresh_token) & 
            (RefreshToken.is_revoked == False)
        )
        result = await self.db.execute(stmt)
        db_token = result.scalar_one_or_none()

        if not db_token or db_token.expires_at < datetime.now(timezone.utc):
            if db_token:
                db_token.is_revoked = True
                await self.db.flush()
            raise AuthenticationError("Refresh token đã hết hạn hoặc bị thu hồi")

        # Find user
        stmt_user = select(User).where(User.id == db_token.user_id)
        res_user = await self.db.execute(stmt_user)
        user = res_user.scalar_one_or_none()

        if not user or not user.is_active:
            raise AuthenticationError("Người dùng không còn hoạt động")

        # Rotate tokens (revoke old, issue new pair)
        db_token.is_revoked = True
        await self.db.flush()

        access_token = create_access_token(
            user_id=user.id,
            role=user.role,
            email=user.email,
            full_name=user.full_name
        )
        new_refresh_val = create_refresh_token(user_id=user.id)
        
        # Save new refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        new_db_token = RefreshToken(
            user_id=user.id,
            token_hash=new_refresh_val,
            expires_at=expires_at,
            device_info=user_agent,
            ip_address=ip_address
        )
        self.db.add(new_db_token)

        # Log event
        await self._write_auth_log(
            event_type="refresh",
            success=True,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )

        return TokenRefreshResponseData(
            access_token=access_token,
            refresh_token=new_refresh_val,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    async def logout_user(
        self, 
        refresh_token: str, 
        user_id: Any, 
        ip_address: str | None = None, 
        user_agent: str | None = None
    ) -> bool:
        stmt = select(RefreshToken).where(
            (RefreshToken.token_hash == refresh_token) & 
            (RefreshToken.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        db_token = result.scalar_one_or_none()

        if db_token:
            db_token.is_revoked = True
            await self.db.flush()

        # Log event
        await self._write_auth_log(
            event_type="logout",
            success=True,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return True

    async def forgot_password(
        self, 
        payload: ForgotPasswordRequest, 
        ip_address: str | None = None, 
        user_agent: str | None = None
    ) -> bool:
        stmt = select(User).where(User.email == payload.email)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            # Silently succeed to prevent email enumeration attacks
            await self._write_auth_log(
                event_type="forgot_password",
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message=f"Email not found: {payload.email}"
            )
            return True

        # Generate recovery token
        token_val = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Save to DB
        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_val,
            expires_at=expires_at
        )
        self.db.add(reset_token)
        await self.db.flush()

        # Log recovery link in console for development
        print("=" * 60)
        print(f"DEVELOPMENT PASSWORD RESET LINK FOR USER: {user.email}")
        print(f"http://localhost:3000/reset-password?token={token_val}")
        print("=" * 60)

        # Log event
        await self._write_auth_log(
            event_type="forgot_password",
            success=True,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return True

    async def reset_password(
        self, 
        payload: ResetPasswordRequest, 
        ip_address: str | None = None, 
        user_agent: str | None = None
    ) -> bool:
        stmt = select(PasswordResetToken).where(
            (PasswordResetToken.token_hash == payload.token) & 
            (PasswordResetToken.used == False)
        )
        result = await self.db.execute(stmt)
        db_token = result.scalar_one_or_none()

        if not db_token or db_token.expires_at < datetime.now(timezone.utc):
            await self._write_auth_log(
                event_type="reset_password",
                success=False,
                ip_address=ip_address,
                user_agent=user_agent,
                error_message="Invalid or expired reset token"
            )
            raise ValidationError("Mã khôi phục mật khẩu không hợp lệ hoặc đã hết hạn")

        # Update user password
        stmt_user = select(User).where(User.id == db_token.user_id)
        res_user = await self.db.execute(stmt_user)
        user = res_user.scalar_one_or_none()

        if not user:
            raise NotFoundError("Không tìm thấy thông tin tài khoản người dùng")

        user.password_hash = get_password_hash(payload.new_password)
        db_token.used = True
        
        # Revoke all current active refresh tokens for safety
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user.id)
            .values(is_revoked=True)
        )
        await self.db.flush()

        # Log event
        await self._write_auth_log(
            event_type="reset_password",
            success=True,
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return True

    async def update_profile(
        self, 
        user_id: Any, 
        payload: UserProfileUpdateRequest
    ) -> UserProfileResponse:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundError("Không tìm thấy thông tin tài khoản người dùng")

        if payload.full_name is not None:
            user.full_name = payload.full_name
        if payload.avatar_url is not None:
            user.avatar_url = payload.avatar_url

        await self.db.flush()
        return UserProfileResponse.model_validate(user)
