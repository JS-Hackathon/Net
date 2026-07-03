"use client";

import React from "react";
import Link from "next/link";
import { Bookmark, BookmarkCheck, MapPin, Building2, Wallet, Clock } from "lucide-react";
import { JobSummary } from "@/lib/services/jobs";

interface JobCardProps {
  job: JobSummary;
  onBookmarkToggle: (job: JobSummary) => void;
}

const relativeDate = (iso: string | null): string => {
  if (!iso) return "";
  const diff = Date.now() - new Date(iso).getTime();
  const days = Math.floor(diff / 86400000);
  if (days <= 0) return "Hôm nay";
  if (days === 1) return "Hôm qua";
  if (days < 30) return `${days} ngày trước`;
  return `${Math.floor(days / 30)} tháng trước`;
};

export const JobCard: React.FC<JobCardProps> = ({ job, onBookmarkToggle }) => {
  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm hover:shadow-md hover:border-primary/30 transition duration-200 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-3">
        <Link href={`/jobs/${job.id}`} className="flex-1 min-w-0 group">
          <h3 className="font-extrabold text-base text-zinc-900 dark:text-white truncate group-hover:text-primary transition">
            {job.title}
          </h3>
          <p className="flex items-center gap-1.5 text-sm font-semibold text-muted-foreground mt-0.5">
            <Building2 className="h-3.5 w-3.5 shrink-0" /> {job.company}
          </p>
        </Link>
        <button
          onClick={() => onBookmarkToggle(job)}
          aria-label={job.isBookmarked ? "Bỏ lưu" : "Lưu việc làm"}
          className="shrink-0 h-9 w-9 rounded-xl border border-zinc-200 dark:border-zinc-800 flex items-center justify-center hover:bg-zinc-50 dark:hover:bg-zinc-800 transition"
        >
          {job.isBookmarked ? (
            <BookmarkCheck className="h-4.5 w-4.5 text-primary" />
          ) : (
            <Bookmark className="h-4.5 w-4.5 text-zinc-400" />
          )}
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs font-medium text-muted-foreground">
        {job.location && (
          <span className="flex items-center gap-1"><MapPin className="h-3.5 w-3.5" /> {job.location}</span>
        )}
        {job.salaryRange && (
          <span className="flex items-center gap-1 text-success font-bold"><Wallet className="h-3.5 w-3.5" /> {job.salaryRange}</span>
        )}
        {job.employmentType && (
          <span className="py-0.5 px-2 rounded-full bg-primary/10 text-primary font-bold uppercase tracking-wide text-[10px]">
            {job.employmentType}
          </span>
        )}
        {job.postedDate && (
          <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" /> {relativeDate(job.postedDate)}</span>
        )}
      </div>

      {job.skillsRequired.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {job.skillsRequired.slice(0, 6).map((s, i) => (
            <span key={i} className="py-0.5 px-2 rounded-lg bg-zinc-100 dark:bg-zinc-800 text-[11px] font-bold text-zinc-700 dark:text-zinc-300">
              {s}
            </span>
          ))}
          {job.skillsRequired.length > 6 && (
            <span className="py-0.5 px-2 text-[11px] font-bold text-muted-foreground">
              +{job.skillsRequired.length - 6}
            </span>
          )}
        </div>
      )}

      <div className="flex items-center gap-2 pt-1">
        <Link
          href={`/jobs/${job.id}`}
          className="flex-1 text-center py-2 px-3 rounded-xl bg-zinc-950 dark:bg-white text-white dark:text-zinc-950 text-xs font-bold hover:opacity-90 transition"
        >
          Xem chi tiết
        </Link>
      </div>
    </div>
  );
};

export default JobCard;
