"use client";

import React, { useState } from "react";
import Link from "next/link";
import { authService } from "@/lib/services/auth";
import { toast } from "sonner";
import { Mail, ArrowLeft, Send, CheckCircle2, ShieldAlert } from "lucide-react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) {
      toast.error("Vui lòng nhập địa chỉ email");
      return;
    }

    setIsSubmitting(true);
    try {
      await authService.forgotPassword(email);
      toast.success("Yêu cầu khôi phục mật khẩu đã được gửi!");
      setIsSubmitted(true);
    } catch (error: any) {
      const msg = error.response?.data?.message || "Đã xảy ra lỗi trong quá trình gửi yêu cầu.";
      toast.error(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-black p-6 font-sans text-foreground">
      {/* Glow Effects */}
      <div className="absolute top-[10%] left-[10%] w-[300px] h-[300px] rounded-full bg-primary/10 blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[10%] right-[10%] w-[300px] h-[300px] rounded-full bg-secondary/10 blur-[100px] pointer-events-none" />

      <div className="w-full max-w-[440px] bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-8 shadow-xl relative overflow-hidden">
        {/* Top Accent Line */}
        <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-primary via-tertiary to-secondary" />

        <div className="space-y-6">
          {/* Back button */}
          <Link
            href="/login"
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-muted-foreground hover:text-foreground transition duration-150"
          >
            <ArrowLeft className="h-4 w-4" />
            Quay lại đăng nhập
          </Link>

          {!isSubmitted ? (
            <>
              <div className="space-y-2">
                <h2 className="text-2xl font-extrabold tracking-tight">Quên mật khẩu?</h2>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Nhập địa chỉ email của bạn dưới đây. Chúng tôi sẽ gửi một liên kết khôi phục để bạn thiết lập lại mật khẩu mới.
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Email Field */}
                <div className="space-y-1.5">
                  <label className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 flex items-center gap-1.5">
                    <Mail className="h-4 w-4 text-zinc-400" />
                    Địa chỉ Email
                  </label>
                  <input
                    type="email"
                    placeholder="name@company.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full px-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/50 focus:bg-white dark:focus:bg-black focus:outline-none focus:ring-2 focus:ring-primary/45 transition duration-200"
                    disabled={isSubmitting}
                    required
                  />
                </div>

                {/* Info Card for Dev */}
                <div className="p-4 rounded-xl border border-primary/20 bg-primary/5 flex gap-2.5 items-start">
                  <ShieldAlert className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                  <div className="text-xs text-muted-foreground space-y-1 leading-normal">
                    <span className="font-bold text-primary block uppercase tracking-wider">Lưu ý kiểm thử</span>
                    Trong môi trường thử nghiệm (Development), liên kết đổi mật khẩu sẽ được ghi nhận trực tiếp ở <strong>console/terminal của backend</strong>.
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-gradient-to-r from-primary to-primary/90 text-white font-semibold shadow-md shadow-primary/20 hover:opacity-95 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none transition-all duration-200"
                >
                  {isSubmitting ? (
                    <div className="h-5 w-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    <>
                      Gửi liên kết khôi phục
                      <Send className="h-4 w-4" />
                    </>
                  )}
                </button>
              </form>
            </>
          ) : (
            <div className="text-center py-6 space-y-5 animate-scaleUp">
              <div className="mx-auto h-16 w-16 bg-success/10 text-success rounded-full flex items-center justify-center">
                <CheckCircle2 className="h-10 w-10" />
              </div>
              <div className="space-y-2">
                <h3 className="text-2xl font-extrabold tracking-tight text-success">Đã gửi yêu cầu</h3>
                <p className="text-sm text-muted-foreground leading-relaxed max-w-sm mx-auto">
                  Nếu email <strong>{email}</strong> đã đăng ký trên hệ thống, một email chứa liên kết đặt lại mật khẩu đã được gửi đi.
                </p>
              </div>
              <div className="p-4 rounded-xl border border-dashed border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/50 text-left space-y-2">
                <span className="text-xs font-bold text-zinc-600 dark:text-zinc-400 block uppercase tracking-wider">Các bước tiếp theo:</span>
                <ol className="text-xs text-muted-foreground list-decimal pl-4 space-y-1 leading-normal">
                  <li>Kiểm tra hộp thư đến (hoặc thư rác).</li>
                  <li>Nếu chạy thử nghiệm local, hãy xem <strong>Terminal chạy Backend</strong> để lấy link reset.</li>
                  <li>Nhấp vào liên kết để tạo mật khẩu mới.</li>
                </ol>
              </div>
              <Link
                href="/login"
                className="inline-flex w-full items-center justify-center py-3 px-4 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-semibold hover:bg-zinc-50 dark:hover:bg-zinc-900 transition duration-200"
              >
                Quay lại Đăng nhập
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
