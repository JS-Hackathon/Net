"use client";

import React from "react";
import { 
  Sparkles, 
  CheckCircle2, 
  ArrowRight,
  TrendingUp 
} from "lucide-react";
import { ProfileCompleteness as CompletenessType } from "@/lib/services/profile";

interface ProfileCompletenessProps {
  completeness: CompletenessType;
  onSuggestionClick?: (section: string) => void;
}

export const ProfileCompleteness: React.FC<ProfileCompletenessProps> = ({
  completeness,
  onSuggestionClick,
}) => {
  const { overallScore, sectionScores, suggestions } = completeness;

  const getStrengthDetails = (score: number) => {
    if (score >= 90) {
      return {
        label: "Xuất sắc",
        color: "bg-emerald-500 text-white dark:bg-emerald-600",
        bgLight: "bg-emerald-50 dark:bg-emerald-950/10 border-emerald-100 dark:border-emerald-900/35",
        barColor: "bg-emerald-500",
        textColor: "text-emerald-700 dark:text-emerald-400",
        message: "Hồ sơ của bạn đã sẵn sàng! Nhà tuyển dụng rất thích các hồ sơ chi tiết thế này."
      };
    }
    if (score >= 70) {
      return {
        label: "Tốt",
        color: "bg-blue-500 text-white dark:bg-blue-600",
        bgLight: "bg-blue-50 dark:bg-blue-950/10 border-blue-100 dark:border-blue-900/35",
        barColor: "bg-blue-500",
        textColor: "text-blue-700 dark:text-blue-400",
        message: "Hồ sơ ở mức Tốt. Hãy thêm một vài chi tiết nhỏ để trở nên nổi bật hơn."
      };
    }
    if (score >= 40) {
      return {
        label: "Khá",
        color: "bg-amber-500 text-white dark:bg-amber-600",
        bgLight: "bg-amber-50 dark:bg-amber-950/10 border-amber-100 dark:border-amber-900/35",
        barColor: "bg-amber-500",
        textColor: "text-amber-700 dark:text-amber-400",
        message: "Hồ sơ ở mức cơ bản. Bổ sung các kỹ năng và kinh nghiệm để thu hút nhà tuyển dụng."
      };
    }
    return {
      label: "Yếu",
      color: "bg-red-500 text-white dark:bg-red-600",
      bgLight: "bg-red-50 dark:bg-red-950/10 border-red-100 dark:border-red-900/35",
      barColor: "bg-red-500",
      textColor: "text-red-700 dark:text-red-400",
      message: "Hồ sơ của bạn quá sơ sài. Vui lòng tải CV lên hoặc bổ sung thông tin cá nhân."
    };
  };

  const strength = getStrengthDetails(overallScore);

  return (
    <div className="space-y-6">
      {/* Overview Block */}
      <div className={`p-6 border rounded-2xl ${strength.bgLight} transition-all duration-300`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <h3 className="font-extrabold text-lg text-zinc-900 dark:text-white">
                Độ hoàn thiện hồ sơ
              </h3>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-black uppercase tracking-wider ${strength.color}`}>
                {strength.label}
              </span>
            </div>
            <p className="text-sm text-muted-foreground leading-normal max-w-md">
              {strength.message}
            </p>
          </div>

          {/* Radial score simulation or large percentage */}
          <div className="flex items-center gap-4 shrink-0">
            <div className="relative h-20 w-20 flex items-center justify-center rounded-full bg-white dark:bg-zinc-900 shadow-sm border border-zinc-100 dark:border-zinc-800">
              <span className="font-black text-2xl text-zinc-900 dark:text-white">
                {Math.round(overallScore)}%
              </span>
            </div>
          </div>
        </div>

        {/* Global Progress Bar */}
        <div className="mt-6 space-y-1">
          <div className="w-full h-3 bg-zinc-200 dark:bg-zinc-800 rounded-full overflow-hidden">
            <div 
              className={`h-full ${strength.barColor} rounded-full transition-all duration-500`}
              style={{ width: `${overallScore}%` }}
            />
          </div>
        </div>
      </div>

      {/* Breakdown and suggestions */}
      <div className="grid gap-6 md:grid-cols-5">
        {/* Section Scores */}
        <div className="md:col-span-2 space-y-4">
          <h4 className="font-bold text-sm text-zinc-900 dark:text-white uppercase tracking-wider flex items-center gap-1.5">
            <TrendingUp className="h-4 w-4 text-primary" /> Chi tiết phân đoạn
          </h4>
          <div className="p-5 border border-zinc-200 dark:border-zinc-800 rounded-2xl bg-white dark:bg-zinc-900 shadow-sm space-y-4">
            {Object.entries(sectionScores).map(([section, score]) => {
              const label = section === "personal_info" ? "Thông tin cá nhân" :
                            section === "work_experience" ? "Kinh nghiệm làm việc" :
                            section === "education" ? "Học vấn" :
                            section === "skills" ? "Kỹ năng chuyên môn" : "Mục khác";

              return (
                <div key={section} className="space-y-1.5">
                  <div className="flex justify-between items-center text-xs font-semibold">
                    <span className="text-zinc-700 dark:text-zinc-300">{label}</span>
                    <span className="text-zinc-900 dark:text-white">{Math.round(score)}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-zinc-100 dark:bg-zinc-800 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary rounded-full transition-all"
                      style={{ width: `${score * (100 / (section === "personal_info" ? 25 : section === "work_experience" ? 35 : section === "education" ? 15 : section === "skills" ? 20 : 5))}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Suggestions / Optimization Action Plan */}
        <div className="md:col-span-3 space-y-4">
          <h4 className="font-bold text-sm text-zinc-900 dark:text-white uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="h-4 w-4 text-amber-500" /> Gợi ý tối ưu hồ sơ
          </h4>
          <div className="space-y-2.5">
            {suggestions.length === 0 ? (
              <div className="p-6 text-center border border-zinc-100 dark:border-zinc-900 rounded-2xl bg-zinc-50/50 dark:bg-zinc-900/20">
                <CheckCircle2 className="h-8 w-8 text-emerald-500 mx-auto mb-2" />
                <p className="text-sm font-bold text-zinc-900 dark:text-white">Tuyệt vời! Không còn gợi ý nào.</p>
                <p className="text-xs text-muted-foreground mt-0.5">Hồ sơ của bạn đã được tối ưu hoàn thiện 100%.</p>
              </div>
            ) : (
              suggestions.map((suggestion, idx) => (
                <div 
                  key={idx}
                  onClick={() => onSuggestionClick?.(suggestion.section)}
                  className={`p-4 border rounded-xl flex items-start justify-between gap-3 bg-white dark:bg-zinc-900 shadow-xs transition duration-200 cursor-pointer ${
                    suggestion.priority === "high"
                      ? "border-red-100 dark:border-red-950/30 hover:border-red-200 dark:hover:border-red-900/50 hover:bg-red-50/30 dark:hover:bg-red-950/5"
                      : "border-zinc-200 dark:border-zinc-800 hover:border-primary/30 hover:bg-zinc-50/50"
                  }`}
                >
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className={`h-1.5 w-1.5 rounded-full shrink-0 ${suggestion.priority === "high" ? "bg-red-500" : "bg-amber-500"}`} />
                      <span className="text-xs font-black uppercase text-muted-foreground tracking-wider">
                        {suggestion.section === "personal_info" ? "Cá nhân" :
                         suggestion.section === "work_experience" ? "Kinh nghiệm" :
                         suggestion.section === "education" ? "Học vấn" :
                         suggestion.section === "skills" ? "Kỹ năng" : "Khác"}
                      </span>
                    </div>
                    <p className="text-sm font-bold text-zinc-800 dark:text-zinc-200 leading-normal">
                      {suggestion.message}
                    </p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-zinc-400 group-hover:text-primary transition shrink-0 mt-1" />
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
