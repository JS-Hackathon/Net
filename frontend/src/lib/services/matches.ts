import api from "@/lib/axios";

export interface MatchScore {
  matchId: string;
  overallScore: number;
  skillsScore: number | null;
  experienceScore: number | null;
  educationScore: number | null;
  locationScore: number | null;
  confidenceScore: number | null;
  needsReview: boolean;
  processingTime: number | null;
  createdAt: string | null;
}

export interface JobBrief {
  id: string;
  title: string;
  company: string;
  location: string | null;
  employmentType: string | null;
}

export interface SkillMatch {
  skillName: string;
  skillCategory: string | null;
  requiredProficiency: string | null;
  candidateProficiency: string | null;
  matchType: string | null;
  matchScore: number | null;
}

export interface MatchAnalysis {
  summary: string | null;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  strengths: any[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  weaknesses: any[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  missingSkills: any[];
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  areasForImprovement: any[];
  recommendation: Record<string, unknown>;
  skillsMatches: SkillMatch[];
}

export interface MatchDetail {
  id: string;
  job: JobBrief | null;
  overallScore: number;
  skillsScore: number | null;
  experienceScore: number | null;
  educationScore: number | null;
  locationScore: number | null;
  confidenceScore: number | null;
  needsReview: boolean;
  analysis: MatchAnalysis;
  processingTime: number | null;
  createdAt: string | null;
}

export interface MatchListItem {
  matchId: string;
  job: JobBrief;
  overallScore: number;
  matchSummary: string | null;
  needsReview: boolean;
  createdAt: string | null;
}

export interface MatchList {
  matches: MatchListItem[];
  pagination: { page: number; perPage: number; total: number; totalPages: number };
}

export interface BatchMatchResult {
  matches: {
    jobId: string;
    matchId: string | null;
    overallScore: number | null;
    status: string;
  }[];
  processingSummary: {
    totalJobs: number;
    successful: number;
    failed: number;
    averageProcessingTime: number;
  };
}

export interface AutoMatchCompany {
  jobId: string;
  title: string;
  company: string;
  location: string | null;
  employmentType: string | null;
  matchScore: number;
  reason: string | null;
  skillsRequired: string[];
}

export interface InterviewQuestion {
  category: string | null;
  question: string | null;
  assesses: string | null;
  answerTip: string | null;
}

export interface InterviewScenario {
  opening: string | null;
  focusSkills: string[];
  gapsToPrepare: string[];
  questions: InterviewQuestion[];
  preparationTips: string[];
  closing: string | null;
}

export interface AutoMatchResult {
  companies: AutoMatchCompany[];
  target: { jobId: string; title: string | null; company: string | null; location: string | null };
  interviewScenario: InterviewScenario;
}

const num = (v: unknown): number | null => (v != null ? parseFloat(String(v)) : null);

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const mapScore = (d: any): MatchScore => ({
  matchId: d.match_id,
  overallScore: parseFloat(d.overall_score),
  skillsScore: num(d.skills_score),
  experienceScore: num(d.experience_score),
  educationScore: num(d.education_score),
  locationScore: num(d.location_score),
  confidenceScore: num(d.confidence_score),
  needsReview: !!d.needs_review,
  processingTime: d.processing_time ?? null,
  createdAt: d.created_at ?? null,
});

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const mapJobBrief = (j: any): JobBrief => ({
  id: j.id,
  title: j.title,
  company: j.company,
  location: j.location ?? null,
  employmentType: j.employment_type ?? null,
});

export const matchService = {
  async autoMatch(): Promise<AutoMatchResult> {
    const response = await api.post("/api/v1/matches/auto");
    const d = response.data.data;
    return {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      companies: (d.companies || []).map((c: any) => ({
        jobId: c.job_id,
        title: c.title,
        company: c.company,
        location: c.location ?? null,
        employmentType: c.employment_type ?? null,
        matchScore: parseFloat(c.match_score ?? 0),
        reason: c.reason ?? null,
        skillsRequired: c.skills_required || [],
      })),
      target: {
        jobId: d.target.job_id,
        title: d.target.title ?? null,
        company: d.target.company ?? null,
        location: d.target.location ?? null,
      },
      interviewScenario: {
        opening: d.interview_scenario.opening ?? null,
        focusSkills: d.interview_scenario.focus_skills || [],
        gapsToPrepare: d.interview_scenario.gaps_to_prepare || [],
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        questions: (d.interview_scenario.questions || []).map((q: any) => ({
          category: q.category ?? null,
          question: q.question ?? null,
          assesses: q.assesses ?? null,
          answerTip: q.answer_tip ?? null,
        })),
        preparationTips: d.interview_scenario.preparation_tips || [],
        closing: d.interview_scenario.closing ?? null,
      },
    };
  },

  async calculateMatch(jobId: string): Promise<MatchScore> {
    const response = await api.post(`/api/v1/jobs/${jobId}/match`);
    return mapScore(response.data.data);
  },

  async batchMatch(jobIds: string[]): Promise<BatchMatchResult> {
    const response = await api.post("/api/v1/jobs/batch-match", { job_ids: jobIds });
    const d = response.data.data;
    return {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      matches: (d.matches || []).map((m: any) => ({
        jobId: m.job_id,
        matchId: m.match_id,
        overallScore: num(m.overall_score),
        status: m.status,
      })),
      processingSummary: {
        totalJobs: d.processing_summary.total_jobs,
        successful: d.processing_summary.successful,
        failed: d.processing_summary.failed,
        averageProcessingTime: d.processing_summary.average_processing_time,
      },
    };
  },

  async listMatches(params: {
    minScore?: number;
    sort?: "score" | "date";
    order?: "asc" | "desc";
    page?: number;
    perPage?: number;
  } = {}): Promise<MatchList> {
    const query: Record<string, string | number> = {};
    if (params.minScore != null) query.min_score = params.minScore;
    query.sort = params.sort ?? "score";
    query.order = params.order ?? "desc";
    query.page = params.page ?? 1;
    query.per_page = params.perPage ?? 20;

    const response = await api.get("/api/v1/matches", { params: query });
    const d = response.data.data;
    return {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      matches: (d.matches || []).map((m: any) => ({
        matchId: m.match_id,
        job: mapJobBrief(m.job),
        overallScore: parseFloat(m.overall_score),
        matchSummary: m.match_summary ?? null,
        needsReview: !!m.needs_review,
        createdAt: m.created_at ?? null,
      })),
      pagination: {
        page: d.pagination.page,
        perPage: d.pagination.per_page,
        total: d.pagination.total,
        totalPages: d.pagination.total_pages,
      },
    };
  },

  async getMatchDetail(matchId: string): Promise<MatchDetail> {
    const response = await api.get(`/api/v1/matches/${matchId}`);
    const d = response.data.data;
    return {
      id: d.id,
      job: d.job ? mapJobBrief(d.job) : null,
      overallScore: parseFloat(d.overall_score),
      skillsScore: num(d.skills_score),
      experienceScore: num(d.experience_score),
      educationScore: num(d.education_score),
      locationScore: num(d.location_score),
      confidenceScore: num(d.confidence_score),
      needsReview: !!d.needs_review,
      analysis: {
        summary: d.analysis.summary ?? null,
        strengths: d.analysis.strengths || [],
        weaknesses: d.analysis.weaknesses || [],
        missingSkills: d.analysis.missing_skills || [],
        areasForImprovement: d.analysis.areas_for_improvement || [],
        recommendation: d.analysis.recommendation || {},
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        skillsMatches: (d.analysis.skills_matches || []).map((s: any) => ({
          skillName: s.skill_name,
          skillCategory: s.skill_category ?? null,
          requiredProficiency: s.required_proficiency ?? null,
          candidateProficiency: s.candidate_proficiency ?? null,
          matchType: s.match_type ?? null,
          matchScore: num(s.match_score),
        })),
      },
      processingTime: d.processing_time ?? null,
      createdAt: d.created_at ?? null,
    };
  },

  async submitFeedback(
    matchId: string,
    payload: { feedbackType?: string; userRating?: number; feedbackNotes?: string }
  ): Promise<void> {
    await api.post(`/api/v1/matches/${matchId}/feedback`, {
      feedback_type: payload.feedbackType,
      user_rating: payload.userRating,
      feedback_notes: payload.feedbackNotes,
    });
  },
};
