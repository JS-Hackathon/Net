# Hướng Dẫn Chuẩn Phát Triển Backend (Python 3.12 + FastAPI)

Tài liệu này tổng hợp Tech Stack, cấu trúc thư mục, chuẩn đặt tên, thư viện sử dụng và thiết kế mẫu cho dự án Backend **ClassManager**, viết bằng **Python + FastAPI**. Đây là bản chuẩn hoá thay thế cho bản Spring Boot/Java trước đó, và thống nhất với skill `fastapi-backend-expert` đã có.

---

## 1. Tech Stack & Thư Viện Cốt Lõi (Dependencies)

### Core Technologies
* **Python Version**: 3.12 (LTS)
* **Web Framework**: FastAPI (>= 0.115)
* **ASGI Server**: Uvicorn (+ Gunicorn worker manager khi deploy production)
* **Database**: PostgreSQL (driver `asyncpg`) — hoặc MySQL (`aiomysql`) tuỳ môi trường, cấu hình qua `DB_URL`
* **Migration Tool**: Alembic
* **Package/Env Manager**: `venv` hoặc `uv`/`poetry`

### Thư Viện & Tiện Ích Trong `requirements.txt` / `pyproject.toml`

| Nhóm Thư Viện | Package | Mục Đích |
| :--- | :--- | :--- |
| **ORM & DB** | `sqlalchemy[asyncio]>=2.0` | ORM bất đồng bộ, giao tiếp Database. |
| **Migration** | `alembic` | Quản lý version schema database. |
| **Web & API** | `fastapi`, `uvicorn[standard]` | Xây dựng RESTful API (ASGI). |
| **Validation** | `pydantic>=2.0`, `pydantic-settings` | Validate dữ liệu đầu vào & đọc `.env`. |
| **Authentication** | `python-jose[cryptography]` (hoặc `pyjwt`) | Tạo và xác thực JSON Web Token (JWT). |
| **Password / OTP Hash** | `passlib[bcrypt]` | Băm mật khẩu và mã OTP. |
| **OAuth2** | `authlib` hoặc `httpx-oauth` | Tích hợp đăng nhập Google OAuth2. |
| **DB Driver (Postgres)** | `asyncpg` | Driver bất đồng bộ cho PostgreSQL. |
| **DB Driver (MySQL, nếu dùng)** | `aiomysql` | Driver bất đồng bộ cho MySQL. |
| **Mail** | `fastapi-mail` hoặc `aiosmtplib` | Gửi Email tự động (VD: gửi mã OTP). |
| **Scheduler** | `apscheduler` (in-process) hoặc `celery[redis]` + `celery beat` | Chạy job định kỳ (khoá điểm tuần, v.v.) |
| **Docs** | Tự động tích hợp sẵn trong FastAPI (`/docs`, `/redoc`) qua OpenAPI 3.1 | Tài liệu hoá API. |
| **Lint / Type-check** | `ruff`, `mypy` | Kiểm tra style & kiểu dữ liệu tĩnh. |
| **Testing** | `pytest`, `pytest-asyncio`, `httpx` (AsyncClient) | Unit Test & Integration Test. |
| **CORS** | `fastapi.middleware.cors.CORSMiddleware` | Cấu hình CORS built-in của FastAPI. |

---

## 2. Cấu Trúc Thư Mục Dự Án (Directory Structure)

Dự án tuân thủ **Clean/Layered Architecture**, tách biệt rõ Interface (Protocol) và Implementation (`impl`) ở tầng Service để đảm bảo Loose Coupling — tương đương tinh thần `IAuthService` / `AuthServiceImpl` bên Java, nhưng dùng `typing.Protocol` thay cho interface.

```text
backend/
├── pyproject.toml / requirements.txt   # Khai báo dependencies
├── alembic/                            # Thư mục migration (alembic init)
│   └── versions/
├── .env                                # Biến môi trường local (KHÔNG commit)
├── .env.example                        # Bản mẫu biến môi trường (commit lên Git)
├── app/
│   ├── main.py                         # Entry point, khởi tạo FastAPI app, mount router, middleware
│   │
│   ├── core/                           # Cấu hình hệ thống (settings, security, DB session, CORS, JWT)
│   │   ├── config.py                   # pydantic-settings BaseSettings
│   │   ├── security.py                 # require_role(), get_current_user(), JWT encode/decode
│   │   └── database.py                 # engine, async_session_factory, Base
│   │
│   ├── api/                            # FastAPI routers — nhận request, validate, gọi Service
│   │   └── v1/
│   │       ├── admin/
│   │       ├── teacher/
│   │       ├── leader/
│   │       └── student/
│   │
│   ├── models/                         # SQLAlchemy ORM models (tương đương entity/)
│   │   ├── user.py
│   │   └── point_log.py
│   │
│   ├── schemas/                        # Pydantic DTO (tương đương dto/)
│   │   ├── request/
│   │   └── response/
│   │
│   ├── repositories/                   # Data access layer (SQLAlchemy Session/AsyncSession)
│   │   ├── user_repository.py
│   │   └── point_log_repository.py
│   │
│   ├── services/                       # Business logic & transaction boundaries
│   │   ├── I_auth_service.py             # Protocol, PascalCase, kết thúc bằng "Service"
│   │   │                               # class AuthService(Protocol)
│   │   └── impl/                       # PascalCase, kết thúc bằng "Impl"
│   │       └── auth_service_impl.py    # class AuthServiceImpl
│   │
│   ├── exceptions/                     # Custom exception classes + global exception handler
│   │   ├── base.py                     # class AppException(Exception)
│   │   ├── auth_exceptions.py
│   │   └── handlers.py                 # register_exception_handlers(app)
│   │
│   ├── enums/                          # Enum định nghĩa kiểu dữ liệu cố định (Role, Status)
│   │   ├── role.py
│   │   └── user_status.py
│   │
│   └── scheduler/                      # APScheduler jobs / Celery beat tasks
│       └── weekly_lock_job.py
│
└── tests/                              # Unit/Integration Tests (pytest)
    └── test_auth.py
```

---

## 3. Chuẩn Đặt Tên & Quy Tắc Thiết Kế (Naming Conventions)

### 3.1. Quy Tắc Đặt Tên Module & Class (Python)

| Đối tượng | Quy tắc đặt tên | Ví dụ |
| :--- | :--- | :--- |
| **Module/File** | `snake_case`, số ít. | `user_repository.py`, `point_log.py` |
| **Model (ORM) Class** | PascalCase, số ít, trùng tên thực thể DB. | `User`, `Class`, `PointLog` |
| **Router file** | `snake_case`, biến router luôn đặt tên `router`. | `api/v1/leader/points.py` → `router = APIRouter(...)` |
| **Service Interface** | `Protocol`, PascalCase, kết thúc bằng `Service`. | `IAuthService`, `IPointService` (đặt trong `services/`) |
| **Service Impl Class** | PascalCase, kết thúc bằng `Impl`. | `AuthServiceImpl`, `PointServiceImpl` (đặt trong `services/impl/` )|
| **Repository Class** | PascalCase, kết thúc bằng `Repository`. | `UserRepository`, `PointLogRepository` |
| **Schema (DTO) Class** | PascalCase, kết thúc bằng `Request` hoặc `Response`. | `LoginRequest`, `UserResponse` |
| **Enum Class** | PascalCase, kế thừa `str, Enum` hoặc `enum.Enum`. | `Role`, `UserStatus` |
| **Custom Exception** | PascalCase, kết thúc bằng `Exception`. | `WeekAlreadyLockedException` |

> Lưu ý khác biệt so với Java: Python **không** dùng tiền tố `I` cho interface — dùng `typing.Protocol` thuần, không cần kế thừa tường minh ở lớp `Impl` (duck typing), nhưng vẫn nên khai báo `class AuthServiceImpl(AuthService):`-style hoặc kiểm tra bằng `isinstance` nếu cần runtime check (`@runtime_checkable`).

### 3.2. Quy Tắc Thiết Kế Database (SQLAlchemy)

1. **Tên bảng (`__tablename__`)**: viết thường toàn bộ, dạng **số nhiều**, `snake_case`.
   *Ví dụ*: `__tablename__ = "users"`, `__tablename__ = "course_classes"`
2. **Khoá chính (Primary Key)**: đặt tên dạng `{entity}_id`.
   *Ví dụ*: `user_id` trong bảng `users`, `class_id` trong bảng `classes`.
3. **Tên cột**: `snake_case`, viết thường toàn bộ.
   *Ví dụ*: `full_name`, `activated_at`.
4. **Text dài**: dùng `sqlalchemy.Text` (không giới hạn độ dài) thay cho `VARCHAR`.
5. **Dữ liệu JSON**: dùng `sqlalchemy.dialects.postgresql.JSONB` (Postgres) hoặc `sqlalchemy.JSON` (generic) để lưu trực tiếp `dict`/`list`.
6. **Thuộc tính Model**: khác với Java (camelCase), trong Python **thuộc tính và tên cột đều dùng `snake_case`** — không cần mapping riêng.
   *Ví dụ*: `full_name: Mapped[str] = mapped_column(String(100))`
7. **Bất biến `point_logs`**: bảng `point_logs` **chỉ INSERT**, tuyệt đối không `UPDATE`/`DELETE` (BR-POINT-01, BR-POINT-08) — repository layer không được cung cấp method update/delete cho bảng này.

### 3.3. Quy Tắc REST API & Request Validation

1. **Endpoint URLs**:
   * `kebab-case` nếu nhiều từ, viết thường toàn bộ.
   * Gom nhóm theo vai trò: `/api/v1/admin/...`, `/api/v1/teacher/...`, `/api/v1/leader/...`, `/api/v1/student/...`
   * *Ví dụ*: `POST /api/v1/auth/login`, `POST /api/v1/auth/send-otp`, `GET /api/v1/teacher/classes/{class_id}`
2. **Đầu ra chuẩn**:
   * Response thành công: trả trực tiếp Pydantic `response_model` (quy ước chuẩn FastAPI) — **không** bọc thêm wrapper `APIResponse<T>` như Java, trừ khi dự án chủ động chọn dùng wrapper.
   * Response lỗi: bắt buộc theo đúng format chuẩn hoá đã định nghĩa trong skill `fastapi-backend-expert` (mục 5: `timestamp`, `status`, `error`, `message`, `details`, `path`).
3. **Validation**: dùng Pydantic v2 `Field(...)`, `field_validator`, `pattern=` ngay tại Schema — FastAPI tự động validate khi khai báo type ở tham số hàm route, **không cần** annotation kiểu `@Valid` như Java.

---

## 4. Thiết Kế Mẫu Cho Dự Án (Template Classes)

### 4.1 Custom Exception Base (`exceptions/base.py`)

```python
class AppException(Exception):
    """Base exception cho toàn bộ business exceptions của hệ thống."""

    def __init__(self, message: str, status_code: int = 400, error_code: str = "BAD_REQUEST"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


class WeekAlreadyLockedException(AppException):
    def __init__(self, message: str = "This week points have already been locked."):
        super().__init__(message, status_code=409, error_code="WEEK_ALREADY_LOCKED")


class StudentNotInGroupException(AppException):
    def __init__(self, message: str = "Student is not in your group."):
        super().__init__(message, status_code=403, error_code="STUDENT_NOT_IN_GROUP")
```

### 4.2 Global Exception Handler (`exceptions/handlers.py`)

```python
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.exceptions.base import AppException


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": exc.status_code,
                "error": exc.error_code,
                "message": exc.message,
                "details": [],
                "path": str(request.url.path),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {"field": ".".join(str(loc) for loc in err["loc"][1:]), "message": err["msg"]}
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": 422,
                "error": "VALIDATION_ERROR",
                "message": "Invalid data",
                "details": details,
                "path": str(request.url.path),
            },
        )
```

### 4.3 Model Mẫu (`models/user.py`)

```python
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
from app.enums.role import Role
from app.enums.user_status import UserStatus


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role: Mapped[Role] = mapped_column(default=Role.STUDENT)
    status: Mapped[UserStatus] = mapped_column(default=UserStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

### 4.4 Schema Request Mẫu (`schemas/request/auth_request.py`)

```python
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=1, description="Họ tên đầy đủ")
    username: str = Field(..., min_length=4, max_length=30, description="Tên đăng nhập, 4-30 ký tự")
    email: EmailStr = Field(..., description="Email hợp lệ")
    password: str = Field(..., min_length=8, description="Mật khẩu tối thiểu 8 ký tự")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "full_name": "Nguyen Van A",
                    "username": "nguyenvana",
                    "email": "a@example.com",
                    "password": "SecurePass123",
                }
            ]
        }
    )
```

### 4.5 Repository Mẫu (`repositories/user_repository.py`)

```python
from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def exists_by_username(self, username: str) -> bool:
        stmt = select(exists().where(User.username == username))
        return bool(await self.session.scalar(stmt))

    async def exists_by_email(self, email: str) -> bool:
        stmt = select(exists().where(User.email == email))
        return bool(await self.session.scalar(stmt))

    async def find_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return await self.session.scalar(stmt)
```

### 4.6 Service Mẫu (`services/interfaces/auth_service.py` + `impl`)

```python
# services/interfaces/auth_service.py
from typing import Protocol
from app.schemas.request.auth_request import RegisterRequest
from app.schemas.response.auth_response import AuthResponse


class AuthService(Protocol):
    async def register(self, payload: RegisterRequest) -> AuthResponse:
        """Đăng ký tài khoản người dùng mới.

        Args:
            payload (RegisterRequest): Dữ liệu đăng ký.

        Returns:
            AuthResponse: Kết quả đăng ký.

        Raises:
            AppException: Nếu username hoặc email đã tồn tại.
        """
        ...
```

```python
# services/impl/auth_service_impl.py
from passlib.hash import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.base import AppException
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.request.auth_request import RegisterRequest
from app.schemas.response.auth_response import AuthResponse


class AuthServiceImpl:
    def __init__(self, session: AsyncSession, user_repository: UserRepository):
        self.session = session
        self.user_repository = user_repository

    async def register(self, payload: RegisterRequest) -> AuthResponse:
        if await self.user_repository.exists_by_username(payload.username):
            raise AppException("This username is already in use", 409, "USERNAME_TAKEN")
        if await self.user_repository.exists_by_email(payload.email):
            raise AppException("This email is already in use", 409, "EMAIL_TAKEN")

        async with self.session.begin():
            user = User(
                full_name=payload.full_name,
                username=payload.username,
                email=payload.email,
                password=bcrypt.hash(payload.password),
            )
            self.session.add(user)

        return AuthResponse(message="Register successfully")
```

### 4.7 Router Mẫu (`api/v1/auth.py`)

```python
from fastapi import APIRouter, Depends
from app.schemas.request.auth_request import RegisterRequest
from app.schemas.response.auth_response import AuthResponse
from app.services.interfaces.auth_service import AuthService
from app.core.security import get_auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=AuthResponse,
    summary="Đăng ký tài khoản mới",
    description="Đăng ký tài khoản người dùng local.",
)
async def register(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    # Router không chứa business logic — chỉ delegate cho Service
    return await auth_service.register(payload)
```

---

## 5. Cấu Hình Bảo Mật & JWT Claims

Chuỗi JWT sinh ra sau khi Authenticate bắt buộc chứa các claim sau (giữ nguyên như skill `fastapi-backend-expert`):

```json
{
  "sub": "id của user",
  "role": "TEACHER | STUDENT | LEADER | ADMIN | null",
  "class_id": "integer | null",
  "group_id": "integer | null",
  "school_id": "integer | null",
  "iat": 1770000000,
  "exp": 1770007200
}
```

* Access Token: trả trong response body.
* Refresh Token: lưu trong **HttpOnly Cookie** — không trả về trong body.
* OTP: lưu trong DB dưới dạng bcrypt hash (`passlib.hash.bcrypt`) — không lưu plain text.

---

## 6. File Cấu Hình Môi Trường

Đã được định nghĩa chi tiết trong skill `fastapi-backend-expert` (mục 8, `app/core/config.py` dùng `pydantic-settings`) — áp dụng nguyên trạng cho dự án, không định nghĩa lại `application.yml` kiểu Spring.

---

## 7. Chỉ Thị Thực Thi Cho Agents (Agent Directives)

Khi các Sub-Agent thực hiện viết mã nguồn cho backend Python, bắt buộc tuân thủ:

1. **Cấm tuyệt đối** dùng placeholder hoặc `# TODO: implement later`. Mọi hàm nghiệp vụ phải viết trọn vẹn logic từ đầu đến cuối.
2. Lỗi nghiệp vụ **không** được `try/except` nuốt lỗi rồi trả về `None`/response rỗng — phải định nghĩa class exception cụ thể kế thừa `AppException` và raise ra để `exceptions/handlers.py` xử lý tập trung.
3. Tuân thủ cấu trúc Clean/Layered Architecture đã định nghĩa (`api/` → `services/` → `repositories/` → `models/`), không inject Repository trực tiếp vào Router, không đặt business logic ở Router.
4. Không update trực tiếp cột tổng điểm (`total_point`) — luôn tính từ `point_logs` (BR-POINT-01/08).
5. Mọi endpoint phải có `tags`, `summary`, `description`; mọi field Schema phải có `description` (theo mục 11 của skill `fastapi-backend-expert`).