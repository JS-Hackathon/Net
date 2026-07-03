import api from "@/lib/axios";

export interface ResumeAnalysis {
  id: string;
  resumeId: string;
  status: string;
  confidenceScore: number | null;
  parsedData: Record<string, unknown> | null;
  errorMessage: string | null;
  parsingDuration: number | null;
  createdAt: string;
  completedAt: string | null;
}

export interface ParsingStatus {
  status: string;
  progressPercentage: number;
  estimatedCompletion: string | null;
  currentStep: string | null;
}

interface RawAnalysis {
  id: string;
  resume_id: string;
  status: string;
  confidence_score: string | number | null;
  parsed_data: Record<string, unknown> | null;
  error_message: string | null;
  parsing_duration: number | null;
  created_at: string;
  completed_at: string | null;
}

const mapAnalysis = (a: RawAnalysis): ResumeAnalysis => ({
  id: a.id,
  resumeId: a.resume_id,
  status: a.status,
  confidenceScore: a.confidence_score !== null ? parseFloat(String(a.confidence_score)) : null,
  parsedData: a.parsed_data,
  errorMessage: a.error_message,
  parsingDuration: a.parsing_duration,
  createdAt: a.created_at,
  completedAt: a.completed_at,
});

export const analysisService = {
  async parseResume(resumeId: string): Promise<ResumeAnalysis> {
    const response = await api.post(`/api/v1/resumes/${resumeId}/parse`);
    return mapAnalysis(response.data.data);
  },

  async getAnalysis(analysisId: string): Promise<ResumeAnalysis> {
    const response = await api.get(`/api/v1/analyses/${analysisId}`);
    return mapAnalysis(response.data.data);
  },

  async getParsingStatus(analysisId: string): Promise<ParsingStatus> {
    const response = await api.get(`/api/v1/analyses/${analysisId}/status`);
    const data = response.data.data;
    return {
      status: data.status,
      progressPercentage: data.progress_percentage,
      estimatedCompletion: data.estimated_completion,
      currentStep: data.current_step,
    };
  },

  async submitAnalysisReview(analysisId: string, corrections: Record<string, unknown>, approved: boolean): Promise<ResumeAnalysis> {
    const response = await api.put(`/api/v1/analyses/${analysisId}/review`, {
      corrections,
      approved,
    });
    return mapAnalysis(response.data.data);
  },

  async retryParsing(analysisId: string): Promise<ResumeAnalysis> {
    const response = await api.post(`/api/v1/analyses/${analysisId}/retry`);
    return mapAnalysis(response.data.data);
  },
};
