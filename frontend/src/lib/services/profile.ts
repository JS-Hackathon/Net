import api from "@/lib/axios";

export interface WorkExperience {
  title: string;
  company: string;
  location?: string;
  startDate: string;
  endDate?: string;
  isCurrent: boolean;
  description: string;
  keyAchievements: string[];
  technologiesUsed: string[];
}

export interface Education {
  degree: string;
  fieldOfStudy?: string;
  institution: string;
  location?: string;
  graduationDate?: string;
  gpa?: string;
  honors: string[];
}

export interface TechnicalSkill {
  name: string;
  category: string;
  proficiency: string;
  yearsExperience?: number;
}

export interface SoftSkill {
  name: string;
  description?: string;
}

export interface Certification {
  name: string;
  issuer: string;
  issueDate?: string;
  expiryDate?: string;
  credentialId?: string;
  verificationUrl?: string;
}

export interface Language {
  language: string;
  proficiency: string;
}

export interface Project {
  name: string;
  description: string;
  technologies: string[];
  url?: string;
  startDate?: string;
  endDate?: string;
}

export interface Achievement {
  title: string;
  description?: string;
  date?: string;
  issuer?: string;
}

export interface CandidateProfile {
  id: string;
  userId: string;
  sourceAnalysisId: string | null;
  fullName: string | null;
  email: string | null;
  phone: string | null;
  location: string | null;
  linkedinUrl: string | null;
  portfolioUrl: string | null;
  githubUrl: string | null;
  websiteUrl: string | null;
  professionalSummary: string | null;
  careerObjective: string | null;
  yearsOfExperience: number | null;
  currentRole: string | null;
  currentCompany: string | null;
  salaryExpectationMin: number | null;
  salaryExpectationMax: number | null;
  availability: string | null;
  workExperience: WorkExperience[];
  education: Education[];
  technicalSkills: TechnicalSkill[];
  softSkills: SoftSkill[];
  certifications: Certification[];
  languages: Language[];
  projects: Project[];
  achievements: Achievement[];
  completenessScore: number;
  profileStrength: string;
  isPublic: boolean;
  isSearchable: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface CompletenessSuggestion {
  section: string;
  message: string;
  priority: string;
}

export interface ProfileCompleteness {
  overallScore: number;
  sectionScores: Record<string, number>;
  suggestions: CompletenessSuggestion[];
  missingFields: Record<string, string[]>;
}

export interface ExportResponse {
  downloadUrl: string;
  expiresAt: string;
  fileName: string;
}

interface RawWorkExperience {
  title: string;
  company: string;
  location?: string;
  start_date: string;
  end_date?: string;
  is_current: boolean;
  description: string;
  key_achievements?: string[];
  technologies_used?: string[];
}

interface RawEducation {
  degree: string;
  field_of_study?: string;
  institution: string;
  location?: string;
  graduation_date?: string;
  gpa?: string;
  honors?: string[];
}

interface RawTechnicalSkill {
  name: string;
  category: string;
  proficiency: string;
  years_experience?: number;
}

interface RawSoftSkill {
  name: string;
  description?: string;
}

interface RawCertification {
  name: string;
  issuer: string;
  issue_date?: string;
  expiry_date?: string;
  credential_id?: string;
  verification_url?: string;
}

interface RawLanguage {
  language: string;
  proficiency: string;
}

interface RawProject {
  name: string;
  description: string;
  technologies?: string[];
  url?: string;
  start_date?: string;
  end_date?: string;
}

interface RawAchievement {
  title: string;
  description?: string;
  date?: string;
  issuer?: string;
}

interface RawProfile {
  id: string;
  user_id: string;
  source_analysis_id: string | null;
  full_name: string | null;
  email: string | null;
  phone: string | null;
  location: string | null;
  linkedin_url: string | null;
  portfolio_url: string | null;
  github_url: string | null;
  website_url: string | null;
  professional_summary: string | null;
  career_objective: string | null;
  years_of_experience: number | null;
  current_role: string | null;
  current_company: string | null;
  salary_expectation_min: number | null;
  salary_expectation_max: number | null;
  availability: string | null;
  work_experience?: RawWorkExperience[];
  education?: RawEducation[];
  technical_skills?: RawTechnicalSkill[];
  soft_skills?: RawSoftSkill[];
  certifications?: RawCertification[];
  languages?: RawLanguage[];
  projects?: RawProject[];
  achievements?: RawAchievement[];
  completeness_score: string | number | null;
  profile_strength: string;
  is_public: boolean;
  is_searchable: boolean;
  created_at: string;
  updated_at: string;
}

const mapProfile = (p: RawProfile): CandidateProfile => ({
  id: p.id,
  userId: p.user_id,
  sourceAnalysisId: p.source_analysis_id,
  fullName: p.full_name,
  email: p.email,
  phone: p.phone,
  location: p.location,
  linkedinUrl: p.linkedin_url,
  portfolioUrl: p.portfolio_url,
  githubUrl: p.github_url,
  websiteUrl: p.website_url,
  professionalSummary: p.professional_summary,
  careerObjective: p.career_objective,
  yearsOfExperience: p.years_of_experience,
  currentRole: p.current_role,
  currentCompany: p.current_company,
  salaryExpectationMin: p.salary_expectation_min,
  salaryExpectationMax: p.salary_expectation_max,
  availability: p.availability,
  workExperience: (p.work_experience || []).map((w) => ({
    title: w.title,
    company: w.company,
    location: w.location,
    startDate: w.start_date,
    endDate: w.end_date,
    isCurrent: w.is_current,
    description: w.description,
    keyAchievements: w.key_achievements || [],
    technologiesUsed: w.technologies_used || [],
  })),
  education: (p.education || []).map((e) => ({
    degree: e.degree,
    fieldOfStudy: e.field_of_study,
    institution: e.institution,
    location: e.location,
    graduationDate: e.graduation_date,
    gpa: e.gpa,
    honors: e.honors || [],
  })),
  technicalSkills: (p.technical_skills || []).map((s) => ({
    name: s.name,
    category: s.category,
    proficiency: s.proficiency,
    yearsExperience: s.years_experience,
  })),
  softSkills: (p.soft_skills || []).map((s) => ({
    name: s.name,
    description: s.description,
  })),
  certifications: (p.certifications || []).map((c) => ({
    name: c.name,
    issuer: c.issuer,
    issueDate: c.issue_date,
    expiryDate: c.expiry_date,
    credentialId: c.credential_id,
    verificationUrl: c.verification_url,
  })),
  languages: (p.languages || []).map((l) => ({
    language: l.language,
    proficiency: l.proficiency,
  })),
  projects: (p.projects || []).map((proj) => ({
    name: proj.name,
    description: proj.description,
    technologies: proj.technologies || [],
    url: proj.url,
    startDate: proj.start_date,
    endDate: proj.end_date,
  })),
  achievements: (p.achievements || []).map((ac) => ({
    title: ac.title,
    description: ac.description,
    date: ac.date,
    issuer: ac.issuer,
  })),
  completenessScore: p.completeness_score !== null ? parseFloat(String(p.completeness_score)) : 0,
  profileStrength: p.profile_strength,
  isPublic: p.is_public,
  isSearchable: p.is_searchable,
  createdAt: p.created_at,
  updatedAt: p.updated_at,
});

export const profileService = {
  async getProfile(): Promise<CandidateProfile> {
    const response = await api.get("/api/v1/profile");
    return mapProfile(response.data.data);
  },

  async updateProfileSection(section: string, data: Record<string, unknown>): Promise<CandidateProfile> {
    const response = await api.put("/api/v1/profile", {
      section,
      data,
    });
    return mapProfile(response.data.data);
  },

  async getCompleteness(): Promise<ProfileCompleteness> {
    const response = await api.get("/api/v1/profile/completeness");
    const d = response.data.data;
    return {
      overallScore: d.overall_score !== null ? parseFloat(d.overall_score) : 0,
      sectionScores: d.section_scores || {},
      suggestions: d.suggestions || [],
      missingFields: d.missing_fields || {},
    };
  },

  async exportProfile(format: "pdf" | "json"): Promise<ExportResponse> {
    const response = await api.post("/api/v1/profile/export", {
      format,
    });
    const d = response.data.data;
    return {
      downloadUrl: d.download_url,
      expiresAt: d.expires_at,
      fileName: d.file_name,
    };
  },
};
