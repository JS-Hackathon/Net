import logging
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import urllib.parse

logger = logging.getLogger(__name__)


from app.core.database import get_db
from app.core.dependencies import get_auth_service, get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    GoogleLoginRequest,
    TokenRefreshRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserProfileUpdateRequest,
    RegisterResponse,
    LoginResponse,
    GoogleLoginResponse,
    TokenRefreshResponse,
    MessageResponse,
    UserMeResponse,
    AuthResponseData,
    TokenRefreshResponseData,
    MessageResponseData,
    UserProfileResponse
)
from app.services.interfaces.auth_service import IAuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication - Hệ thống xác thực"]
)

@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Đăng ký tài khoản mới",
    description="Đăng ký tài khoản ứng viên (candidate) mới bằng email và mật khẩu."
)
async def register(
    request: Request,
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: IAuthService = Depends(get_auth_service)
) -> RegisterResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    data = await auth_service.register_user(
        payload=payload,
        ip_address=ip_address,
        user_agent=user_agent
    )
    await db.commit()
    return RegisterResponse(success=True, data=data)

@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Đăng nhập tài khoản",
    description="Đăng nhập bằng email và mật khẩu. Hỗ trợ cơ chế khóa tài khoản sau 5 lần nhập sai."
)
async def login(
    request: Request,
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: IAuthService = Depends(get_auth_service)
) -> LoginResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Gọi trực tiếp (không dùng async with db.begin()) vì service tự commit
    # trong trường hợp thất bại để lưu số lần đăng nhập sai và lockout
    data = await auth_service.login_user(
        payload=payload,
        ip_address=ip_address,
        user_agent=user_agent
    )
    await db.commit()
    return LoginResponse(success=True, data=data)

@router.get(
    "/google/login",
    summary="Chuyển hướng người dùng sang trang Đăng nhập Google",
    description="Sinh ra URL OAuth2 chứa Client ID và scope, sau đó redirect sang Google."
)
async def google_login_redirect():
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url)

@router.get(
    "/google/callback",
    summary="Nhận Authorization Code từ Google",
    description="Nhận authorization code, đổi lấy token và tự động tạo session/user."
)
async def google_callback(
    request: Request,
    code: str,
    db: AsyncSession = Depends(get_db),
    auth_service: IAuthService = Depends(get_auth_service)
):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    try:
        data = await auth_service.google_oauth_login(
            code=code,
            ip_address=ip_address,
            user_agent=user_agent
        )
        await db.commit()
        # Redirect về frontend kèm theo access_token và refresh_token
        redirect_url = f"{settings.FRONTEND_URL}/login-success?access_token={data.access_token}&refresh_token={data.refresh_token}"
        return RedirectResponse(redirect_url)
    except Exception as e:
        logger.exception("Google authentication callback failed:")
        await db.rollback()
        # Redirect về frontend kèm tham số lỗi (nếu cần)
        redirect_url = f"{settings.FRONTEND_URL}/login?error=google_auth_failed"
        return RedirectResponse(redirect_url)


@router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
    summary="Làm mới Access Token",
    description="Sử dụng Refresh Token còn hiệu lực để làm mới cặp Access/Refresh Token."
)
async def refresh_token(
    request: Request,
    payload: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: IAuthService = Depends(get_auth_service)
) -> TokenRefreshResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    data = await auth_service.refresh_token_session(
        payload=payload,
        ip_address=ip_address,
        user_agent=user_agent
    )
    await db.commit()
    return TokenRefreshResponse(success=True, data=data)

@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Đăng xuất người dùng",
    description="Thu hồi Refresh Token hiện tại để đăng xuất tài khoản an toàn."
)
async def logout(
    request: Request,
    payload: TokenRefreshRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    auth_service: IAuthService = Depends(get_auth_service)
) -> MessageResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    await auth_service.logout_user(
        refresh_token=payload.refresh_token,
        user_id=current_user.id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    await db.commit()
    return MessageResponse(
        success=True, 
        data=MessageResponseData(message="Đăng xuất thành công")
    )

@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Yêu cầu quên mật khẩu",
    description="Nhập email đăng ký để nhận liên kết/mã khôi phục tài khoản."
)
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: IAuthService = Depends(get_auth_service)
) -> MessageResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    await auth_service.forgot_password(
        payload=payload,
        ip_address=ip_address,
        user_agent=user_agent
    )
    await db.commit()
    return MessageResponse(
        success=True, 
        data=MessageResponseData(message="Nếu tài khoản tồn tại, email khôi phục mật khẩu đã được gửi")
    )

@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Đặt lại mật khẩu mới",
    description="Sử dụng mã đặt lại mật khẩu nhận được để cập nhật mật khẩu mới."
)
async def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: IAuthService = Depends(get_auth_service)
) -> MessageResponse:
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    await auth_service.reset_password(
        payload=payload,
        ip_address=ip_address,
        user_agent=user_agent
    )
    await db.commit()
    return MessageResponse(
        success=True, 
        data=MessageResponseData(message="Đặt lại mật khẩu thành công")
    )

@router.get(
    "/me",
    response_model=UserMeResponse,
    summary="Lấy thông tin tài khoản hiện tại",
    description="Trả về thông tin hồ sơ chi tiết của người dùng đang được đăng nhập."
)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserMeResponse:
    profile = UserProfileResponse.model_validate(current_user)
    return UserMeResponse(success=True, data={"user": profile})

@router.put(
    "/profile",
    response_model=UserMeResponse,
    summary="Cập nhật hồ sơ cá nhân",
    description="Cập nhật các thông tin cơ bản trong hồ sơ cá nhân (họ tên, ảnh đại diện)."
)
async def update_profile(
    payload: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    auth_service: IAuthService = Depends(get_auth_service)
) -> UserMeResponse:
    profile = await auth_service.update_profile(
        user_id=current_user.id,
        payload=payload
    )
    await db.commit()
    return UserMeResponse(success=True, data={"user": profile})
