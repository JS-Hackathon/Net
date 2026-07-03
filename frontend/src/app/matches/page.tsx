"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { toast } from "sonner";
import { Loader2, Sparkles, Building2, MapPin, AlertTriangle, ChevronRight } from "lucide-react";
import { useAuthStore } from "@/lib/store/authStore";
import { matchService, MatchListItem } from "@/lib/services/matches";
import { AppHeader } from "@/components/layout/AppHeader";
import { MatchScoreIndicator } from "@/components/jobs/MatchScoreIndicator";

export default function MatchesPage() {
  const router = useRouter();
  const { user, checkAuth, isInitialized } = useAuthStore();

  const [matches, setMatches] = useState<MatchListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [minScore, setMinScore] = useState<number>(0);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (isInitialized && !user) router.push("/login");
  }, [isInitialized, user, router]);

  const load = async (min: number) => {
    setLoading(true);
    try {
      const result = await matchService.listMatches({ minScore: min > 0 ? min : undefined, sort: "score" });
      setMatches(result.matches);
    } catch {
      toast.error("Không tải được danh sách kết quả so khớp");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    if (user) load(minScore);
  }, [user, minScore]);

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

      <main className="max-w-4xl mx-auto px-6 mt-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <h1 className="text-2xl font-extrabold tracking-tight flex items-center gap-2">
            <Sparkles className="h-6 w-6 text-primary" /> Kết quả so khớp
          </h1>
          <div className="flex items-center gap-2">
            <label className="text-xs font-semibold text-muted-foreground">Điểm tối thiểu</label>
            <select
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              className="px-3 py-2 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-sm font-semibold"
            >
              <option value={0}>Tất cả</option>
              <option value={60}>≥ 60</option>
              <option value={80}>≥ 80</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-28 rounded-2xl bg-zinc-100 dark:bg-zinc-900 animate-pulse" />
            ))}
          </div>
        ) : matches.length === 0 ? (
          <div className="text-center py-20 text-muted-foreground">
            <Sparkles className="h-12 w-12 mx-auto mb-3 opacity-30" />
            <p className="font-semibold">Chưa có kết quả so khớp nào</p>
            <p className="text-sm mt-1">
              Vào <Link href="/jobs" className="text-primary font-bold hover:underline">Tìm việc</Link> và bấm &quot;Match với CV của tôi&quot; ở một tin tuyển dụng.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {matches.map((m) => (
              <Link
                key={m.matchId}
                href={`/matches/${m.matchId}`}
                className="flex items-center gap-4 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm hover:shadow-md hover:border-primary/30 transition"
              >
                <MatchScoreIndicator score={m.overallScore} size="sm" showLabel={false} />
                <div className="flex-1 min-w-0 space-y-1">
                  <h3 className="font-extrabold text-base text-zinc-900 dark:text-white truncate">{m.job.title}</h3>
                  <p className="flex items-center gap-3 text-xs font-semibold text-muted-foreground">
                    <span className="flex items-center gap-1"><Building2 className="h-3.5 w-3.5" /> {m.job.company}</span>
                    {m.job.location && <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {m.job.location}</span>}
                  </p>
                  {m.matchSummary && <p className="text-xs text-muted-foreground line-clamp-1">{m.matchSummary}</p>}
                  {m.needsReview && (
                    <span className="inline-flex items-center gap-1 text-[11px] font-bold text-amber-600">
                      <AlertTriangle className="h-3 w-3" /> Độ tin cậy thấp
                    </span>
                  )}
                </div>
                <ChevronRight className="h-5 w-5 text-zinc-300 shrink-0" />
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
