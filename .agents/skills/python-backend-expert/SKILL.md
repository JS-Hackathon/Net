---
name: fastapi-backend-expert
description: Train Agent to write REST API FastAPI (Python) for ClassManager — adhering to Clean Architecture, immutable audit log, JWT auth.
---

# Objective
Ensure the entire ClassManager Backend is written strictly according to the architecture, without violating immutable Business Rules (especially immutable point_logs), securing access by role, and maintaining consistent error responses.

---

## Instructions

### 1. Context Checklist
- All Python modules must reside in `backend/app/`
- Read `docs/SRS.md` and `docs/schema.sql` before writing any logic.
- Read `CLAUDE.md` to understand the mandatory Business Rules.

### 2. Architectural Rules & Project Structure (DO NOT violate)

**Standard Package Structure:**
All new Python modules must be organized in the correct packages under `backend/app/`:
- `core/`: System configuration (settings, security, database session, CORS, JWT).
- `api/`: FastAPI routers to receive requests, validate (via Pydantic), and delegate to Services.
  - Prefix by role: `api/v1/admin/`, `api/v1/teacher/`, `api/v1/leader/`, `api/v1/student/`
- `services/`: Core business logic, transaction boundaries:
  - Interface (Protocol, PascalCase, end with `Service`, start with `I`): `app.services.IAuthService`
  - `services/impl/`: Implementation (PascalCase, end with `Impl`): `app.services.impl.AuthServiceImpl`
- `repositories/`: Data access layer using SQLAlchemy `Session`/`AsyncSession`.
- `models/`: SQLAlchemy ORM models mapping to database tables.
- `schemas/`: Pydantic models (DTOs):
  - `schemas/request/`: Request payloads.
  - `schemas/response/`: Response payloads.
- `exceptions/`: Custom exception classes and a global exception handler (`app/exceptions/handlers.py`).
- `scheduler/`: Scheduled tasks and automation (APScheduler jobs or Celery beat tasks).

**Backend Feature Development Flow:**
When developing a new backend feature, adhere to the following sequence:
1. **Model**: Declare/update the SQLAlchemy model in the `models` package.
2. **Repository**: Create the repository class/functions in the `repositories` package. Use `selectinload`/`joinedload` to prevent N+1 queries if necessary.
3. **Service & Transaction**: Create the Service in the `services` package, define business logic, and handle transactions explicitly (`async with session.begin():` for mutations, plain read-only session for queries).
4. **Audit Logging Integration**: If the feature involves actions that require auditing (BR-AUDIT-02), integrate audit logging via SQLAlchemy event listeners (`before_flush`/`after_flush`) or call `AuditLogService` synchronously within the same transaction.
5. **Schemas & Validation**: Create Request/Response Pydantic schemas in the `schemas` package, applying validators (`Field(..., min_length=...)`, `field_validator`, `pattern=`).
6. **Router**: Create the router in the `api` package, use `Depends()` for the current user, and enforce access control using a `require_role(...)` dependency.
7. **Verify**: Run type checks and tests.

**Layer Conventions:**
**API/Router Layer:**
- Use `APIRouter(prefix="/api/v1/...")`
- DO NOT contain business logic — only receive requests, delegate to Services, and return responses.
- DO NOT inject Repositories directly into routers.
- Prefix endpoints by role: `/api/v1/admin/`, `/api/v1/teacher/`, `/api/v1/leader/`, `/api/v1/student/`

**Service Layer:**
- All business logic and transaction boundaries must reside here.
- DO NOT allow circular dependencies between Services.
- Raise custom exceptions — DO NOT return `None` in place of a real error.

**Repository Layer:**
- Use SQLAlchemy Core/ORM (prefer `AsyncSession` with `asyncpg`/`aiomysql`).
- For complex queries (multiple joins): use `selectinload`/`joinedload`/explicit `select(...).join(...)` to avoid N+1 queries.
- DO NOT build raw SQL strings with user input via f-strings/concatenation (SQL Injection risk) — always use parameter binding or the ORM query builder.

**Schema (DTO) Layer:**
- Separate Request schemas from Response schemas — DO NOT expose SQLAlchemy models directly to the API.
- Use Pydantic v2 (`BaseModel`, `model_config = ConfigDict(from_attributes=True)`).
- Validate Request schemas using Pydantic validators: `Field(min_length=...)`, `Field(pattern=...)`, `field_validator`.

### 3. Mandatory Business Rules

**Immutable Point Log (BR-POINT-01, BR-POINT-08):**
```python
# ✅ CORRECT — INSERT only
session.add(PointLog(**point_log_data))
await session.flush()

# ❌ INCORRECT — never do this
student.total_point += value
session.add(student)
```

**Calculate current points:**
```python
# Always compute from point_logs, do not use a cached total field.
current_point = class_entity.base_point + await point_log_repository.sum_point_values_by_student_id(student_id)
```

**Check if the week is locked before grading:**
```python
if await weekly_report_repository.is_locked(student_id, week_start_date):
    raise WeekAlreadyLockedException("This week points have already been locked.")
```

**Ensure Group Leaders only grade within their group:**
```python
if student.group_id != leader.group_id:
    raise StudentNotInGroupException("Student is not in your group.")
```

### 4. Authentication & Authorization
- Use a `require_role("TEACHER")` FastAPI dependency (built on `Depends(get_current_user)`), or a custom `Security(...)` scheme.
- JWT payload must contain: `sub`, `role`, `class_id`, `group_id`, `school_id`.
- Store Refresh Token in an HttpOnly Cookie — DO NOT return it in the response body.
- Store OTP in the Database as a bcrypt hash (`passlib.hash.bcrypt`) — DO NOT store as plain text.
- **Mock OTP Mechanism (MVP/Dev)**: When `SMS_API_KEY` is not configured (left blank), the OTP sending response (`SmsResponse`) must return the plain text OTP in the `otp` field so the Frontend can display it. When `SMS_API_KEY` is active, the `otp` field in `SmsResponse` must return `null` (no exposure).

### 5. Error Response (Mandatory Standardization)
```python
# Global exception handler (registered via app.add_exception_handler) must return this exact format
{
  "timestamp": "2025-09-01T10:00:00+07:00",
  "status": 400,
  "error": "VALIDATION_ERROR",
  "message": "Invalid data",
  "details": [{"field": "pointValue", "message": "Points must not be 0"}],
  "path": "/api/v1/leader/points"
}
```

### 6. Audit Logging (BR-AUDIT-01, BR-AUDIT-02, BR-AUDIT-03)
- Any sensitive administrative actions listed below (BR-AUDIT-02) must write an Audit Log entry into the `audit_logs` table synchronously within the same transaction:
  1. Approve/Reject teacher registration (`APPROVE_TEACHER`, `REJECT_TEACHER`)
  2. Approve/Reject student registration (`APPROVE_STUDENT`, `REJECT_STUDENT`)
  3. Assign group leader (`ASSIGN_LEADER`)
  4. Transfer student group (`TRANSFER_STUDENT_GROUP`)
  5. Activate dynamic form template (`ACTIVATE_FORM_TEMPLATE`)
  6. Lock weekly points manually/automatically (`WEEKLY_LOCK_MANUAL`, `WEEKLY_LOCK_AUTO`)
  7. End class (`END_CLASS`)
- How to implement: Call `AuditLogService.log_action(...)` in the Service, or use SQLAlchemy `before_flush`/`after_flush` event listeners to automatically capture `old_value` and `new_value` as JSONB.
- **Strictly prohibit** providing any APIs that allow `UPDATE` or `DELETE` on the `audit_logs` table. Only `INSERT` is permitted.

### 7. Scheduled Jobs
Use APScheduler (in-process) for simple deployments, or Celery beat for distributed setups.

```python
# APScheduler example
@scheduler.scheduled_job("cron", day_of_week="sun", hour=23, minute=59, timezone="Asia/Ho_Chi_Minh")
async def weekly_lock_job():
    # 1. Check is_locked first — skip if already locked
    # 2. Calculate point snapshot for each student
    # 3. Calculate rank_in_class and rank_in_group
    # 4. Save weekly_report with locked_by = 'CRON'
    # Log fully: start, end, record count
    async with session_factory() as session:
        async with session.begin():
            ...
```

### 8. Environment Variables & Configuration

**Mandatory Rules:**
- DO NOT hardcode any URLs, secrets, or credentials in code or config files.
- All sensitive values must be separated into a `.env` file, loaded via `pydantic-settings` (`BaseSettings`).
- The `.env` file MUST NOT be committed to Git — only commit `.env.example`.

**`app/core/config.py` (pydantic-settings):**
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Basic Application Configuration
    app_name: str = "backend"
    port: int = 8080

    # Database Configuration
    db_url: str
    db_username: str
    db_password: str

    # Google OAuth2 Configuration
    google_client_id: str
    google_client_secret: str

    # Mail Configuration
    email_host: str
    email_port: int
    email_smtp: str
    email_password: str

    # Custom Application Properties
    frontend_url: str
    jwt_secret: str
    allowed_origins: str

settings = Settings()
```

**`.env` content:**
```properties
# Database Keys
DB_URL=mysql+aiomysql://root:your_local_password@localhost:3306/classmanager
DB_USERNAME=root
DB_PASSWORD=your_local_password

# Google OAuth2 Keys
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Mail Keys
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_SMTP=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# System Keys
FRONTEND_URL=http://localhost:3000
JWT_SECRET=4036717551323267566B5970337336763979244226452F484F4D514D58753978
ALLOWED_ORIGINS=http://localhost:5173
```

**When deploying to Koyeb:**
- Set all environment variables via Koyeb Dashboard → Service → Environment.
- Change `ALLOWED_ORIGINS` to the actual Vercel domain.
- Change `ENV=prod` (used to select settings/profile in `app/core/config.py`).

### 9. CORS
- Allow origins specified in the ENV variable `ALLOWED_ORIGINS` (never hardcode), wired into FastAPI's `CORSMiddleware`.
- Dev: `http://localhost:5173`
- Production: Vercel domain

### 10. Query Optimization & Performance Best Practices

To prevent performance degradation and N+1 query problems in listing/dashboard endpoints, strictly adhere to the following optimization patterns:

- **Use read-only sessions for GET endpoints**: Do not call `session.commit()` on read paths; let the session close without flushing writes.
- **Strictly prohibit DB writes/saves inside GET endpoints**: Never insert default or missing records (e.g., default `StudentProfile` objects) inside a listing GET request. Instead:
  - Create these records proactively when their parent entity is created (e.g., auto-create profile inside `join_class`).
  - Handle missing data gracefully by returning `None` or defaults in the response mapper.
  - Let records heal/create dynamically when the user submits a mutation (e.g. `POST`/`PUT` to update profile).
- **RAM-based validation**: Instead of making multiple database roundtrips to validate input (e.g., checking class owner, checking student enrollment) before querying the collection, execute the primary query first (with `selectinload`/`joinedload`). Perform checks and validations on RAM using Python list/generator comprehensions.
- **Avoid redundant parent entity queries**: Extract parent entities from fetched children rather than calling `repository.get_by_id(id)` again (e.g. `enrollments[0].class_entity`).
- **Use `EXISTS` queries for validation**: If you must check permissions or ownership (e.g., if a teacher owns a class), use a lightweight `select(exists().where(...))` query instead of loading the entire entity via `get_by_id`.
- **Pre-aggregate using SQLAlchemy `GROUP BY`**: When compiling points or aggregate metrics, use a grouped query (`point_log_repository.sum_point_values_group_by_student_id`) rather than executing separate count/sum queries inside a loop.

### 11. Documentation Standards (Swagger / OpenAPI)

To fully leverage FastAPI's auto-generated interactive docs (`/docs` and `/redoc`), the following documentation conventions are mandatory when writing code.

**11.1 Router declarations — OpenAPI tags & descriptions**
Every role-scoped router (`admin`, `teacher`, `leader`, `student`) must declare `tags` so Swagger UI groups endpoints visually, and every endpoint must declare `summary` + `description`.

```python
# api/v1/leader/points.py
from fastapi import APIRouter, Depends
from app.schemas.request import PointGradingRequest
from app.schemas.response import PointLogResponse
from app.core.security import require_role

router = APIRouter(
    prefix="/api/v1/leader/points",
    tags=["Leader - Point Management"],  # groups endpoints into their own section in Swagger
)

@router.post(
    "",
    response_model=PointLogResponse,
    summary="Chấm điểm cho học sinh",
    description=(
        "Nhập điểm cộng/trừ cho học sinh trong nhóm. "
        "Hệ thống sẽ kiểm tra tuần học đã bị khóa hay chưa trước khi ghi nhận."
    ),
)
async def grade_student(
    payload: PointGradingRequest,
    current_user=Depends(require_role("LEADER")),
) -> PointLogResponse:
    # delegate to service, do not put business logic here
    ...
```

**11.2 Pydantic schemas — field-level docs**
Use `description` on every `Field`. For examples, Pydantic v2 no longer supports the v1-style singular `example=` kwarg on `Field` — use one of the two supported approaches instead:

```python
# schemas/request/point_request.py
from pydantic import BaseModel, Field, ConfigDict

class PointGradingRequest(BaseModel):
    student_id: int = Field(..., description="ID của học sinh được chấm điểm")
    point_value: int = Field(..., ne=0, description="Giá trị điểm (cộng hoặc trừ), không được bằng 0")
    reason: str = Field(..., min_length=5, max_length=255, description="Lý do chấm điểm")

    # Model-level example(s) — the correct Pydantic v2 / OpenAPI 3.1 approach
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"student_id": 102, "point_value": 5, "reason": "Phát biểu xây dựng bài tập toán"}
            ]
        }
    )
```

If a single field truly needs its own example independent of the model example, use the plural `examples=[...]` list on `Field`, never the singular `example=`:

```python
student_id: int = Field(..., description="ID của học sinh được chấm điểm", examples=[102])
```

**11.3 Service & Repository docstrings**
All `Protocol` interfaces and their `Impl` classes must document every public method using Google-style docstrings (not just complex ones), so tools like Sphinx/MkDocs can generate complete internal API references without gaps.

```python
# services/interfaces/point_service.py
from typing import Protocol

class PointService(Protocol):
    async def log_points(self, leader_id: int, payload: PointGradingRequest) -> PointLogEntity:
        """Ghi nhận điểm số của học sinh (chỉ cho phép INSERT — BR-POINT-01).

        Args:
            leader_id (int): ID của trưởng nhóm thực hiện chấm điểm.
            payload (PointGradingRequest): Dữ liệu yêu cầu chấm điểm.

        Returns:
            PointLogEntity: Thực thể nhật ký điểm đã được tạo.

        Raises:
            WeekAlreadyLockedException: Nếu tuần học đã bị khóa.
            StudentNotInGroupException: Nếu học sinh không thuộc nhóm của leader.
        """
        ...
```

**11.4 Response schemas & null handling**
Keep the documented response shape consistent with the standardized error format in Section 5. Decide explicitly, per endpoint, whether optional fields should be omitted or returned as `null`:
- Use `response_model_exclude_none=True` on the route decorator if optional/absent fields should be dropped from the JSON entirely.
- Otherwise, declare the field as `Optional[...] = None` and document in `description` that `null` is a valid, meaningful value (e.g. `otp` field in `SmsResponse`, see Section 4).

**11.5 Checklist before merging any endpoint**
1. Router has `tags`; endpoint has `summary` and `description`.
2. Every field in Request/Response Pydantic schemas has a `description`; example values are provided via `model_config.json_schema_extra` (model-level) or `Field(examples=[...])` (field-level) — never the deprecated singular `Field(example=...)`.
3. Every public method on a Service `Protocol` (and its `Impl`) has a Google-style docstring with `Args`, `Returns`, and `Raises`.
4. No `# TODO`, `...`, or unexplained placeholder logic in merged code.

---

## Verification Workflow

After creating or modifying Python code:

```bash
# Step 1: Navigate to backend directory
cd backend

# Step 2: Type-check and lint
mypy app
ruff check app

# Step 3: Run related tests (if applicable)
pytest tests/test_<feature>.py

# Step 4: Only create the Walkthrough artifact if type-check and tests succeed
```

---

## Anti-patterns to Avoid

```
❌ Performing database writes/saves inside GET or listing endpoints
❌ Querying parent entities multiple times instead of extracting them from child objects
❌ Running validation/security count/exists queries individually when collection is fetched
❌ Running multiple N+1 lazy queries inside loops (always use selectinload/joinedload)
❌ Updating student points directly
❌ Exposing SQLAlchemy models directly to the API (without a Pydantic schema)
❌ Business logic in the router
❌ Managing transactions in the router
❌ Injecting Repository into the router
❌ Using // TODO, ..., placeholder comments — write complete implementations
❌ Hardcoding secrets, URLs, or credentials — always use `settings.<field>` sourced from `.env`
❌ Committing `.env` file to Git — only commit `.env.example`
❌ Building raw SQL strings with user input via string formatting/concatenation
❌ Teacher creating a second Class when they already have an ACTIVE one
❌ Using the deprecated Pydantic v1 syntax `Field(..., example=...)` (singular) — use `examples=[...]` or `model_config.json_schema_extra` instead
❌ Router endpoints without `tags`, `summary`, or `description` (breaks Swagger/OpenAPI docs quality)
❌ Public Service/Repository methods without a Google-style docstring (`Args`/`Returns`/`Raises`)
```