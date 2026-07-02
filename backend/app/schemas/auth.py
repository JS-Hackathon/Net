import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re

class UserProfileResponse(BaseModel):
    id: uuid.UUID = Field(..., description="ID của người dùng")
    email: str = Field(..., description="Địa chỉ email", examples=["user@example.com"])
    full_name: str = Field(..., description="Họ và tên người dùng", examples=["Nguyễn Văn A"])
    role: str = Field(..., description="Vai trò của người dùng", examples=["candidate"])
    avatar_url: str | None = Field(default=None, description="Đường dẫn ảnh đại diện")
    email_verified: bool = Field(..., description="Trạng thái xác thực email")
    is_active: bool = Field(..., description="Trạng thái tài khoản hoạt động")
    created_at: datetime = Field(..., description="Thời gian tạo tài khoản")

    model_config = ConfigDict(from_attributes=True)

class UserRegisterRequest(BaseModel):
    email: str = Field(..., description="Địa chỉ email đăng ký", examples=["user@example.com"])
    password: str = Field(..., description="Mật khẩu đăng ký (tối thiểu 8 ký tự, 1 hoa, 1 thường, 1 số, 1 đặc biệt)")
    full_name: str = Field(..., description="Họ và tên đầy đủ", min_length=2, max_length=100, examples=["Nguyễn Văn A"])
    terms_accepted: bool = Field(..., description="Chấp nhận điều khoản dịch vụ")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, v):
            raise ValueError("Email không đúng định dạng")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Mật khẩu phải chứa ít nhất 8 ký tự")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Mật khẩu phải chứa ít nhất 1 chữ cái viết hoa")
        if not re.search(r"[a-z]", v):
            raise ValueError("Mật khẩu phải chứa ít nhất 1 chữ cái viết thường")
        if not re.search(r"\d", v):
            raise ValueError("Mật khẩu phải chứa ít nhất 1 chữ số")
        if not re.search(r"[@$!%*?&]", v):
            raise ValueError("Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt (@$!%*?&)")
        return v

    @field_validator("terms_accepted")
    @classmethod
    def validate_terms(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Bạn phải đồng ý với điều khoản dịch vụ")
        return v

class UserLoginRequest(BaseModel):
    email: str = Field(..., description="Địa chỉ email đăng nhập", examples=["user@example.com"])
    password: str = Field(..., description="Mật khẩu đăng nhập")
    remember_me: bool = Field(default=False, description="Tùy chọn ghi nhớ phiên đăng nhập")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.lower()

class GoogleLoginRequest(BaseModel):
    google_token: str = Field(..., description="Token nhận từ Google OAuth2")
    device_info: str | None = Field(default=None, description="Thông tin thiết bị (Trình duyệt/Hệ điều hành)")

class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="Token để làm mới phiên đăng nhập")

class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., description="Email nhận liên kết khôi phục mật khẩu", examples=["user@example.com"])

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.lower()

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., description="Token khôi phục nhận qua email")
    new_password: str = Field(..., description="Mật khẩu mới (tối thiểu 8 ký tự, tuân thủ độ phức tạp mật khẩu)")

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Mật khẩu phải chứa ít nhất 8 ký tự")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Mật khẩu phải chứa ít nhất 1 chữ cái viết hoa")
        if not re.search(r"[a-z]", v):
            raise ValueError("Mật khẩu phải chứa ít nhất 1 chữ cái viết thường")
        if not re.search(r"\d", v):
            raise ValueError("Mật khẩu phải chứa ít nhất 1 chữ số")
        if not re.search(r"[@$!%*?&]", v):
            raise ValueError("Mật khẩu phải chứa ít nhất 1 ký tự đặc biệt (@$!%*?&)")
        return v

class UserProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, description="Cập nhật họ và tên", min_length=2, max_length=100)
    avatar_url: str | None = Field(default=None, description="Cập nhật đường dẫn ảnh đại diện")

# Generic Wrappers for API responses
class AuthResponseData(BaseModel):
    user: UserProfileResponse = Field(..., description="Thông tin hồ sơ người dùng")
    access_token: str = Field(..., description="JWT Access Token")
    refresh_token: str = Field(..., description="JWT Refresh Token")
    expires_in: int = Field(..., description="Thời gian hết hạn của Access Token (giây)")
    is_new_user: bool | None = Field(default=None, description="Đánh dấu người dùng mới đăng ký qua OAuth")

class TokenRefreshResponseData(BaseModel):
    access_token: str = Field(..., description="JWT Access Token mới")
    refresh_token: str = Field(..., description="JWT Refresh Token mới")
    expires_in: int = Field(..., description="Thời gian hết hạn của Access Token mới (giây)")

class MessageResponseData(BaseModel):
    message: str = Field(..., description="Thông điệp thông báo kết quả", examples=["Thao tác thành công"])

class RegisterResponse(BaseModel):
    success: bool = Field(default=True, description="Trạng thái phản hồi thành công")
    data: AuthResponseData = Field(..., description="Dữ liệu kết quả đăng ký")

class LoginResponse(BaseModel):
    success: bool = Field(default=True, description="Trạng thái phản hồi thành công")
    data: AuthResponseData = Field(..., description="Dữ liệu kết quả đăng nhập")

class GoogleLoginResponse(BaseModel):
    success: bool = Field(default=True, description="Trạng thái phản hồi thành công")
    data: AuthResponseData = Field(..., description="Dữ liệu kết quả đăng nhập Google")

class TokenRefreshResponse(BaseModel):
    success: bool = Field(default=True, description="Trạng thái phản hồi thành công")
    data: TokenRefreshResponseData = Field(..., description="Dữ liệu kết quả làm mới token")

class MessageResponse(BaseModel):
    success: bool = Field(default=True, description="Trạng thái phản hồi thành công")
    data: MessageResponseData = Field(..., description="Thông điệp phản hồi từ máy chủ")

class UserMeResponse(BaseModel):
    success: bool = Field(default=True, description="Trạng thái phản hồi thành công")
    data: dict[str, UserProfileResponse] = Field(..., description="Thông tin hồ sơ người dùng hiện tại")
