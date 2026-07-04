"use client";

import React, { useEffect, useState, useCallback, useRef } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Search, Loader2, Sparkles, Briefcase, Upload } from "lucide-react";
import { useAuthStore } from "@/lib/store/authStore";
import { jobService, JobSummary, JobRecommendation, Pagination } from "@/lib/services/jobs";
import { AppHeader } from "@/components/layout/AppHeader";
import { JobCard } from "@/components/jobs/JobCard";
import { JobSearchFilters, FilterState } from "@/components/jobs/JobSearchFilters";

const EMPTY_FILTERS: FilterState = {
  location: "",
  employmentType: "",
  experienceLevel: "",
  salaryMin: "",
  remote: false,
};

export default function JobsPage() {
  const router = useRouter();
  const { user, checkAuth, isInitialized } = useAuthStore();

  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState<FilterState>(EMPTY_FILTERS);
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [pagination, setPagination] = useState<Pagination | null>(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [recommendations, setRecommendations] = useState<JobRecommendation[]>([]);
  const [recLoading, setRecLoading] = useState(false);
  const [uploadingJd, setUploadingJd] = useState(false);
  const jdInputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (isInitialized && !user) router.push("/login");
  }, [isInitialized, user, router]);

  const runSearch = useCallback(
    async (page = 1) => {
      if (!query.trim()) {
        toast.error("Vui lòng nhập từ khóa tìm kiếm");
        return;
      }
      setLoading(true);
      try {
        const result = await jobService.search({
          q: query.trim(),
          location: filters.location || undefined,
          employmentType: filters.employmentType || undefined,
          experienceLevel: filters.experienceLevel || undefined,
          salaryMin: filters.salaryMin ? Number(filters.salaryMin) : undefined,
          remote: filters.remote,
          page,
        });
        setJobs(result.jobs);
        setPagination(result.pagination);
        setSearched(true);
      } catch {
        toast.error("Tìm kiếm việc làm thất bại. Vui lòng thử lại.");
      } finally {
        setLoading(false);
      }
    },
    [query, filters]
  );

  const loadRecommendations = async () => {
    setRecLoading(true);
    try {
      const recs = await jobService.getRecommendations();
      setRecommendations(recs);
      if (recs.length === 0) toast.info("Chưa có gợi ý. Hãy tìm kiếm vài việc làm và hoàn thiện hồ sơ trước.");
    } catch {
      toast.error("Không tải được gợi ý việc làm");
    } finally {
      setRecLoading(false);
    }
  };

  const handleJdUpload = async (file: File) => {
    setUploadingJd(true);
    try {
      const job = await jobService.uploadJd(file);
      toast.success(`Đã thêm tin tuyển dụng: ${job.title}`);
      setJobs((prev) => [job, ...prev.filter((j) => j.id !== job.id)]);
      setSearched(true);
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      toast.error(err.response?.data?.message || "Tải JD lên thất bại. Vui lòng thử lại.");
    } finally {
      setUploadingJd(false);
      if (jdInputRef.current) jdInputRef.current.value = "";
    }
  };

  const toggleBookmark = async (job: JobSummary) => {
    try {
      if (job.isBookmarked) {
        await jobService.unbookmark(job.id);
      } else {
        await jobService.bookmark(job.id);
      }
      setJobs((prev) => prev.map((j) => (j.id === job.id ? { ...j, isBookmarked: !j.isBookmarked } : j)));
    } catch {
      toast.error("Thao tác lưu việc làm thất bại");
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
      <AppHeader />

      <main className="max-w-6xl mx-auto px-6 mt-8 space-y-6">
        {/* Search bar */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 shadow-sm space-y-4">
          <h1 className="text-2xl font-extrabold tracking-tight flex items-center gap-2">
            <Briefcase className="h-6 w-6 text-primary" /> Khám phá việc làm
          </h1>
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4.5 w-4.5 text-zinc-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && runSearch(1)}
                placeholder="Chức danh, kỹ năng (VD: React developer)..."
                className="w-full pl-11 pr-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 focus:bg-white dark:focus:bg-black focus:outline-none focus:ring-2 focus:ring-primary/40 transition"
              />
            </div>
            <button
              onClick={() => runSearch(1)}
              disabled={loading}
              className="flex items-center justify-center gap-2 py-3 px-6 rounded-xl bg-primary text-white font-bold shadow-md shadow-primary/20 hover:opacity-95 active:scale-[0.98] disabled:opacity-60 transition"
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              Tìm kiếm
            </button>
            <button
              onClick={loadRecommendations}
              disabled={recLoading}
              className="flex items-center justify-center gap-2 py-3 px-5 rounded-xl border border-zinc-200 dark:border-zinc-800 font-bold hover:bg-zinc-50 dark:hover:bg-zinc-900 disabled:opacity-60 transition"
            >
              {recLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4 text-primary" />}
              Gợi ý cho tôi
            </button>
            <button
              onClick={() => jdInputRef.current?.click()}
              disabled={uploadingJd}
              title="Tải file JD (PDF/DOCX) để thêm tin tuyển dụng"
              className="flex items-center justify-center gap-2 py-3 px-5 rounded-xl border border-zinc-200 dark:border-zinc-800 font-bold hover:bg-zinc-50 dark:hover:bg-zinc-900 disabled:opacity-60 transition"
            >
              {uploadingJd ? <Loader2 className="h-4 w-4 animate-spin" /> : <Upload className="h-4 w-4 text-primary" />}
              Tải JD lên
            </button>
            <input
              ref={jdInputRef}
              type="file"
              accept=".pdf,.docx"
              className="hidden"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) handleJdUpload(f);
              }}
            />
          </div>
          <p className="text-xs text-muted-foreground">
            Không tìm thấy việc phù hợp? <span className="font-semibold text-primary">Tải JD lên</span> để AI thêm tin tuyển dụng vào danh sách tìm kiếm & Auto Match.
          </p>
        </div>

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <div className="space-y-3">
            <h2 className="font-extrabold text-lg flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" /> Gợi ý theo hồ sơ của bạn
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              {recommendations.map((r) => (
                <div key={r.job.id} className="relative">
                  <span className="absolute -top-2 -right-2 z-10 py-0.5 px-2 rounded-full bg-primary text-white text-[10px] font-black shadow">
                    {Math.round(r.recommendationScore)}% phù hợp
                  </span>
                  <JobCard job={r.job} onBookmarkToggle={toggleBookmark} />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Results grid */}
        <div className="grid lg:grid-cols-[260px_1fr] gap-6">
          <aside className="lg:sticky lg:top-24 h-fit">
            <JobSearchFilters filters={filters} onChange={setFilters} />
          </aside>

          <section className="space-y-4">
            {loading ? (
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-40 rounded-2xl bg-zinc-100 dark:bg-zinc-900 animate-pulse" />
                ))}
              </div>
            ) : !searched ? (
              <div className="text-center py-20 text-muted-foreground">
                <Briefcase className="h-12 w-12 mx-auto mb-3 opacity-30" />
                <p className="font-semibold">Nhập từ khóa để bắt đầu tìm việc</p>
              </div>
            ) : jobs.length === 0 ? (
              <div className="text-center py-20 text-muted-foreground">
                <p className="font-semibold">Không tìm thấy việc làm phù hợp</p>
                <p className="text-sm mt-1">Thử đổi từ khóa hoặc nới lỏng bộ lọc.</p>
              </div>
            ) : (
              <>
                {pagination && (
                  <p className="text-sm text-muted-foreground font-medium">
                    Tìm thấy <strong className="text-zinc-900 dark:text-white">{pagination.total}</strong> việc làm
                  </p>
                )}
                {jobs.map((job) => (
                  <JobCard key={job.id} job={job} onBookmarkToggle={toggleBookmark} />
                ))}

                {pagination && pagination.totalPages > 1 && (
                  <div className="flex items-center justify-center gap-3 pt-4">
                    <button
                      disabled={pagination.page <= 1}
                      onClick={() => runSearch(pagination.page - 1)}
                      className="py-2 px-4 rounded-xl border border-zinc-200 dark:border-zinc-800 text-sm font-bold disabled:opacity-40 hover:bg-zinc-50 dark:hover:bg-zinc-900 transition"
                    >
                      Trước
                    </button>
                    <span className="text-sm font-semibold">
                      Trang {pagination.page}/{pagination.totalPages}
                    </span>
                    <button
                      disabled={pagination.page >= pagination.totalPages}
                      onClick={() => runSearch(pagination.page + 1)}
                      className="py-2 px-4 rounded-xl border border-zinc-200 dark:border-zinc-800 text-sm font-bold disabled:opacity-40 hover:bg-zinc-50 dark:hover:bg-zinc-900 transition"
                    >
                      Sau
                    </button>
                  </div>
                )}
              </>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

