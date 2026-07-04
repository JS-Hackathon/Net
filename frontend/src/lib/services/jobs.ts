import api from "@/lib/axios";

export interface JobSummary {
  id: string;
  externalId: string;
  title: string;
  company: string;
  companyLogoUrl: string | null;
  location: string | null;
  employmentType: string | null;
  experienceLevel: string | null;
  salaryRange: string | null;
  salaryMin: number | null;
  salaryMax: number | null;
  skillsRequired: string[];
  postedDate: string | null;
  applicationUrl: string | null;
  isBookmarked: boolean;
}

export interface JobDetail extends JobSummary {
  description: string | null;
  requirements: string | null;
  benefits: string | null;
  industry: string | null;
  sourcePlatform: string | null;
  jobType: string | null;
}

export interface Pagination {
  page: number;
  perPage: number;
  total: number;
  totalPages: number;
}

export interface JobSearchResult {
  jobs: JobSummary[];
  pagination: Pagination;
}

export interface JobSearchFilters {
  q: string;
  location?: string;
  employmentType?: string;
  experienceLevel?: string;
  salaryMin?: number;
  remote?: boolean;
  page?: number;
  perPage?: number;
}

export interface BookmarkItem {
  job: JobSummary;
  bookmarkedAt: string;
}

export interface JobRecommendation {
  job: JobSummary;
  recommendationScore: number;
  recommendationReason: string;
}

export interface SavedSearch {
  id: string;
  name: string;
  searchCriteria: Record<string, unknown>;
  alertFrequency: string;
  isActive: boolean;
  createdAt: string;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const mapJob = (j: any): JobDetail => ({
  id: j.id,
  externalId: j.external_id,
  title: j.title,
  company: j.company,
  companyLogoUrl: j.company_logo_url ?? null,
  location: j.location ?? null,
  employmentType: j.employment_type ?? null,
  experienceLevel: j.experience_level ?? null,
  salaryRange: j.salary_range ?? null,
  salaryMin: j.salary_min ?? null,
  salaryMax: j.salary_max ?? null,
  skillsRequired: (j.skills_required || []).map((s: unknown) => String(s)),
  postedDate: j.posted_date ?? null,
  applicationUrl: j.application_url ?? null,
  isBookmarked: !!j.is_bookmarked,
  description: j.description ?? null,
  requirements: j.requirements ?? null,
  benefits: j.benefits ?? null,
  industry: j.industry ?? null,
  sourcePlatform: j.source_platform ?? null,
  jobType: j.job_type ?? null,
});

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const mapPagination = (p: any): Pagination => ({
  page: p.page,
  perPage: p.per_page,
  total: p.total,
  totalPages: p.total_pages,
});

export const jobService = {
  async search(filters: JobSearchFilters): Promise<JobSearchResult> {
    const params: Record<string, string | number | boolean> = { q: filters.q };
    if (filters.location) params.location = filters.location;
    if (filters.employmentType) params.employment_type = filters.employmentType;
    if (filters.experienceLevel) params.experience_level = filters.experienceLevel;
    if (filters.salaryMin != null) params.salary_min = filters.salaryMin;
    if (filters.remote) params.remote = true;
    params.page = filters.page ?? 1;
    params.per_page = filters.perPage ?? 20;

    const response = await api.get("/api/v1/jobs/search", { params });
    const d = response.data.data;
    return { jobs: (d.jobs || []).map(mapJob), pagination: mapPagination(d.pagination) };
  },

  async getJob(jobId: string): Promise<JobDetail> {
    const response = await api.get(`/api/v1/jobs/${jobId}`);
    return mapJob(response.data.data);
  },

  async bookmark(jobId: string): Promise<void> {
    await api.post(`/api/v1/jobs/${jobId}/bookmark`);
  },

  async unbookmark(jobId: string): Promise<void> {
    await api.delete(`/api/v1/jobs/${jobId}/bookmark`);
  },

  async getBookmarks(): Promise<BookmarkItem[]> {
    const response = await api.get("/api/v1/jobs/bookmarks");
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return (response.data.data.bookmarks || []).map((b: any) => ({
      job: mapJob(b.job),
      bookmarkedAt: b.bookmarked_at,
    }));
  },

  async getRecommendations(): Promise<JobRecommendation[]> {
    const response = await api.get("/api/v1/jobs/recommendations");
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return (response.data.data.recommendations || []).map((r: any) => ({
      job: mapJob(r.job),
      recommendationScore:
        r.recommendation_score != null ? parseFloat(r.recommendation_score) : 0,
      recommendationReason: r.recommendation_reason,
    }));
  },

  async listSavedSearches(): Promise<SavedSearch[]> {
    const response = await api.get("/api/v1/jobs/saved-searches");
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return (response.data.data.saved_searches || []).map((s: any) => ({
      id: s.id,
      name: s.name,
      searchCriteria: s.search_criteria,
      alertFrequency: s.alert_frequency,
      isActive: s.is_active,
      createdAt: s.created_at,
    }));
  },

  async createSavedSearch(
    name: string,
    criteria: Record<string, unknown>,
    alertFrequency = "daily"
  ): Promise<SavedSearch> {
    const response = await api.post("/api/v1/jobs/saved-searches", {
      name,
      search_criteria: criteria,
      alert_frequency: alertFrequency,
    });
    const s = response.data.data;
    return {
      id: s.id,
      name: s.name,
      searchCriteria: s.search_criteria,
      alertFrequency: s.alert_frequency,
      isActive: s.is_active,
      createdAt: s.created_at,
    };
  },
};
