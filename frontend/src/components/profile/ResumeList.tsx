"use client";

import React from "react";
import { 
  FileText, 
  Trash2, 
  Download, 
  Star, 
  Play, 
  AlertTriangle,
  Clock,
  CheckCircle2 
} from "lucide-react";
import { Resume } from "@/lib/services/resume";

interface ResumeListProps {
  resumes: Resume[];
  onDelete: (id: string) => void;
  onSetPrimary: (id: string) => void;
  onDownload: (id: string) => void;
  onParse: (id: string) => void;
}

export const ResumeList: React.FC<ResumeListProps> = ({
  resumes,
  onDelete,
  onSetPrimary,
  onDownload,
  onParse,
}) => {
  const formatSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    return (bytes / k / k).toFixed(2) + " MB";
  };

  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr);
      return d.toLocaleDateString("vi-VN", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    } catch {
      return dateStr;
    }
  };

  if (resumes.length === 0) {
    return (
      <div className="text-center py-12 border border-zinc-200 dark:border-zinc-800 rounded-2xl bg-white dark:bg-zinc-900 shadow-sm">
        <FileText className="h-12 w-12 text-zinc-300 dark:text-zinc-700 mx-auto mb-4" />
        <h3 className="font-bold text-lg text-zinc-900 dark:text-white mb-1.5">
          Chưa có CV nào được tải lên
        </h3>
        <p className="text-sm text-muted-foreground max-w-sm mx-auto leading-normal">
          Hãy tải CV đầu tiên lên hệ thống để bắt đầu quá trình phân tích năng lực và chuẩn bị phỏng vấn với AI.
        </p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {resumes.map((resume) => {
        const isPdf = resume.fileType.toLowerCase() === "pdf";

        return (
          <div
            key={resume.id}
            className={`border rounded-2xl p-5 bg-white dark:bg-zinc-900 shadow-sm flex flex-col justify-between gap-4 transition duration-200 ${
              resume.isPrimary
                ? "border-primary/45 ring-1 ring-primary/20 bg-primary/[0.01] dark:bg-primary/[0.005]"
                : "border-zinc-200 dark:border-zinc-800 hover:border-zinc-300 dark:hover:border-zinc-700"
            }`}
          >
            {/* Header info */}
            <div className="flex items-start justify-between gap-3 min-w-0">
              <div className="flex items-start gap-3.5 min-w-0">
                {/* File Icon */}
                <div
                  className={`h-11 w-11 rounded-xl flex items-center justify-center shrink-0 shadow-sm ${
                    isPdf
                      ? "bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400"
                      : "bg-blue-50 dark:bg-blue-950/20 text-blue-600 dark:text-blue-400"
                  }`}
                >
                  <FileText className="h-6 w-6" />
                </div>

                <div className="min-w-0">
                  <span className="font-extrabold text-sm md:text-base text-zinc-900 dark:text-white truncate block">
                    {resume.originalFilename}
                  </span>
                  
                  {/* Metadata */}
                  <div className="flex flex-wrap items-center gap-x-2.5 gap-y-1 mt-1 text-xs text-muted-foreground font-medium">
                    <span>{formatSize(resume.fileSize)}</span>
                    <span className="h-1 w-1 rounded-full bg-zinc-300 dark:bg-zinc-700" />
                    <span>{formatDate(resume.createdAt)}</span>
                  </div>
                </div>
              </div>

              {resume.isPrimary && (
                <span className="inline-flex items-center gap-1 py-1 px-2.5 rounded-full bg-primary/10 text-primary text-[10px] font-bold uppercase tracking-wider shrink-0">
                  <Star className="h-3 w-3 fill-primary text-primary" />
                  CV Chính
                </span>
              )}
            </div>

            {/* Status indication */}
            <div className="border-t border-zinc-100 dark:border-zinc-800/80 pt-4 flex flex-wrap items-center justify-between gap-3">
              {/* Parse status details */}
              <div className="flex items-center gap-2">
                {resume.uploadStatus === "processing" ? (
                  <span className="flex items-center gap-1.5 text-xs font-bold text-amber-500 bg-amber-50 dark:bg-amber-950/20 px-2.5 py-1 rounded-full">
                    <Clock className="h-3.5 w-3.5 animate-spin" />
                    Đang xử lý...
                  </span>
                ) : resume.uploadStatus === "failed" ? (
                  <span className="flex items-center gap-1.5 text-xs font-bold text-red-500 bg-red-50 dark:bg-red-950/20 px-2.5 py-1 rounded-full">
                    <AlertTriangle className="h-3.5 w-3.5" />
                    Phân tích lỗi
                  </span>
                ) : (
                  <span className="flex items-center gap-1.5 text-xs font-bold text-success bg-success/10 px-2.5 py-1 rounded-full">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    Đã phân tích
                  </span>
                )}
              </div>

              {/* Action buttons */}
              <div className="flex items-center gap-1.5 ml-auto">
                {/* Parse action if failed or pending */}
                {(resume.uploadStatus === "failed" || !resume.textExtractionStatus) && (
                  <button
                    onClick={() => onParse(resume.id)}
                    title="Chạy lại phân tích AI"
                    className="h-8 w-8 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 hover:bg-zinc-50 dark:hover:bg-zinc-900 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white flex items-center justify-center transition"
                  >
                    <Play className="h-3.5 w-3.5" />
                  </button>
                )}

                {/* Set Primary */}
                {!resume.isPrimary && (
                  <button
                    onClick={() => onSetPrimary(resume.id)}
                    title="Đặt làm CV chính"
                    className="h-8 w-8 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 hover:bg-zinc-50 dark:hover:bg-zinc-900 text-zinc-400 hover:text-amber-500 hover:border-amber-200 dark:hover:border-amber-950 flex items-center justify-center transition"
                  >
                    <Star className="h-3.5 w-3.5" />
                  </button>
                )}

                {/* Download */}
                <button
                  onClick={() => onDownload(resume.id)}
                  title="Tải xuống CV gốc"
                  className="h-8 w-8 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 hover:bg-zinc-50 dark:hover:bg-zinc-900 text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-white flex items-center justify-center transition"
                >
                  <Download className="h-3.5 w-3.5" />
                </button>

                {/* Delete */}
                <button
                  onClick={() => {
                    if (confirm("Bạn có chắc chắn muốn xóa CV này? Hành động này không thể hoàn tác.")) {
                      onDelete(resume.id);
                    }
                  }}
                  title="Xóa CV"
                  className="h-8 w-8 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 hover:bg-red-50 dark:hover:bg-red-950/20 text-zinc-400 hover:text-red-500 hover:border-red-200 dark:hover:border-red-950 flex items-center justify-center transition"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
