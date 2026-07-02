# Hướng Dẫn Chuẩn Phát Triển Backend (Spring Boot 4.x + Java 21)

Tài liệu này tổng hợp toàn bộ Tech Stack, cấu trúc thư mục, chuẩn đặt tên, các thư viện sử dụng và thiết kế mẫu của dự án Backend hiện tại để có thể áp dụng trực tiếp khi khởi tạo các dự án mới.

---

## 1. Tech Stack & Thư Viện Cốt Lõi (Dependencies)

### Core Technologies
*   **Java Version**: 21 (LTS)
*   **Spring Boot**: 4.1.0 (sử dụng phiên bản Spring Boot cấu hình trong `pom.xml`)
*   **Database**: PostgreSQL (sử dụng Driver `org.postgresql:postgresql`)
*   **Build Tool**: Maven

### Thư Viện & Tiện Ích Trong `pom.xml`

| Nhóm Thư Viện | Dependency | Mục Đích |
| :--- | :--- | :--- |
| **Data & JPA** | `spring-boot-starter-data-jpa` | Quản lý ORM qua Hibernate, giao tiếp Database. |
| **Security** | `spring-boot-starter-security` | Bảo mật phân quyền hệ thống. |
| **Security - OAuth2** | `spring-boot-starter-security-oauth2-client` <br> `spring-boot-starter-oauth2-resource-server` | Tích hợp đăng nhập bên thứ 3 (Google, Facebook) và xác thực Resource Server. |
| **Authentication** | `io.jsonwebtoken:jjwt-api:0.11.5` <br> `jjwt-impl` & `jjwt-jackson` | Thư viện tạo và xác thực JSON Web Token (JWT). |
| **Web & API** | `spring-boot-starter-web` | Xây dựng RESTful API (Spring MVC). |
| **Validation** | `spring-boot-starter-validation` | Validate dữ liệu đầu vào sử dụng Jakarta Bean Validation. |
| **Documentation** | `org.springdoc:springdoc-openapi-starter-webmvc-ui:3.0.2` | Tự động tạo Swagger UI để kiểm thử và tài liệu hóa API. |
| **Utility** | `org.projectlombok:lombok` | Tự động sinh Getter, Setter, Constructor, Builder bằng annotation để giảm boilerplate code. |
| **Communication** | `spring-boot-starter-mail` | Hỗ trợ gửi Email tự động (Ví dụ: gửi mã OTP). |
| **Testing (Dev)** | `spring-boot-starter-test` <br> `spring-boot-starter-security-test` | Các thư viện test phục vụ viết Unit Test & Integration Test. |

---

## 2. Cấu Trúc Thư Mục Dự Án (Directory Structure)

Dự án tuân thủ mô hình phân tầng chuẩn **Layered Architecture**. Toàn bộ mã nguồn Java nằm trong `src/main/java/com/classmanager/`. Tầng Service được phân tách rõ ràng giữa Interface và lớp triển khai (`impl`) để đảm bảo tính Loose Coupling.

```text
backend/
├── pom.xml                            # Khai báo dependencies và cấu hình build Maven
├── .env                               # File lưu các biến môi trường cấu hình chạy local (không commit lên Git)
├── .env.example                       # Bản mẫu cấu hình biến môi trường (commit lên Git)
├── src/
│   ├── main/
│   │   ├── java/com/classmanager/
│   │   │   ├── BackendApplication.java # Entry point chạy ứng dụng Spring Boot
│   │   │   │
│   │   │   ├── config/                # Chứa cấu hình hệ thống (CORS, Security, OpenAPI,...)
│   │   │   │   ├── SecurityConfig.java
│   │   │   │   └── OpenAPIConfig.java
│   │   │   │
│   │   │   ├── controller/            # Tầng API: Tiếp nhận Request từ Client, điều hướng và trả Response
│   │   │   │   ├── AuthController.java
│   │   │   │   └── UserController.java
│   │   │   │
│   │   │   ├── dto/                   # Data Transfer Objects: Đóng gói dữ liệu trao đổi
│   │   │   │   ├── common/            # DTO dùng chung cho toàn bộ dự án
│   │   │   │   │   └── APIResponse.java # Standard Response Wrapper
│   │   │   │   ├── auth/              # DTO theo từng Module/Domain
│   │   │   │   │   ├── request/       # Dữ liệu từ Client gửi lên (VD: LoginRequest)
│   │   │   │   │   └── response/      # Dữ liệu Server trả về (VD: AuthResponse)
│   │   │   │   └── user/
│   │   │   │
│   │   │   ├── entity/                # Các JPA Entity ánh xạ với các bảng cơ sở dữ liệu PostgreSQL
│   │   │   │   ├── User.java
│   │   │   │   └── Course.java
│   │   │   │
│   │   │   ├── enums/                 # Chứa các Enum định nghĩa kiểu dữ liệu cố định (Role, Status)
│   │   │   │   ├── Role.java
│   │   │   │   └── UserStatus.java
│   │   │   │
│   │   │   ├── exception/             # Xử lý ngoại lệ toàn cục (Global Exception Handler)
│   │   │   │   └── GlobalExceptionHandler.java
│   │   │   │
│   │   │   ├── repository/            # Tầng giao tiếp Database: Các interface kế thừa JpaRepository
│   │   │   │   ├── UserRepository.java
│   │   │   │   └── CourseRepository.java
│   │   │   │
│   │   │   ├── security/              # Tầng bảo mật, cấu hình Filter JWT, xử lý UserDetails
│   │   │   │   ├── AuthenticationFilter.java
│   │   │   │   ├── JwtUtil.java
│   │   │   │   └── SecurityUtil.java
│   │   │   │
│   │   │   └── service/               # Tầng Logic nghiệp vụ (Chứa các Service Interface bên ngoài)
│   │   │       ├── AuthService.java
│   │   │       ├── UserService.java
│   │   │       └── impl/              # Thư mục chứa các lớp triển khai thực tế của Service
│   │   │           ├── AuthServiceImpl.java
│   │   │           └── UserServiceImpl.java
│   │   │
│   │   └── resources/
│   │       ├── application.properties # File cấu hình môi trường của Spring Boot
│   │       ├── static/                # Chứa tài nguyên tĩnh (ít dùng trong API-only)
│   │       └── templates/             # File HTML Template (Ví dụ: Email template)
│   │
│   └── test/                          # Viết Unit/Integration Tests
```

---

## 3. Chuẩn Đặt Tên & Quy Tắc Thiết Kế (Naming Conventions)

### 3.1. Quy tắc Đặt tên Package & Class (Java)

| Đối tượng | Quy tắc đặt tên | Ví dụ |
| :--- | :--- | :--- |
| **Package** | Viết thường toàn bộ, dạng số ít. | `com.classmanager.controller`<br>`com.classmanager.entity` |
| **Entity Class** | PascalCase, số ít. Trùng tên với thực thể trong DB. | `User.java`, `Course.java`, `CourseModule.java` |
| **Controller Class** | PascalCase, kết thúc bằng chữ `Controller`. | `AuthController.java`, `CourseController.java` |
| **Service Interface** | Interface, PascalCase, kết thúc bằng chữ `Service`, bắt đầu bằng chữ `I`. | `IAuthService.java`, `ICourseService.java` |
| **Service Class** | PascalCase, kết thúc bằng chữ `Impl`. | `AuthServiceImpl.java`, `CourseServiceImpl.java` |
| **Repository Class** | Interface, PascalCase, kết thúc bằng chữ `Repository`. | `UserRepository.java`, `CourseRepository.java` |
| **DTO Class** | PascalCase, kết thúc bằng chữ `Request` hoặc `Response`. | `LoginRequest.java`, `UserResponse.java` |
| **Enum Class** | PascalCase, đại diện cho tập hằng số logic. | `Role.java`, `UserStatus.java` |

### 3.2. Quy tắc Thiết kế Database (JPA)

1.  **Tên bảng (`@Table`)**: Viết thường toàn bộ, dạng **số nhiều** (Plural), phân tách bằng dấu gạch dưới `snake_case` nếu có nhiều từ.
    *   *Ví dụ*: `@Table(name = "users")`, `@Table(name = "course_classes")`
2.  **Khóa chính (Primary Key)**: Đặt tên dạng `[entity_name_lowercase]_id`.
    *   *Ví dụ*: `@Column(name = "user_id")` trong bảng `users`, `@Column(name = "class_id")` trong bảng `classes`.
3.  **Tên cột (`@Column`)**: Viết thường toàn bộ, dạng `snake_case`.
    *   *Ví dụ*: `@Column(name = "full_name")`, `@Column(name = "activated_at")`.
4.  **Kiểu dữ liệu text dài**: Sử dụng `columnDefinition = "TEXT"` hoặc `columnDefinition = "LONGTEXT"` khi cần lưu lượng text lớn.
    *   *Ví dụ*: `@Column(name = "avatar_url", columnDefinition = "LONGTEXT")`
5.  **Dữ liệu dạng JSON**: Dùng annotation `@JdbcTypeCode(SqlTypes.JSON)` để lưu trực tiếp Map hoặc List Object thành JSON trong PostgreSQL.
6.  **Thuộc tính Entity**: Trong code Java dùng chuẩn `camelCase`.
    *   *Ví dụ*: `private String fullName;` tương ứng `@Column(name = "full_name")`
7.  **Không chỉnh sửa nhật ký điểm**: Bảng `point_logs` là bất biến (chỉ thêm, không sửa, không xóa).

### 3.3. Quy tắc REST API & Request Validation

1.  **Endpoint URLs**:
    *   Viết thường toàn bộ, phân cách bằng dấu gạch ngang `-` nếu có nhiều từ (`kebab-case`).
    *   Tất cả các API được gom nhóm bắt đầu bằng `/api/...` thông qua `@RequestMapping(path = "/api/...")`.
    *   *Ví dụ*: `POST /api/auth/login`, `POST /api/auth/send-otp`, `GET /api/course/{id}`.
2.  **Đầu ra chuẩn (APIResponse)**:
    *   Tất cả các API trả về đều được đóng gói qua thực thể `ResponseEntity<APIResponse<T>>`.
    *   Cấu trúc của `APIResponse` gồm: `isSuccess` (boolean), `code` (HTTP status code), `message` (thông báo), `data` (dữ liệu payload).
3.  **Validation**:
    *   Sử dụng `@Valid` ở Controller tại tham số nhận `@RequestBody`.
    *   Sử dụng các annotation validation tại DTO để kiểm tra dữ liệu đầu vào tự động (Ví dụ: `@NotBlank`, `@Size`, `@Pattern`, `@Email`).

---

## 4. Thiết Kế Mẫu Cho Dự Án Mới (Template Classes)

### 4.1. Standard Response Wrapper (`APIResponse.java`)

```java
package com.classmanager.dto.common;

import lombok.*;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class APIResponse<T> {
    private boolean isSuccess;
    private int code;
    private String message;
    private T data;

    public static <T> APIResponse<T> success(String message, T data){
        return new APIResponse<>(true, 200, message, data);
    }

    public static <T> APIResponse<T> error(int code, String message, T data){
        return new APIResponse<>(false, code, message, data);
    }
}
```

### 4.2. Global Exception Handler (`GlobalExceptionHandler.java`)

```java
package com.classmanager.exception;

import com.classmanager.dto.common.APIResponse;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.stream.Collectors;

@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<APIResponse<Object>> handleAccessDeniedException(AccessDeniedException ex) {
        return ResponseEntity.status(403).body(
                APIResponse.error(403, "You are not authorized to access this resource!", null));
    }

    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<APIResponse<Object>> handleRuntimeException(RuntimeException ex) {
        return ResponseEntity.badRequest().body(
                APIResponse.error(400, ex.getMessage(), null));
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<APIResponse<Object>> handleValidationException(MethodArgumentNotValidException ex) {
        String message = ex.getBindingResult().getFieldErrors().stream()
                .map(FieldError::getDefaultMessage)
                .collect(Collectors.joining(", "));

        return ResponseEntity.badRequest().body(
                APIResponse.error(400, message, null));
    }
}
```

### 4.3. Entity Mẫu (`User.java`)

```java
package com.classmanager.entity;

import jakarta.persistence.*;
import lombok.*;
import com.classmanager.enums.Role;
import com.classmanager.enums.UserStatus;

import java.time.LocalDateTime;

@Entity
@Table(name = "users")
@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "user_id")
    private Long id;

    @Column(name = "full_name", length = 100, nullable = false)
    private String fullName;

    @Column(name = "username", length = 100, nullable = false, unique = true)
    private String username;

    @Column(name = "password", length = 255, nullable = false)
    private String password;

    @Column(name = "email", nullable = false, unique = true)
    private String email;

    @Column(name = "role")
    @Enumerated(EnumType.STRING)
    @Builder.Default
    private Role role = Role.STUDENT;

    @Column(name = "status")
    @Enumerated(EnumType.STRING)
    @Builder.Default
    private UserStatus status = UserStatus.ACTIVE;

    @Column(name = "created_at")
    private LocalDateTime createdAt;
}
```

### 4.4. DTO Request Mẫu (`RegisterRequest.java`)

```java
package com.classmanager.dto.auth.request;

import jakarta.validation.constraints.*;
import lombok.*;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class RegisterRequest {
    @NotBlank(message = "Cannot be left fullname blank")
    private String fullName;

    @NotBlank(message = "Cannot be left username blank")
    @Size(min = 4, max = 30, message = "At least 4-30 characters")
    private String username;

    @NotBlank(message = "Cannot be left email blank")
    @Email(message = "Invalid email format")
    private String email;

    @NotBlank(message = "Cannot be left password blank")
    @Size(min = 8, message = "Password must contain at least 8 characters")
    private String password;
}
```

### 4.5. Repository Mẫu (`UserRepository.java`)

```java
package com.classmanager.repository;

import com.classmanager.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    boolean existsByUsername(String username);
    boolean existsByEmail(String email);
    Optional<User> findByUsername(String username);
    Optional<User> findByEmail(String email);
}
```

### 4.6. Service Mẫu (`AuthService.java`)

```java
package com.classmanager.service;

import lombok.RequiredArgsConstructor;
import com.classmanager.dto.auth.request.RegisterRequest;
import com.classmanager.dto.auth.response.AuthResponse;
import com.classmanager.entity.User;
import com.classmanager.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class AuthService {
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public AuthResponse register(RegisterRequest request) {
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new RuntimeException("This username is already in use");
        }
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new RuntimeException("This email is already in use");
        }

        User user = User.builder()
                .fullName(request.getFullName())
                .username(request.getUsername())
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .createdAt(LocalDateTime.now())
                .build();

        userRepository.save(user);

        return AuthResponse.builder()
                .message("Register successfully")
                .build();
    }
}
```

### 4.7. Controller Mẫu (`AuthController.java`)

```java
package com.classmanager.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import com.classmanager.dto.auth.request.RegisterRequest;
import com.classmanager.dto.auth.response.AuthResponse;
import com.classmanager.dto.common.APIResponse;
import com.classmanager.service.AuthService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping(path = "/api/v1/auth")
@RequiredArgsConstructor
@Tag(name = "Auth", description = "Các API xác thực tài khoản")
public class AuthController {
    
    private final AuthService authService;

    @Operation(summary = "Đăng ký tài khoản mới", description = "Đăng ký tài khoản người dùng local.")
    @PostMapping(path = "/register")
    public ResponseEntity<APIResponse<AuthResponse>> register(
            @Valid @RequestBody RegisterRequest request) {
        AuthResponse response = authService.register(request);
        return ResponseEntity.ok(
                APIResponse.success("Successful Register", response));
    }
}
```

---

## 5. CẤU HÌNH BẢO MẬT & ĐIỀU HƯỚNG LUỒNG (SECURITY & AUTH GUARD)

### Cấu trúc JWT Claims

Chuỗi mã hóa JWT sinh ra sau quá trình Authenticate bắt buộc chứa các tham số định danh:

```json
{
  "sub": "string (chứa ID của user gốc)",
  "username": "string",
  "role": "TEACHER | STUDENT | null",
  "schoolId": "integer | null",
  "iat": 1770000000,
  "exp": 1770007200
}
```

---

## 6. FILE CẤU HÌNH KHỞI TẠO (APPLICATION ENVIRONMENT)

### application.yml (Cấu hình chuẩn cho Agent)

```yaml
spring:
  datasource:
    url: ${DB_URL:jdbc:postgresql://localhost:5432/classmanager}
    username: ${DB_USERNAME:postgres}
    password: ${DB_PASSWORD:yourpassword}
    driver-class-name: org.postgresql.Driver
  jpa:
    hibernate:
      ddl-auto: validate
    show-sql: true
    properties:
      hibernate:
        format_sql: true

jwt:
  secret: ${JWT_SECRET:4036717551323267566B5970337336763979244226452F484F4D514D58753978}
  access-expiration: ${JWT_EXPIRATION:7200} # 2 giờ tính bằng giây
  refresh-expiration: ${JWT_REFRESH_EXPIRATION:604800} # 7 ngày tính bằng giây

google:
  client-id: ${GOOGLE_CLIENT_ID:your-google-client-id.apps.googleusercontent.com}
```

---

## 7. CHỈ THỊ THỰC THI CHO AGENTS (AGENTS DIRECTIVES)

Khi lệnh `/orchestrate` kích hoạt cấu hình này cho các Sub-Agents thực hiện viết mã nguồn, các Agent phải tuân thủ:

1. **Cấm tuyệt đối** sử dụng mã giả (Placeholder) hoặc comment `// TODO: Implement later`. Mọi hàm nghiệp vụ phải được viết trọn vẹn logic từ đầu đến cuối.
2. Tất cả các lỗi nghiệp vụ không được xử lý cục bộ bằng khối `try-catch` trả về đối tượng ResponseEntity rỗng, mà phải định nghĩa lớp Exception cụ thể kế thừa `RuntimeException` và ném ra để `GlobalExceptionHandler` xử lý tập trung.
3. Tuân thủ cấu trúc phân rã thư mục Clean Architecture/Layered Architecture đã đề xuất (Tách rõ rệt `controller`, `service`, `repository`, `entity`, `dto`, `exception`).
