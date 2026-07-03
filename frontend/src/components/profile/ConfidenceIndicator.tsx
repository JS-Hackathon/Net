"use client";

import React from "react";
import { CheckCircle2, AlertTriangle, AlertCircle } from "lucide-react";

interface ConfidenceIndicatorProps {
  score: number;
}

export const ConfidenceIndicator: React.FC<ConfidenceIndicatorProps> = ({ score }) => {
  const getScoreDetails = (s: number) => {
    if (s >= 85) {
      return {
        color: "text-emerald-600 bg-emerald-50 dark:bg-emerald-950/20 dark:text-emerald-400 border-emerald-200 dark:border-emerald-900/50",
        label: "Độ chính xác cao",
        icon: <CheckCircle2 className="h-4 w-4" />,
        desc: "Dữ liệu được trích xuất rất đầy đủ và khớp cao với định dạng chuẩn."
      };
    }
    if (s >= 70) {
      return {
        color: "text-amber-600 bg-amber-50 dark:bg-amber-950/20 dark:text-amber-400 border-amber-200 dark:border-amber-900/50",
        label: "Độ chính xác trung bình",
        icon: <AlertTriangle className="h-4 w-4" />,
        desc: "Một số trường dữ liệu có thể không đầy đủ hoặc cần kiểm tra lại định dạng."
      };
    }
    return {
      color: "text-red-600 bg-red-50 dark:bg-red-950/20 dark:text-red-400 border-red-200 dark:border-red-900/50",
      label: "Độ chính xác thấp",
      icon: <AlertCircle className="h-4 w-4" />,
      desc: "Có nhiều thông tin bị thiếu hoặc không đồng nhất. Nên xem kỹ lại và chỉnh sửa thủ công."
    };
  };

  const { color, label, icon, desc } = getScoreDetails(score);

  return (
    <div className={`flex items-start gap-3 p-3.5 border rounded-xl ${color}`}>
      <div className="shrink-0 mt-0.5">{icon}</div>
      <div className="space-y-1">
        <div className="flex items-center gap-1.5">
          <span className="font-extrabold text-sm">{label}</span>
          <span className="h-1.5 w-1.5 rounded-full bg-current opacity-40" />
          <span className="font-extrabold text-sm">{score}%</span>
        </div>
        <p className="text-xs leading-normal opacity-90">{desc}</p>
      </div>
    </div>
  );
};
