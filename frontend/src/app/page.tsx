"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { useAuthStore } from "@/lib/store/authStore";
import { ArrowRight, Sparkles, User, LogIn, ArrowUpRight } from "lucide-react";

export default function Home() {
  const { user, checkAuth, isInitialized } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <div className="min-h-screen flex flex-col justify-between bg-[#fbf9f8] dark:bg-[#111212] text-foreground select-none font-sans relative overflow-hidden">
      {/* Background glow animations */}
      <div className="absolute top-[-20%] left-[-20%] w-[60%] h-[60%] rounded-full bg-primary/10 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-20%] w-[60%] h-[60%] rounded-full bg-secondary/5 blur-[120px] pointer-events-none" />

      {/* Navbar */}
      <header className="max-w-5xl w-full mx-auto px-6 h-20 flex items-center justify-between z-10">
        <div className="flex items-center gap-2">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-tr from-primary to-secondary flex items-center justify-center font-bold text-white text-md shadow-md shadow-primary/15">
            M
          </div>
          <span className="font-extrabold tracking-wider text-lg">MockAI</span>
        </div>

        <nav className="flex items-center gap-4">
          {isInitialized && user ? (
            <Link
              href="/profile"
              className="flex items-center gap-1.5 py-2 px-4 rounded-xl bg-primary text-white font-semibold text-sm shadow-md shadow-primary/20 hover:opacity-95 transition"
            >
              <User className="h-4 w-4" />
              Hồ sơ ứng viên
            </Link>
          ) : (
            <>
              <Link
                href="/login"
                className="text-sm font-semibold hover:text-primary transition"
              >
                Đăng nhập
              </Link>
              <Link
                href="/register"
                className="flex items-center gap-1.5 py-2 px-4 rounded-xl bg-zinc-950 dark:bg-white text-white dark:text-zinc-950 font-semibold text-sm hover:opacity-90 transition"
              >
                Đăng ký
                <ArrowRight className="h-4 w-4" />
              </Link>
            </>
          )}
        </nav>
      </header>

      {/* Hero section */}
      <main className="max-w-4xl mx-auto px-6 text-center my-auto py-16 space-y-8 z-10">
        {/* Floating badge */}
        <div className="inline-flex items-center gap-1.5 py-1.5 px-3 rounded-full bg-primary/10 text-primary text-xs font-bold uppercase tracking-wider">
          <Sparkles className="h-3.5 w-3.5" />
          Nền tảng phỏng vấn AI thông minh
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-[1.15] text-zinc-900 dark:text-white">
          Chinh phục mọi nhà tuyển dụng cùng{" "}
          <span className="bg-gradient-to-r from-primary via-tertiary to-secondary bg-clip-text text-transparent">
            MockAI
          </span>
        </h1>

        <p className="text-base sm:text-xl text-muted-foreground leading-relaxed max-w-2xl mx-auto">
          Tối ưu hóa khả năng trả lời phỏng vấn, rèn luyện tư duy lập trình và nhận phản hồi chi tiết từ AI để nâng cấp bản thân mỗi ngày.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
          {isInitialized && user ? (
            <Link
              href="/profile"
              className="flex items-center justify-center gap-2 py-3.5 px-8 rounded-xl bg-gradient-to-r from-primary to-primary/95 text-white font-bold shadow-lg shadow-primary/20 hover:opacity-98 active:scale-[0.98] transition-all"
            >
              Vào cổng ứng viên
              <ArrowUpRight className="h-5 w-5" />
            </Link>
          ) : (
            <>
              <Link
                href="/login"
                className="flex items-center justify-center gap-2 py-3.5 px-8 rounded-xl bg-gradient-to-r from-primary to-primary/95 text-white font-bold shadow-lg shadow-primary/20 hover:opacity-98 active:scale-[0.98] transition-all"
              >
                Đăng nhập bắt đầu
                <LogIn className="h-5 w-5" />
              </Link>
              <Link
                href="/register"
                className="flex items-center justify-center py-3.5 px-8 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold hover:bg-zinc-50 dark:hover:bg-zinc-900 active:scale-[0.98] transition-all"
              >
                Đăng ký tài khoản
              </Link>
            </>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-zinc-200 dark:border-zinc-800 py-8 text-center text-sm text-muted-foreground z-10 bg-white/40 dark:bg-zinc-950/40 backdrop-blur-md">
        © 2026 JS Club. coding-inspiration-2026. Made with passion.
      </footer>
    </div>
  );
}
