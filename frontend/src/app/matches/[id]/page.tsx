"use client";

import React, { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { toast } from "sonner";
import { Loader2, ArrowLeft, Building2, MapPin, Star } from "lucide-react";
import { useAuthStore } from "@/lib/store/authStore";
import { matchService, MatchDetail } from "@/lib/services/matches";
import { AppHeader } from "@/components/layout/AppHeader";
import { MatchAnalysisDetail } from "@/components/jobs/MatchAnalysisDetail";

export default function MatchDetailPage() {
  const router = useRouter();
  const params = useParams();
  const matchId = params.id as string;
  const { user, checkAuth, isInitialized } = useAuthStore();

  const [match, setMatch] = useState<MatchDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [rating, setRating] = useState(0);
  const [submitting, setSubmitting] = useState(false);

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
        setMatch(await matchService.getMatchDetail(matchId));
      } catch {
        toast.error("Không tải được kết quả so khớp");
      } finally {
        setLoading(false);
      }
    })();
  }, [user, matchId]);

  const submitRating = async (value: number) => {
    setRating(value);
    setSubmitting(true);
    try {
      await matchService.submitFeedback(matchId, { userRating: value });
      toast.success("Cảm ơn phản hồi của bạn!");
    } catch {
      toast.error("Gửi phản hồi thất bại");
    } finally {
      setSubmitting(false);
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
  if (!match) {
    return (
      <div className="min-h-screen bg-zinc-50 dark:bg-black">
        <AppHeader />
        <div className="max-w-3xl mx-auto px-6 mt-16 text-center text-muted-foreground">
          <p className="font-semibold">Không tìm thấy kết quả so khớp.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black font-sans text-foreground pb-16">
      <AppHeader />

      <main className="max-w-4xl mx-auto px-6 mt-6 space-y-6">
        <button
          onClick={() => router.push("/matches")}
          className="flex items-center gap-1.5 text-sm font-bold text-muted-foreground hover:text-primary transition"
        >
          <ArrowLeft className="h-4 w-4" /> Danh sách kết quả
        </button>

        {/* Job header */}
        {match.job && (
          <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm flex items-center justify-between gap-4">
            <div className="min-w-0">
              <Link href={`/jobs/${match.job.id}`} className="font-extrabold text-lg text-zinc-900 dark:text-white hover:text-primary transition truncate block">
                {match.job.title}
              </Link>
              <p className="flex items-center gap-3 text-xs font-semibold text-muted-foreground mt-0.5">
                <span className="flex items-center gap-1"><Building2 className="h-3.5 w-3.5" /> {match.job.company}</span>
                {match.job.location && <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {match.job.location}</span>}
              </p>
            </div>
          </div>
        )}

        <MatchAnalysisDetail match={match} />

        {/* Feedback */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm space-y-3">
          <h4 className="font-extrabold text-sm text-zinc-900 dark:text-white">Kết quả này có hữu ích không?</h4>
          <div className="flex items-center gap-1.5">
            {[1, 2, 3, 4, 5].map((v) => (
              <button
                key={v}
                onClick={() => submitRating(v)}
                disabled={submitting}
                aria-label={`Đánh giá ${v} sao`}
                className="disabled:opacity-50 transition hover:scale-110"
              >
                <Star className={`h-6 w-6 ${v <= rating ? "fill-amber-400 text-amber-400" : "text-zinc-300 dark:text-zinc-700"}`} />
              </button>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
