# MockAI — Runbook

Vận hành local + deploy. Đọc kèm **Environment Matrix** (bảng biến môi trường trong kế hoạch xây lại hạ tầng).

---

## 1. Yêu cầu

- Docker Desktop (chạy Postgres local)
- Python 3.10+ và `venv` cho backend
- Node 18+ cho frontend

---

## 2. Chạy local

### 2.1. Cấu hình biến môi trường

```bash
# Backend (đọc .env ở GỐC repo)
cp .env.example .env            # rồi điền giá trị thật

# Frontend
cp frontend/.env.example frontend/.env.local
```

> **Windows:** trong `DATABASE_URL` và `NEXT_PUBLIC_API_URL` dùng `127.0.0.1` (KHÔNG `localhost`) để tránh độ trễ IPv6 ~1–2s mỗi request.

### 2.2. Khởi động Postgres (Docker)

```bash
docker compose up -d postgres      # Postgres publish ở host cổng 5433
docker compose ps                  # chờ tới khi healthy
```

### 2.3. Backend

```bash
cd backend
python -m venv venv
./venv/Scripts/activate            # Windows;  Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head               # tạo/migrate schema
uvicorn app.main:app --reload --port 8000
```

Lúc khởi động, log sẽ in tóm tắt cấu hình (ENV, CORS origins, integrations) và **kết quả kết nối DB**. Nếu DB lỗi, log báo rõ + gợi ý — sửa trước khi đi tiếp.

### 2.4. Frontend

```bash
cd frontend
npm install
npm run dev                        # http://localhost:3000
```

### 2.5. Kiểm tra nhanh (smoke test)

```bash
cd backend
./venv/Scripts/python.exe scripts/smoke_test.py            # local
./venv/Scripts/python.exe scripts/smoke_test.py https://net-bzr9.onrender.com   # prod
```

Kỳ vọng: `SMOKE TEST PASSED` với `services.db == ok`.

---

## 3. Deploy

### Backend → Render
- Blueprint `render.yaml` định nghĩa web service (Docker) + Postgres.
- Các biến `sync: false` (secrets + `DATABASE_URL`) phải set thủ công trong dashboard.
- **`DATABASE_URL`:** lấy external connection string của Render Postgres rồi đổi scheme thành `postgresql+asyncpg://...` (config bắt buộc driver async).
- `Dockerfile` tự chạy `alembic upgrade head` khi container khởi động.

### Frontend → Vercel
- Set `NEXT_PUBLIC_API_URL=https://net-bzr9.onrender.com` (KHÔNG kèm `/api/v1`).

### Google OAuth Console
Chỉ cần 2 redirect URI: `…/api/v1/auth/google/callback` cho `http://localhost:8000` và `https://net-bzr9.onrender.com`. JS origins: `http://localhost:3000` và domain Vercel.

---

## 4. Sự cố thường gặp

| Triệu chứng | Nguyên nhân | Xử lý |
|---|---|---|
| Backend timeout/500 lúc chạm DB (local) | DATABASE_URL trỏ DB cloud / Docker chưa lên | `docker compose up -d`; dùng `127.0.0.1:5433` |
| Boot lỗi "DATABASE_URL must use asyncpg" | URL dùng driver sync | Đổi thành `postgresql+asyncpg://...` |
| CORS chặn `/auth/me`, `/auth/refresh` | `ALLOWED_ORIGINS` thiếu origin Vercel | Thêm domain Vercel (không dấu `/` cuối) |
| Lỗi 500 hiện dạng "No CORS header" | `ENV=development` bật debug | Set `ENV=production` trên Render |
| Gọi API ra `/api/v1/api/v1/...` → 404 | `NEXT_PUBLIC_API_URL` dư `/api/v1` | Bỏ hậu tố, chỉ để origin |
| Login Google xong bị đá về `/login` | `checkAuth` xoá token khi `getMe` lỗi | (Phase 2) chỉ xoá khi thực sự 401 |

---

## 5. Trạng thái phase

- **P0 — Nền tảng:** `docker-compose.yml`, `.env.example` (root + frontend), config fail-fast + DB check lúc startup. ✅
- **P1 — Platform xanh:** `render.yaml`, `scripts/smoke_test.py`, runbook này. ✅
- **P2–P5:** Auth · CV parsing · Jobs · Matching — theo kế hoạch.
