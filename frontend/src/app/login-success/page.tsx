"use client";

import { useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/lib/store/authStore";
import { Loader2 } from "lucide-react";

function LoginSuccessContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setTokens, checkAuth } = useAuthStore();

  useEffect(() => {
    const accessToken = searchParams.get("access_token");
    const refreshToken = searchParams.get("refresh_token");
    const error = searchParams.get("error");

    if (error) {
      router.push("/login?error=" + error);
      return;
    }

    if (accessToken && refreshToken) {
      // Lưu token vào localStorage qua Zustand action
      setTokens(accessToken, refreshToken);

      // Gọi checkAuth để fetch thông tin user profile
      checkAuth(true).then(() => {
        router.push("/");
      });
    } else {
      router.push("/login");
    }
  }, [searchParams, router, setTokens, checkAuth]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-zinc-950">
      <div className="text-center space-y-4">
        <Loader2 className="h-10 w-10 animate-spin text-primary mx-auto" />
        <h2 className="text-xl font-semibold text-zinc-800 dark:text-zinc-200">
          Đang hoàn tất đăng nhập...
        </h2>
        <p className="text-zinc-500 text-sm">
          Vui lòng đợi trong giây lát, bạn sẽ được chuyển hướng.
        </p>
      </div>
    </div>
  );
}

export default function LoginSuccessPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-zinc-950">
        <Loader2 className="h-10 w-10 animate-spin text-primary mx-auto" />
      </div>
    }>
      <LoginSuccessContent />
    </Suspense>
  );
}
