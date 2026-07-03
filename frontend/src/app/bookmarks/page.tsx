"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { toast } from "sonner";
import { Loader2, Bookmark } from "lucide-react";
import { useAuthStore } from "@/lib/store/authStore";
import { jobService, BookmarkItem, JobSummary } from "@/lib/services/jobs";
import { JobsNav } from "@/components/jobs/JobsNav";
import { JobCard } from "@/components/jobs/JobCard";

export default function BookmarksPage() {
  const router = useRouter();
  const { user, checkAuth, isInitialized } = useAuthStore();

  const [items, setItems] = useState<BookmarkItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (isInitialized && !user) router.push("/login");
  }, [isInitialized, user, router]);

  const load = async () => {
    setLoading(true);
    try {
      setItems(await jobService.getBookmarks());
    } catch {
      toast.error("Không tải được danh sách đã lưu");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (user) load();
  }, [user]);

  const toggleBookmark = async (job: JobSummary) => {
    try {
      await jobService.unbookmark(job.id);
      setItems((prev) => prev.filter((b) => b.job.id !== job.id));
      toast.success("Đã bỏ lưu việc làm");
    } catch {
      toast.error("Thao tác thất bại");
    }
  };

  if (!isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-black">
        <Loader2 className="h-8 w-8 text-primary animate-spin" />
      </div>
    );
  }
  if (!user) return null;

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black font-sans text-foreground pb-16">
      <JobsNav />

      <main className="max-w-4xl mx-auto px-6 mt-8 space-y-6">
        <h1 className="text-2xl font-extrabold tracking-tight flex items-center gap-2">
          <Bookmark className="h-6 w-6 text-primary" /> Việc làm đã lưu
        </h1>

        {loading ? (
          <div className="grid md:grid-cols-2 gap-4">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="h-40 rounded-2xl bg-zinc-100 dark:bg-zinc-900 animate-pulse" />
            ))}
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-20 text-muted-foreground">
            <Bookmark className="h-12 w-12 mx-auto mb-3 opacity-30" />
            <p className="font-semibold">Bạn chưa lưu việc làm nào</p>
            <p className="text-sm mt-1">
              Vào <Link href="/jobs" className="text-primary font-bold hover:underline">Tìm việc</Link> để khám phá và lưu các tin phù hợp.
            </p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-4">
            {items.map((b) => (
              <JobCard key={b.job.id} job={b.job} onBookmarkToggle={toggleBookmark} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
