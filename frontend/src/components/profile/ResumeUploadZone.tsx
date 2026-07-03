"use client";

import React, { useState, useRef, DragEvent, ChangeEvent } from "react";
import { Upload, FileText, AlertCircle } from "lucide-react";

interface ResumeUploadZoneProps {
  onFileSelect: (file: File) => void;
  isUploading: boolean;
  onFallbackManual?: () => void;
}

export const ResumeUploadZone: React.FC<ResumeUploadZoneProps> = ({
  onFileSelect,
  isUploading,
  onFallbackManual,
}) => {
  const [isDragActive, setIsDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateAndSelectFile = (file: File) => {
    setError(null);
    const maxFileSize = 5 * 1024 * 1024; // 5MB
    const allowedExtensions = [".pdf", ".docx"];
    const ext = "." + file.name.split(".").pop()?.toLowerCase();

    if (!allowedExtensions.includes(ext)) {
      setError("Chỉ hỗ trợ file định dạng .pdf hoặc .docx");
      return;
    }

    if (file.size > maxFileSize) {
      setError("Kích thước file vượt quá giới hạn cho phép (tối đa 5MB)");
      return;
    }

    onFileSelect(file);
  };

  const handleDrag = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSelectFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      validateAndSelectFile(e.target.files[0]);
    }
  };

  const onButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="space-y-4">
      <div
        onDragEnter={handleDrag}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
        onClick={onButtonClick}
        className={`relative w-full min-h-[220px] rounded-2xl border-2 border-dashed flex flex-col items-center justify-center p-6 text-center cursor-pointer transition-all duration-300 ${
          isDragActive
            ? "border-primary bg-primary/5 scale-[0.99] shadow-inner"
            : "border-zinc-200 dark:border-zinc-800 hover:border-primary/50 hover:bg-zinc-50 dark:hover:bg-zinc-900/30"
        } ${isUploading ? "pointer-events-none opacity-60" : ""}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept=".pdf,.docx"
          onChange={handleChange}
          disabled={isUploading}
        />

        <div className="h-12 w-12 rounded-2xl bg-primary/10 text-primary flex items-center justify-center mb-4 transition group-hover:scale-110">
          <Upload className="h-6 w-6" />
        </div>

        <h3 className="font-bold text-base md:text-lg mb-1.5 text-zinc-900 dark:text-white">
          Kéo thả CV của bạn vào đây hoặc click để duyệt
        </h3>
        <p className="text-xs text-muted-foreground max-w-sm mb-4 leading-normal">
          Hỗ trợ định dạng PDF và DOCX (Kích thước tối đa 5MB)
        </p>

        <div className="flex gap-4 text-xs font-semibold text-zinc-500 bg-zinc-100 dark:bg-zinc-800/80 px-4 py-2 rounded-xl">
          <span className="flex items-center gap-1">
            <FileText className="h-3.5 w-3.5 text-red-500" /> PDF
          </span>
          <span className="flex items-center gap-1">
            <FileText className="h-3.5 w-3.5 text-blue-500" /> DOCX
          </span>
        </div>
      </div>

      {error && (
        <div className="flex items-start gap-2.5 p-4 rounded-xl border border-red-200 bg-red-50 dark:bg-red-950/20 dark:border-red-900/50 text-red-600 dark:text-red-400 text-sm animate-shake">
          <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
          <div className="space-y-0.5">
            <span className="font-bold block">Tải file không thành công</span>
            <span className="text-xs leading-normal opacity-90">{error}</span>
          </div>
        </div>
      )}
      {onFallbackManual && (
        <div className="text-center pt-2">
          <p className="text-xs text-zinc-500 dark:text-zinc-400">
            Gặp sự cố khi upload?{" "}
            <button
              type="button"
              onClick={onFallbackManual}
              className="font-bold text-primary hover:underline transition cursor-pointer"
            >
              Nhập thông tin thủ công &rarr;
            </button>
          </p>
        </div>
      )}
    </div>
  );
};
