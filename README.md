# MockAI - AI-powered Career Copilot

Dự án này là nền tảng **MockAI** hỗ trợ ứng viên chuẩn bị nghề nghiệp thông qua AI. Dự án bao gồm hai phần chính:
- **Backend**: FastAPI (Python), PostgreSQL, SQLAlchemy (Async), Alembic, và tích hợp các API ngoài (Google Gemini API, JSearch API, Cloudflare R2).
- **Frontend**: Next.js (TypeScript), TailwindCSS, TanStack Query, Zustand.

---

## 🛠️ Hướng dẫn cài đặt và chạy dự án

### 📋 Yêu cầu hệ thống
- **Docker** và **Docker Compose** (để chạy cơ sở dữ liệu PostgreSQL).
- **Python 3.10+** (cho Backend).
- **Node.js 18+** & **npm** / **yarn** / **pnpm** (cho Frontend).

---

### Bước 1: Khởi động cơ sở dữ liệu (PostgreSQL)
Dự án sử dụng Docker Compose để chạy nhanh một container cơ sở dữ liệu PostgreSQL.

1. Mở terminal tại thư mục gốc của dự án (`Net/`).
2. Chạy lệnh sau để khởi động PostgreSQL container ở chế độ nền (detached mode):
   ```bash
   docker-compose up -d
   ```
   *Cơ sở dữ liệu sẽ chạy ở cổng `5433` (như cấu hình trong `docker-compose.yml`).*

---

### Bước 2: Cài đặt & Khởi chạy Backend (FastAPI)

1. Mở terminal mới và di chuyển vào thư mục `backend/`:
   ```bash
   cd backend
   ```

2. Tạo và kích hoạt môi trường ảo (virtual environment):
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD)**:
     ```cmd
     python -m venv venv
     .\venv\Scripts\activate.bat
     ```
   - **macOS / Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

4. Cấu hình biến môi trường:
   - Copy file `.env.example` ở thư mục gốc thành file `.env`:
     ```bash
     cp ../.env.example ../.env
     ```
     *(Hoặc copy thủ công bằng File Explorer và cập nhật các API Key như `GEMINI_API_KEY`, `JSEARCH_API_KEY` nếu có).*

5. Chạy cơ sở dữ liệu di trú (Database Migrations) bằng Alembic:
   ```bash
   alembic upgrade head
   ```

6. Khởi động máy chủ phát triển (Development Server):
   ```bash
   uvicorn app.main:app --reload
   ```
   *Backend sẽ chạy tại: [http://localhost:8000](http://localhost:8000)*
   *Tài liệu API tự động (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)*

---

### Bước 3: Cài đặt & Khởi chạy Frontend (Next.js)

1. Mở một terminal mới khác và di chuyển vào thư mục `frontend/`:
   ```bash
   cd frontend
   ```

2. Cài đặt các gói phụ thuộc (Dependencies):
   ```bash
   npm install
   ```

3. Cấu hình biến môi trường cho Frontend (Tùy chọn):
   - Mặc định, frontend sẽ kết nối với API backend tại `http://localhost:8000`.
   - Nếu bạn muốn cấu hình khác đi, hãy tạo file `.env.local` bên trong thư mục `frontend/` và điền:
     ```env
     NEXT_PUBLIC_API_URL=http://localhost:8000
     NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id_here
     ```

4. Khởi động máy chủ phát triển (Development Server):
   ```bash
   npm run dev
   ```
   *Frontend sẽ chạy tại: [http://localhost:3000](http://localhost:3000)*

---

## 🧪 Chạy Kiểm thử (Testing)
Để chạy toàn bộ các bài kiểm thử tự động của Backend:
1. Di chuyển vào thư mục `backend/` và kích hoạt môi trường ảo.
2. Chạy lệnh:
   ```bash
   pytest
   ```
