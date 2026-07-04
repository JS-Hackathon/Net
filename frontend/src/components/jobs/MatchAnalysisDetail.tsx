"use client";

import React from "react";
import { CheckCircle2, XCircle, AlertTriangle, Sparkles, Target, Lightbulb } from "lucide-react";
import { MatchDetail } from "@/lib/services/matches";
import { MatchScoreIndicator, scoreColor } from "./MatchScoreIndicator";

interface MatchAnalysisDetailProps {
  match: MatchDetail;
}

const ScoreBar: React.FC<{ label: string; score: number | null }> = ({ label, score }) => {
  const value = score ?? 0;
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs font-semibold">
        <span className="text-zinc-600 dark:text-zinc-400">{label}</span>
        <span style={{ color: scoreColor(value) }}>{Math.round(value)}</span>
      </div>
      <div className="h-2 rounded-full bg-zinc-100 dark:bg-zinc-800 overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${Math.max(0, Math.min(100, value))}%`, backgroundColor: scoreColor(value) }}
        />
      </div>
    </div>
  );
};

const matchTypeBadge = (type: string | null) => {
  const map: Record<string, { cls: string; label: string }> = {
    exact: { cls: "bg-success/15 text-success", label: "Khớp tốt" },
    partial: { cls: "bg-amber-500/15 text-amber-600", label: "Khớp một phần" },
    missing: { cls: "bg-red-500/15 text-red-600", label: "Còn thiếu" },
    bonus: { cls: "bg-primary/10 text-primary", label: "Điểm cộng" },
  };
  const m = map[type || ""] || { cls: "bg-zinc-100 text-zinc-600", label: type || "" };
  return <span className={`py-0.5 px-2 rounded-lg text-[10px] font-bold uppercase tracking-wide ${m.cls}`}>{m.label}</span>;
};

export const MatchAnalysisDetail: React.FC<MatchAnalysisDetailProps> = ({ match }) => {
  const rec = match.analysis.recommendation as {
    should_apply?: boolean;
    likelihood_of_success?: string;
    preparation_advice?: string;
  };

  return (
    <div className="space-y-6">
      {/* Score overview */}
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 shadow-sm flex flex-col sm:flex-row items-center gap-6">
        <MatchScoreIndicator score={match.overallScore} size="lg" />
        <div className="flex-1 w-full space-y-3">
          <ScoreBar label="Kỹ năng (40%)" score={match.skillsScore} />
          <ScoreBar label="Kinh nghiệm (35%)" score={match.experienceScore} />
          <ScoreBar label="Học vấn (15%)" score={match.educationScore} />
          <ScoreBar label="Địa điểm (10%)" score={match.locationScore} />
        </div>
      </div>

      {match.needsReview && (
        <div className="flex items-center gap-2 p-3 rounded-xl bg-amber-500/10 text-amber-700 dark:text-amber-400 text-sm font-semibold">
          <AlertTriangle className="h-4 w-4" />
          Độ tin cậy của phân tích ở mức thấp ({Math.round(match.confidenceScore || 0)}%), hãy cân nhắc thêm.
        </div>
      )}

      {match.analysis.summary && (
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm">
          <p className="text-sm leading-relaxed text-zinc-700 dark:text-zinc-300">{match.analysis.summary}</p>
        </div>
      )}

      {/* Strengths & missing skills */}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm space-y-3">
          <h4 className="flex items-center gap-2 font-extrabold text-sm text-zinc-900 dark:text-white">
            <CheckCircle2 className="h-4 w-4 text-success" /> Điểm mạnh
          </h4>
          <ul className="space-y-1.5 text-sm">
            {match.analysis.strengths.length === 0 && <li className="text-muted-foreground">Chưa có dữ liệu</li>}
            {match.analysis.strengths.map((s, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-success mt-0.5">•</span>
                <span className="text-zinc-700 dark:text-zinc-300">{String(s)}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm space-y-3">
          <h4 className="flex items-center gap-2 font-extrabold text-sm text-zinc-900 dark:text-white">
            <XCircle className="h-4 w-4 text-red-500" /> Kỹ năng còn thiếu
          </h4>
          <ul className="space-y-1.5 text-sm">
            {match.analysis.missingSkills.length === 0 && <li className="text-muted-foreground">Không có</li>}
            {match.analysis.missingSkills.map((s, i) => {
              const skill = typeof s === "string" ? s : s.skill;
              const importance = typeof s === "object" ? s.importance : null;
              return (
                <li key={i} className="flex items-start gap-2">
                  <span className="text-red-500 mt-0.5">•</span>
                  <span className="text-zinc-700 dark:text-zinc-300">
                    {skill}{importance ? <span className="text-muted-foreground text-xs"> ({importance})</span> : null}
                  </span>
                </li>
              );
            })}
          </ul>
        </div>
      </div>

      {/* Skills matrix */}
      {match.analysis.skillsMatches.length > 0 && (
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm space-y-3">
          <h4 className="flex items-center gap-2 font-extrabold text-sm text-zinc-900 dark:text-white">
            <Sparkles className="h-4 w-4 text-primary" /> Chi tiết kỹ năng
          </h4>
          <div className="flex flex-wrap gap-2">
            {match.analysis.skillsMatches.map((s, i) => (
              <span key={i} className="flex items-center gap-1.5 py-1 px-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 text-xs font-bold text-zinc-700 dark:text-zinc-300">
                {s.skillName} {matchTypeBadge(s.matchType)}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Areas for improvement */}
      {match.analysis.areasForImprovement.length > 0 && (
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm space-y-3">
          <h4 className="flex items-center gap-2 font-extrabold text-sm text-zinc-900 dark:text-white">
            <Target className="h-4 w-4 text-primary" /> Cần cải thiện
          </h4>
          <div className="space-y-2.5">
            {match.analysis.areasForImprovement.map((a, i) => {
              const area = typeof a === "string" ? a : a.area;
              const suggestion = typeof a === "object" ? a.suggestion : null;
              const priority = typeof a === "object" ? a.priority : null;
              return (
                <div key={i} className="border-l-2 border-primary/30 pl-3 text-sm">
                  <p className="font-bold text-zinc-800 dark:text-zinc-200">
                    {area}{priority ? <span className="text-xs text-muted-foreground font-medium"> · ưu tiên {priority}</span> : null}
                  </p>
                  {suggestion && <p className="text-xs text-muted-foreground mt-0.5">{suggestion}</p>}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Recommendation */}
      {rec && (rec.preparation_advice || rec.likelihood_of_success) && (
        <div className="bg-primary/5 border border-primary/20 rounded-2xl p-5 space-y-2">
          <h4 className="flex items-center gap-2 font-extrabold text-sm text-primary">
            <Lightbulb className="h-4 w-4" /> Khuyến nghị
          </h4>
          {rec.likelihood_of_success && (
            <p className="text-sm text-zinc-700 dark:text-zinc-300">
              Khả năng thành công: <strong className="uppercase">{rec.likelihood_of_success}</strong>
              {rec.should_apply != null && (
                <> · {rec.should_apply ? "Nên ứng tuyển ✅" : "Cân nhắc kỹ trước khi ứng tuyển"}</>
              )}
            </p>
          )}
          {rec.preparation_advice && (
            <p className="text-sm text-zinc-700 dark:text-zinc-300">{rec.preparation_advice}</p>
          )}
        </div>
      )}
    </div>
  );
};

export default MatchAnalysisDetail;
