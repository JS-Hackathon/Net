"use client";

import React from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { toast } from "sonner";
import { Search, Sparkles, Bookmark, User, LogOut } from "lucide-react";
import { useAuthStore } from "@/lib/store/authStore";

const LINKS = [
  { href: "/jobs", label: "Tìm việc", icon: Search },
  { href: "/matches", label: "Kết quả match", icon: Sparkles },
  { href: "/bookmarks", label: "Đã lưu", icon: Bookmark },
  { href: "/profile", label: "Hồ sơ", icon: User },
];

/**
 * Shared application header used across all authenticated pages
 * (jobs, matches, bookmarks, profile, and their detail routes).
 * Keeps navigation + logout consistent in one place.
 */
export const AppHeader: React.FC = () => {
  const pathname = usePathname();
  const router = useRouter();
  const { logout } = useAuthStore();

  const handleLogout = async () => {
    try {
      await logout();
      toast.success("Đăng xuất thành công!");
    } catch {
      toast.error("Lỗi khi đăng xuất");
    } finally {
      router.push("/login");
    }
  };

  return (
    <header className="border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 sticky top-0 z-30 shadow-xs">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-primary to-secondary flex items-center justify-center font-bold text-white">
            M
          </div>
          <span className="font-bold tracking-wide hidden sm:inline">MockAI</span>
        </Link>

        <div className="flex items-center gap-1">
          <nav className="flex items-center gap-1">
            {LINKS.map(({ href, label, icon: Icon }) => {
              const active = pathname === href || (href !== "/jobs" && pathname.startsWith(href));
              return (
                <Link
                  key={href}
                  href={href}
                  className={`flex items-center gap-1.5 py-2 px-3 rounded-xl text-xs font-bold transition ${
                    active
                      ? "bg-primary/10 text-primary"
                      : "text-zinc-500 hover:text-zinc-900 dark:hover:text-white"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span className="hidden sm:inline">{label}</span>
                </Link>
              );
            })}
          </nav>

          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 py-2 px-3 ml-1 rounded-xl text-xs font-bold text-zinc-500 border border-transparent hover:text-red-500 hover:border-red-200 dark:hover:border-red-950 transition"
          >
            <LogOut className="h-4 w-4" />
            <span className="hidden sm:inline">Đăng xuất</span>
          </button>
        </div>
      </div>
    </header>
  );
};

export default AppHeader;
