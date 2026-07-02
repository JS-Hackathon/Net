---
name: spring-backend-expert
description: Train Agent to write REST API Spring Boot 3.x for ClassManager — adhering to Clean Architecture, immutable audit log, JWT auth and RBAC 4 role permissions.
---

# Objective
Ensure the entire ClassManager Backend is written strictly according to the architecture, without violating immutable Business Rules (especially immutable point_logs), securing access by role, and maintaining consistent error responses.

---

## Instructions

### 1. Context Checklist
- All Java classes must reside in `backend/src/main/java/com/classmanager/`
- Read `docs/srs/classmanager_srs_full.md` and `docs/schema.sql` before writing any logic.
- Read `CLAUDE.md` to understand the mandatory Business Rules.

### 2. Architectural Rules & Project Structure (DO NOT violate)

**Standard Package Structure:**
All new Java classes must be organized in the correct packages under `backend/src/main/java/com/classmanager/`:
- `config/`: System configuration (Security, Database, CORS, JWT...).
- `controller/`: Restful Controllers to receive requests, validate, and delegate to Services.
- `service/`: Core business logic interfaces & implementations, transaction management.
- `repository/`: Repositories extending Spring Data JPA for data access.
- `entity/`: Entities mapping to database tables.
- `dto/`: Data Transfer Objects (DTOs):
  - `dto/request/`: Request payloads.
  - `dto/response/`: Response payloads.
- `exception/`: Custom exception classes and `GlobalExceptionHandler`.
- `scheduler/`: Scheduled tasks and automation (Cron Jobs).

**Backend Feature Development Flow:**
When developing a new backend feature, adhere to the following sequence:
1. **Entity**: Declare/update the JPA Entity in the `entity` package.
2. **Repository**: Create the JPA Repository interface in the `repository` package. Use `@EntityGraph` or Join Fetch to prevent N+1 queries if necessary.
3. **Service & Transaction**: Create the Service in the `service` package, define business logic, and handle transactions. Use `@Transactional(readOnly = true)` for queries and `@Transactional` for mutations.
4. **Audit Logging Integration**: If the feature involves actions that require auditing (BR-AUDIT-02), integrate audit logging via JPA Entity Listeners or call `AuditLogService` synchronously within the transaction.
5. **DTOs & Validation**: Create Request/Response DTOs in the `dto` package, applying Bean Validation annotations (`@NotNull`, `@NotBlank`, `@Size`, `@Pattern`, `@Min`, `@Max`).
6. **Controller**: Create the Controller in the `controller` package, map requests with `@Valid`, and enforce access control using `@PreAuthorize`.
7. **Verify**: Compile and test using Maven.

**Layer Conventions:**
**Controller Layer:**
- Use `@RestController` + `@RequestMapping("/api/v1/...")`
- DO NOT contain business logic — only receive requests, delegate to Services, and return responses.
- DO NOT inject Repositories directly into Controllers.
- Prefix endpoints by role: `/api/v1/admin/`, `/api/v1/teacher/`, `/api/v1/leader/`, `/api/v1/student/`

**Service Layer:**
- All business logic and `@Transactional` configurations must reside here.
- DO NOT allow circular dependencies between Services.
- Throw custom exceptions — DO NOT return null.

**Repository Layer:**
- Use Spring Data JPA.
- For complex queries (multiple joins): use `@Query` with JPQL or `@EntityGraph` to avoid N+1 queries.
- DO NOT use native queries with raw user inputs (SQL Injection risk).

**DTO Layer:**
- Separate Request DTOs from Response DTOs — DO NOT expose Entities directly to the API.
- Use Lombok annotations: `@Data`, `@Builder`, `@NoArgsConstructor`, `@AllArgsConstructor`.
- Validate Request DTOs using Bean Validation: `@NotNull`, `@NotBlank`, `@Size`, `@Pattern`.

### 3. Mandatory Business Rules

**Immutable Point Log (BR-POINT-01, BR-POINT-08):**
```java
// ✅ CORRECT — INSERT only
pointLogRepository.save(new PointLog(...));

// ❌ INCORRECT — never do this
student.setTotalPoint(student.getTotalPoint() + value);
studentRepository.save(student);
```

**Calculate current points:**
```java
// Always compute from point_logs, do not use a cached total field.
int currentPoint = classEntity.getBasePoint()
    + pointLogRepository.sumPointValuesByStudentId(studentId);
```

**Check if the week is locked before grading:**
```java
if (weeklyReportRepository.isLocked(studentId, weekStartDate)) {
    throw new WeekAlreadyLockedException("This week points have already been locked.");
}
```

**Ensure Group Leaders only grade within their group:**
```java
if (!student.getGroupId().equals(leader.getGroupId())) {
    throw new StudentNotInGroupException("Student is not in your group.");
}
```

### 4. Authentication & Authorization
- Use `@PreAuthorize("hasRole('TEACHER')")` or custom `@SecurityRequirement`.
- JWT payload must contain: `sub`, `role`, `classId`, `groupId`, `schoolId`.
- Store Refresh Token in an HttpOnly Cookie — DO NOT return it in the response body.
- Store OTP in the Database as a BCrypt hash — DO NOT store as plain text.
- **Mock OTP Mechanism (MVP/Dev)**: When `SMS_API_KEY` is not configured (left blank), the OTP sending response (`SmsResponse`) must return the plain text OTP in the `otp` field so the Frontend can display it. When `SMS_API_KEY` is active, the `otp` field in `SmsResponse` must return `null` (no exposure).

### 5. Error Response (Mandatory Standardization)
```java
// GlobalExceptionHandler must return this exact format
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
- How to implement: Call `AuditLogService.logAction(...)` in the Service, or use JPA `@EntityListeners` to automatically capture `old_value` and `new_value` as JSONB.
- **Strictly prohibit** providing any APIs that allow `UPDATE` or `DELETE` on the `audit_logs` table. Only `INSERT` is permitted.

### 7. Cron Jobs
```java
@Scheduled(cron = "59 23 * * 0", zone = "Asia/Ho_Chi_Minh")
@Transactional
public void weeklyLockJob() {
    // 1. Check is_locked first — skip if already locked
    // 2. Calculate point snapshot for each student
    // 3. Calculate rank_in_class and rank_in_group
    // 4. Save weekly_report with locked_by = 'CRON'
    // Log fully: start, end, record count
}
```

### 8. Environment Variables & Configuration

**Mandatory Rules:**
- DO NOT hardcode any URLs, secrets, or credentials in code.
- All sensitive values must be read from ENV variables using `${ENV_VAR}` in `application.yml`.
- The `.env` file MUST NOT be committed to Git — only commit `.env.example`.

**`application.yml` reading from ENV:**
```yaml
spring:
  datasource:
    url: ${DB_URL}
    username: ${DB_USERNAME}
    password: ${DB_PASSWORD}
  jpa:
    hibernate:
      ddl-auto: update
  hikari:
    maximum-pool-size: 15
    minimum-idle: 3

app:
  jwt:
    secret: ${JWT_SECRET}
    expiration-ms: ${JWT_EXPIRATION_MS:7200000}
    refresh-expiration-ms: ${JWT_REFRESH_EXPIRATION_MS:604800000}
  google:
    client-id: ${GOOGLE_CLIENT_ID}
  cors:
    allowed-origins: ${ALLOWED_ORIGINS}
  admin:
    allowed-emails: ${ADMIN_ALLOWED_EMAILS}
  timezone: ${APP_TIMEZONE:Asia/Ho_Chi_Minh}
  sms:
    api-key: ${SMS_API_KEY}
    sender: ${SMS_SENDER:ClassManager}
```

**When deploying to Koyeb:**
- Set all environment variables via Koyeb Dashboard → Service → Environment.
- Change `ALLOWED_ORIGINS` to the actual Vercel domain.
- Change `SPRING_PROFILES_ACTIVE=prod`.

### 9. CORS
- Allow origins specified in the ENV variable `ALLOWED_ORIGINS` (never hardcode).
- Dev: `http://localhost:5173`
- Production: Vercel domain

### 10. Query Optimization & Performance Best Practices

To prevent performance degradation and N+1 query problems in listing/dashboard endpoints, strictly adhere to the following optimization patterns:

- **Prefer `@Transactional(readOnly = true)` for GET endpoints**: Ensures Spring/Hibernate optimizes dirty checking and session management.
- **Strictly prohibit DB writes/saves inside GET endpoints**: Never insert default or missing records (e.g., default `StudentProfile` objects) inside a listing GET request. Instead:
  - Create these records proactively when their parent entity is created (e.g., auto-create profile inside `joinClass`).
  - Handle missing data gracefully by returning `null` or defaults in the response mapper.
  - Let records heal/create dynamically when the user submits a mutation (e.g. `POST`/`PUT` to update profile).
- **RAM-based validation**: Instead of making multiple database roundtrips to validate input (e.g., checking class owner, checking student enrollment) before querying the collection, execute the primary JPQL `FETCH JOIN` query first. Perform checks and validations on RAM using Java Streams over the retrieved collection.
- **Avoid redundant parent entity queries**: Extract parent entities from fetched children rather than calling `repository.findById(id)` (e.g. `enrollments.get(0).getClassEntity()`).
- **Use `EXISTS` queries for validation**: If you must check permissions or ownership (e.g., if a teacher owns a class), use a lightweight `exists` query (e.g., `existsByIdAndTeacherId`) instead of loading the entire entity via `findById`.
- **Pre-aggregate using JPQL `GROUP BY`**: When compiling points or aggregate metrics, use JPQL grouping queries (`pointLogRepository.sumPointValuesGroupByStudentId`) rather than executing separate count/sum queries inside a loop.

---

## Verification Workflow

After creating or modifying Java code:

```bash
# Step 1: Navigate to backend directory
cd backend

# Step 2: Compile and check for errors
./mvnw compile

# Step 3: Run related tests (if applicable)
./mvnw test -Dtest=ClassNameTest

# Step 4: Only create the Walkthrough artifact if compile succeeds
```

---

## Anti-patterns to Avoid

```
❌ Performing database writes/saves inside GET or listing endpoints
❌ Querying parent entities multiple times instead of extracting them from child objects
❌ Running validation/security count/exists queries individually when collection is fetched
❌ Running multiple N+1 lazy queries inside loops (always use FETCH JOIN / @EntityGraph)
❌ Updating student points directly
❌ Exposing Entity directly to API (without DTO)
❌ Business logic in Controller
❌ @Transactional in Controller
❌ Injecting Repository into Controller
❌ Using // TODO, // ..., placeholder comments — write complete implementations
❌ Hardcoding secrets, URLs, or credentials — always use `${ENV_VAR}` in application.yml
❌ Committing `.env` file to Git — only commit `.env.example`
❌ Native queries with user inputs
❌ Teacher creating a second Class when they already have an ACTIVE one
```