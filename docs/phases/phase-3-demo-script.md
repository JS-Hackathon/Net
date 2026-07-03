# Phase 3 — Kịch bản Demo (Job Discovery + AI Matching)

> Mục tiêu: trình diễn end-to-end luồng **Tìm việc → Lưu → So khớp AI → Phân tích → Phản hồi** trong ~5–7 phút.
> Kịch bản **chạy được offline** (không cần Gemini/JSearch API key): JSearch trả 5 job mock có kỹ năng, matching dùng phân tích mock deterministic.

---

## 0. Chuẩn bị (trước khi lên demo)

```bash
# 1. Database
docker-compose up -d

# 2. Backend (Python 3.10–3.12)
cd backend
python -m venv venv && venv\Scripts\activate      # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head                               # tạo 7 bảng Phase 3 + trigger tsvector
uvicorn app.main:app --reload                      # http://localhost:8000/docs

# 3. Frontend
cd frontend && npm install && npm run dev          # http://localhost:3000
```

**Kiểm tra sẵn sàng:** mở `http://localhost:8000/health` → `db: ok`. Nếu `gemini`/`jsearch` = `mock_mode` là **bình thường** cho demo offline.

> 💡 Muốn demo dữ liệu thật: điền `GEMINI_API_KEY`, `JSEARCH_API_KEY` vào `.env` rồi restart backend. Mọi bước dưới đây giữ nguyên.

---

## 1. Nhân vật & bối cảnh

**Minh** — Frontend Developer ~2 năm kinh nghiệm, thạo **React, TypeScript, Next.js, TailwindCSS**, đang tìm việc tốt hơn.
Câu chuyện demo: Minh đăng nhập → tìm việc React → lưu tin hay → để AI chấm mức độ phù hợp với CV → xem điểm mạnh/kỹ năng còn thiếu → gửi phản hồi.

---

## 2. Kịch bản trình diễn (UI)

### Bước 1 — Đăng nhập & chuẩn bị hồ sơ
- Đăng nhập tài khoản Minh (hoặc đăng ký mới tại `/register`).
- Vào **Hồ sơ ứng viên** (`/profile`) → đảm bảo mục **Kỹ năng chuyên môn** có: React, TypeScript, Next.js, TailwindCSS, JavaScript. (Nếu chưa có, bấm *Chỉnh sửa* thêm nhanh — hoặc chạy script seed ở Phụ lục A.)

> 🎤 *"Mọi tính năng AI của MockAI đều dựa trên Hồ sơ năng lực đã cấu trúc — không parse lại CV mỗi lần."*

### Bước 2 — Tìm việc
- Vào **Tìm việc** (`/jobs`), gõ `react developer`, Enter.
- Kết quả: danh sách job hiển thị chức danh, công ty, **khoảng lương**, badge hình thức (remote/hybrid), kỹ năng, ngày đăng.

> 🎤 *"Dữ liệu lấy từ JSearch API và được cache 4 giờ trong Postgres để tiết kiệm quota. Tìm kiếm dùng full-text search (tsvector + GIN index)."*

### Bước 3 — Lọc
- Ở panel **Bộ lọc** bên trái, bật **Chỉ việc làm remote** → danh sách thu hẹp còn các tin remote.
- (Tùy chọn) chọn cấp độ **Senior** hoặc nhập lương tối thiểu.

### Bước 4 — Gợi ý theo hồ sơ
- Bấm **Gợi ý cho tôi**.
- Xuất hiện khu "Gợi ý theo hồ sơ của bạn": mỗi thẻ có badge **`% phù hợp`** (tính theo độ trùng kỹ năng giữa hồ sơ và job).

> 🎤 *"Đây là recommendation engine — xếp hạng job theo kỹ năng trong hồ sơ Minh."*

### Bước 5 — Lưu việc làm
- Bấm icon **bookmark** trên vài tin → icon chuyển sang dấu tick.
- Vào tab **Đã lưu** (`/bookmarks`) → thấy đúng các tin vừa lưu (bền vững qua phiên).

### Bước 6 — So khớp AI (điểm nhấn) ⭐
- Mở một tin (VD **Senior React Frontend Developer**) → trang chi tiết `/jobs/[id]`.
- Bấm **Match với CV của tôi** → AI phân tích → toast hiện điểm → tự chuyển sang trang kết quả `/matches/[id]`.
- Trang phân tích hiển thị:
  - **Vòng tròn điểm tổng** (màu: <60 đỏ, 60–80 vàng, >80 xanh).
  - **4 thanh điểm thành phần**: Kỹ năng 40% · Kinh nghiệm 35% · Học vấn 15% · Địa điểm 10%.
  - **Điểm mạnh** / **Kỹ năng còn thiếu** (kèm mức quan trọng).
  - **Ma trận kỹ năng** (badge Khớp tốt / Một phần / Còn thiếu / Điểm cộng).
  - **Cần cải thiện** + **Khuyến nghị** (nên ứng tuyển không, khả năng thành công, lời khuyên chuẩn bị).

> 🎤 *"Điểm tổng được tính có trọng số ở tầng service (deterministic) — không để AI tự cộng, đảm bảo ổn định. Nếu độ tin cậy < 80% hệ thống tự gắn cờ 'cần rà soát'."*

### Bước 7 — Phản hồi & (tùy chọn) so khớp hàng loạt
- Cuối trang, chấm **sao đánh giá** kết quả → toast cảm ơn (dữ liệu vào `match_quality_feedback` để cải thiện thuật toán).
- Vào **Kết quả match** (`/matches`) → danh sách tất cả match, lọc theo điểm (≥60, ≥80), sắp theo điểm giảm dần.
- (Tùy chọn nâng cao) demo **batch-match** qua Swagger `POST /api/v1/jobs/batch-match` với nhiều `job_ids` → trả `processing_summary` (tổng/thành công/thất bại/thời gian TB).

---

## 3. Thông điệp chốt
- **Feature 5**: tìm việc thật + cache + full-text + bookmark + gợi ý theo hồ sơ.
- **Feature 6**: chấm điểm tương thích bằng AI, giải thích **VÌ SAO** khớp/không khớp — giá trị cốt lõi giúp ứng viên ra quyết định.
- Kiến trúc sạch: AI provider thay thế được (Gemini → OpenAI/Claude) mà không đổi business logic.

---

## Phụ lục A — Script seed + demo bằng cURL (offline, không cần key)

Chạy trọn luồng bằng API (hữu ích khi demo backend hoặc chuẩn bị dữ liệu trước cho UI). Cần `curl` + `jq`.

```bash
BASE=http://localhost:8000/api/v1

# 1) Đăng ký (bỏ qua nếu đã có tài khoản) & đăng nhập lấy token
curl -s -X POST $BASE/auth/register -H 'Content-Type: application/json' -d '{
  "email":"minh.demo@example.com","password":"Demo@1234",
  "full_name":"Nguyen Van Minh","terms_accepted":true
}' >/dev/null

TOKEN=$(curl -s -X POST $BASE/auth/login -H 'Content-Type: application/json' -d '{
  "email":"minh.demo@example.com","password":"Demo@1234"
}' | jq -r '.data.access_token')
AUTH="Authorization: Bearer $TOKEN"

# 2) Seed hồ sơ: kỹ năng + kinh nghiệm + học vấn (để matching có dữ liệu đẹp)
curl -s -X PUT $BASE/profile -H "$AUTH" -H 'Content-Type: application/json' -d '{
  "section":"technical_skills",
  "data":{"technical_skills":[
    {"name":"React","category":"frontend","proficiency":"advanced","years_experience":2},
    {"name":"TypeScript","category":"frontend","proficiency":"advanced","years_experience":2},
    {"name":"Next.js","category":"frontend","proficiency":"intermediate","years_experience":1},
    {"name":"TailwindCSS","category":"frontend","proficiency":"advanced","years_experience":2},
    {"name":"JavaScript","category":"frontend","proficiency":"advanced","years_experience":3}
  ]}}' >/dev/null

curl -s -X PUT $BASE/profile -H "$AUTH" -H 'Content-Type: application/json' -d '{
  "section":"professional_summary",
  "data":{"years_of_experience":2,"current_role":"Frontend Developer"}}' >/dev/null

curl -s -X PUT $BASE/profile -H "$AUTH" -H 'Content-Type: application/json' -d '{
  "section":"education",
  "data":{"education":[{"degree":"BSc Software Engineering","institution":"FPT University","graduation_date":"2024"}]}}' >/dev/null

# 3) Tìm việc (nạp cache job từ JSearch mock)
curl -s "$BASE/jobs/search?q=react%20developer&page=1" -H "$AUTH" | jq '.data.pagination, (.data.jobs[] | {id,title,company,salary_range,is_bookmarked})'

# Lưu 1 job_id để dùng tiếp
JOB_ID=$(curl -s "$BASE/jobs/search?q=react%20developer" -H "$AUTH" | jq -r '.data.jobs[0].id')

# 4) Bookmark + xem danh sách đã lưu
curl -s -X POST $BASE/jobs/$JOB_ID/bookmark -H "$AUTH" | jq '.data'
curl -s $BASE/jobs/bookmarks -H "$AUTH" | jq '.data.total'

# 5) Gợi ý theo hồ sơ
curl -s $BASE/jobs/recommendations -H "$AUTH" | jq '.data.recommendations[] | {title:.job.title, score:.recommendation_score}'

# 6) So khớp AI 1 job → lấy match_id
MATCH_ID=$(curl -s -X POST $BASE/jobs/$JOB_ID/match -H "$AUTH" | jq -r '.data.match_id')
curl -s $BASE/matches/$MATCH_ID -H "$AUTH" | jq '{overall:.data.overall_score, skills:.data.skills_score, analysis:.data.analysis.summary, strengths:.data.analysis.strengths}'

# 7) So khớp hàng loạt (lấy tất cả job_id đang có)
IDS=$(curl -s "$BASE/jobs/search?q=developer&per_page=50" -H "$AUTH" | jq -c '[.data.jobs[].id]')
curl -s -X POST $BASE/jobs/batch-match -H "$AUTH" -H 'Content-Type: application/json' -d "{\"job_ids\":$IDS}" | jq '.data.processing_summary'

# 8) Danh sách match (lọc điểm ≥ 60) + gửi phản hồi 5 sao
curl -s "$BASE/matches?min_score=60&sort=score&order=desc" -H "$AUTH" | jq '.data.matches[] | {title:.job.title, score:.overall_score}'
curl -s -X POST $BASE/matches/$MATCH_ID/feedback -H "$AUTH" -H 'Content-Type: application/json' -d '{"user_rating":5,"feedback_type":"applied"}' | jq '.data.message'
```

---

## Phụ lục B — Bảng endpoint Phase 3

| Method | Endpoint | Chức năng |
|---|---|---|
| GET | `/jobs/search` | Tìm việc (cache 4h, filter, phân trang, full-text) |
| GET | `/jobs/{id}` | Chi tiết job (ghi nhận lượt xem) |
| POST/DELETE | `/jobs/{id}/bookmark` | Lưu / bỏ lưu |
| GET | `/jobs/bookmarks` | Danh sách đã lưu |
| GET | `/jobs/recommendations` | Gợi ý theo hồ sơ |
| GET/POST | `/jobs/saved-searches` | Tìm kiếm đã lưu (alert) |
| POST | `/jobs/{id}/match` | So khớp AI 1 job |
| POST | `/jobs/batch-match` | So khớp ≤50 job cùng lúc |
| GET | `/matches` | Danh sách match (lọc/sắp xếp) |
| GET | `/matches/{id}` | Chi tiết phân tích match |
| POST | `/matches/{id}/feedback` | Phản hồi chất lượng match |

---

## Phụ lục C — Xử lý sự cố nhanh
| Triệu chứng | Nguyên nhân / cách xử lý |
|---|---|
| `alembic upgrade head` lỗi | Postgres chưa chạy, hoặc block SQL `tsvector`/trigger — cần đúng Postgres (không phải SQLite) |
| Tìm việc trả rỗng | Query quá hẹp; mock luôn trả 5 job cho mọi từ khóa — thử `q=developer` |
| Match báo lỗi "hoàn thiện hồ sơ" | Hồ sơ chưa có kỹ năng — chạy bước seed (Phụ lục A) trước |
| Recommendation toàn 0% | Hồ sơ chưa có `technical_skills` trùng với kỹ năng job |
| `gemini/jsearch: mock_mode` | Bình thường khi demo offline; cắm key thật vào `.env` để dùng dữ liệu thật |
