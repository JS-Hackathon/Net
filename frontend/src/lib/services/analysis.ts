import api from "@/lib/axios";

export interface ResumeAnalysis {
  id: string;
  resumeId: string;
  status: string;
  confidenceScore: number | null;
  parsedData: any | null;
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

const mapAnalysis = (a: any): ResumeAnalysis => ({
  id: a.id,
  resumeId: a.resume_id,
  status: a.status,
  confidenceScore: a.confidence_score !== null ? parseFloat(a.confidence_score) : null,
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

  async submitAnalysisReview(analysisId: string, corrections: any, approved: boolean): Promise<ResumeAnalysis> {
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
