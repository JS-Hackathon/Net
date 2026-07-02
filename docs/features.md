Dựa trên SRS, nếu triển khai theo hướng feature-based architecture (Frontend + Backend + AI Service) thì mình không khuyến nghị implement theo đúng thứ tự FR-01 → FR-10. Thay vào đó nên đi theo dependency order, tức là feature nào là nền tảng thì làm trước để các feature AI phía sau có thể tái sử dụng. SRS cũng mô tả rõ luồng xử lý: Authentication → Upload → Resume Parsing → Candidate Profile → Job Discovery → Matching → Skill Gap → Recommendation → Roadmap → Interview → Snapshot.

Phase 0 — Foundation
Đây là phần chưa được ghi thành FR nhưng là nền móng.
Feature 0.1 - Project Infrastructure
Mục tiêu
Khởi tạo toàn bộ project.
Backend
FastAPI
PostgreSQL
SQLAlchemy
Alembic
JWT
Google OAuth
Gemini SDK
JSearch Client
Cloudflare R2 Storage
Frontend
NextJS
Tailwind
shadcn/ui
Tanstack Query
Zustand
React Hook Form
Zod

Feature 0.2 - Design System
Các component dùng chung
Button
Card
Dialog
Form
Input
Textarea
Badge
Avatar
Dropdown
Table
Pagination
Tabs
Timeline
Progress
Alert
Sonner
Loading
EmptyState
Skeleton


Phase 1 — User & Authentication
Đây là toàn bộ FR-01.

Feature 1 — Authentication
User Story
Là một Guest,
Tôi muốn đăng ký hoặc đăng nhập
để sử dụng hệ thống.

Bao gồm
Login
Email
Password
Register
Email
Password
Confirm Password
Google OAuth
Logout
Refresh Token

Database
User

Role

RefreshToken


API
POST /auth/register

POST /auth/login

POST /auth/google

POST /auth/logout

POST /auth/refresh

GET /me


UI
Login Page

Register Page

Forgot Password

Profile Menu


Done khi
JWT hoạt động
Google Login hoạt động
Route Guard hoạt động

Phase 2 — Candidate Profile
Đây là phần nền của toàn bộ AI.

Feature 2 — Resume Upload
FR-02.

User Story
Candidate upload CV.

Bao gồm
Upload
PDF
DOCX
Validation
file type
size
Storage
Cloudflare R2

Database
Resume


API
POST /resume

GET /resume

DELETE /resume


UI
Upload Card

Drag Drop

Upload Progress


Feature 3 — Resume Parsing
FR-03.

AI Pipeline
Resume

↓

Extract text

↓

Gemini

↓

Structured JSON

↓

Candidate Profile


Database
ResumeAnalysis

CandidateProfile


API
POST /resume/analyze

GET /analysis/{id}


UI
Analysis Result

Skills

Education

Experience


Feature 4 — Candidate Profile
FR-04.
Đây là nơi người dùng chỉnh sửa dữ liệu AI parse.

Chức năng
Edit
Skills
Education
Experience
Certificates
Languages

API
GET /profile

PUT /profile


Phase 3 — Job Matching

Feature 5 — Job Discovery
FR-05.

Chức năng
Search
Filter
Location
Salary
Company
Bookmark

API
GET /jobs

GET /jobs/{id}


UI
Search Bar

Job Card

Job Detail

Filter


Feature 6 — AI Matching
FR-06.

AI
Resume JSON


Job JSON
↓
Gemini
↓
Match Score

API
POST /matching

GET /matching


UI
Match %

Strength

Weakness

Ranking


Phase 4 — AI Career Advisor

Feature 7 — Skill Gap
FR-07.

AI sinh
Critical

High

Medium

Low


UI
Gap Table

Priority Badge

Suggestion


Feature 8 — Career Recommendation
FR-08.

AI sinh
Top Careers

Confidence

Reason


UI
Career Cards


Feature 9 — Learning Roadmap
FR-09.

AI sinh
Week

Topic

Priority

Resources


UI
Timeline

Week Card

Progress


Phase 5 — Mock Interview

Feature 10 — Mock Interview
FR-10.

Bao gồm
Generate Questions
↓
Answer
↓
Gemini Evaluate
↓
Feedback
↓
Summary

Database
Interview

Question

Answer

Evaluation


UI
Interview Room

Question

Timer

Answer Box

Feedback


Phase 6 — History

Feature 11 — Career Snapshot
FR-12.

Lưu
Analysis

Matching

Gap

Career

Roadmap

Interview


UI
Snapshot List

Snapshot Detail


Feature 12 — Analysis History
FR-13.

Cho phép
Timeline

Compare

History

Restore View


Phase 7 — Admin

Feature 13 — Admin Dashboard (Optional)
FR-14.

Users

Quota

Gemini Cost

Statistics

Logs


Thứ tự triển khai khuyến nghị cho Hackathon
Thay vì đi theo FR, nên chia thành các milestone để luôn có sản phẩm chạy được sau mỗi giai đoạn:
Sprint
Feature
Kết quả đạt được
Sprint 1
Foundation + Authentication
Người dùng đăng ký/đăng nhập và truy cập hệ thống
Sprint 2
Resume Upload + Resume Parsing + Candidate Profile
Upload CV và tạo hồ sơ ứng viên bằng AI
Sprint 3
Job Discovery + AI Matching
Gợi ý việc làm và tính Match Score
Sprint 4
Skill Gap + Career Recommendation + Learning Roadmap
Đưa ra phân tích và lộ trình phát triển cá nhân
Sprint 5
Mock Interview
Luyện phỏng vấn với AI và nhận đánh giá
Sprint 6
Career Snapshot + Analysis History
Lưu trữ lịch sử phân tích và theo dõi tiến trình
Sprint 7
Admin Dashboard (tùy chọn)
Quản trị người dùng và theo dõi hệ thống

Cách chia này phù hợp với kiến trúc trong SRS, nơi các chức năng AI được xây dựng tuần tự trên kết quả của các bước trước (Resume → Candidate Profile → Job Discovery → AI Matching → Skill Gap → Recommendation → Roadmap → Interview → Snapshot), giúp giảm phụ thuộc và tăng khả năng hoàn thành MVP trong thời gian hackathon.

