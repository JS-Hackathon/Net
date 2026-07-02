# TÀI LIỆU ĐẶC TẢ YÊU CẦU PHẦN MỀM (SRS ĐẦY ĐỦ)
## HỆ THỐNG QUẢN LÝ LỚP CHỦ NHIỆM — ClassManager Production-Ready
### Phiên bản: 2.0 | Ngày: 2026

---

## MỤC LỤC
1. Tổng quan hệ thống
2. Actors & Phân quyền
3. Business Rules
4. Database Schema đầy đủ
5. API Endpoints chi tiết
6. OAuth2 + JWT Flow
7. Validation Rules
8. Error Handling
9. Non-Functional Requirements
10. Implementation Checklist
11. Project Structure

---

## 1. TỔNG QUAN HỆ THỐNG

### 1.1 Mục đích
ClassManager là hệ thống quản lý lớp chủ nhiệm trực tuyến dành cho giáo viên chủ nhiệm để theo dõi điểm thi đua, hồ sơ học sinh, và tổng kết tuần một cách tự động và minh bạch. Hệ thống hỗ trợ mô hình quản lý trực tiếp giữa Giáo viên chủ nhiệm và Lớp học / Học sinh.

### 1.2 Phạm vi hệ thống
- **Quản lý Lớp học (Class-centric):** Hệ thống có cấu trúc tổ chức từ Giáo viên chủ nhiệm ➔ Lớp học ➔ Tổ.
- **Mô hình User-centric:** Hợp nhất việc quản lý tài khoản, xác thực (Google OAuth2 và số điện thoại kèm OTP) trên thực thể User gốc.
- **Duyệt hồ sơ học sinh qua Dynamic Form có Versioning:** Thu thập thông tin học sinh tùy biến theo từng lớp, hỗ trợ lưu vết lịch sử phiên bản form.
- **Hệ thống chấm điểm thi đua:** Chấm điểm theo tổ dựa trên chức vụ Tổ trưởng (Position) thay vì Role hệ thống.
- **Chốt điểm tuần tự động/thủ công:** Lưu trữ đầy đủ snapshot điểm, điểm cơ bản, tổng điểm cộng, tổng điểm trừ để audit.
- **Audit Logs:** Ghi nhận toàn bộ hành động quản trị nhạy cảm nhằm đảm bảo tính minh bạch.
- **Dashboard phân tích:** Cho giáo viên và học sinh theo dõi trực quan kết quả thi đua.

### 1.3 Ngoài phạm vi MVP
- AI / RAG Chatbot (Giai đoạn 2)
- Thông báo tự động qua Zalo / SMS (ngoài luồng gửi OTP xác thực SĐT)
- Ứng dụng di động native

---

## 2. ACTORS & PHÂN QUYỀN

### 2.1 Danh sách Roles hệ thống
Hệ thống sử dụng mô hình Phân quyền dựa trên Vai trò (RBAC) với 3 vai trò hệ thống cốt lõi:

| Role | Mô tả |
|------|-------|
| **ADMIN** | Quản trị viên hệ thống — phê duyệt tài khoản Giáo viên (`TEACHER`). |
| **TEACHER** | Giáo viên chủ nhiệm — quản trị lớp học do mình quản lý. |
| **STUDENT** | Học sinh — thành viên của lớp học, xem điểm cá nhân và điền thông tin lý lịch. |

### 2.2 Chức vụ trong tổ chức (Positions)
Chức vụ không phải là Role hệ thống nhưng được sử dụng để phân quyền nghiệp vụ tại tầng Service:

| Chức vụ | Mô tả |
|---------|-------|
| **GROUP_LEADER (Tổ trưởng)** | Là một người dùng có Role `STUDENT` được Giáo viên chỉ định làm trưởng nhóm của một Tổ (`groups`). Có quyền chấm điểm các thành viên khác trong tổ của mình và tự chấm điểm bản thân. |

### 2.3 Permission Matrix

| Chức năng | ADMIN | TEACHER | STUDENT (Tổ trưởng) | STUDENT (Thường) |
|-----------|-------|---------|---------------------|------------------|
| Phê duyệt tài khoản Giáo viên | ✅ | ❌ | ❌ | ❌ |
| Phê duyệt học sinh vào lớp | ❌ | ✅ | ❌ | ❌ |
| Import danh sách học sinh | ❌ | ✅ | ❌ | ❌ |
| Chỉ định/thay đổi Tổ trưởng | ❌ | ✅ | ❌ | ❌ |
| Tạo phiên bản Dynamic Form mới | ❌ | ✅ | ❌ | ❌ |
| Chuyển học sinh giữa các tổ | ❌ | ✅ | ❌ | ❌ |
| Chấm điểm thi đua | ❌ | ✅ (toàn lớp) | ✅ (chỉ thành viên trong tổ) | ❌ |
| Chốt điểm tuần thủ công | ❌ | ✅ | ❌ | ❌ |
| Dừng lớp học (End Class) | ❌ | ✅ | ❌ | ❌ |
| Xem lịch sử Audit Logs | ✅ (hệ thống) | ✅ (lớp quản lý) | ❌ | ❌ |
| Xem điểm cá nhân | ❌ | ✅ (toàn lớp) | ✅ (bản thân & thành viên tổ) | ✅ (chỉ bản thân) |
| Điền/cập nhật Form lý lịch | ❌ | ❌ | ✅ | ✅ |

---

## 3. BUSINESS RULES

### 3.1 Nhóm Xác thực & Tài khoản (Auth)
- **BR-AUTH-01:** Mọi người dùng (`users`) bắt buộc phải đăng ký bằng tài khoản Google (`google_email`) hoặc Số điện thoại đã xác thực (`phone_number` + `phone_verified = true`).
- **BR-AUTH-02:** Tài khoản mới đăng ký sẽ ở trạng thái `PENDING`. Người dùng ở trạng thái `PENDING` hoặc bị `REJECTED` không thể truy cập bất kỳ tài nguyên bảo mật nào của hệ thống và sẽ nhận mã lỗi `403 PENDING_APPROVAL` hoặc `REGISTRATION_REJECTED`.
- **BR-AUTH-03:** Giáo viên tự đăng ký tài khoản Giáo viên và chỉ được hoạt động sau khi được `ADMIN` phê duyệt.
- **BR-AUTH-04:** Học sinh tự đăng ký phải chọn lớp học tham gia. Tài khoản Học sinh chỉ được hoạt động sau khi được Giáo viên chủ nhiệm (`TEACHER`) của lớp đó phê duyệt.
- **BR-AUTH-05:** JWT Access Token có thời hạn 2 giờ, chứa thông tin `userId`, `role`, `teacherProfileId` (nếu có), `classId` (nếu có), và `groupId` (nếu có). Refresh Token có thời hạn 7 ngày, được lưu trữ trong HttpOnly Cookie bảo mật.
- **BR-AUTH-06:** Khi đăng nhập bằng Google OAuth2, nếu email trùng khớp với một tài khoản đã xác thực bằng SĐT trước đó, hệ thống sẽ tự động liên kết và đăng nhập vào tài khoản đó.

### 3.2 Nhóm Lớp học (Classes)
- **BR-CLASS-01:** Giáo viên chủ nhiệm chỉ được phép quản lý tối đa 1 lớp ở trạng thái `ACTIVE` tại một thời điểm.
- **BR-CLASS-02:** Giáo viên chủ nhiệm có thể dừng lớp học tương ứng (chuyển trạng thái `classes.status` sang `ENDED`). Khi lớp học đã `ENDED`, toàn bộ dữ liệu điểm số, log điểm, và báo cáo tuần của lớp học đó trở thành chỉ đọc (read-only), không cho phép tạo mới hay thay đổi.

### 3.3 Nhóm Tổ (Groups)
- **BR-GROUP-01:** Mỗi học sinh (`student_profiles`) chỉ được thuộc tối đa 1 tổ tại một thời điểm.
- **BR-GROUP-02:** Mỗi tổ (`groups`) có tối đa 1 Tổ trưởng, lưu trữ tại cột `leader_student_id`. Khi thay đổi tổ trưởng, Giáo viên sẽ cập nhật trường này. Người dùng cũ và mới vẫn giữ nguyên Role hệ thống là `STUDENT`, chỉ thay đổi chức vụ kiểm tra tại Service layer.

### 3.4 Nhóm Điểm số & Chấm điểm
- **BR-POINT-01:** Điểm thi đua hiện tại của học sinh được tính động bằng: `Base Point` (của lớp học hiện tại) cộng với tổng điểm (`point_value`) từ tất cả các bản ghi `point_logs` hợp lệ của học sinh đó trong lớp học hiện tại.
- **BR-POINT-02:** Bảng `point_logs` là bất biến (immutable). Không cho phép bất kỳ hành vi `UPDATE` hoặc `DELETE` nào trên bảng này. Nếu cần điều chỉnh sai sót, Giáo viên phải tạo một bản ghi `point_log` đối trừ (điểm ngược lại kèm lý do hiệu chỉnh).
- **BR-POINT-03:** Phân quyền chấm điểm tại Service layer:
  - Giáo viên được chấm điểm cho mọi học sinh trong lớp do mình quản lý.
  - Tổ trưởng chỉ được phép chấm điểm cho các thành viên trong cùng tổ (và tự chấm điểm bản thân). Nếu chấm điểm cho học sinh ngoài tổ, hệ thống trả về lỗi `403 STUDENT_NOT_IN_GROUP`.
- **BR-POINT-04:** Không thể tạo `point_log` cho một tuần đã bị khóa (`weekly_reports.is_locked = true`).

### 3.5 Nhóm Chốt điểm tuần (Weekly Lock)
- **BR-WEEK-01:** Cron Job tự động chốt điểm chạy lúc 23:59 Chủ Nhật hàng tuần theo múi giờ `Asia/Ho_Chi_Minh` (UTC+7).
- **BR-WEEK-02:** Khi chốt điểm tuần (tự động hoặc do Giáo viên bấm chốt thủ công trước thời hạn), hệ thống sẽ tính toán và lưu trữ snapshot vào bảng `weekly_reports`. Snapshot bao gồm: điểm số cuối cùng (`snapshot_point`), điểm cơ bản (`snapshot_base_point` của lớp), tổng điểm cộng thu được trong tuần (`total_bonus`), tổng điểm trừ trong tuần (`total_penalty`), cùng xếp hạng trong lớp và xếp hạng trong tổ.
- **BR-WEEK-03:** Sau khi tuần học đã chốt (`is_locked = true`), không ai có quyền thêm hoặc sửa đổi log điểm thuộc tuần đó.

### 3.6 Nhóm Dynamic Form có Versioning
- **BR-FORM-01:** Cấu trúc form thông tin học sinh (`form_templates`) hỗ trợ phiên bản (versioning). Khi Giáo viên cập nhật cấu trúc form, hệ thống không cập nhật trực tiếp bản ghi cũ mà sẽ tạo bản ghi mới với `version = version + 1` và đặt `is_active = true`, đồng thời cập nhật bản ghi cũ thành `is_active = false`.
- **BR-FORM-02:** Chỉ cho phép duy nhất 1 phiên bản form hoạt động (`is_active = true`) cho mỗi lớp tại một thời điểm.
- **BR-FORM-03:** Câu trả lời lý lịch của học sinh được lưu dạng `JSONB` trong `student_profiles.dynamic_profile`. Các key trong JSONB phải tuân thủ đúng cấu trúc trường của phiên bản form hoạt động tại thời điểm học sinh điền/cập nhật form.

### 3.7 Nhóm Audit Log
- **BR-AUDIT-01:** Hệ thống tự động ghi lại lịch sử các hoạt động quản trị nhạy cảm vào bảng `audit_logs`.
- **BR-AUDIT-02:** Các hành động bắt buộc phải ghi log bao gồm:
  - Phê duyệt / Từ chối hồ sơ Học sinh hoặc Giáo viên đăng ký.
  - Chỉ định / Thay đổi vị trí Tổ trưởng của lớp.
  - Chuyển học sinh sang tổ khác.
  - Kích hoạt phiên bản Dynamic Form mới.
  - Khóa điểm tuần (Weekly Lock).
  - Dừng lớp học (End Class).
- **BR-AUDIT-03:** Dữ liệu log bao gồm mã định danh của người thực hiện (`actor_user_id`), hành động (`action`), đối tượng bị tác động (`entity_name`, `entity_id`), giá trị cũ (`old_value` dưới dạng JSON hoặc Text) và giá trị mới (`new_value`).

---

## 4. DATABASE SCHEMA ĐẦY ĐỦ

```sql
-- ===========================================
-- HỆ THỐNG QUẢN LÝ LỚP CHỦ NHIỆM - POSTGRESQL SCHEMA
-- ===========================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. NGƯỜI DÙNG GỐC (USERS)
CREATE TABLE users (
    id               SERIAL PRIMARY KEY,
    full_name        VARCHAR(100) NOT NULL,
    google_email     VARCHAR(100) UNIQUE,              -- NULL nếu chưa liên kết Google
    phone_number     VARCHAR(15)  UNIQUE,              -- NULL nếu chưa liên kết SĐT
    phone_verified   BOOLEAN      NOT NULL DEFAULT FALSE,
    role             VARCHAR(20)  NOT NULL DEFAULT 'STUDENT'
                                  CHECK (role IN ('ADMIN', 'TEACHER', 'STUDENT')),
    approval_status  VARCHAR(20)  NOT NULL DEFAULT 'PENDING'
                                  CHECK (approval_status IN ('PENDING', 'APPROVED', 'REJECTED')),
    rejection_reason TEXT,
    approved_at      TIMESTAMP,
    created_at       TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_user_auth CHECK (
        google_email IS NOT NULL OR (phone_number IS NOT NULL AND phone_verified = TRUE)
    )
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_approval ON users(approval_status);

-- 2. HỒ SƠ GIÁO VIÊN (TEACHER PROFILES)
CREATE TABLE teacher_profiles (
    id          SERIAL PRIMARY KEY,
    user_id     INT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. LỚP HỌC (CLASSES)
CREATE TABLE classes (
    id             SERIAL PRIMARY KEY,
    class_name     VARCHAR(10) NOT NULL,              -- Ví dụ: "10A1"
    grade          INT NOT NULL CHECK (grade BETWEEN 10 AND 12),
    teacher_id     INT NOT NULL REFERENCES teacher_profiles(id),
    status         VARCHAR(10)  NOT NULL DEFAULT 'ACTIVE'
                                CHECK (status IN ('ACTIVE', 'ENDED')),
    base_point     INT          NOT NULL DEFAULT 100,
    created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Ràng buộc: chỉ cho phép tối đa 1 lớp học ACTIVE cho mỗi giáo viên chủ nhiệm
CREATE UNIQUE INDEX uq_class_active_per_teacher
    ON classes (teacher_id, status)
    WHERE status = 'ACTIVE';

-- 4. HỒ SƠ HỌC SINH (STUDENT PROFILES)
CREATE TABLE student_profiles (
    id               SERIAL PRIMARY KEY,
    user_id          INT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    class_id         INT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    group_id         INT,                              -- Được cập nhật sau khi phân tổ, tham chiếu chéo vòng tròn sẽ được khai báo sau
    dynamic_profile  JSONB DEFAULT '{}',               -- Lưu câu trả lời của form lý lịch
    status           VARCHAR(20) NOT NULL DEFAULT 'STUDYING'
                                 CHECK (status IN ('STUDYING', 'GRADUATED')),
    created_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_students_class ON student_profiles(class_id);

-- 5. TỔ (GROUPS)
CREATE TABLE groups (
    id                 SERIAL PRIMARY KEY,
    class_id           INT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    group_name         VARCHAR(50) NOT NULL,           -- Ví dụ: "Tổ 1"
    leader_student_id  INT REFERENCES student_profiles(id) ON DELETE SET NULL, -- Lưu trữ position Tổ trưởng
    created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (class_id, group_name)
);

-- Thêm khóa ngoại cho student_profiles.group_id để tránh lỗi lúc khởi tạo tuần tự
ALTER TABLE student_profiles ADD CONSTRAINT fk_student_group FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE SET NULL;
CREATE INDEX idx_students_group ON student_profiles(group_id);

-- 6. NHẬT KÝ OTP (OTP LOGS)
CREATE TABLE otp_logs (
    id            BIGSERIAL PRIMARY KEY,
    phone_number  VARCHAR(15) NOT NULL,
    otp_hash      VARCHAR(60) NOT NULL,                -- BCrypt hash của OTP 6 số
    purpose       VARCHAR(20) NOT NULL CHECK (purpose IN ('REGISTER', 'LINK_PHONE')),
    is_used       BOOLEAN NOT NULL DEFAULT FALSE,
    attempt_count INT NOT NULL DEFAULT 0,
    expires_at    TIMESTAMP NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_otp_phone ON otp_logs(phone_number, is_used, expires_at);

-- 7. LOG ĐIỂM SỐ (POINT LOGS - IMMUTABLE)
CREATE TABLE point_logs (
    id                 BIGSERIAL PRIMARY KEY,
    student_id         INT NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    class_id           INT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    created_by_user_id INT NOT NULL REFERENCES users(id), -- Truy vết bất kỳ User nào thực hiện chấm
    point_value        INT NOT NULL CHECK (point_value <> 0),
    reason             TEXT NOT NULL,
    week_start_date    DATE NOT NULL,
    created_at         TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_point_logs_student ON point_logs(student_id, class_id);
CREATE INDEX idx_point_logs_week ON point_logs(week_start_date);

-- 8. BÁO CÁO TUẦN (WEEKLY REPORTS)
CREATE TABLE weekly_reports (
    id                  BIGSERIAL PRIMARY KEY,
    student_id          INT NOT NULL REFERENCES student_profiles(id) ON DELETE CASCADE,
    class_id            INT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    week_start_date     DATE NOT NULL,
    week_end_date       DATE NOT NULL,
    snapshot_point      INT NOT NULL,                  -- Tổng điểm tại thời điểm chốt
    snapshot_base_point INT NOT NULL,                  -- Điểm nền (base_point) tại thời điểm chốt
    total_bonus         INT NOT NULL DEFAULT 0,        -- Tổng điểm cộng trong tuần
    total_penalty       INT NOT NULL DEFAULT 0,        -- Tổng điểm trừ trong tuần
    rank_in_class       INT,
    rank_in_group       INT,
    is_locked           BOOLEAN NOT NULL DEFAULT FALSE,
    locked_at           TIMESTAMP,
    locked_by           VARCHAR(20) CHECK (locked_by IN ('CRON', 'TEACHER')),
    created_at          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (student_id, week_start_date)
);

CREATE INDEX idx_weekly_reports_student ON weekly_reports(student_id, class_id);
CREATE INDEX idx_weekly_reports_week ON weekly_reports(week_start_date, is_locked);

-- 9. FORM ĐỘNG (FORM TEMPLATES - VERSIONED)
CREATE TABLE form_templates (
    id          SERIAL PRIMARY KEY,
    class_id    INT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    title       VARCHAR(200) NOT NULL,
    structure   JSONB NOT NULL DEFAULT '[]',           -- Cấu trúc JSON các trường
    version     INT NOT NULL DEFAULT 1,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (class_id, version)
);

CREATE UNIQUE INDEX uq_form_active_per_class
    ON form_templates (class_id)
    WHERE is_active = TRUE;

-- 10. LOG GIÁM SÁT HỆ THỐNG (AUDIT LOGS)
CREATE TABLE audit_logs (
    id             BIGSERIAL PRIMARY KEY,
    actor_user_id  INT REFERENCES users(id) ON DELETE SET NULL, -- Người thực hiện
    action         VARCHAR(50) NOT NULL,               -- Ví dụ: 'APPROVE_STUDENT', 'ASSIGN_LEADER'
    entity_name    VARCHAR(50) NOT NULL,               -- Ví dụ: 'student_profiles', 'groups'
    entity_id      INT NOT NULL,                       -- ID của bản ghi bị tác động
    old_value      JSONB,                              -- Giá trị cũ
    new_value      JSONB,                              -- Giá trị mới
    created_at     TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
```

---

## 5. API SPECIFICATION CHI TIẾT

Giao diện lập trình ứng dụng (API) được thiết kế dạng RESTful chuẩn, không nhúng vai trò hệ thống vào đường dẫn URL (role-free URLs). Phân quyền được xử lý tập trung tại Service Layer hoặc Web Security Filter.

### 5.1 Quản trị & Xác thực (Authentication)

#### POST `/api/v1/auth/register`
Đăng ký tài khoản người dùng mới (dành cho Giáo viên hoặc Học sinh).
- **Body:**
  ```json
  {
    "fullName": "Nguyễn Văn A",
    "googleIdToken": "eyJhbGci...",             // Tùy chọn (nếu dùng Google)
    "phoneNumber": "0987654321",                // Tùy chọn (nếu dùng SĐT)
    "otpCode": "123456",                        // Bắt buộc nếu đăng ký bằng SĐT
    "role": "STUDENT",                          // 'TEACHER' hoặc 'STUDENT'
    "schoolId": 1,                              // Bắt buộc đối với TEACHER
    "classId": 2                                // Bắt buộc đối với STUDENT
  }
  ```
- **Response 201:** `{"message": "Đăng ký thành công. Vui lòng chờ phê duyệt.", "status": "PENDING"}`

#### POST `/api/v1/auth/google`
Đăng nhập bằng tài khoản Google.
- **Body:** `{"idToken": "eyJhbGci..."}`
- **Response 200:**
  ```json
  {
    "accessToken": "eyJhbGci...",
    "expiresIn": 7200,
    "user": {
      "id": 1,
      "fullName": "Nguyễn Văn A",
      "role": "STUDENT",
      "approvalStatus": "APPROVED",
      "studentProfileId": 5                     // Hoặc teacherProfileId nếu là Giáo viên
    }
  }
  ```

#### POST `/api/v1/auth/refresh`
Làm mới token sử dụng cookie HttpOnly.
- **Response 200:** Trả về Access Token mới.

#### POST `/api/v1/auth/logout`
Đăng xuất và hủy cookie Refresh Token.
- **Response 200:** `{"message": "Đăng xuất thành công"}`

---

### 5.2 Phê duyệt Tài khoản (User Approvals)

#### GET `/api/v1/users/pending`
Lấy danh sách người dùng đang chờ phê duyệt (`PENDING`).
- **Phân quyền:** 
  - `ADMIN`: Xem danh sách Giáo viên (`TEACHER`) đang chờ duyệt.
  - `TEACHER`: Xem danh sách Học sinh (`STUDENT`) thuộc lớp mình quản lý đang chờ duyệt.
- **Response 200:**
  ```json
  {
    "content": [
      {
        "id": 5,
        "fullName": "Trần Thị B",
        "email": "student@gmail.com",
        "createdAt": "2026-09-01T08:00:00"
      }
    ]
  }
  ```

#### PUT `/api/v1/users/{id}/approve`
Phê duyệt người dùng đang chờ duyệt.
- **Phân quyền:** `ADMIN` duyệt Giáo viên, `TEACHER` duyệt Học sinh thuộc lớp mình.
- **Response 200:** Trả về đối tượng `User` đã duyệt với `approvalStatus = APPROVED`. Ghi nhận Audit Log.

#### PUT `/api/v1/users/{id}/reject`
Từ chối duyệt tài khoản kèm lý do.
- **Body:** `{"reason": "Không khớp thông tin lớp học"}`
- **Response 200:** Trả về đối tượng `User` với `approvalStatus = REJECTED`. Ghi nhận Audit Log.

---

### 5.3 Quản lý Lớp học (Classes)

#### POST `/api/v1/classes`
Khởi tạo lớp học mới.
- **Phân quyền:** `TEACHER`.
- **Body:** `{"className": "10A1", "grade": 10, "teacherId": 1, "basePoint": 100}`
- **Response 201:** Trả về đối tượng `ClassEntity` mới tạo. Ghi nhận Audit Log.

#### PUT `/api/v1/classes/{id}/end`
Dừng lớp học. Toàn bộ dữ liệu của lớp học chuyển sang read-only.
- **Phân quyền:** `TEACHER`.
- **Response 200:** Trả về lớp học có `status = ENDED`. Ghi nhận Audit Log.

---

### 5.4 Quản lý Học sinh & Tổ (Students & Groups)

#### GET `/api/v1/students`
Lấy danh sách học sinh (hỗ trợ phân trang, lọc theo tổ, trạng thái).
- **Phân quyền:** 
  - `TEACHER`: Xem toàn bộ học sinh lớp mình.
  - `STUDENT` là Tổ trưởng: Xem các thành viên trong tổ của mình.
- **Query params:** `?groupId=1&status=STUDYING&page=0&size=20`
- **Response 200:** Danh sách học sinh kèm thông tin điểm thi đua hiện tại.

#### GET `/api/v1/students/me`
Học sinh tự xem thông tin hồ sơ cá nhân và câu trả lời form lý lịch.
- **Response 200:** Đối tượng hồ sơ học sinh.

#### PUT `/api/v1/students/me/profile`
Học sinh điền/cập nhật thông tin lý lịch cá nhân.
- **Body:** `{"dynamicProfile": {"shirtSize": "L", "bus": true}}`
- **Response 200:** Hồ sơ học sinh đã cập nhật thành công.

#### POST `/api/v1/groups`
Tạo tổ mới trong lớp.
- **Phân quyền:** `TEACHER`.
- **Body:** `{"classId": 1, "groupName": "Tổ 1"}`

#### PUT `/api/v1/groups/{id}/leader`
Chỉ định Tổ trưởng cho tổ (Position).
- **Phân quyền:** `TEACHER`.
- **Body:** `{"studentProfileId": 5}`
- **Response 200:** Trả về thông tin nhóm đã được cập nhật Tổ trưởng mới. Ghi nhận Audit Log.

#### PUT `/api/v1/students/{id}/group`
Chuyển tổ cho học sinh.
- **Phân quyền:** `TEACHER`.
- **Body:** `{"groupId": 2}`
- **Response 200:** Trả về hồ sơ học sinh đã chuyển tổ. Ghi nhận Audit Log.

---

### 5.5 Chấm điểm thi đua (Points)

#### POST `/api/v1/points`
Tạo mới một log điểm thưởng/phạt cho học sinh.
- **Phân quyền:** 
  - `TEACHER`: Chấm điểm cho bất kỳ học sinh nào trong lớp.
  - `STUDENT` (chức vụ Tổ trưởng): Chấm điểm cho thành viên trong tổ.
- **Body:**
  ```json
  {
    "studentProfileId": 3,
    "pointValue": -5,
    "reason": "Đi học muộn",
    "weekStartDate": "2026-09-07"
  }
  ```
- **Response 201:** Đối tượng `PointLog` vừa tạo.

#### GET `/api/v1/points`
Lấy lịch sử log điểm của học sinh.
- **Phân quyền:** 
  - `TEACHER`: Xem của toàn lớp.
  - `STUDENT` (Tổ trưởng): Xem của các thành viên trong tổ.
  - `STUDENT` (Thường): Chỉ xem được lịch sử log điểm của chính mình.
- **Query Params:** `?studentProfileId=3&weekStartDate=2026-09-07`

---

### 5.6 Báo cáo & Dashboard (Weekly Reports & Dashboard)

#### GET `/api/v1/reports/weekly`
Lấy bảng xếp hạng tuần thi đua.
- **Phân quyền:** Mọi vai trò trong trường đều có thể xem báo cáo tuần của lớp.

#### POST `/api/v1/reports/weekly/lock`
Khóa và chốt điểm tuần thủ công trước khi Cron Job tự động chạy.
- **Phân quyền:** `TEACHER` của lớp.
- **Body:** `{"weekStartDate": "2026-09-07"}`
- **Response 200:** Snapshot tổng kết điểm tuần của cả lớp. Ghi nhận Audit Log.

#### GET `/api/v1/dashboard`
Lấy số liệu tổng quan hiển thị trên trang Dashboard.
- **Phân quyền:** `TEACHER` xem toàn lớp, `STUDENT` xem thông số của mình và tổ.

---

### 5.7 Cấu hình Form lý lịch (Dynamic Form)

#### POST `/api/v1/forms`
Tạo cấu trúc form mới cho lớp (phiên bản mới, không sửa đè phiên bản cũ).
- **Phân quyền:** `TEACHER`.
- **Body:**
  ```json
  {
    "classId": 1,
    "title": "Phiếu thu thập thông tin y tế 2026",
    "structure": [
      {"fieldName": "hasAllergy", "label": "Có dị ứng không?", "type": "boolean", "required": true},
      {"fieldName": "detailAllergy", "label": "Chi tiết dị ứng", "type": "textarea", "required": false}
    ]
  }
  ```
- **Response 201:** Trả về form template mới với `version` tự động tăng. Ghi nhận Audit Log.

#### GET `/api/v1/forms/active`
Lấy cấu trúc form đang hoạt động (`is_active = true`) của lớp.
- **Response 200:** Đối tượng Form Template đang hoạt động.

---

### 5.8 Giám sát Hệ thống (Audit Logs)

#### GET `/api/v1/audit-logs`
Lấy danh sách log giám sát hoạt động.
- **Phân quyền:** `ADMIN` xem toàn hệ thống, `TEACHER` xem các log liên quan đến trường/lớp mình quản lý.
- **Response 200:** Danh sách đối tượng `AuditLog`.

---

## 6. OAUTH2 + JWT FLOW

```
FLOW 1 — Đăng ký tài khoản Giáo viên & Học sinh (User-centric)

[React Frontend]               [Spring Boot Backend]             [Google/SMS]
       │                                 │                             │
       │─────── POST /auth/register ────►│                             │
       │        { googleToken, SĐT,      │                             │
       │          role, classId... }     │── Verify Google Token ─────►│
       │                                 │◄─ Trả về Email/Name ────────│
       │                                 │                             │
       │                                 │── Kiểm tra SĐT & verify OTP │
       │                                 │── Tạo User (PENDING)        │
       │◄────── 201 Created (Chờ duyệt) ─│                             │
       │                                 │                             │
       │   [Phê duyệt bởi Admin (TEACHER) hoặc Giáo viên (STUDENT)]    │
       │   [Trạng thái User cập nhật sang APPROVED]                    │

---

FLOW 2 — Đăng nhập hệ thống

[React Frontend]               [Spring Boot Backend]             [Google]
       │                                 │                          │
       │─────── POST /auth/google ──────►│                          │
       │        { idToken }              │── Verify idToken ───────►│
       │                                 │◄─ Trả về Email, Name ────│
       │                                 │                          │
       │                                 │── Kiểm tra trạng thái User
       │                                 │   - PENDING/REJECTED ➔ 403
       │                                 │   - APPROVED ➔ Sinh JWT  │
       │◄────── 200 OK {accessToken} ────│                          │
```

### Cấu trúc JWT Claims mới (User-centric)
```json
{
  "sub": "12",                                  // user_id
  "email": "teacher@gmail.com",
  "role": "TEACHER",                            // ADMIN | TEACHER | STUDENT
  "teacherProfileId": 3,                        // Hoặc studentProfileId nếu là STUDENT
  "classId": 2,                                 // Chỉ có đối với STUDENT
  "groupId": 4,                                 // Chỉ có đối với STUDENT (nếu đã phân tổ)
  "iat": 1770000000,
  "exp": 1770007200
}
```

---

## 7. VALIDATION RULES

### Chấm điểm (Point Log)
- `studentProfileId`: Phải tồn tại và đang học (`status = 'STUDYING'`). Nếu người chấm là Tổ trưởng, học sinh bị chấm phải nằm trong cùng tổ.
- `pointValue`: Kiểu số nguyên, khác 0, nằm trong đoạn `[-100, 100]`.
- `reason`: Bắt buộc, độ dài từ 5 đến 500 ký tự.
- `weekStartDate`: Phải là ngày thứ Hai đầu tuần, không được lớn hơn ngày hiện tại.

### Cấu trúc Form động (Dynamic Form Structure)
- Phải có dạng mảng JSON các object.
- Mỗi object định nghĩa một trường bắt buộc có: `fieldName` (unique), `label`, `type` (`text`, `number`, `boolean`, `select`, `date`, `textarea`), `required`.
- Với `type = 'select'`, bắt buộc phải cung cấp danh sách `options` khác rỗng.

---

## 8. ERROR HANDLING

### Cấu trúc JSON lỗi thống nhất
```json
{
  "timestamp": "2026-09-01T10:00:00+07:00",
  "status": 403,
  "error": "FORBIDDEN",
  "message": "Không có quyền thực hiện hành động này",
  "details": [],
  "path": "/api/v1/points"
}
```

### Các Mã lỗi đặc trưng (Error Codes)
- `VALIDATION_ERROR` (400): Dữ liệu đầu vào không hợp lệ.
- `INVALID_GOOGLE_TOKEN` (401): Google ID Token sai hoặc hết hạn.
- `REFRESH_TOKEN_EXPIRED` (401): Refresh Token lưu tại Cookie đã hết hạn.
- `UNAUTHORIZED` (401): Người dùng chưa xác thực.
- `FORBIDDEN` (403): Không có quyền hạn thực thi.
- `PENDING_APPROVAL` (403): Tài khoản của bạn đang chờ phê duyệt.
- `REGISTRATION_REJECTED` (403): Tài khoản đăng ký đã bị từ chối.
- `STUDENT_NOT_IN_GROUP` (403): Tổ trưởng chấm điểm cho học sinh ngoài tổ.
- `WEEK_ALREADY_LOCKED` (409): Tuần học đã chốt, không cho phép sửa điểm.
- `CLASS_ENDED` (409): Lớp học đã kết thúc, dữ liệu ở trạng thái read-only.
- `ACTIVE_CLASS_EXISTS` (409): Giáo viên đã có một lớp học ở trạng thái ACTIVE.
- `NOT_FOUND` (404): Bản ghi yêu cầu không tồn tại.

---

## 9. NON-FUNCTIONAL REQUIREMENTS

### 9.1 Tính tách biệt dữ liệu lớp học
- Toàn bộ dữ liệu của Lớp học, Học sinh phải được liên kết chặt chẽ qua khóa ngoại nhằm tránh rò rỉ dữ liệu chéo giữa các giáo viên khác nhau.
- Chỉ số index được thiết lập trên tất cả các khóa ngoại (`class_id`, `user_id`, `student_id`) để tối ưu hóa truy vấn khi lượng dữ liệu lớn.

### 9.2 Cron Job chốt điểm tuần
```java
// Spring Boot Scheduler chạy lúc 23:59 Chủ Nhật (UTC+7)
@Scheduled(cron = "59 23 * * SUN", zone = "Asia/Ho_Chi_Minh")
@Transactional
public void weeklyLockJob() {
    // 1. Quét toàn bộ các lớp học đang ACTIVE
    // 2. Với mỗi lớp học ACTIVE:
    //    a. Xác định tuần hiện tại (Thứ Hai -> Chủ Nhật)
    //    b. Bỏ qua nếu tuần đó đã được chốt thủ công (is_locked = true)
    //    c. Tính snapshot_point, snapshot_base_point, total_bonus, total_penalty của từng học sinh
    //    d. Lưu bản ghi vào weekly_reports với locked_by = 'CRON' và is_locked = true
    //    e. Thực hiện xếp hạng (rank_in_class và rank_in_group)
    // 3. Ghi log kiểm toán (Audit Log)
}
```

---

## 10. IMPLEMENTATION CHECKLIST

### Sprint 1 — Base & Auth Refactor
- [ ] Thiết lập Database Migration (Flyway/Liquibase) cho schema cơ sở dữ liệu User-centric.
- [ ] Triển khai thực thể `User`, `TeacherProfile`, `StudentProfile`.
- [ ] Cấu hình Spring Security hỗ trợ JWT phân quyền 3 role (`ADMIN`, `TEACHER`, `STUDENT`).
- [ ] Chuyển đổi luồng đăng nhập Google OAuth2 và OTP dựa trên `users`.
- [ ] Cập nhật định dạng JSON lỗi thống nhất và Global Exception Handler.

### Sprint 2 — Core API Refactor (Unified Design)
- [ ] Xây dựng API Lớp học (`classes`) và quản lý vòng đời lớp.
- [ ] Xây dựng API học sinh và Tổ (`groups`) sử dụng Position `leader_student_id` cho Tổ trưởng.
- [ ] Tái cấu trúc API chấm điểm `/api/v1/points` (phân quyền logic tại tầng Service).
- [ ] Triển khai Versioning cho `form_templates` và kiểm soát cập nhật.
- [ ] Cài đặt Interceptor / AOP ghi nhận tự động dữ liệu vào `audit_logs`.

### Sprint 3 — Reports, Cron & Dashboard
- [ ] Chỉnh sửa logic Cron Job tuần chốt snapshot nâng cao (`total_bonus`, `total_penalty`).
- [ ] Xây dựng API Dashboard tích hợp số liệu thống kê.
- [ ] Thực hiện di chuyển cấu trúc folder và chuyển đổi React code để gọi API theo thiết kế mới.

---

## 11. PROJECT STRUCTURE ĐỀ XUẤT

### Backend (Spring Boot)
Tổ chức thư mục theo phong cách Clean Architecture / Domain-driven Design kết hợp, gom nhóm các controller theo tài nguyên thay vì theo vai trò người dùng:

```
src/main/java/com/classmanager/
├── config/
│   ├── SecurityConfig.java
│   ├── JwtConfig.java
│   ├── CorsConfig.java
│   └── HikariConfig.java
├── controller/                        -- Thiết kế RESTful theo tài nguyên
│   ├── AuthController.java
│   ├── UserController.java            -- Duyệt duyệt, phân quyền users
│   ├── ClassController.java           -- Quản lý lớp học
│   ├── StudentController.java         -- Danh sách học sinh, lý lịch
│   ├── GroupController.java           -- Quản lý tổ, chức vụ tổ trưởng
│   ├── PointController.java           -- Chấm điểm, lịch sử log điểm
│   ├── WeeklyReportController.java    -- Xem xếp hạng, chốt tuần
│   ├── DashboardController.java       -- Thống kê tổng hợp
│   ├── FormTemplateController.java    -- Quản lý form động versioned
│   └── AuditLogController.java        -- Giám sát hoạt động
├── service/
│   ├── AuthService.java
│   ├── UserService.java
│   ├── ClassService.java
│   ├── StudentService.java
│   ├── GroupService.java
│   ├── PointLogService.java           -- Validate nghiệp vụ chấm điểm ở đây
│   ├── WeeklyReportService.java
│   ├── FormTemplateService.java       -- Logic versioning form động
│   └── AuditLogService.java           -- Ghi log giám sát
├── repository/
│   ├── UserRepository.java
│   ├── ClassRepository.java
│   ├── TeacherProfileRepository.java
│   ├── StudentProfileRepository.java
│   ├── GroupRepository.java
│   ├── PointLogRepository.java
│   ├── WeeklyReportRepository.java
│   ├── FormTemplateRepository.java
│   └── AuditLogRepository.java
├── entity/                            -- Entity tương ứng JPA
│   ├── User.java
│   ├── ClassEntity.java
│   ├── TeacherProfile.java
│   ├── StudentProfile.java
│   ├── Group.java
│   ├── PointLog.java
│   ├── WeeklyReport.java
│   ├── FormTemplate.java
│   └── AuditLog.java
├── dto/
│   ├── request/
│   │   ├── UserRegisterRequest.java
│   │   ├── PointLogRequest.java
│   │   ├── FormTemplateRequest.java
│   │   └── LeaderAssignRequest.java
│   └── response/
│       ├── AuthResponse.java
│       ├── StudentProfileResponse.java
│       └── PointLogResponse.java
├── exception/
│   ├── GlobalExceptionHandler.java
│   └── CustomExceptions.java          -- Định nghĩa các RuntimeException nghiệp vụ
└── scheduler/
    └── WeeklyLockScheduler.java       -- Cron Job lock tuần
```

### Frontend (React + TypeScript)
```
src/
├── components/
│   ├── common/
│   │   ├── ProtectedRoute.tsx
│   │   ├── Navbar.tsx
│   │   ├── Sidebar.tsx
│   │   └── TableSkeleton.tsx
│   ├── dashboard/
│   │   ├── OverviewCards.tsx
│   │   └── WeeklyChart.tsx
│   └── points/
│       ├── PointLogTable.tsx
│       └── AddPointForm.tsx
├── pages/
│   ├── auth/
│   │   └── LoginPage.tsx
│   ├── DashboardPage.tsx
│   ├── StudentListPage.tsx
│   ├── WeeklyReportPage.tsx
│   ├── FormBuilderPage.tsx
│   ├── ProfilePage.tsx
│   ├── MyPointsPage.tsx
│   └── AuditLogPage.tsx
├── types/                             -- Quản lý type tập trung
│   ├── auth.ts
│   ├── student.ts
│   ├── point.ts
│   └── api.ts
├── services/                          -- Axios API calls
│   ├── axiosInstance.ts
│   ├── authService.ts
│   ├── studentService.ts
│   ├── pointService.ts
│   └── dashboardService.ts
├── context/
│   └── AuthContext.tsx
└── utils/
    ├── constants.ts
    └── dateUtils.ts
```