"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/lib/store/authStore";
import { toast } from "sonner";
import { LogIn, Mail, Lock, ShieldAlert, ArrowRight } from "lucide-react";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, googleLogin, checkAuth, user, isLoading } = useAuthStore();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [mockGoogleEmail, setMockGoogleEmail] = useState("");
  const [showMockGoogle] = useState(false);

  // Lấy thông điệp thông báo từ redirect nếu có (ví dụ: đổi mật khẩu thành công)
  useEffect(() => {
    const message = searchParams.get("message");
    if (message) {
      toast.success(message);
    }
    // Hiển thị lý do khi bị đưa về trang đăng nhập (OAuth lỗi, phiên hết hạn...)
    const error = searchParams.get("error");
    if (error) {
      const errorMessages: Record<string, string> = {
        google_auth_failed: "Đăng nhập bằng Google thất bại. Vui lòng thử lại.",
        session_setup_failed: "Không thiết lập được phiên đăng nhập. Vui lòng thử lại.",
      };
      toast.error(errorMessages[error] || "Đăng nhập thất bại. Vui lòng thử lại.");
    }
    // Check auth status on mount
    checkAuth();
  }, [searchParams, checkAuth]);

  // Nếu đã đăng nhập thì tự động chuyển về trang chủ hoặc trang profile
  useEffect(() => {
    if (user) {
      router.push("/");
    }
  }, [user, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error("Vui lòng nhập đầy đủ email và mật khẩu");
      return;
    }

    setIsSubmitting(true);
    try {
      await login({ email, password });
      toast.success("Đăng nhập thành công!");
      router.push("/");
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } } };
      const msg = err.response?.data?.message || "Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.";
      toast.error(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGoogleLogin = async (token: string) => {
    setIsSubmitting(true);
    try {
      await googleLogin({ googleToken: token });
      toast.success("Đăng nhập bằng Google thành công!");
      router.push("/");
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } } };
      const msg = err.response?.data?.message || "Xác thực qua tài khoản Google thất bại";
      toast.error(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen grid lg:grid-cols-12 bg-background select-none font-sans text-foreground">
      {/* Cột Trái - Branding & Visuals */}
      <div className="hidden lg:flex lg:col-span-5 relative bg-zinc-950 p-12 flex-col justify-between overflow-hidden">
        {/* Glow Effects */}
        <div className="absolute top-[-20%] left-[-20%] w-[80%] h-[80%] rounded-full bg-primary/20 blur-[120px] pointer-events-none" />
        <div className="absolute bottom-[-20%] right-[-20%] w-[80%] h-[80%] rounded-full bg-secondary/15 blur-[120px] pointer-events-none" />

        {/* Logo */}
        <div className="flex items-center gap-2 z-10">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-primary to-secondary flex items-center justify-center font-bold text-white text-xl shadow-lg">
            M
          </div>
          <span className="text-xl font-bold tracking-wider bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">
            MockAI
          </span>
        </div>

        {/* Hero Text */}
        <div className="my-auto z-10 max-w-md space-y-6">
          <h1 className="text-4xl font-extrabold tracking-tight text-white leading-tight">
            Nâng tầm phỏng vấn với{" "}
            <span className="bg-gradient-to-r from-primary via-tertiary to-secondary bg-clip-text text-transparent">
              Trí tuệ nhân tạo
            </span>
          </h1>
          <p className="text-zinc-400 text-lg">
            Hệ thống chấm điểm ứng viên tự động, phản hồi kỹ năng phỏng vấn chuyên nghiệp bằng công nghệ AI tiên tiến.
          </p>
        </div>

        {/* Footer */}
        <div className="text-zinc-500 text-sm z-10">
          © 2026 JS Club. Coding Inspiration. All rights reserved.
        </div>
      </div>

      {/* Cột Phải - Form Đăng Nhập */}
      <div className="flex lg:col-span-7 items-center justify-center p-6 sm:p-12 md:p-16 relative">
        <div className="w-full max-w-[420px] space-y-8">
          <div className="space-y-2">
            <h2 className="text-3xl font-extrabold tracking-tight">Đăng nhập</h2>
            <p className="text-muted-foreground">
              Vui lòng nhập tài khoản để truy cập hệ thống phỏng vấn
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Field */}
            <div className="space-y-1.5">
              <label className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 flex items-center gap-1.5">
                <Mail className="h-4 w-4 text-zinc-400" />
                Địa chỉ Email
              </label>
              <div className="relative group">
                <input
                  type="email"
                  placeholder="name@company.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/50 focus:bg-white dark:focus:bg-black focus:outline-none focus:ring-2 focus:ring-primary/45 transition duration-200"
                  disabled={isLoading || isSubmitting}
                  required
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 flex items-center gap-1.5">
                  <Lock className="h-4 w-4 text-zinc-400" />
                  Mật khẩu
                </label>
                <Link
                  href="/forgot-password"
                  className="text-sm font-medium text-primary hover:underline transition duration-150"
                >
                  Quên mật khẩu?
                </Link>
              </div>
              <div className="relative group">
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/50 focus:bg-white dark:focus:bg-black focus:outline-none focus:ring-2 focus:ring-primary/45 transition duration-200"
                  disabled={isLoading || isSubmitting}
                  required
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading || isSubmitting}
              className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-gradient-to-r from-primary to-primary/90 text-white font-semibold shadow-md shadow-primary/20 hover:opacity-95 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none transition-all duration-200"
            >
              {isSubmitting ? (
                <div className="h-5 w-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  Đăng nhập
                  <LogIn className="h-4 w-4" />
                </>
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="relative flex py-2 items-center text-xs text-muted-foreground">
            <div className="flex-grow border-t border-zinc-200 dark:border-zinc-800"></div>
            <span className="flex-shrink mx-4 font-semibold uppercase tracking-wider">Hoặc tiếp tục với</span>
            <div className="flex-grow border-t border-zinc-200 dark:border-zinc-800"></div>
          </div>

          <div className="space-y-3">
            {/* Google OAuth Button */}
            <button
              type="button"
              onClick={() => {
                const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/api\/v1\/?$/, "").replace(/\/api\/?$/, "");
                window.location.href = `${baseUrl}/api/v1/auth/google/login`;
              }}
              disabled={isLoading || isSubmitting}
              className="w-full flex items-center justify-center gap-2.5 py-3 px-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-medium hover:bg-zinc-50 dark:hover:bg-zinc-900 active:scale-[0.98] transition duration-200"
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05" />
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335" />
              </svg>
              Đăng nhập qua Google
            </button>

            {/* Developer Mock Google Login Section */}
            {showMockGoogle && (
              <div className="p-4 rounded-xl border border-dashed border-primary/30 bg-primary/5 space-y-3 animate-fadeIn">
                <div className="flex items-center gap-2 text-xs font-bold text-primary uppercase tracking-wider">
                  <ShieldAlert className="h-4 w-4" />
                  Môi trường Thử nghiệm Developer
                </div>
                <p className="text-xs text-muted-foreground leading-normal">
                  Bạn có thể nhập email bất kỳ để giả lập luồng Google OAuth đăng ký/đăng nhập tự động mà không cần Client ID.
                </p>
                <div className="flex gap-2">
                  <input
                    type="email"
                    placeholder="candidate@jsclub.com"
                    value={mockGoogleEmail}
                    onChange={(e) => setMockGoogleEmail(e.target.value)}
                    className="flex-1 px-3 py-2 text-sm rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 focus:outline-none"
                  />
                  <button
                    onClick={() => {
                      if (!mockGoogleEmail) {
                        toast.error("Vui lòng nhập email mock");
                        return;
                      }
                      handleGoogleLogin(`mock_${mockGoogleEmail}`);
                    }}
                    disabled={isSubmitting}
                    className="px-3 py-2 text-sm font-semibold rounded-lg bg-primary text-white hover:bg-primary/95 flex items-center gap-1"
                  >
                    Go <ArrowRight className="h-3 w-3" />
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Register Link */}
          <div className="text-center text-sm text-muted-foreground">
            Chưa có tài khoản ứng viên?{" "}
            <Link
              href="/register"
              className="font-semibold text-secondary hover:underline transition duration-150"
            >
              Đăng ký ngay
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-black">
        <div className="h-10 w-10 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
      </div>
    }>
      <LoginForm />
    </Suspense>
  );
}
