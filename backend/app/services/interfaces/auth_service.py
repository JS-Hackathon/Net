from typing import Protocol, Any
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

class IAuthService(Protocol):
    async def register_user(
        self, 
        payload: UserRegisterRequest, 
        ip_address: str | None = None, 
        user_agent: str | None = None
    ) -> AuthResponseData:
        """Đăng ký tài khoản người dùng mới.

        Args:
            payload (UserRegisterRequest): Dữ liệu yêu cầu đăng ký.
            ip_address (str | None): Địa chỉ IP thực hiện yêu cầu.
            user_agent (str | None): Thiết bị thực hiện yêu cầu.

        Returns:
            AuthResponseData: Thông tin tài khoản cùng cặp token.
        """
        ...

    async def login_user(
        self, 
        payload: UserLoginRequest, 
        ip_address: str | None = None, 
        user_agent: str | None = None
    ) -> AuthResponseData:
        """Đăng nhập bằng email và mật khẩu.

        Args:
            payload (UserLoginRequest): Dữ liệu yêu cầu đăng nhập.
            ip_address (str | None): Địa chỉ IP thực hiện yêu cầu.
            user_agent (str | None): Thiết bị thực hiện yêu cầu.

        Returns:
            AuthResponseData: Thông tin tài khoản cùng cặp token.
        """
        ...

    async def google_oauth_login(
        self, 
        code: str, 
        ip_address: str | None = None, 
        user_agent: str | None = None
    ) -> AuthResponseData:
        """Đăng nhập qua tài khoản Google.

        Args:
            code (str): Authorization code từ Google.
            ip_address (str | None): Địa chỉ IP thực hiện yêu cầu.
            user_agent (str | None): Thiết bị thực hiện yêu cầu.

        Returns:
            AuthResponseData: Thông tin tài khoản cùng cặp token.
        """
        ...

    async def refresh_token_session(
        self, 
        payload: TokenRefreshRequest, 
        ip_address: str | None = None, 
        user_agent: str | None = None
    ) -> TokenRefreshResponseData:
        """Làm mới access token và refresh token.

        Args:
            payload (TokenRefreshRequest): Refresh token hiện tại.
            ip_address (str | None): Địa chỉ IP thực hiện yêu cầu.
            user_agent (str | None): Thiết bị thực hiện yêu cầu.

        Returns:
            TokenRefreshResponseData: Cặp token mới.
        """
        ...

    async def logout_user(
        self, 
        refresh_token: str, 
        user_id: Any, 
        ip_address: str | None = None, 
        user_agent: str | None = None
    ) -> bool:
        """Đăng xuất người dùng và thu hồi token.

        Args:
            refresh_token (str): Refresh token cần thu hồi.
            user_id (Any): ID của người dùng đăng xuất.
            ip_address (str | None): Địa chỉ IP thực hiện yêu cầu.
            user_agent (str | None): Thiết bị thực hiện yêu cầu.

        Returns:
            bool: Kết quả đăng xuất.
        """
        ...

    async def forgot_password(
        self, 
        payload: ForgotPasswordRequest, 
        ip_address: str | None = None, 
        user_agent: str | None = None
    ) -> bool:
        """Yêu cầu gửi mã đặt lại mật khẩu.

        Args:
            payload (ForgotPasswordRequest): Địa chỉ email nhận mã.
            ip_address (str | None): Địa chỉ IP thực hiện yêu cầu.
            user_agent (str | None): Thiết bị thực hiện yêu cầu.

        Returns:
            bool: Kết quả gửi yêu cầu.
        """
        ...

    async def reset_password(
        self, 
        payload: ResetPasswordRequest, 
        ip_address: str | None = None, 
        user_agent: str | None = None
    ) -> bool:
        """Đặt lại mật khẩu mới bằng mã thông báo.

        Args:
            payload (ResetPasswordRequest): Mã thông báo và mật khẩu mới.
            ip_address (str | None): Địa chỉ IP thực hiện yêu cầu.
            user_agent (str | None): Thiết bị thực hiện yêu cầu.

        Returns:
            bool: Kết quả cập nhật mật khẩu.
        """
        ...

    async def update_profile(
        self, 
        user_id: Any, 
        payload: UserProfileUpdateRequest
    ) -> UserProfileResponse:
        """Cập nhật thông tin hồ sơ của người dùng.

        Args:
            user_id (Any): ID của người dùng cần cập nhật.
            payload (UserProfileUpdateRequest): Thông tin cập nhật.

        Returns:
            UserProfileResponse: Hồ sơ người dùng sau cập nhật.
        """
        ...
