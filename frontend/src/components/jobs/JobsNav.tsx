"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Search, Sparkles, Bookmark, User } from "lucide-react";

const LINKS = [
  { href: "/jobs", label: "Tìm việc", icon: Search },
  { href: "/matches", label: "Kết quả match", icon: Sparkles },
  { href: "/bookmarks", label: "Đã lưu", icon: Bookmark },
  { href: "/profile", label: "Hồ sơ", icon: User },
];

export const JobsNav: React.FC = () => {
  const pathname = usePathname();

  return (
    <header className="border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 sticky top-0 z-30 shadow-xs">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-primary to-secondary flex items-center justify-center font-bold text-white">
            M
          </div>
          <span className="font-bold tracking-wide hidden sm:inline">MockAI</span>
        </Link>

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
      </div>
    </header>
  );
};

export default JobsNav;
