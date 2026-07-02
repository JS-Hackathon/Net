# EduSpace React 19 + Tailwind v4 Project Template Spec

Tài liệu này chứa thông tin chi tiết về Tech Stack, danh sách thư viện (Libraries), cấu trúc thư mục (Folder Structure), các cấu hình cốt lõi (Core Configurations) và mã nguồn mẫu của dự án **SWP391-Group2-EduSpace**.

Bạn có thể sử dụng cấu trúc và các đoạn mã mẫu này làm khuôn mẫu (template) chuẩn để áp dụng, khởi tạo hoặc đồng bộ hóa các dự án mới có chung kiến trúc.

---

## 1. Công Nghệ Cốt Lõi (Tech Stack & Libraries)

Dự án sử dụng các phiên bản thư viện mới nhất tại thời điểm phát triển, tối ưu hóa cho React 19 và Tailwind CSS v4.

### Danh Sách Thư Viện (Dependencies)

| Tên Thư Viện | Phiên bản | Mô tả |
| :--- | :---: | :--- |
| **react** | `^19.2.6` | Thư viện giao diện chính (React 19) |
| **react-dom** | `^19.2.6` | React DOM hỗ trợ render môi trường trình duyệt |
| **react-router** | `^7.15.0` | Thư viện định tuyến React Router v7 |
| **tailwindcss** | `^4.3.0` | Framework CSS thế hệ mới Tailwind CSS v4 |
| **@tailwindcss/vite** | `^4.3.0` | Plugin tích hợp chính thức Tailwind CSS v4 vào Vite |
| **axios** | `^1.16.0` | HTTP Client phục vụ giao tiếp API với backend |
| **nprogress** | `0.2.0` | Thanh tiến trình chạy trên đầu trang khi gọi API |
| **sonner** | `^2.0.7` | Thư viện hiển thị thông báo Toast đẹp mắt, giàu tính năng |
| **class-variance-authority** | `^0.7.1` | Hỗ trợ định nghĩa nhiều biến thể (variants) cho UI components |
| **clsx** & **tailwind-merge** | `^2.1.1` / `^3.6.0` | Tiện ích ghép nối class Tailwind động mà không bị xung đột |
| **lucide-react** & **react-icons** | `^1.17.0` / `^5.6.0` | Bộ thư viện icon vector phong phú |
| **@hello-pangea/dnd** | `^18.0.1` | Thư viện kéo thả (Drag and Drop) thay thế cho react-beautiful-dnd |
| **@fontsource-variable/geist**| `^5.2.9` | Phông chữ Geist hỗ trợ cấu hình đa dạng (Variable Font) |
| **tw-animate-css** | `^1.4.0` | Tiện ích hỗ trợ tạo hiệu ứng chuyển động CSS |
| **shadcn** | `^4.11.0` | CLI và công cụ quản lý UI Components hệ Shadcn |

---

## 2. Cấu Trúc Thư Mục Chuẩn (Folder Structure)

Dự án áp dụng mô hình **Modular Architecture** (thiết kế theo Module tính năng) kết hợp với **View Wrapping Pattern** để dễ mở rộng và kiểm soát mã nguồn.

```text
frontend/
├── public/                 # Các tài nguyên tĩnh công cộng (images, icons, robots.txt...)
├── src/
│   ├── assets/             # Hình ảnh, logo tĩnh sử dụng trong mã nguồn
│   ├── components/         # Các Component dùng chung toàn dự án
│   │   ├── common/         # Layout chung, Logo, RouteProgressBar...
│   │   └── ui/             # Shadcn UI base components (Button, Input, Badge, Dialog...)
│   ├── contexts/           # Global Contexts chia sẻ trạng thái toàn bộ ứng dụng (AuthContext...)
│   ├── lib/                # Cấu hình các thư viện bên thứ ba (axios.js, utils.js...)
│   ├── modules/            # [MANDATORY] Chứa các tính năng được module hóa độc lập
│   │   ├── auth/           # Ví dụ: Module Auth
│   │   │   ├── components/ # Component chỉ dùng riêng trong module này (LoginForm, RegisterForm...)
│   │   │   ├── pages/      # Các trang hoàn chỉnh thuộc module (LoginPage, RegisterPage...)
│   │   │   └── index.js    # Điểm xuất khẩu (export) duy nhất các page chính của module
│   │   ├── course-lifecycle/
│   │   ├── learning/
│   │   └── roadmap/
│   ├── routes/             # Định nghĩa phân quyền và bảo vệ tuyến đường (ProtectedRoute.jsx)
│   ├── services/           # Lớp giao tiếp API (authService.js, courseService.js...)
│   ├── utils/              # Các hàm trợ giúp và tiện ích dùng chung (utils.js...)
│   ├── views/              # [MANDATORY] Điểm đích của Router (chỉ import và bọc layout cho module pages)
│   │   ├── auth/           # Thư mục bọc các route Auth (Login.jsx, Register.jsx)
│   │   ├── admin/          # Thư mục bọc các route Admin
│   │   ├── creator/        # Thư mục bọc các route Creator
│   │   ├── Home.jsx        # Landing page
│   │   └── Error.jsx       # Trang báo lỗi 404
│   ├── App.jsx             # Cấu hình React Router, AuthProvider và khai báo toàn bộ Routes
│   ├── index.css           # Cấu hình Tailwind v4, Fonts, custom CSS Variables & Theme màu sắc
│   └── main.jsx            # Điểm khởi tạo ứng dụng React (React DOM root render)
├── components.json         # File cấu hình của Shadcn UI CLI
├── vite.config.js          # File cấu hình của Vite bundler (alias, plugins)
└── package.json            # Quản lý script và danh sách dependencies của dự án
```

---

## 3. Các File Cấu Hình Cốt Lõi (Core Configurations)

### 3.1. Cấu hình Vite (`vite.config.js`)
Sử dụng Plugin chính thức của Tailwind v4 (`@tailwindcss/vite`) và cấu hình Alias `@/` trỏ về thư mục `src`.

```javascript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

// https://vite.dev/config/
export default defineConfig({
    plugins: [react(), tailwindcss()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
});
```

### 3.2. Cấu hình Shadcn UI CLI (`components.json`)
Cấu hình chỉ định các alias thư mục phù hợp với dự án sử dụng Javascript (`.jsx` và `.js`).

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "radix-nova",
  "rsc": false,
  "tsx": false,
  "tailwind": {
    "config": "",
    "css": "src/index.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "iconLibrary": "lucide",
  "rtl": false,
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  },
  "registries": {}
}
```

### 3.3. Cấu hình Styles & Theme màu (`src/index.css`)
Cú pháp Tailwind v4 tích hợp với CSS Variables cho chế độ Light/Dark Mode và bảng màu thương hiệu đặc trưng:

```css
@import "tailwindcss";
@import "tw-animate-css";
@import "shadcn/tailwind.css";
@import "@fontsource-variable/geist";

@custom-variant dark (&:is(.dark *));

@theme {
    /* Font mặc định */
    --font-sans: "Be Vietnam Pro", ui-sans-serif, system-ui, sans-serif;

    /* Màu sắc thương hiệu (Brand Colors) */
    --color-primary: #0897C8;
    --color-secondary: #F28020;
    --color-tertiary: #75BB47;

    /* Màu văn bản (Neutral Text) */
    --color-neutral-dark: #1b1c1c;   /* Tiêu đề & text chính */
    --color-neutral-medium: #464555; /* Mô tả & text phụ */
    --color-neutral-light: #8e8d99;  /* Placeholder & disabled text */

    /* Nền và Bề mặt (Surfaces & Backgrounds) */
    --color-bg-base: #fbf9f8;        /* Nền trang chính */
    --color-bg-card: #f6f3f2;        /* Nền card, input */
    --color-bg-sidebar: #f0eded;     /* Nền sidebar */

    /* Viền (Borders) */
    --color-border-light: #c7c4d8;

    /* Hiệu ứng tương tác (Interactive States) */
    --color-hover-light: #e4e2e1;
    --color-active-light: #eae8e7;

    /* Trạng thái hệ thống (Semantic Colors) */
    --color-success: #10b981;
    --color-warning: #f59e0b;
    --color-danger: #ef4444;
    --color-info: #3b82f6;
}

body {
    font-family: var(--font-sans);
    color: var(--color-neutral-dark);
    background-color: var(--color-bg-base);
    -webkit-font-smoothing: antialiased;
}

/* Tùy chỉnh thanh tiến trình NProgress */
#nprogress .bar {
    background: var(--color-primary) !important;
    height: 4px !important;
}

#nprogress .peg {
    box-shadow: 0 0 10px var(--color-primary), 0 0 5px var(--color-primary) !important;
}

/* Biến CSS đồng bộ với Shadcn UI */
:root {
    --background: #fbf9f8;
    --foreground: #1b1c1c;
    --card: #f6f3f2;
    --card-foreground: #1b1c1c;
    --popover: #ffffff;
    --popover-foreground: #1b1c1c;
    --primary: #0897C8;
    --primary-foreground: #ffffff;
    --secondary: #F28020;
    --secondary-foreground: #ffffff;
    --muted: #f6f3f2;
    --muted-foreground: #8e8d99;
    --accent: #f0eded;
    --accent-foreground: #1b1c1c;
    --destructive: #ef4444;
    --destructive-foreground: #ffffff;
    --border: #c7c4d8;
    --input: #c7c4d8;
    --ring: #0897C8;
    --radius: 1rem;
    --sidebar: #f0eded;
    --sidebar-foreground: #1b1c1c;
    --sidebar-primary: #0897C8;
    --sidebar-primary-foreground: #ffffff;
    --sidebar-accent: #e4e2e1;
    --sidebar-accent-foreground: #1b1c1c;
    --sidebar-border: #c7c4d8;
    --sidebar-ring: #0897C8;
}

.dark {
    --background: #1b1c1c;
    --foreground: #fbf9f8;
    --card: #2c2b38;
    --card-foreground: #fbf9f8;
    --popover: #1b1c1c;
    --popover-foreground: #fbf9f8;
    --primary: #0897C8;
    --primary-foreground: #ffffff;
    --secondary: #F28020;
    --secondary-foreground: #ffffff;
    --muted: #2c2b38;
    --muted-foreground: #8e8d99;
    --accent: #2c2b38;
    --accent-foreground: #fbf9f8;
    --destructive: #ef4444;
    --destructive-foreground: #ffffff;
    --border: #464555;
    --input: #464555;
    --ring: #0897C8;
    --sidebar: #1b1c1c;
}

@layer base {
    * {
        @apply border-border outline-ring/50;
    }
    body {
        @apply bg-background text-foreground;
    }
}
```

---

## 4. Lớp Mạng & Xử Lý API (Network Layer & Axios Client)

### 4.1. Axios Instance (`src/lib/axios.js`)
Instance này tự động tích hợp thanh tiến trình `NProgress` và tự gắn token `Authorization: Bearer <token>` nếu người dùng đã đăng nhập.

```javascript
import axios from "axios";
import { getTokens } from "@/utils/utils.js";
import NProgress from "nprogress";
import "nprogress/nprogress.css";

// Tắt spinner tròn chỉ giữ lại thanh chạy ngang đầu trang
NProgress.configure({ showSpinner: false, speed: 400 });

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8080/api"
});

// Request Interceptor: Gắn Token và bắt đầu chạy progress bar
api.interceptors.request.use(
  (config) => {
    NProgress.start();
    const token = getTokens();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    NProgress.done();
    return Promise.reject(error);
  }
);

// Response Interceptor: Tắt progress bar khi hoàn tất
api.interceptors.response.use(
  (response) => {
    NProgress.done();
    return response;
  },
  (error) => {
    NProgress.done();
    return Promise.reject(error);
  }
);

export default api;
```

### 4.2. File Tiện Ích Đọc/Ghi Token (`src/utils/utils.js`)
Cung cấp helper giải mã JWT token ở client không cần thư viện ngoài, xử lý LocalStorage và bọc loading state.

```javascript
// Quản lý Token
export const setTokens = (accessToken) => {
    localStorage.setItem("access_token", accessToken);
}

export const getTokens = () => localStorage.getItem("access_token")

export const clearTokens = () => {
    localStorage.removeItem("access_token")
}

// Giải mã JWT Token ở Client
export const decodeToken = (token) => {
    if (!token) return null;
    try {
        const base64Url = token.split(".")[1];
        const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
        const jsonPayload = decodeURIComponent(
            window
                .atob(base64)
                .split("")
                .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
                .join("")
        );
        const claims = JSON.parse(jsonPayload);
        
        // Trả về định dạng Object User chuẩn của ứng dụng
        return {
            id: claims.userId,
            username: claims.sub,
            fullName: claims.name,
            email: claims.email,
            avatarUrl: claims.avatar || null,
            role: claims.role,
        };
    } catch (error) {
        console.error("Giải mã Token thất bại:", error);
        return null;
    }
};

// Đồng bộ hóa trạng thái Loading của UI Component với tác vụ Async
export const runWithLoading = async (setLoading, asyncFn) => {
    if (typeof setLoading !== "function") return asyncFn();
    setLoading(true);
    try {
        return await asyncFn();
    } finally {
        setLoading(false);
    }
};
```

---

## 5. Quản Lý Trạng Thái Xác Thực & Phân Quyền (Auth & Guarded Routes)

### 5.1. Authentication Context (`src/contexts/AuthContext.jsx`)
Giúp phục hồi session đăng nhập tự động khi người dùng F5 tải lại trang.

```javascript
import { createContext, useContext, useState, useEffect } from "react";
import { setTokens, clearTokens, getTokens, decodeToken } from "@/utils/utils";
import authService from "@/services/authService";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(() => {
        const savedUser = localStorage.getItem("user");
        if (savedUser) {
            try {
                return JSON.parse(savedUser);
            } catch (e) {
                console.error("Không thể khôi phục thông tin user lưu trữ:", e);
            }
        }
        const token = getTokens();
        return token ? decodeToken(token) : null;
    });
    const [isLoading, setIsLoading] = useState(true);

    const checkAuth = async () => {
        const token = getTokens();
        if (!token) {
            setUser(null);
            localStorage.removeItem("user");
            setIsLoading(false);
            return;
        }
        setIsLoading(true);
        try {
            const userData = await authService.getUserProfile();
            setUser(userData);
            localStorage.setItem("user", JSON.stringify(userData));
        } catch (error) {
            console.error("Auto login failed:", error);
            clearTokens();
            setUser(null);
            localStorage.removeItem("user");
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        checkAuth();
    }, []);

    const login = async (username, password) => {
        const { token, user: userData } = await authService.login(username, password);
        setTokens(token);
        setUser(userData);
        localStorage.setItem("user", JSON.stringify(userData));
    };

    const logout = () => {
        clearTokens();
        setUser(null);
        localStorage.removeItem("user");
    };

    const contextValue = {
        user,
        isLoading,
        login,
        logout,
        checkAuth,
    };

    return (
        <AuthContext.Provider value={contextValue}>
            {children}
        </AuthContext.Provider>
    );
};

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth phải được bọc bên trong AuthProvider");
    }
    return context;
}

export default AuthContext;
```

### 5.2. Đường Dẫn Được Bảo Vệ (`src/routes/ProtectedRoute.jsx`)
Thành phần bọc các trang chỉ cho phép các Role cụ thể truy cập.

```javascript
import { Navigate, Outlet } from "react-router";
import { useAuth } from "@/contexts/AuthContext";

const ProtectedRoute = ({ allowedRoles }) => {
    const { user, isLoading } = useAuth();

    // Màn hình chờ khi đang checkAuth khôi phục session
    if (isLoading) {
        return (
            <div className="flex h-screen w-screen items-center justify-center bg-slate-50">
                <div className="text-sm font-medium text-slate-500 animate-pulse">
                    Đang tải dữ liệu EduSpace...
                </div>
            </div>
        );
    }

    // Nếu chưa đăng nhập, đá về trang chủ
    if (!user) {
        return <Navigate to="/" replace />;
    }

    // Nếu đã đăng nhập nhưng không có Role thích hợp, đá về trang lỗi
    if (allowedRoles && !allowedRoles.includes(user.role)) {
        console.warn(`Từ chối quyền truy cập: Yêu cầu vai trò trong [${allowedRoles}], tài khoản có vai trò: ${user.role}`);
        return <Navigate to="/*" replace />;
    }

    return <Outlet />;
};

export default ProtectedRoute;
```

---

## 6. Các UI Component Cốt Lõi Tùy Biến (Custom Core UI Components)

### 6.1. Thành Phần Nút Bấm Đa Năng (`src/components/ui/Button.jsx`)
Được tùy biến từ Shadcn Button để tích hợp sẵn trạng thái `isLoading` cùng icon loading xoay tròn và tự động khóa nút khi đang hoạt động.

```javascript
import * as React from "react"
import { cva } from "class-variance-authority";
import { Slot } from "radix-ui"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "group/button inline-flex shrink-0 items-center justify-center rounded-lg border border-transparent bg-clip-padding text-sm font-medium whitespace-nowrap transition-all outline-none select-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 active:not-aria-[haspopup]:translate-y-px disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/20 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/80",
        outline: "border-border bg-background hover:bg-muted hover:text-foreground dark:border-input dark:bg-input/30",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/90",
        ghost: "hover:bg-muted hover:text-foreground",
        destructive: "bg-destructive/10 text-destructive hover:bg-destructive/20",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-8 gap-1.5 px-2.5",
        xs: "h-6 gap-1 px-2 text-xs",
        sm: "h-7 gap-1 px-2.5 text-[0.8rem]",
        lg: "h-9 gap-1.5 px-2.5",
        icon: "size-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant = "default",
  size = "default",
  asChild = false,
  isLoading = false,
  children,
  ...props
}) {
  const Comp = asChild ? Slot.Root : "button"

  return (
    <Comp
      data-slot="button"
      data-variant={variant}
      data-size={size}
      className={cn(buttonVariants({ variant, size, className }))}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading && (
        <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
      )}
      <Slot.Slottable>{children}</Slot.Slottable>
    </Comp>
  );
}

export { Button, buttonVariants }
export default Button
```

### 6.2. Nút Đăng Xuất An Toàn (`src/components/ui/LogoutButton.jsx`)
Tích hợp sẵn hiệu ứng dừng chờ 800ms tạo cảm giác mượt mà trước khi chuyển hướng.

```javascript
import React, { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { LogOut, Loader2 } from "lucide-react";

const LogoutButton = ({
    className = "flex items-center gap-2 px-4 py-2 text-sm font-semibold text-red-600 hover:bg-red-50 rounded-xl transition-all cursor-pointer",
    iconSize = 16,
    iconClassName = "",
    redirectPath = "/",
    children = "Đăng xuất",
    ...props
}) => {
    const { logout } = useAuth();
    const [isLoading, setIsLoading] = useState(false);

    const handleLogout = async (e) => {
        e.preventDefault();
        if (isLoading) return;
        setIsLoading(true);

        try {
            // Hiệu ứng chờ trải nghiệm mượt mà
            await new Promise((resolve) => setTimeout(resolve, 800));
            logout();
            window.location.href = redirectPath;
        } catch (error) {
            console.error("Logout failed:", error);
            setIsLoading(false);
        }
    };

    return (
        <button
            onClick={handleLogout}
            disabled={isLoading}
            className={`${className} ${isLoading ? "opacity-75 cursor-not-allowed" : ""}`}
            {...props}
        >
            {isLoading ? (
                <Loader2 size={iconSize} className="animate-spin shrink-0" />
            ) : (
                <LogOut size={iconSize} className={`shrink-0 ${iconClassName}`} />
            )}
            <span>{children}</span>
        </button>
    );
};

export default LogoutButton;
```

---

## 7. Các Quy Quy Tắc Phát Triển Đặc Thù (Development Conventions)

### 7.1. Định Dạng Phản Hồi Từ API (API Response Contract)
Hệ thống sử dụng chung định dạng phản hồi chuẩn từ Backend Spring Boot:
```json
{
  "isSuccess": true,  // boolean xác định trạng thái gọi API
  "code": 200,        // Mã HTTP status code
  "message": "...",   // Thông điệp kết quả hoặc mô tả lỗi
  "data": { ... }     // Payload chính trả về (có thể null)
}
```
**Quy định bóc tách ở Service:** Lớp Service tại Frontend bóc tách trực tiếp thuộc tính `response.data.data` để trả về cho Component, và ném lỗi (throw Error) chứa `response.data.message` khi `isSuccess === false`.

```javascript
// Ví dụ mẫu Service Layer
import api from '@/lib/axios';

const courseService = {
    getDetail: async (id) => {
        try {
            const response = await api.get(`/courses/${id}`);
            return response.data.data; // Trả thẳng data thô
        } catch (error) {
            const errorMsg = error.response?.data?.message || 'Lấy chi tiết khóa học thất bại!';
            throw new Error(errorMsg);
        }
    }
};
export default courseService;
```

### 7.2. Lập Trình Biểu Mẫu (Form Handling Pattern)
Dự án **không dùng** `react-hook-form`. Mọi form nhập liệu phải là **Controlled Form** truyền thống:

```javascript
import { useState } from "react";
import { runWithLoading } from "@/utils/utils";
import { toast } from "sonner";

const MyForm = () => {
    const [formData, setFormData] = useState({ title: "", content: "" });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        await runWithLoading(setIsSubmitting, async () => {
            try {
                // Gọi API qua Service
                await courseService.submit(formData);
                toast.success("Gửi biểu mẫu thành công!");
            } catch (error) {
                toast.error(error.message);
            }
        });
    };

    return (
        <form onSubmit={handleSubmit}>
            <input 
                name="title" 
                value={formData.title} 
                onChange={handleChange} 
                disabled={isSubmitting} 
            />
            <button type="submit" isLoading={isSubmitting}>
                Gửi đi
            </button>
        </form>
    );
};
```

---

## 8. Quy Tắc Đặt Tên File & Thư Mục (Naming Conventions)

Để giữ code gọn gàng, đồng bộ và tránh lỗi import trên các hệ điều hành phân biệt chữ hoa/thường (Linux):

| Thành Phần | Quy Tắc Đặt Tên | Ví Dụ |
| :--- | :--- | :--- |
| **Thư mục Module** | kebab-case | `src/modules/course-lifecycle/` |
| **Component UI / Common** | PascalCase | `src/components/ui/Button.jsx` |
| **Component trong Module** | PascalCase | `src/modules/auth/components/LoginForm.jsx` |
| **Trang hoàn chỉnh (Page)** | PascalCase + hậu tố `Page` | `src/modules/auth/pages/LoginPage.jsx` |
| **Service Layer** | camelCase + hậu tố `Service` | `src/services/courseService.js` |
| **Custom React Hooks** | camelCase + tiền tố `use` | `src/hooks/useCourse.js` |
| **React Context** | PascalCase + hậu tố `Context` | `src/contexts/AuthContext.jsx` |
| **Hàm tiện ích (Utility)** | camelCase | `src/utils/dateFormatter.js` |
