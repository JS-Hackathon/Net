# Backlog & Kế hoạch Tối ưu hóa Hệ thống

Tài liệu này ghi lại các công việc cần thực hiện tiếp theo (Backlog) để tối ưu hóa, nâng cấp và ổn định hệ thống MockAI, đặc biệt tập trung vào việc xử lý các vấn đề hiện tại của tính năng bóc tách CV tự động bằng AI.

---

## 🚀 Nhiệm vụ Trọng tâm: Ổn định hóa & Tối ưu hóa luồng Bóc tách CV (Gemini AI)

Hiện tại, tính năng bóc tách thông tin từ CV (CV Parsing) sử dụng Gemini AI đang hoạt động chưa thực sự ổn định (đôi khi gặp lỗi trích xuất hoặc phản hồi chậm). Dưới đây là các đầu việc cần triển khai để tối ưu:

### 1. Tối ưu hóa System Prompt & JSON Schema cho Gemini
* **Vấn đề**: Định dạng dữ liệu bóc tách đôi khi không khớp với schema mong đợi của backend, dẫn đến lỗi parse JSON.
* **Giải pháp**:
  * Định nghĩa cấu trúc JSON Output cực kỳ chặt chẽ trong Prompt gửi cho Gemini.
  * Sử dụng tính năng `response_schema` (Pydantic / Structured Outputs) của Gemini API để ép buộc định dạng trả về thay vì parse text thủ công.
  * Thêm các ví dụ mẫu (Few-shot learning) trong Prompt để AI bóc tách chính xác hơn đối với các mục phức tạp như khoảng thời gian làm việc (Start/End Date) và danh sách dự án.

### 2. Xử lý CV dạng ảnh quét (Scan / OCR)
* **Vấn đề**: Các file PDF dạng ảnh quét không thể trích xuất text thông thường bằng thư viện PyPDF/PDFPlumber.
* **Giải pháp**:
  * Sử dụng **Gemini 1.5 Pro / Flash** ở chế độ multimodal: gửi trực tiếp file ảnh hoặc file PDF chứa ảnh scan cho mô hình để phân tích trực quan (Vision parsing).
  * Tích hợp công cụ OCR như Tesseract làm fallback để trích xuất văn bản thô trước khi gửi tới LLM.

### 3. Di chuyển Lưu trữ CV sang Cloud Storage (Cloudinary / Uploadcare)
* **Vấn đề**: Hiện tại CV được lưu tạm thời trên thư mục static của Backend, dễ gây đầy bộ nhớ và khó scale.
* **Giải pháp**:
  * Chuyển đổi luồng lưu trữ sang **Cloudinary** hoặc **Uploadcare** để quản lý CDN tốt hơn, tối ưu hóa kích thước file tải lên và tăng tính bảo mật.

### 4. Nâng cấp Cơ chế Xử lý Bất đồng bộ & Rate Limit
* **Vấn đề**: Cuộc gọi tới API của Gemini có thể bị nghẽn (timeout) hoặc vượt quá hạn mức miễn phí (Rate Limit) khi có nhiều người dùng đồng thời.
* **Giải pháp**:
  * Thiết lập cơ chế xếp hàng tác vụ (Task Queue) bằng **Celery + Redis** để tách biệt luồng upload và luồng phân tích.
  * Cài đặt thuật toán retry thông minh (Exponential backoff) tại backend khi gặp lỗi API Gemini.
  * Bổ sung cơ chế thông báo tiến trình qua WebSockets thay vì HTTP Polling liên tục.

---

## 🎨 Cải tiến Trải nghiệm Người dùng (UX Backlog)

### 1. Giao diện xem trước CV trực quan (Resume Preview)
* Tích hợp thanh xem trước CV trực tiếp (PDF viewer) ngay cạnh bảng đối chiếu thông tin bóc tách ([ParsedDataReview](file:///d:/Data/Personal/FPT_UNIVERSITY/JS_CLUB/2026/coding-inspiration-2026/Net/frontend/src/components/ParsedDataReview.tsx)), giúp ứng viên dễ dàng đối chiếu dữ liệu gốc và dữ liệu AI bóc tách được.

### 2. Sắp xếp danh mục kéo thả (Drag-and-Drop Reorder)
* Cho phép ứng viên kéo thả để thay đổi thứ tự hiển thị của các mục trong phần Kinh nghiệm làm việc, Học tập, hoặc các Dự án thực tế.

### 3. Đánh giá độ khớp CV với Job Description (JD Matcher)
* Phát triển tính năng cho phép ứng viên dán tin tuyển dụng (JD) để AI so khớp với Profile và đưa ra điểm số % tương thích cùng các gợi ý chỉnh sửa cụ thể.
