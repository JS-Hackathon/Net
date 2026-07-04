"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { toast } from "sonner";
import {
  Loader2, Sparkles, Building2, MapPin, Wand2,
  MessageSquareText, Target, Lightbulb, CheckCircle2, AlertTriangle,
} from "lucide-react";
import { useAuthStore } from "@/lib/store/authStore";
import { matchService, AutoMatchResult } from "@/lib/services/matches";
import { AppHeader } from "@/components/layout/AppHeader";
import { MatchScoreIndicator } from "@/components/jobs/MatchScoreIndicator";

const CATEGORY_STYLES: Record<string, { label: string; cls: string }> = {
  behavioral: { label: "Hành vi", cls: "bg-blue-500/10 text-blue-600 dark:text-blue-400" },
  technical: { label: "Kỹ thuật", cls: "bg-primary/10 text-primary" },
  role: { label: "Vị trí", cls: "bg-purple-500/10 text-purple-600 dark:text-purple-400" },
  culture: { label: "Văn hoá", cls: "bg-amber-500/10 text-amber-600 dark:text-amber-500" },
};

export default function MatchesPage() {
  const router = useRouter();
  const { user, checkAuth, isInitialized } = useAuthStore();

  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<AutoMatchResult | null>(null);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (isInitialized && !user) router.push("/login");
  }, [isInitialized, user, router]);

  const runAutoMatch = async () => {
    setRunning(true);
    try {
      const r = await matchService.autoMatch();
      setResult(r);
      if (r.companies.length === 0) {
        toast.info("Chưa tìm thấy công ty phù hợp. Hãy vào Tìm việc để tải tin tuyển dụng trước.");
      } else {
        toast.success("Đã tạo gợi ý công ty & kịch bản phỏng vấn!");
      }
    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      toast.error(err.response?.data?.message || "Auto Match thất bại. Vui lòng thử lại.");
    } finally {
      setRunning(false);
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

  const scenario = result?.interviewScenario;

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black font-sans text-foreground pb-16">
      <AppHeader />

      <main className="max-w-4xl mx-auto px-6 mt-8 space-y-6">
        {/* Hero — the single Auto Match action */}
        <div className="relative overflow-hidden bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-8 shadow-sm text-center">
          <div className="absolute top-[-30%] right-[-10%] w-72 h-72 rounded-full bg-primary/10 blur-[90px] pointer-events-none" />
          <div className="relative space-y-4">
            <span className="inline-flex items-center gap-1.5 py-1 px-3 rounded-full bg-primary/10 text-primary text-[11px] font-black uppercase tracking-wider">
              <Sparkles className="h-3.5 w-3.5" /> AI Auto Match
            </span>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-zinc-900 dark:text-white text-balance">
              Công ty phù hợp & kịch bản phỏng vấn — trong một chạm
            </h1>
            <p className="text-sm text-muted-foreground max-w-xl mx-auto">
              AI xếp hạng các công ty hợp với hồ sơ của bạn và tạo sẵn một kịch bản phỏng vấn thử riêng cho vị trí phù hợp nhất.
            </p>
            <button
              onClick={runAutoMatch}
              disabled={running}
              className="inline-flex items-center justify-center gap-2 py-3.5 px-8 rounded-xl bg-primary text-white font-bold shadow-lg shadow-primary/20 hover:opacity-95 active:scale-[0.98] disabled:opacity-60 transition"
            >
              {running ? <Loader2 className="h-5 w-5 animate-spin" /> : <Wand2 className="h-5 w-5" />}
              {running ? "Đang phân tích hồ sơ..." : result ? "Chạy lại Auto Match" : "Auto Match ngay"}
            </button>
          </div>
        </div>

        {/* Empty helper before first run */}
        {!result && !running && (
          <div className="text-center py-10 text-muted-foreground">
            <Target className="h-10 w-10 mx-auto mb-3 opacity-30" />
            <p className="text-sm font-semibold">
              Cần hồ sơ có kỹ năng. Chưa có? Vào{" "}
              <Link href="/profile" className="text-primary font-bold hover:underline">Hồ sơ</Link> để hoàn thiện,
              và <Link href="/jobs" className="text-primary font-bold hover:underline">Tìm việc</Link> để tải tin tuyển dụng.
            </p>
          </div>
        )}

        {result && result.companies.length > 0 && (
          <>
            {/* Matched companies */}
            <section className="space-y-3">
              <h2 className="font-extrabold text-lg flex items-center gap-2">
                <Building2 className="h-5 w-5 text-primary" /> Công ty phù hợp
              </h2>
              <div className="space-y-3">
                {result.companies.map((c) => (
                  <div
                    key={c.jobId}
                    className="flex items-center gap-4 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm"
                  >
                    <MatchScoreIndicator score={c.matchScore} size="sm" showLabel={false} />
                    <div className="flex-1 min-w-0 space-y-1">
                      <Link href={`/jobs/${c.jobId}`} className="font-extrabold text-base text-zinc-900 dark:text-white truncate hover:text-primary transition block">
                        {c.title}
                      </Link>
                      <p className="flex flex-wrap items-center gap-3 text-xs font-semibold text-muted-foreground">
                        <span className="flex items-center gap-1"><Building2 className="h-3.5 w-3.5" /> {c.company}</span>
                        {c.location && <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {c.location}</span>}
                      </p>
                      {c.reason && <p className="text-xs text-muted-foreground line-clamp-1">{c.reason}</p>}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Interview scenario */}
            {scenario && (
              <section className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 shadow-sm space-y-5">
                <div className="flex items-center gap-2">
                  <MessageSquareText className="h-5 w-5 text-primary" />
                  <h2 className="font-extrabold text-lg">
                    Kịch bản phỏng vấn{result.target.company ? ` — ${result.target.company}` : ""}
                  </h2>
                </div>

                {scenario.opening && (
                  <p className="text-sm text-zinc-700 dark:text-zinc-300 bg-zinc-50 dark:bg-zinc-950 rounded-xl p-4 border border-zinc-100 dark:border-zinc-800">
                    {scenario.opening}
                  </p>
                )}

                {(scenario.focusSkills.length > 0 || scenario.gapsToPrepare.length > 0) && (
                  <div className="grid sm:grid-cols-2 gap-4">
                    {scenario.focusSkills.length > 0 && (
                      <div className="space-y-2">
                        <p className="text-xs font-black uppercase tracking-wider text-success flex items-center gap-1.5">
                          <CheckCircle2 className="h-4 w-4" /> Điểm mạnh nên nhấn mạnh
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {scenario.focusSkills.map((s, i) => (
                            <span key={i} className="py-1 px-2.5 rounded-lg bg-success/10 text-success text-xs font-bold">{s}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {scenario.gapsToPrepare.length > 0 && (
                      <div className="space-y-2">
                        <p className="text-xs font-black uppercase tracking-wider text-amber-600 flex items-center gap-1.5">
                          <AlertTriangle className="h-4 w-4" /> Điểm cần chuẩn bị
                        </p>
                        <div className="flex flex-wrap gap-1.5">
                          {scenario.gapsToPrepare.map((s, i) => (
                            <span key={i} className="py-1 px-2.5 rounded-lg bg-amber-500/10 text-amber-600 dark:text-amber-500 text-xs font-bold">{s}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                <div className="space-y-3">
                  <p className="text-xs font-black uppercase tracking-wider text-muted-foreground">Câu hỏi luyện tập</p>
                  {scenario.questions.map((q, i) => {
                    const cat = CATEGORY_STYLES[(q.category || "").toLowerCase()] || { label: q.category || "Khác", cls: "bg-zinc-500/10 text-zinc-500" };
                    return (
                      <div key={i} className="border border-zinc-100 dark:border-zinc-800 rounded-2xl p-4 space-y-2">
                        <div className="flex items-start gap-2">
                          <span className={`shrink-0 py-0.5 px-2 rounded-md text-[10px] font-black uppercase tracking-wider ${cat.cls}`}>{cat.label}</span>
                          <p className="font-bold text-sm text-zinc-900 dark:text-white">{q.question}</p>
                        </div>
                        {q.assesses && <p className="text-xs text-muted-foreground"><span className="font-semibold">Đánh giá:</span> {q.assesses}</p>}
                        {q.answerTip && (
                          <p className="text-xs text-primary/90 bg-primary/5 rounded-lg p-2.5 flex items-start gap-1.5">
                            <Lightbulb className="h-3.5 w-3.5 mt-0.5 shrink-0" /> {q.answerTip}
                          </p>
                        )}
                      </div>
                    );
                  })}
                </div>

                {scenario.preparationTips.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-xs font-black uppercase tracking-wider text-muted-foreground">Mẹo chuẩn bị</p>
                    <ul className="space-y-1.5">
                      {scenario.preparationTips.map((t, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-zinc-700 dark:text-zinc-300">
                          <CheckCircle2 className="h-4 w-4 text-success mt-0.5 shrink-0" /> {t}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {scenario.closing && (
                  <p className="text-sm font-semibold text-center text-primary pt-2">{scenario.closing}</p>
                )}
              </section>
            )}
          </>
        )}
      </main>
    </div>
  );
}
