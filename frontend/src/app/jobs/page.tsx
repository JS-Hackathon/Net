"use client";

import React, { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { jobService, Job } from "@/lib/services/job";
import { JobFilters } from "@/components/jobs/JobFilters";
import { JobCard } from "@/components/jobs/JobCard";
import { Briefcase, Loader2 } from "lucide-react";

export default function JobsPage() {
  const [filter, setFilter] = useState({ query: "Python Developer" });

  const { data: jobs, isLoading, error, refetch } = useQuery<Job[]>({
    queryKey: ["jobs", filter.query],
    queryFn: () => jobService.searchJobs(filter.query, 1),
    placeholderData: (prev) => prev,
  });

  const handleFilterChange = (newFilters: { query: string }) => {
    setFilter(newFilters);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className="bg-blue-600 p-2.5 rounded-xl text-white">
          <Briefcase size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Khám phá Cơ hội Việc làm</h1>
          <p className="text-sm text-gray-500 font-medium">Tìm kiếm công việc tuyển dụng và đánh giá độ phù hợp tức thì với CV của bạn</p>
        </div>
      </div>

      {/* Filter panel */}
      <div className="mb-8">
        <JobFilters onFilterChange={handleFilterChange} />
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <Loader2 className="animate-spin text-blue-600 w-10 h-10 mb-4" />
          <p className="text-gray-500 text-sm font-medium">Đang tải danh sách công việc phù hợp...</p>
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-100 p-4 rounded-xl text-center">
          <p className="text-red-700 text-sm font-semibold">Lỗi tải dữ liệu: {(error as Error).message}</p>
        </div>
      ) : jobs && jobs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {jobs.map((job) => (
            <JobCard key={job.job_id} job={job} />
          ))}
        </div>
      ) : (
        <div className="text-center py-20 bg-gray-50 border border-dashed border-gray-200 rounded-xl">
          <p className="text-gray-500 text-sm font-medium">Không tìm thấy cơ hội công việc nào phù hợp với từ khóa của bạn.</p>
        </div>
      )}
    </div>
  );
}
