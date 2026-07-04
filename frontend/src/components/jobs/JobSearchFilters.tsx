"use client";

import React from "react";
import { SlidersHorizontal } from "lucide-react";

export interface FilterState {
  location: string;
  employmentType: string;
  experienceLevel: string;
  salaryMin: string;
  remote: boolean;
}

interface JobSearchFiltersProps {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
}

const EMPLOYMENT_TYPES = [
  { value: "", label: "Tất cả hình thức" },
  { value: "remote", label: "Remote" },
  { value: "hybrid", label: "Hybrid" },
  { value: "on-site", label: "On-site" },
  { value: "full-time", label: "Full-time" },
  { value: "part-time", label: "Part-time" },
];

const EXPERIENCE_LEVELS = [
  { value: "", label: "Mọi cấp độ" },
  { value: "entry", label: "Entry (0-2 năm)" },
  { value: "mid", label: "Mid (3-5 năm)" },
  { value: "senior", label: "Senior (6+ năm)" },
];

const inputClass =
  "w-full px-3 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 transition";

export const JobSearchFilters: React.FC<JobSearchFiltersProps> = ({ filters, onChange }) => {
  const update = (patch: Partial<FilterState>) => onChange({ ...filters, ...patch });

  return (
    <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm space-y-4">
      <h3 className="flex items-center gap-2 font-extrabold text-sm text-zinc-900 dark:text-white">
        <SlidersHorizontal className="h-4 w-4 text-primary" /> Bộ lọc
      </h3>

      <div className="space-y-1.5">
        <label className="text-xs font-semibold text-zinc-600 dark:text-zinc-400">Địa điểm</label>
        <input
          type="text"
          value={filters.location}
          onChange={(e) => update({ location: e.target.value })}
          placeholder="VD: Ho Chi Minh, Remote..."
          className={inputClass}
        />
      </div>

      <div className="space-y-1.5">
        <label className="text-xs font-semibold text-zinc-600 dark:text-zinc-400">Hình thức làm việc</label>
        <select
          value={filters.employmentType}
          onChange={(e) => update({ employmentType: e.target.value })}
          className={inputClass}
        >
          {EMPLOYMENT_TYPES.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
      </div>

      <div className="space-y-1.5">
        <label className="text-xs font-semibold text-zinc-600 dark:text-zinc-400">Cấp độ kinh nghiệm</label>
        <select
          value={filters.experienceLevel}
          onChange={(e) => update({ experienceLevel: e.target.value })}
          className={inputClass}
        >
          {EXPERIENCE_LEVELS.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
      </div>

      <div className="space-y-1.5">
        <label className="text-xs font-semibold text-zinc-600 dark:text-zinc-400">Mức lương tối thiểu (USD)</label>
        <input
          type="number"
          min={0}
          value={filters.salaryMin}
          onChange={(e) => update({ salaryMin: e.target.value })}
          placeholder="VD: 1000"
          className={inputClass}
        />
      </div>

      <label className="flex items-center gap-2.5 cursor-pointer pt-1">
        <input
          type="checkbox"
          checked={filters.remote}
          onChange={(e) => update({ remote: e.target.checked })}
          className="h-4 w-4 rounded accent-primary"
        />
        <span className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">Chỉ việc làm remote</span>
      </label>
    </div>
  );
};

export default JobSearchFilters;
