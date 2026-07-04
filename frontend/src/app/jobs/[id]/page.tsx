"use client";

import React, { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { jobService } from "@/lib/services/job";
import { profileService } from "@/lib/services/profile";
import { matchingService, CompareResponse } from "@/lib/services/matching";
import { MatchScoreDial } from "@/components/jobs/MatchScoreDial";
import { RequirementMatrixView } from "@/components/jobs/RequirementMatrixView";
import { toast } from "sonner";
import { MapPin, DollarSign, Briefcase, FileSearch, Sparkles, Loader2, ArrowLeft } from "lucide-react";

export default function JobDetailPage() {
  const { id } = useParams() as { id: string };
  const router = useRouter();
  const [matchResult, setMatchResult] = useState<CompareResponse | null>(null);
  const [statusMessage, setStatusMessage] = useState("");

  // Fetch job details
  const { data: job, isLoading: isJobLoading, error: jobError } = useQuery({
    queryKey: ["job", id],
    queryFn: () => jobService.getJobDetail(id),
  });

  // Fetch candidate profile (to get profile ID)
  const { data: profile, isLoading: isProfileLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: () => profileService.getProfile(),
  });

  // API Call to extract requirements from JD & compare with profile
  const matchMutation = useMutation({
    mutationFn: async () => {
      if (!job || !profile) {
        throw new Error("Không đủ thông tin công việc hoặc hồ sơ để so khớp.");
      }

      setStatusMessage("Đang dùng AI trích xuất yêu cầu tuyển dụng...");
      
      // Step 1: Call API to extract requirements from job description
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/jobs/extract-requirements`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${localStorage.getItem("access_token")}`
        },
        body: JSON.stringify({ job_description: job.job_description })
      });

      if (!response.ok) {
        throw new Error("Lỗi trích xuất yêu cầu công việc từ JD.");
      }
      
      const requirements = await response.json();

      setStatusMessage("Đang đối chiếu yêu cầu với hồ sơ CV của bạn...");

      // Step 2: Call matching API
      return await matchingService.compare({
        candidate_profile_id: profile.id,
        job_id: job.job_id,
        job_title: job.job_title,
        company_name: job.employer_name,
        requirements: requirements
      });
    },
    onSuccess: (data) => {
      setMatchResult(data);
      toast.success("So khớp thành công!");
    },
    onError: (error: any) => {
      toast.error(error.message || "Quá trình so khớp gặp lỗi.");
    },
    onSettled: () => {
      setStatusMessage("");
    }
  });

  const handleStartMatching = () => {
    matchMutation.mutate();
  };

  if (isJobLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-40">
        <Loader2 className="animate-spin text-blue-600 w-10 h-10 mb-4" />
        <p className="text-gray-500 text-sm font-medium">Đang tải thông tin chi tiết công việc...</p>
      </div>
    );
  }

  if (jobError || !job) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-12 text-center">
        <div className="bg-red-50 border border-red-100 p-6 rounded-2xl">
          <p className="text-red-700 font-bold mb-4">Không thể tải thông tin công việc</p>
          <button onClick={() => router.back()} className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-800 rounded-lg text-sm font-medium">
            Quay lại
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Back button */}
      <button
        onClick={() => router.back()}
        className="inline-flex items-center gap-1.5 text-gray-500 hover:text-gray-900 text-sm font-bold mb-6 cursor-pointer"
      >
        <ArrowLeft size={16} />
        <span>Quay lại</span>
      </button>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Job details */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
            <h1 className="text-2xl font-bold text-gray-900 leading-snug">{job.job_title}</h1>
            <p className="text-gray-600 font-medium mt-1">{job.employer_name}</p>

            <div className="flex flex-wrap gap-x-6 gap-y-2 mt-4 text-sm text-gray-500 border-t border-b border-gray-50 py-3">
              <div className="flex items-center gap-1.5">
                <MapPin size={16} className="text-gray-400" />
                <span>{job.job_city || "Từ xa"}, {job.job_country}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <DollarSign size={16} className="text-gray-400" />
                <span>
                  {job.job_max_salary 
                    ? `${job.job_max_salary.toLocaleString()} ${job.job_salary_currency || "USD"}`
                    : "Thỏa thuận"}
                </span>
              </div>
            </div>

            <div className="mt-6">
              <h2 className="font-bold text-gray-900 text-base mb-3">Mô tả công việc (Job Description)</h2>
              <p className="text-gray-700 text-sm leading-relaxed whitespace-pre-line">{job.job_description}</p>
            </div>

            <div className="mt-8 flex justify-end">
              <a
                href={job.job_apply_link}
                target="_blank"
                rel="noopener noreferrer"
                className="px-6 py-2.5 bg-gray-900 hover:bg-gray-800 text-white rounded-xl text-sm font-bold transition-all"
              >
                Ứng tuyển trực tiếp
              </a>
            </div>
          </div>
        </div>

        {/* Right Column: Match Analysis */}
        <div className="space-y-6">
          
          {/* Match Trigger Box */}
          {!matchResult && (
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-2xl border border-blue-100/50 shadow-sm text-center">
              <div className="bg-blue-600 w-12 h-12 rounded-xl flex items-center justify-center text-white mx-auto mb-4 shadow-md shadow-blue-500/20">
                <Sparkles size={24} />
              </div>
              <h3 className="font-bold text-gray-900 text-base mb-2">Đánh giá Độ phù hợp</h3>
              <p className="text-xs text-gray-500 font-medium mb-6">
                Sử dụng AI phân tích CV của bạn để đối chiếu tức thì với các yêu cầu kỹ thuật của công việc này.
              </p>

              {matchMutation.isPending ? (
                <div className="flex flex-col items-center justify-center py-2">
                  <Loader2 className="animate-spin text-blue-600 w-8 h-8 mb-2" />
                  <p className="text-xs text-blue-700 font-bold animate-pulse">{statusMessage}</p>
                </div>
              ) : (
                <button
                  onClick={handleStartMatching}
                  disabled={isProfileLoading}
                  className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-55 text-white rounded-xl text-sm font-bold shadow-md shadow-blue-500/10 transition-all cursor-pointer"
                >
                  {isProfileLoading ? "Đang tải hồ sơ..." : "So khớp hồ sơ của tôi"}
                </button>
              )}
            </div>
          )}

          {/* Match Score Display */}
          {matchResult && (
            <div className="space-y-6 animate-fade-in">
              <MatchScoreDial score={matchResult.overall_score} />
              
              <RequirementMatrixView matrix={matchResult.match_matrix} />

              <div className="text-center">
                <button
                  onClick={() => setMatchResult(null)}
                  className="text-xs font-semibold text-gray-500 hover:text-gray-900 transition-all cursor-pointer"
                >
                  Xóa kết quả & So khớp lại
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
