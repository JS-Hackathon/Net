import api from "@/lib/axios";

export interface Job {
  job_id: string;
  job_title: string;
  employer_name: string;
  job_description: string;
  job_city?: string;
  job_country?: string;
  job_apply_link: string;
  job_max_salary?: number;
  job_salary_currency?: string;
  employer_logo?: string;
}

export const jobService = {
  searchJobs: async (query: string, page: number = 1): Promise<Job[]> => {
    try {
      const response = await api.get<Job[]>("/api/v1/jobs/search", {
        params: { query, page },
      });
      return response.data;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || "Tìm kiếm việc làm thất bại!";
      throw new Error(errorMsg);
    }
  },

  getJobDetail: async (jobId: string): Promise<Job> => {
    try {
      const response = await api.get<Job>(`/api/v1/jobs/${jobId}`);
      return response.data;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || "Lấy chi tiết công việc thất bại!";
      throw new Error(errorMsg);
    }
  },
};
