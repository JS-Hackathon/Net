import api from "@/lib/axios";

export interface MatchEvidence {
  section: string;
  text: string;
}

export interface PriorityInfo {
  level: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  score: number;
}

export interface RequirementMatchResult {
  requirement_id: string;
  requirement: string;

  status: "SATISFIED" | "PARTIAL" | "CLARIFICATION" | "MISSING";
  priority: PriorityInfo;
  confidence: number;
  evidence_score: number;
  matched_skill: string;
  matching_method: string;
  evidence: MatchEvidence[];
  reasoning: string[];
  contribution: number;
}

export interface CompareRequest {
  candidate_profile_id: string;
  job_id: string;
  job_title: string;
  company_name: string;
  requirements: Array<{
    id: string;
    text: string;
    canonical: string;
    category: string;
    section: "must_have" | "required" | "preferred" | "nice_to_have";
    priority: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  }>;
}

export interface CompareResponse {
  match_id: string;
  overall_score: number;
  match_matrix: RequirementMatchResult[];
}

export interface MatchHistoryItem {
  match_id: string;
  job_id: string;
  job_title: string;
  company_name: string;
  overall_score: number;
  created_at: string;
}

export const matchingService = {
  compare: async (payload: CompareRequest): Promise<CompareResponse> => {
    try {
      const response = await api.post<CompareResponse>("/api/v1/matching/compare", payload);
      return response.data;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || "So khớp cơ hội việc làm thất bại!";
      throw new Error(errorMsg);
    }
  },

  getHistory: async (): Promise<MatchHistoryItem[]> => {
    try {
      const response = await api.get<MatchHistoryItem[]>("/api/v1/matching/history");
      return response.data;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || "Lấy lịch sử so khớp thất bại!";
      throw new Error(errorMsg);
    }
  },

  getMatchDetail: async (matchId: string): Promise<CompareResponse> => {
    try {
      const response = await api.get<CompareResponse>(`/api/v1/matching/history/${matchId}`);
      return response.data;
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || "Lấy chi tiết so khớp thất bại!";
      throw new Error(errorMsg);
    }
  },
};
