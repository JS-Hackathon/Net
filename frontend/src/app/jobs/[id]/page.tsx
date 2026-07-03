"use client";

import React, { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { toast } from "sonner";
import {
  Loader2, Bookmark, BookmarkCheck, MapPin, Building2, Wallet, ExternalLink,
  Sparkles, ArrowLeft,
} from "lucide-react";
import { useAuthStore } from "@/lib/store/authStore";
import { jobService, JobDetail } from "@/lib/services/jobs";
import { matchService } from "@/lib/services/matches";
import { JobsNav } from "@/components/jobs/JobsNav";

export default function JobDetailPage() {
  const router = useRouter();
  const params = useParams();
  const jobId = params.id as string;
  const { user, checkAuth, isInitialized } = useAuthStore();

  const [job, setJob] = useState<JobDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [matching, setMatching] = useState(false);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (isInitialized && !user) router.push("/login");
  }, [isInitialized, user, router]);

  useEffect(() => {
    if (!user) return;
    (async () => {
      try {
        setJob(await jobService.getJob(jobId));
      } catch {
        toast.error("Không tải được thông tin việc làm");
      } finally {
        setLoading(false);
      }
    })();
  }, [user, jobId]);

  const toggleBookmark = async () => {
    if (!job) return;
    try {
      if (job.isBookmarked) await jobService.unbookmark(job.id);
      else await jobService.bookmark(job.id);
      setJob({ ...job, isBookmarked: !job.isBookmarked });
    } catch {
      toast.error("Thao tác lưu việc làm thất bại");
    }
  };

  const runMatch = async () => {
    if (!job) return;
    setMatching(true);
    toast.info("AI đang phân tích mức độ phù hợp...");
    try {
      const result = await matchService.calculateMatch(job.id);
      toast.success(`Điểm phù hợp: ${Math.round(result.overallScore)}%`);
      router.push(`/matches/${result.matchId}`);
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      toast.error(err.response?.data?.message || "So khớp thất bại. Hãy đảm bảo hồ sơ đã hoàn thiện.");
    } finally {
      setMatching(false);
    }
  };

  if (!isInitialized || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-black">
        <Loader2 className="h-8 w-8 text-primary animate-spin" />
      </div>
    );
  }
  if (!user) return null;
  if (!job) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-black">
        <JobsNav />
        <div className="max-w-3xl mx-auto px-6 mt-16 text-center text-muted-foreground">
          <p className="font-semibold">Không tìm thấy việc làm.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black font-sans text-foreground pb-16">
      <JobsNav />

      <main className="max-w-4xl mx-auto px-6 mt-6 space-y-6">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-1.5 text-sm font-bold text-muted-foreground hover:text-primary transition"
        >
          <ArrowLeft className="h-4 w-4" /> Quay lại
        </button>

        {/* Header */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 shadow-sm space-y-4">
          <div className="flex items-start justify-between gap-4">
            <div className="space-y-2 min-w-0">
              <h1 className="text-2xl font-extrabold tracking-tight text-zinc-900 dark:text-white">{job.title}</h1>
              <p className="flex items-center gap-1.5 font-semibold text-muted-foreground">
                <Building2 className="h-4 w-4" /> {job.company}
              </p>
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-sm font-medium text-muted-foreground">
                {job.location && <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {job.location}</span>}
                {job.salaryRange && <span className="flex items-center gap-1 text-success font-bold"><Wallet className="h-3.5 w-3.5" /> {job.salaryRange}</span>}
                {job.employmentType && (
                  <span className="py-0.5 px-2 rounded-full bg-primary/10 text-primary font-bold uppercase tracking-wide text-[10px]">{job.employmentType}</span>
                )}
              </div>
            </div>
            <button
              onClick={toggleBookmark}
              className="shrink-0 h-10 w-10 rounded-xl border border-zinc-200 dark:border-zinc-800 flex items-center justify-center hover:bg-zinc-50 dark:hover:bg-zinc-800 transition"
            >
              {job.isBookmarked ? <BookmarkCheck className="h-5 w-5 text-primary" /> : <Bookmark className="h-5 w-5 text-zinc-400" />}
            </button>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 pt-2">
            <button
              onClick={runMatch}
              disabled={matching}
              className="flex items-center justify-center gap-2 py-3 px-6 rounded-xl bg-gradient-to-r from-primary to-primary/95 text-white font-bold shadow-md shadow-primary/20 hover:opacity-95 active:scale-[0.98] disabled:opacity-60 transition"
            >
              {matching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
              Match với CV của tôi
            </button>
            {job.applicationUrl && (
              <a
                href={job.applicationUrl}
                target="_blank"
                rel="noreferrer"
                className="flex items-center justify-center gap-2 py-3 px-6 rounded-xl border border-zinc-200 dark:border-zinc-800 font-bold hover:bg-zinc-50 dark:hover:bg-zinc-900 transition"
              >
                Ứng tuyển ngay <ExternalLink className="h-4 w-4" />
              </a>
            )}
          </div>
        </div>

        {/* Skills */}
        {job.skillsRequired.length > 0 && (
          <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm space-y-3">
            <h3 className="font-extrabold text-sm text-zinc-900 dark:text-white">Kỹ năng yêu cầu</h3>
            <div className="flex flex-wrap gap-2">
              {job.skillsRequired.map((s, i) => (
                <span key={i} className="py-1 px-3 rounded-lg bg-zinc-100 dark:bg-zinc-800 text-xs font-bold text-zinc-700 dark:text-zinc-300">{s}</span>
              ))}
            </div>
          </div>
        )}

        {/* Description / requirements / benefits */}
        {[
          { title: "Mô tả công việc", content: job.description },
          { title: "Yêu cầu", content: job.requirements },
          { title: "Quyền lợi", content: job.benefits },
        ].map(
          (sec) =>
            sec.content && (
              <div key={sec.title} className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm space-y-2">
                <h3 className="font-extrabold text-sm text-zinc-900 dark:text-white">{sec.title}</h3>
                <p className="text-sm leading-relaxed text-zinc-700 dark:text-zinc-300 whitespace-pre-line">{sec.content}</p>
              </div>
            )
        )}
      </main>
    </div>
  );
}
