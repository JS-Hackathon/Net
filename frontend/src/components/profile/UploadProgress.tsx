"use client";

import React from "react";
import { Loader2, X, FileText } from "lucide-react";

interface UploadProgressProps {
  progress: number;
  fileName: string;
  fileSize: number; // bytes
  onCancel?: () => void;
}

export const UploadProgress: React.FC<UploadProgressProps> = ({
  progress,
  fileName,
  fileSize,
  onCancel,
}) => {
  const formatSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const dm = 2;
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
  };

  return (
    <div className="p-4 rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 shadow-sm space-y-3">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="h-10 w-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center shrink-0">
            <FileText className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <span className="font-bold text-sm text-zinc-900 dark:text-white truncate block">
              {fileName}
            </span>
            <span className="text-xs text-muted-foreground block">
              {formatSize(fileSize)}
            </span>
          </div>
        </div>

        {onCancel && (
          <button
            onClick={onCancel}
            className="h-8 w-8 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 flex items-center justify-center text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      <div className="space-y-1">
        <div className="flex justify-between items-center text-xs font-semibold">
          <span className="text-muted-foreground flex items-center gap-1.5">
            <Loader2 className="h-3 w-3 text-primary animate-spin" />
            Đang tải lên hệ thống...
          </span>
          <span className="text-primary">{progress}%</span>
        </div>
        <div className="w-full h-2 bg-zinc-100 dark:bg-zinc-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-primary to-primary/80 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>
    </div>
  );
};
