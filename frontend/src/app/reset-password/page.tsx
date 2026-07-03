"use client";

import React, { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { authService } from "@/lib/services/auth";
import { toast } from "sonner";
import { Lock, ArrowLeft, ShieldAlert, KeyRound } from "lucide-react";

function ResetPasswordForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const isValidToken = !!token;

  useEffect(() => {
    if (!token) {
      toast.error("Thiếu mã xác thực khôi phục mật khẩu. Vui lòng kiểm tra lại liên kết.");
    }
  }, [token]);

  const isPasswordStrong = (pw: string) => {
    return (
      pw.length >= 8 &&
      /[A-Z]/.test(pw) &&
      /[a-z]/.test(pw) &&
      /[0-9]/.test(pw) &&
      /[^A-Za-z0-9]/.test(pw)
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) {
      toast.error("Mã khôi phục mật khẩu không khả dụng");
      return;
    }

    if (!newPassword || !confirmPassword) {
      toast.error("Vui lòng nhập mật khẩu mới");
      return;
    }

    if (newPassword !== confirmPassword) {
      toast.error("Mật khẩu xác nhận không trùng khớp");
      return;
    }

    if (!isPasswordStrong(newPassword)) {
      toast.error(
        "Mật khẩu yếu! Cần ít nhất 8 ký tự bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt"
      );
      return;
    }

    setIsSubmitting(true);
    try {
      await authService.resetPassword({
        token,
        newPassword,
      });
      // Điều hướng về login cùng với thông báo thành công
      router.push("/login?message=Đặt lại mật khẩu thành công. Vui lòng đăng nhập bằng mật khẩu mới.");
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } } };
      const msg = err.response?.data?.message || "Mã khôi phục mật khẩu không hợp lệ hoặc đã hết hạn.";
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

          <div className="space-y-2">
            <h2 className="text-2xl font-extrabold tracking-tight">Đặt lại mật khẩu</h2>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Vui lòng nhập mật khẩu mới của bạn bên dưới. Mật khẩu mới cần đảm bảo tính bảo mật cao.
            </p>
          </div>

          {isValidToken ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* New Password Field */}
              <div className="space-y-1">
                <label className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 flex items-center gap-1.5">
                  <Lock className="h-4 w-4 text-zinc-400" />
                  Mật khẩu mới
                </label>
                <input
                  type="password"
                  placeholder="••••••••"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/50 focus:bg-white dark:focus:bg-black focus:outline-none focus:ring-2 focus:ring-primary/45 transition duration-200"
                  disabled={isSubmitting}
                  required
                />
                {newPassword && (
                  <div className="pt-2 text-xs space-y-1 text-zinc-500">
                    <div className="flex items-center gap-1">
                      <div className={`h-1.5 w-1.5 rounded-full ${newPassword.length >= 8 ? 'bg-success' : 'bg-zinc-300'}`} />
                      <span>Tối thiểu 8 ký tự</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className={`h-1.5 w-1.5 rounded-full ${/[A-Z]/.test(newPassword) && /[a-z]/.test(newPassword) ? 'bg-success' : 'bg-zinc-300'}`} />
                      <span>Chữ hoa và chữ thường</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <div className={`h-1.5 w-1.5 rounded-full ${/[0-9]/.test(newPassword) && /[^A-Za-z0-9]/.test(newPassword) ? 'bg-success' : 'bg-zinc-300'}`} />
                      <span>Số và ký tự đặc biệt (!@#...)</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Confirm Password Field */}
              <div className="space-y-1">
                <label className="text-sm font-semibold text-zinc-700 dark:text-zinc-300 flex items-center gap-1.5">
                  <Lock className="h-4 w-4 text-zinc-400" />
                  Xác nhận mật khẩu mới
                </label>
                <input
                  type="password"
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/50 focus:bg-white dark:focus:bg-black focus:outline-none focus:ring-2 focus:ring-primary/45 transition duration-200"
                  disabled={isSubmitting}
                  required
                />
                {confirmPassword && newPassword !== confirmPassword && (
                  <span className="text-xs text-red-500 font-medium">Mật khẩu xác nhận chưa khớp</span>
                )}
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
                    Cập nhật mật khẩu
                    <KeyRound className="h-4 w-4" />
                  </>
                )}
              </button>
            </form>
          ) : (
            <div className="p-4 rounded-xl border border-red-200 bg-red-50/50 dark:bg-red-950/20 text-red-600 dark:text-red-400 flex gap-2.5 items-start">
              <ShieldAlert className="h-5 w-5 flex-shrink-0 mt-0.5" />
              <div className="text-sm leading-normal">
                Không tìm thấy mã xác thực khôi phục mật khẩu hợp lệ trong liên kết. Vui lòng kiểm tra lại email hoặc yêu cầu liên kết mới.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-black">
        <div className="h-10 w-10 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
      </div>
    }>
      <ResetPasswordForm />
    </Suspense>
  );
}
