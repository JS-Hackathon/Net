"use client";

import React from "react";
import Link from "next/link";
import { Briefcase, MapPin, DollarSign, ArrowRight } from "lucide-react";
import { Job } from "@/lib/services/job";

interface JobCardProps {
  job: Job;
}

export const JobCard: React.FC<JobCardProps> = ({ job }) => {
  return (
    <div className="bg-white p-5 rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all flex flex-col justify-between h-full">
      <div>
        <div className="flex items-start justify-between gap-2 mb-3">
          <div>
            <h3 className="font-semibold text-gray-900 text-base leading-snug line-clamp-1">{job.job_title}</h3>
            <p className="text-sm text-gray-500 font-medium">{job.employer_name}</p>
          </div>
        </div>

        <p className="text-sm text-gray-600 line-clamp-3 mb-4">{job.job_description}</p>

        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-gray-500 mb-5">
          <div className="flex items-center gap-1">
            <MapPin size={14} className="text-gray-400" />
            <span>{job.job_city || "Từ xa"}, {job.job_country}</span>
          </div>
          <div className="flex items-center gap-1">
            <DollarSign size={14} className="text-gray-400" />
            <span>
              {job.job_max_salary 
                ? `${job.job_max_salary.toLocaleString()} ${job.job_salary_currency || "USD"}`
                : "Thỏa thuận"}
            </span>
          </div>
        </div>
      </div>

      <div className="pt-3 border-t border-gray-50 flex items-center justify-end">
        <Link
          href={`/jobs/${job.job_id}`}
          className="inline-flex items-center gap-1 text-sm font-semibold text-blue-600 hover:text-blue-700 hover:underline"
        >
          <span>Xem chi tiết & So khớp</span>
          <ArrowRight size={14} />
        </Link>
      </div>
    </div>
  );
};
