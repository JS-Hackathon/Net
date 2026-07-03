"use client";

import React, { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/lib/store/authStore";
import api from "@/lib/axios";
import { toast } from "sonner";
import { 
  User as UserIcon, 
  Shield, 
  LogOut, 
  Save, 
  Loader2,
  FileText,
  Download,
  X,
  Plus,
  Trash2,
  Wrench,
  GraduationCap,
  Briefcase
} from "lucide-react";

import { resumeService, Resume } from "@/lib/services/resume";
import { analysisService, ResumeAnalysis } from "@/lib/services/analysis";
import { profileService, CandidateProfile, ProfileCompleteness as CompletenessType } from "@/lib/services/profile";

import { ResumeUploadZone } from "@/components/profile/ResumeUploadZone";
import { UploadProgress } from "@/components/profile/UploadProgress";
import { ResumeList } from "@/components/profile/ResumeList";
import { ParsedDataReview } from "@/components/profile/ParsedDataReview";
import { ProfileCompleteness } from "@/components/profile/ProfileCompleteness";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type RecordStringUnknown = any;

export default function ProfilePage() {
  const router = useRouter();
  const { user, updateProfile, logout, checkAuth, isInitialized, isLoading } = useAuthStore();
  
  const [fullName, setFullName] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [isUpdatingAccount, setIsUpdatingAccount] = useState(false);

  // Tabs layout state
  const [activeTab, setActiveTab] = useState<"account" | "resumes" | "profile">("resumes");

  // Phase 2 state
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [profile, setProfile] = useState<CandidateProfile | null>(null);
  const [completeness, setCompleteness] = useState<CompletenessType | null>(null);
  
  // File Upload State
  const [isUploading, setIsUploading] = useState(false);
  const [uploadingFileName, setUploadingFileName] = useState("");
  const [uploadingFileSize, setUploadingFileSize] = useState(0);
  
  // Parsing status & Polling
  const [activeAnalysis, setActiveAnalysis] = useState<ResumeAnalysis | null>(null);
  const [pollingProgress, setPollingProgress] = useState(0);
  const [pollingStep, setPollingStep] = useState("");
  
  // Review Mode
  const [reviewAnalysis, setReviewAnalysis] = useState<ResumeAnalysis | null>(null);

  // Editing Profile Section States
  const [editingSection, setEditingSection] = useState<string | null>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [editFormData, setEditFormData] = useState<RecordStringUnknown | RecordStringUnknown[] | null>(null);

  // Ref for polling interval
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  const fetchCandidateData = async () => {
    try {
      const [resList, prof, comp] = await Promise.all([
        resumeService.listResumes(),
        profileService.getProfile(),
        profileService.getCompleteness()
      ]);

      setResumes(resList);
      setProfile(prof);
      setCompleteness(comp);

      // Check if any resume is still processing on initial load
      const processingResume = resList.find(r => r.uploadStatus === "processing");
      if (processingResume && !activeAnalysis) {
        // Find or create pending analysis to poll
        toast.info("Đang phát hiện CV đang phân tích dở dang, tự động kết nối...");
      }
    } catch (e: unknown) {
      console.error("Error loading profile data:", e);
    }
  };

  // Load account data
  useEffect(() => {
    /* eslint-disable react-hooks/set-state-in-effect */
    if (user) {
      // Only state update if values are different to avoid unnecessary renders
      if (fullName !== (user.fullName || "")) {
        setFullName(user.fullName || "");
      }
      if (avatarUrl !== (user.avatarUrl || "")) {
        setAvatarUrl(user.avatarUrl || "");
      }
      if (previewUrl !== (user.avatarUrl || "")) {
        setPreviewUrl(user.avatarUrl || "");
      }
    } else if (isInitialized && !user) {
      router.push("/login");
    }
    /* eslint-enable react-hooks/set-state-in-effect */
  }, [user, isInitialized, router]);

  // Fetch candidate profile data once on mount when user is loaded
  const hasFetched = useRef(false);
  useEffect(() => {
    if (user && !hasFetched.current) {
      hasFetched.current = true;
      fetchCandidateData();
    }
  }, [user]);

  const handleUpdateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim()) {
      toast.error("Họ và tên không được để trống");
      return;
    }

    setIsUpdatingAccount(true);
    try {
      let finalAvatarUrl = avatarUrl;
      
      if (avatarFile) {
        const formData = new FormData();
        formData.append("file", avatarFile);
        
        const uploadRes = await api.post("/api/v1/upload", formData, {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        });
        
        if (uploadRes.data?.success) {
          finalAvatarUrl = uploadRes.data.data.url;
          setAvatarUrl(finalAvatarUrl);
          setPreviewUrl(finalAvatarUrl);
        }
      }

      await updateProfile({ fullName, avatarUrl: finalAvatarUrl });
      toast.success("Cập nhật thông tin hồ sơ thành công!");
      setAvatarFile(null);
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } } };
      const msg = err.response?.data?.message || "Cập nhật tài khoản thất bại";
      toast.error(msg);
    } finally {
      setIsUpdatingAccount(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      toast.success("Đăng xuất thành công!");
      router.push("/login");
    } catch (error: unknown) {
      toast.error("Lỗi khi đăng xuất");
    }
  };

  // Upload trigger
  const handleFileSelect = async (file: File) => {
    setIsUploading(true);
    setUploadingFileName(file.name);
    setUploadingFileSize(file.size);

    try {
      const resume = await resumeService.uploadResume(file);
      toast.success(`Đã tải lên CV "${file.name}" thành công!`);
      
      // Reload resume lists
      const resList = await resumeService.listResumes();
      setResumes(resList);

      toast.info("Đang khởi động phân tích CV bằng AI...");
      const analysis = await analysisService.parseResume(resume.id);
      setActiveAnalysis(analysis);
      startPolling(analysis.id);

    } catch (e: unknown) {
      const err = e as { response?: { data?: { message?: string } } };
      const msg = err.response?.data?.message || "Tải lên CV thất bại";
      toast.error(msg);
    } finally {
      setIsUploading(false);
    }
  };

  // Polling management
  const startPolling = (analysisId: string) => {
    if (pollingRef.current) clearInterval(pollingRef.current);
    
    setPollingProgress(15);
    setPollingStep("Đang chuẩn bị trích xuất...");

    pollingRef.current = setInterval(async () => {
      try {
        const statusData = await analysisService.getParsingStatus(analysisId);
        
        setPollingProgress(statusData.progressPercentage);
        setPollingStep(statusData.currentStep || "Đang xử lý...");

        if (statusData.status === "completed") {
          clearInterval(pollingRef.current!);
          pollingRef.current = null;
          setActiveAnalysis(null);
          toast.success("AI đã phân tích xong CV của bạn!");
          fetchCandidateData(); // Reload all details
        } else if (statusData.status === "reviewing") {
          clearInterval(pollingRef.current!);
          pollingRef.current = null;
          
          // Get the full analysis record so we can load it for review
          const fullAnalysis = await analysisService.getAnalysis(analysisId);
          setActiveAnalysis(null);
          setReviewAnalysis(fullAnalysis);
          
          toast.warning("Phân tích hoàn tất với điểm tin cậy thấp. Vui lòng rà soát lại thông tin.");
          fetchCandidateData();
        } else if (statusData.status === "failed") {
          clearInterval(pollingRef.current!);
          pollingRef.current = null;
          setActiveAnalysis(null);
          toast.error("Quá trình trích xuất & phân tích CV bằng AI đã thất bại.");
          fetchCandidateData();
        }
      } catch (err: unknown) {
        clearInterval(pollingRef.current!);
        pollingRef.current = null;
        setActiveAnalysis(null);
        toast.error("Có lỗi xảy ra khi theo dõi tiến độ phân tích CV.");
      }
    }, 2000);
  };

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Resumes list actions
  const handleDeleteResume = async (id: string) => {
    try {
      await resumeService.deleteResume(id);
      toast.success("Xóa CV thành công!");
      fetchCandidateData();
    } catch (_e) {
      toast.error("Xóa CV thất bại");
    }
  };

  const handleSetPrimaryResume = async (id: string) => {
    try {
      await resumeService.setPrimaryResume(id);
      toast.success("Đã thiết lập CV chính!");
      fetchCandidateData();
    } catch (_e) {
      toast.error("Thiết lập CV chính thất bại");
    }
  };

  const handleDownloadResume = async (id: string) => {
    try {
      const url = await resumeService.getDownloadUrl(id);
      window.open(url, "_blank");
    } catch (_e) {
      toast.error("Tải xuống CV thất bại");
    }
  };

  const handleParseResume = async (id: string) => {
    try {
      toast.info("Đang gửi yêu cầu phân tích CV...");
      const analysis = await analysisService.parseResume(id);
      setActiveAnalysis(analysis);
      startPolling(analysis.id);
    } catch (_e) {
      toast.error("Phân tích CV thất bại");
    }
  };

  // Submit manual corrections & Sync
  const handleApproveReview = async (corrections: RecordStringUnknown) => {
    if (!reviewAnalysis) return;

    try {
      toast.info("Đang đồng bộ dữ liệu vào hồ sơ năng lực...");
      await analysisService.submitAnalysisReview(reviewAnalysis.id, corrections, true);
      toast.success("Đồng bộ hồ sơ thành công!");
      setReviewAnalysis(null);
      fetchCandidateData();
      setActiveTab("profile"); // Switch to profile tab to inspect the completeness
    } catch (_e) {
      toast.error("Đồng bộ và phê duyệt thất bại");
    }
  };

  // Export profile
  const handleExportProfile = async (format: "pdf" | "json") => {
    try {
      toast.info(`Đang tạo file xuất định dạng ${format.toUpperCase()}...`);
      const exportRes = await profileService.exportProfile(format);
      
      // Trigger download
      const link = document.createElement("a");
      link.href = exportRes.downloadUrl;
      link.setAttribute("download", exportRes.fileName);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      toast.success(`Xuất hồ sơ thành công! File đã được tải xuống.`);
    } catch (_e) {
      toast.error("Xuất hồ sơ năng lực thất bại");
    }
  };

  // Edit profile sections manually
  const startEditingSection = (section: string) => {
    if (!profile) return;
    setEditingSection(section);
    
    // Copy the specific data to form state
    let data: RecordStringUnknown | RecordStringUnknown[] = {};
    if (section === "personal_info") {
      data = {
        full_name: profile.fullName,
        email: profile.email,
        phone: profile.phone,
        location: profile.location,
        linkedin_url: profile.linkedinUrl,
        portfolio_url: profile.portfolioUrl,
        github_url: profile.githubUrl,
        website_url: profile.websiteUrl
      };
    } else if (section === "professional_summary") {
      data = {
        professional_summary: profile.professionalSummary,
        career_objective: profile.careerObjective,
        years_of_experience: profile.yearsOfExperience,
        current_role: profile.currentRole,
        current_company: profile.currentCompany,
        salary_expectation_min: profile.salaryExpectationMin,
        salary_expectation_max: profile.salaryExpectationMax,
        availability: profile.availability
      };
    } else {
      data = (profile as RecordStringUnknown)[
        section === "work_experience" ? "workExperience" :
        section === "education" ? "education" :
        section === "technical_skills" ? "technicalSkills" :
        section === "soft_skills" ? "softSkills" :
        section === "certifications" ? "certifications" :
        section === "projects" ? "projects" : "achievements"
      ] as RecordStringUnknown[];
    }
    setEditFormData(JSON.parse(JSON.stringify(data)));
  };

  const saveProfileSection = async () => {
    if (!editingSection || !profile) return;
    try {
      toast.info("Đang lưu chỉnh sửa hồ sơ...");
      // Map section keys to backend snake_case if they're lists
      let payload = editFormData;
      if (editingSection === "work_experience") {
        payload = {
          work_experience: editFormData.map((w: RecordStringUnknown) => ({
            title: w.title,
            company: w.company,
            location: w.location,
            start_date: w.startDate,
            end_date: w.endDate,
            is_current: w.isCurrent,
            description: w.description,
            key_achievements: w.keyAchievements,
            technologies_used: w.technologiesUsed
          }))
        };
      } else if (editingSection === "education") {
        payload = {
          education: editFormData.map((e: RecordStringUnknown) => ({
            degree: e.degree,
            field_of_study: e.fieldOfStudy,
            institution: e.institution,
            location: e.location,
            graduation_date: e.graduationDate,
            gpa: e.gpa,
            honors: e.honors
          }))
        };
      } else if (editingSection === "technical_skills") {
        payload = {
          technical_skills: editFormData.map((s: RecordStringUnknown) => ({
            name: s.name,
            category: s.category,
            proficiency: s.proficiency,
            years_experience: s.yearsExperience
          }))
        };
      } else if (editingSection === "soft_skills") {
        payload = {
          soft_skills: editFormData.map((s: RecordStringUnknown) => ({
            name: s.name,
            description: s.description
          }))
        };
      } else if (editingSection === "certifications") {
        payload = {
          certifications: editFormData.map((c: RecordStringUnknown) => ({
            name: c.name,
            issuer: c.issuer,
            issue_date: c.issueDate,
            expiry_date: c.expiryDate,
            credential_id: c.credentialId,
            verification_url: c.verificationUrl
          }))
        };
      } else if (editingSection === "projects") {
        payload = {
          projects: editFormData.map((proj: RecordStringUnknown) => ({
            name: proj.name,
            description: proj.description,
            technologies: proj.technologies,
            url: proj.url,
            start_date: proj.startDate,
            end_date: proj.endDate
          }))
        };
      } else if (editingSection === "achievements") {
        payload = {
          achievements: editFormData.map((ac: RecordStringUnknown) => ({
            title: ac.title,
            description: ac.description,
            date: ac.date,
            issuer: ac.issuer
          }))
        };
      }

      await profileService.updateProfileSection(editingSection, payload);
      toast.success("Cập nhật phần hồ sơ thành công!");
      setEditingSection(null);
      setEditFormData(null);
      fetchCandidateData();
    } catch (error: unknown) {
      const err = error as { response?: { data?: { message?: string } } };
      toast.error(err.response?.data?.message || "Cập nhật thất bại");
    }
  };

  const handleSuggestionAction = (section: string) => {
    // Focus or scroll to the target section edit
    let sectKey = section;
    if (section === "skills") sectKey = "technical_skills";
    startEditingSection(sectKey);
  };

  // Rendering fallback
  if (!isInitialized || (isLoading && !user)) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-zinc-50 dark:bg-black font-sans">
        <Loader2 className="h-10 w-10 text-primary animate-spin" />
        <p className="mt-4 text-sm text-muted-foreground font-medium">Đang tải cổng thông tin ứng viên...</p>
      </div>
    );
  }

  if (!user) return null;

  const getInitials = (name: string) => {
    if (!name) return "U";
    return name.split(" ").map(part => part[0]).join("").toUpperCase().slice(0, 2);
  };

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-black font-sans text-foreground pb-12 select-none">
      
      {/* Header Bar */}
      <header className="border-b border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 sticky top-0 z-30 shadow-xs">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity cursor-pointer">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-primary to-secondary flex items-center justify-center font-bold text-white text-md">
              M
            </div>
            <span className="font-bold tracking-wide">MockAI Candidate Portal</span>
          </Link>
          
          <div className="flex items-center gap-3">
            <Link
              href="/jobs"
              className="flex items-center gap-1.5 py-2 px-3.5 rounded-xl text-xs font-bold text-zinc-500 hover:text-primary transition duration-200"
            >
              <Briefcase className="h-4 w-4" />
              Tìm việc
            </Link>
            <Link
              href="/matches"
              className="py-2 px-3.5 rounded-xl text-xs font-bold text-zinc-500 hover:text-primary transition duration-200"
            >
              Kết quả match
            </Link>

            <button
              onClick={() => { setActiveTab("account"); setReviewAnalysis(null); }}
              className={`py-2 px-3.5 rounded-xl text-xs font-bold transition duration-200 cursor-pointer ${
                activeTab === "account"
                  ? "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-white"
                  : "text-zinc-500 hover:text-zinc-900 dark:hover:text-white"
              }`}
            >
              Cài đặt tài khoản
            </button>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 py-2 px-3 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 text-sm font-semibold hover:text-red-500 hover:border-red-200 dark:hover:border-red-950 transition duration-200"
            >
              <LogOut className="h-4 w-4" />
              Đăng xuất
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-6xl mx-auto px-6 mt-8 space-y-6">
        
        {/* Profile overview card summary */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-center gap-4.5">
            <div className="relative group">
              {previewUrl ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={previewUrl}
                  alt={user.fullName}
                  className="h-16 w-16 rounded-full object-cover border-2 border-zinc-100 dark:border-zinc-800"
                />
              ) : (
                <div className="h-16 w-16 rounded-full bg-gradient-to-tr from-primary/20 to-secondary/20 border-2 border-zinc-100 dark:border-zinc-800 text-primary flex items-center justify-center font-black text-xl shadow-xs">
                  {getInitials(user.fullName)}
                </div>
              )}
            </div>
            <div className="space-y-1">
              <h2 className="font-extrabold text-xl md:text-2xl text-zinc-900 dark:text-white">{fullName}</h2>
              <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-1.5 py-0.5 px-2.5 rounded-full bg-primary/10 text-primary text-[10px] font-black uppercase tracking-wider">
                  <Shield className="h-3 w-3" />
                  {user.role}
                </span>
                {profile && (
                  <span className="inline-flex items-center gap-1.5 py-0.5 px-2.5 rounded-full bg-success/15 text-success text-[10px] font-black uppercase tracking-wider">
                    Hoàn thiện: {Math.round(profile.completenessScore)}%
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Top navigation tabs */}
          <div className="flex items-center bg-zinc-100 dark:bg-zinc-800 p-1.5 rounded-2xl shrink-0">
            <button
              onClick={() => { setActiveTab("resumes"); setReviewAnalysis(null); }}
              className={`px-4.5 py-2.5 rounded-xl text-xs font-black uppercase tracking-wider transition cursor-pointer ${
                activeTab === "resumes" && !reviewAnalysis
                  ? "bg-white dark:bg-zinc-900 text-zinc-900 dark:text-white shadow-sm font-bold"
                  : "text-zinc-500 hover:text-zinc-900 dark:hover:text-white"
              }`}
            >
              Quản lý CV
            </button>
            <button
              onClick={() => { setActiveTab("profile"); setReviewAnalysis(null); }}
              className={`px-4.5 py-2.5 rounded-xl text-xs font-black uppercase tracking-wider transition cursor-pointer ${
                activeTab === "profile"
                  ? "bg-white dark:bg-zinc-900 text-zinc-900 dark:text-white shadow-sm font-bold"
                  : "text-zinc-500 hover:text-zinc-900 dark:hover:text-white"
              }`}
            >
              Hồ sơ năng lực
            </button>
          </div>
        </div>

        {/* Tab contents wrapper */}
        <div className="space-y-6">
          
          {/* TAB: Account Setting */}
          {activeTab === "account" && (
            <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-2xl p-6 sm:p-8 shadow-sm">
              <div className="pb-6 border-b border-zinc-100 dark:border-zinc-800">
                <h2 className="text-2xl font-extrabold tracking-tight">Cài đặt tài khoản</h2>
                <p className="text-sm text-muted-foreground">
                  Cập nhật thông tin cá nhân và ảnh đại diện của bạn
                </p>
              </div>

              <form onSubmit={handleUpdateAccount} className="pt-6 space-y-6 max-w-xl">
                {/* Full Name */}
                <div className="space-y-1.5">
                  <label className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">
                    Họ và tên
                  </label>
                  <input
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    disabled={isUpdatingAccount}
                    className="w-full px-4 py-3 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900/30 focus:bg-white dark:focus:bg-black focus:outline-none focus:ring-2 focus:ring-primary/45 disabled:opacity-75 disabled:cursor-not-allowed transition duration-200"
                    required
                  />
                </div>

                {/* Avatar File Upload */}
                <div className="space-y-1.5">
                  <label className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">
                    Ảnh đại diện
                  </label>
                  <div className="flex items-center gap-4">
                    {previewUrl ? (
                      <img
                        src={previewUrl}
                        alt="Avatar preview"
                        className="h-16 w-16 rounded-full object-cover border border-zinc-200 dark:border-zinc-800"
                      />
                    ) : (
                      <div className="h-16 w-16 rounded-full bg-zinc-100 dark:bg-zinc-800 flex items-center justify-center font-bold text-zinc-500">
                        {getInitials(fullName)}
                      </div>
                    )}
                    <input
                      type="file"
                      accept="image/*"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          setAvatarFile(file);
                          setPreviewUrl(URL.createObjectURL(file));
                        }
                      }}
                      disabled={isUpdatingAccount}
                      className="w-full text-sm text-zinc-500 dark:text-zinc-400 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20 transition disabled:opacity-50 disabled:cursor-not-allowed"
                    />
                  </div>
                </div>

                {/* Action buttons */}
                <div className="flex gap-3 pt-2">
                  <button
                    type="submit"
                    disabled={isUpdatingAccount}
                    className="flex items-center gap-1.5 py-2.5 px-5 rounded-xl bg-primary text-white font-semibold hover:opacity-95 active:scale-[0.98] disabled:opacity-50 transition duration-200"
                  >
                    {isUpdatingAccount ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Save className="h-4 w-4" />
                    )}
                    Lưu thay đổi
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setFullName(user.fullName || "");
                      setAvatarUrl(user.avatarUrl || "");
                      setPreviewUrl(user.avatarUrl || "");
                      setAvatarFile(null);
                    }}
                    disabled={isUpdatingAccount}
                    className="py-2.5 px-5 rounded-xl border border-zinc-200 dark:border-zinc-800 font-semibold hover:bg-zinc-50 dark:hover:bg-zinc-900 transition duration-200"
                  >
                    Hủy
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* TAB: Resumes Management */}
          {activeTab === "resumes" && !reviewAnalysis && (
            <div className="space-y-6">
              {/* Active Parsing Polling Indicator */}
              {activeAnalysis && (
                <div className="animate-pulse">
                  <UploadProgress 
                    progress={pollingProgress} 
                    fileName={uploadingFileName || "Resume File"} 
                    fileSize={uploadingFileSize || 0}
                  />
                  <p className="mt-2 text-xs font-semibold text-amber-500 flex items-center gap-1 justify-center">
                    <Loader2 className="h-3 w-3 animate-spin" />
                    {pollingStep}
                  </p>
                </div>
              )}

              {/* Upload Zone */}
              <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 shadow-sm">
                <h3 className="font-extrabold text-base md:text-lg text-zinc-900 dark:text-white mb-4">
                  Tải lên hồ sơ CV mới
                </h3>
                <ResumeUploadZone 
                  onFileSelect={handleFileSelect} 
                  isUploading={isUploading} 
                  onFallbackManual={() => {
                    setActiveTab("profile");
                    fetchCandidateData();
                    toast.info("Chuyển sang chế độ nhập thông tin thủ công. Vui lòng bấm 'Chỉnh sửa' hoặc 'Thêm' tại các phần tương ứng để cập nhật.");
                  }}
                />
              </div>

              {/* Resume List */}
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="font-extrabold text-base md:text-lg text-zinc-900 dark:text-white">
                    Các CV đã tải lên ({resumes.length}/10)
                  </h3>
                </div>
                <ResumeList 
                  resumes={resumes} 
                  onDelete={handleDeleteResume}
                  onSetPrimary={handleSetPrimaryResume}
                  onDownload={handleDownloadResume}
                  onParse={handleParseResume}
                />
              </div>
            </div>
          )}

          {/* Inset Review screen */}
          {activeTab === "resumes" && reviewAnalysis && (
            <div className="space-y-4 animate-fadeIn">
              <div className="flex items-center justify-between pb-3 border-b border-zinc-200 dark:border-zinc-800">
                <div className="space-y-0.5">
                  <h3 className="font-extrabold text-lg md:text-xl text-zinc-900 dark:text-white">
                    Kiểm tra và xác thực dữ liệu trích xuất
                  </h3>
                  <p className="text-xs text-muted-foreground">
                    Hệ thống AI đã trích xuất các trường thông tin bên dưới từ CV của bạn.
                  </p>
                </div>
                <button
                  onClick={() => setReviewAnalysis(null)}
                  className="py-1.5 px-3 rounded-lg border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-900 text-xs font-bold transition"
                >
                  Quay lại danh sách
                </button>
              </div>

              <ParsedDataReview 
                analysis={reviewAnalysis} 
                onApprove={handleApproveReview} 
                onCancel={() => setReviewAnalysis(null)}
              />
            </div>
          )}

          {/* TAB: Candidate Profile Details */}
          {activeTab === "profile" && profile && completeness && !editingSection && (
            <div className="space-y-6">
              <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 shadow-sm">
                <ProfileCompleteness completeness={completeness} onSuggestionClick={handleSuggestionAction} />
              </div>

              <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 shadow-sm space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-zinc-100 dark:border-zinc-800">
                  <h3 className="font-extrabold text-lg text-zinc-900 dark:text-white">Hồ sơ chi tiết</h3>
                  <div className="flex items-center gap-2">
                    <button onClick={() => handleExportProfile("json")} className="inline-flex items-center gap-1.5 py-1.5 px-3.5 rounded-xl border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 text-xs font-bold transition text-zinc-700 dark:text-zinc-300">
                      <Download className="h-3.5 w-3.5" /> Xuất JSON
                    </button>
                    <button onClick={() => handleExportProfile("pdf")} className="inline-flex items-center gap-1.5 py-1.5 px-3.5 rounded-xl bg-zinc-950 text-white dark:bg-white dark:text-zinc-950 hover:opacity-90 text-xs font-bold transition">
                      <Download className="h-3.5 w-3.5" /> Xuất PDF
                    </button>
                  </div>
                </div>

                <div className="space-y-8">
                  {/* SECTION 1: Personal Info */}
                  <div className="p-5 border border-zinc-100 dark:border-zinc-800/80 rounded-2xl space-y-3 relative group/sec">
                    <div className="flex items-center justify-between">
                      <h4 className="font-extrabold text-sm md:text-base text-zinc-800 dark:text-zinc-200 flex items-center gap-2">
                        <UserIcon className="h-4.5 w-4.5 text-primary" /> Thông tin liên hệ
                      </h4>
                      <button
                        onClick={() => startEditingSection("personal_info")}
                        className="py-1.5 px-3 rounded-xl border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-900 text-xs font-bold transition duration-200 cursor-pointer"
                      >
                        Chỉnh sửa
                      </button>
                    </div>

                    <div className="grid md:grid-cols-2 gap-x-6 gap-y-2 mt-2 text-sm leading-normal">
                      <p><span className="text-muted-foreground font-medium">Họ & Tên:</span> <strong className="font-bold">{profile.fullName || "N/A"}</strong></p>
                      <p><span className="text-muted-foreground font-medium">Email:</span> <strong className="font-bold">{profile.email || "N/A"}</strong></p>
                      <p><span className="text-muted-foreground font-medium">Số điện thoại:</span> <strong className="font-bold">{profile.phone || "N/A"}</strong></p>
                      <p><span className="text-muted-foreground font-medium">Địa chỉ:</span> <strong className="font-bold">{profile.location || "N/A"}</strong></p>
                      {profile.linkedinUrl && <p><span className="text-muted-foreground font-medium">LinkedIn:</span> <a href={profile.linkedinUrl} className="text-primary font-bold hover:underline" target="_blank" rel="noreferrer">{profile.linkedinUrl}</a></p>}
                      {profile.githubUrl && <p><span className="text-muted-foreground font-medium">GitHub:</span> <a href={profile.githubUrl} className="text-primary font-bold hover:underline" target="_blank" rel="noreferrer">{profile.githubUrl}</a></p>}
                    </div>
                  </div>

                  {/* SECTION 2: Professional Summary */}
                  <div className="p-5 border border-zinc-100 dark:border-zinc-800/80 rounded-2xl space-y-3 relative group/sec">
                    <div className="flex items-center justify-between">
                      <h4 className="font-extrabold text-sm md:text-base text-zinc-800 dark:text-zinc-200 flex items-center gap-2">
                        <FileText className="h-4.5 w-4.5 text-primary" /> Mục tiêu & Tóm tắt năng lực
                      </h4>
                      <button
                        onClick={() => startEditingSection("professional_summary")}
                        className="py-1.5 px-3 rounded-xl border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-900 text-xs font-bold transition duration-200 cursor-pointer"
                      >
                        Chỉnh sửa
                      </button>
                    </div>

                    <div className="space-y-2.5 text-sm leading-normal">
                      <div>
                        <span className="text-xs text-muted-foreground block font-bold uppercase tracking-wider">Tóm tắt sự nghiệp</span>
                        <p className="font-medium mt-0.5 text-zinc-800 dark:text-zinc-200">{profile.professionalSummary || "N/A"}</p>
                      </div>
                      <div>
                        <span className="text-xs text-muted-foreground block font-bold uppercase tracking-wider">Mục tiêu nghề nghiệp</span>
                        <p className="font-medium mt-0.5 text-zinc-800 dark:text-zinc-200">{profile.careerObjective || "N/A"}</p>
                      </div>
                    </div>
                  </div>

                  {/* SECTION 3: Work Experience */}
                  <div className="p-5 border border-zinc-100 dark:border-zinc-800/80 rounded-2xl space-y-4 relative group/sec">
                    <div className="flex items-center justify-between">
                      <h4 className="font-extrabold text-sm md:text-base text-zinc-800 dark:text-zinc-200 flex items-center gap-2">
                        <Briefcase className="h-4.5 w-4.5 text-primary" /> Kinh nghiệm làm việc
                      </h4>
                      <button
                        onClick={() => startEditingSection("work_experience")}
                        className="py-1.5 px-3 rounded-xl border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-900 text-xs font-bold transition duration-200 cursor-pointer"
                      >
                        {profile.workExperience?.length > 0 ? "Chỉnh sửa" : "+ Thêm kinh nghiệm"}
                      </button>
                    </div>

                    <div className="space-y-4">
                      {!profile.workExperience || profile.workExperience.length === 0 ? (
                        <div className="p-6 text-center border border-dashed border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50/50 dark:bg-zinc-900/10">
                          <p className="text-sm font-bold text-zinc-500">Chưa bổ sung thông tin kinh nghiệm làm việc</p>
                          <p className="text-xs text-muted-foreground mt-0.5">Bổ sung ngay để tăng 35% độ tin cậy của hồ sơ ứng viên</p>
                        </div>
                      ) : (
                        profile.workExperience.map((exp, idx) => (
                          <div key={idx} className="border-l-2 border-primary/20 pl-4 py-0.5 space-y-1 text-sm">
                            <h5 className="font-bold text-zinc-900 dark:text-white">{exp.title}</h5>
                            <p className="text-xs font-semibold text-muted-foreground">{exp.company} | {exp.startDate} - {exp.endDate || "Hiện tại"}</p>
                            <p className="text-xs leading-normal mt-1 opacity-90">{exp.description}</p>
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  {/* SECTION 4: Education */}
                  <div className="p-5 border border-zinc-100 dark:border-zinc-800/80 rounded-2xl space-y-4 relative group/sec">
                    <div className="flex items-center justify-between">
                      <h4 className="font-extrabold text-sm md:text-base text-zinc-800 dark:text-zinc-200 flex items-center gap-2">
                        <GraduationCap className="h-4.5 w-4.5 text-primary" /> Học vấn & Đào tạo
                      </h4>
                      <button
                        onClick={() => startEditingSection("education")}
                        className="py-1.5 px-3 rounded-xl border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-900 text-xs font-bold transition duration-200 cursor-pointer"
                      >
                        {profile.education?.length > 0 ? "Chỉnh sửa" : "+ Thêm học vấn"}
                      </button>
                    </div>

                    <div className="space-y-4">
                      {!profile.education || profile.education.length === 0 ? (
                        <div className="p-6 text-center border border-dashed border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50/50 dark:bg-zinc-900/10">
                          <p className="text-sm font-bold text-zinc-500">Chưa bổ sung thông tin học vấn đào tạo</p>
                          <p className="text-xs text-muted-foreground mt-0.5">Bổ sung học vị, chứng chỉ học tập để nâng cao trình độ</p>
                        </div>
                      ) : (
                        profile.education.map((edu, idx) => (
                          <div key={idx} className="border-l-2 border-primary/20 pl-4 py-0.5 space-y-1 text-sm">
                            <h5 className="font-bold text-zinc-900 dark:text-white">{edu.degree}</h5>
                            <p className="text-xs font-semibold text-muted-foreground">{edu.institution} | Tốt nghiệp: {edu.graduationDate || "N/A"}</p>
                            {edu.gpa && <p className="text-xs font-medium mt-1">GPA: {edu.gpa}</p>}
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  {/* SECTION 5: Technical Skills */}
                  <div className="p-5 border border-zinc-100 dark:border-zinc-800/80 rounded-2xl space-y-4 relative group/sec">
                    <div className="flex items-center justify-between">
                      <h4 className="font-extrabold text-sm md:text-base text-zinc-800 dark:text-zinc-200 flex items-center gap-2">
                        <Wrench className="h-4.5 w-4.5 text-primary" /> Kỹ năng chuyên môn
                      </h4>
                      <button
                        onClick={() => startEditingSection("technical_skills")}
                        className="py-1.5 px-3 rounded-xl border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-900 text-xs font-bold transition duration-200 cursor-pointer"
                      >
                        {profile.technicalSkills?.length > 0 ? "Chỉnh sửa" : "+ Thêm kỹ năng"}
                      </button>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      {!profile.technicalSkills || profile.technicalSkills.length === 0 ? (
                        <div className="p-6 w-full text-center border border-dashed border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50/50 dark:bg-zinc-900/10">
                          <p className="text-sm font-bold text-zinc-500">Chưa bổ sung thông tin kỹ năng chuyên môn</p>
                          <p className="text-xs text-muted-foreground mt-0.5">Bổ sung tối thiểu 5 kỹ năng chính mà bạn thông thạo nhất</p>
                        </div>
                      ) : (
                        profile.technicalSkills.map((s, idx) => (
                          <span key={idx} className="py-1 px-3 bg-zinc-100 dark:bg-zinc-850 rounded-xl text-xs font-bold text-zinc-800 dark:text-zinc-200">
                            {s.name} ({s.proficiency})
                          </span>
                        ))
                      )}
                    </div>
                  </div>

                  {/* SECTION 6: Certifications */}
                  <div className="p-5 border border-zinc-100 dark:border-zinc-800/80 rounded-2xl space-y-4 relative group/sec">
                    <div className="flex items-center justify-between">
                      <h4 className="font-extrabold text-sm md:text-base text-zinc-800 dark:text-zinc-200 flex items-center gap-2">
                        <Shield className="h-4.5 w-4.5 text-primary" /> Chứng chỉ chuyên môn
                      </h4>
                      <button
                        onClick={() => startEditingSection("certifications")}
                        className="py-1.5 px-3 rounded-xl border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-900 text-xs font-bold transition duration-200 cursor-pointer"
                      >
                        {profile.certifications?.length > 0 ? "Chỉnh sửa" : "+ Thêm chứng chỉ"}
                      </button>
                    </div>

                    <div className="space-y-4">
                      {!profile.certifications || profile.certifications.length === 0 ? (
                        <div className="p-6 text-center border border-dashed border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50/50 dark:bg-zinc-900/10">
                          <p className="text-sm font-bold text-zinc-500">Chưa bổ sung thông tin chứng chỉ chuyên môn</p>
                          <p className="text-xs text-muted-foreground mt-0.5">Thêm chứng chỉ quốc tế (AWS, Cisco, IELTS,...) nếu có</p>
                        </div>
                      ) : (
                        profile.certifications.map((c, idx) => (
                          <div key={idx} className="border-l-2 border-primary/20 pl-4 py-0.5 space-y-1 text-sm">
                            <h5 className="font-bold text-zinc-900 dark:text-white">{c.name}</h5>
                            <p className="text-xs font-semibold text-muted-foreground">Cung cấp bởi: {c.issuer} {c.issueDate ? `| Ngày cấp: ${c.issueDate}` : ""}</p>
                            {c.verificationUrl && <a href={c.verificationUrl} target="_blank" rel="noreferrer" className="text-xs text-primary font-bold hover:underline">Liên kết xác minh</a>}
                          </div>
                        ))
                      )}
                    </div>
                  </div>

                  {/* SECTION 7: Projects */}
                  <div className="p-5 border border-zinc-100 dark:border-zinc-800/80 rounded-2xl space-y-4 relative group/sec">
                    <div className="flex items-center justify-between">
                      <h4 className="font-extrabold text-sm md:text-base text-zinc-800 dark:text-zinc-200 flex items-center gap-2">
                        <Save className="h-4.5 w-4.5 text-primary" /> Dự án thực tế
                      </h4>
                      <button
                        onClick={() => startEditingSection("projects")}
                        className="py-1.5 px-3 rounded-xl border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 dark:hover:bg-zinc-900 text-xs font-bold transition duration-200 cursor-pointer"
                      >
                        {profile.projects?.length > 0 ? "Chỉnh sửa" : "+ Thêm dự án"}
                      </button>
                    </div>

                    <div className="space-y-4">
                      {!profile.projects || profile.projects.length === 0 ? (
                        <div className="p-6 text-center border border-dashed border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50/50 dark:bg-zinc-900/10">
                          <p className="text-sm font-bold text-zinc-500">Chưa bổ sung thông tin dự án thực tế</p>
                          <p className="text-xs text-muted-foreground mt-0.5">Bổ sung các dự án cá nhân hoặc dự án lớn trong công việc để khẳng định năng lực</p>
                        </div>
                      ) : (
                        profile.projects.map((proj, idx) => (
                          <div key={idx} className="border-l-2 border-primary/20 pl-4 py-0.5 space-y-1 text-sm">
                            <h5 className="font-bold text-zinc-900 dark:text-white">{proj.name}</h5>
                            <p className="text-xs font-semibold text-muted-foreground">Thời gian: {proj.startDate || "N/A"} - {proj.endDate || "Hiện tại"}</p>
                            <p className="text-xs leading-normal mt-1 opacity-90">{proj.description}</p>
                            {proj.url && <a href={proj.url} target="_blank" rel="noreferrer" className="text-xs text-primary font-bold hover:underline">Liên kết dự án</a>}
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Inline Editor Form */}
          {activeTab === "profile" && editingSection && editFormData && (
            <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 sm:p-8 shadow-sm space-y-6 animate-fadeIn">
              <div className="flex justify-between items-center pb-3 border-b border-zinc-100 dark:border-zinc-800">
                <h3 className="font-extrabold text-lg md:text-xl text-zinc-900 dark:text-white uppercase tracking-wider">
                  Chỉnh sửa phần: {editingSection === "personal_info" ? "Thông tin liên hệ" :
                                    editingSection === "professional_summary" ? "Mục tiêu & Tóm tắt" :
                                    editingSection === "work_experience" ? "Kinh nghiệm làm việc" :
                                    editingSection === "education" ? "Học vấn đào tạo" : "Kỹ năng chuyên môn"}
                </h3>
                <button
                  onClick={() => { setEditingSection(null); setEditFormData(null); }}
                  className="h-8 w-8 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-955 flex items-center justify-center text-zinc-400 hover:text-zinc-900 dark:hover:text-white transition"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              {/* Form inputs routing */}
              <div className="space-y-4">
                {editingSection === "personal_info" && (
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-1">
                      <label className="text-xs font-semibold">Họ và tên</label>
                      <input
                        type="text"
                        value={(editFormData as RecordStringUnknown).full_name || ""}
                        onChange={e => setEditFormData({ ...(editFormData as RecordStringUnknown), full_name: e.target.value })}
                        className="w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-955 text-sm"
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-xs font-semibold">Email liên hệ</label>
                      <input
                        type="email"
                        value={(editFormData as RecordStringUnknown).email || ""}
                        onChange={e => setEditFormData({ ...(editFormData as RecordStringUnknown), email: e.target.value })}
                        className="w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-955 text-sm"
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-xs font-semibold">Số điện thoại</label>
                      <input
                        type="text"
                        value={(editFormData as RecordStringUnknown).phone || ""}
                        onChange={e => setEditFormData({ ...(editFormData as RecordStringUnknown), phone: e.target.value })}
                        className="w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-955 text-sm"
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-xs font-semibold">Địa chỉ sinh sống</label>
                      <input
                        type="text"
                        value={(editFormData as RecordStringUnknown).location || ""}
                        onChange={e => setEditFormData({ ...(editFormData as RecordStringUnknown), location: e.target.value })}
                        className="w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-955 text-sm"
                      />
                    </div>
                  </div>
                )}

                {editingSection === "professional_summary" && (
                  <div className="space-y-4">
                    <div className="space-y-1">
                      <label className="text-xs font-semibold">Tóm tắt tiểu sử chuyên môn</label>
                      <textarea
                        rows={4}
                        value={(editFormData as RecordStringUnknown).professional_summary || ""}
                        onChange={e => setEditFormData({ ...(editFormData as RecordStringUnknown), professional_summary: e.target.value })}
                        className="w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-955 text-sm"
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-xs font-semibold">Mục tiêu nghề nghiệp</label>
                      <textarea
                        rows={3}
                        value={(editFormData as RecordStringUnknown).career_objective || ""}
                        onChange={e => setEditFormData({ ...(editFormData as RecordStringUnknown), career_objective: e.target.value })}
                        className="w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-955 text-sm"
                      />
                    </div>
                  </div>
                )}

                {/* Array sections list editing: work experience */}
                {editingSection === "work_experience" && (
                  <div className="space-y-6">
                    <button
                      onClick={() => {
                        const list = [...(editFormData as RecordStringUnknown[])];
                        list.push({ title: "Chức danh", company: "Công ty", startDate: "2024", isCurrent: false, description: "Mô tả..." });
                        setEditFormData(list);
                      }}
                      className="inline-flex items-center gap-1 py-1.5 px-3 rounded-lg border border-primary/20 text-primary text-xs font-bold transition"
                    >
                      <Plus className="h-3.5 w-3.5" /> Thêm kinh nghiệm mới
                    </button>

                    <div className="space-y-4">
                      {(editFormData as RecordStringUnknown[]).map((exp: RecordStringUnknown, idx: number) => (
                        <div key={idx} className="p-4 border border-zinc-200 dark:border-zinc-800 rounded-2xl bg-zinc-50/20 dark:bg-zinc-900/30 relative space-y-3">
                          <button
                            onClick={() => {
                              const list = (editFormData as RecordStringUnknown[]).filter((_: unknown, i: number) => i !== idx);
                              setEditFormData(list);
                            }}
                            className="absolute top-4 right-4 h-8 w-8 text-zinc-400 hover:text-red-500 flex items-center justify-center"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                          
                          <div className="grid md:grid-cols-2 gap-4">
                            <div className="space-y-1">
                              <label className="text-xs font-semibold">Chức danh / Vị trí</label>
                              <input
                                type="text"
                                value={exp.title || ""}
                                onChange={e => {
                                  const list = [...(editFormData as RecordStringUnknown[])];
                                  list[idx].title = e.target.value;
                                  setEditFormData(list);
                                }}
                                className="w-full px-3 py-2 border rounded-xl bg-white dark:bg-zinc-950 text-xs"
                              />
                            </div>
                            <div className="space-y-1">
                              <label className="text-xs font-semibold">Tên công ty</label>
                              <input
                                type="text"
                                value={exp.company || ""}
                                onChange={e => {
                                  const list = [...(editFormData as RecordStringUnknown[])];
                                  list[idx].company = e.target.value;
                                  setEditFormData(list);
                                }}
                                className="w-full px-3 py-2 border rounded-xl bg-white dark:bg-zinc-950 text-xs"
                              />
                            </div>
                            <div className="space-y-1">
                              <label className="text-xs font-semibold">Năm bắt đầu</label>
                              <input
                                type="text"
                                value={exp.startDate || ""}
                                onChange={e => {
                                  const list = [...(editFormData as RecordStringUnknown[])];
                                  list[idx].startDate = e.target.value;
                                  setEditFormData(list);
                                }}
                                className="w-full px-3 py-2 border rounded-xl bg-white dark:bg-zinc-955 text-xs"
                              />
                            </div>
                            <div className="space-y-1">
                              <label className="text-xs font-semibold">Năm kết thúc</label>
                              <input
                                type="text"
                                value={exp.endDate || ""}
                                onChange={e => {
                                  const list = [...(editFormData as RecordStringUnknown[])];
                                  list[idx].endDate = e.target.value;
                                  setEditFormData(list);
                                }}
                                className="w-full px-3 py-2 border rounded-xl bg-white dark:bg-zinc-955 text-xs"
                              />
                            </div>
                            <div className="space-y-1 md:col-span-2">
                              <label className="text-xs font-semibold">Mô tả công việc</label>
                              <textarea
                                rows={3}
                                value={exp.description || ""}
                                onChange={e => {
                                  const list = [...(editFormData as RecordStringUnknown[])];
                                  list[idx].description = e.target.value;
                                  setEditFormData(list);
                                }}
                                className="w-full px-3 py-2 border rounded-xl bg-white dark:bg-zinc-955 text-xs"
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Array: education */}
                {editingSection === "education" && (
                  <div className="space-y-6">
                    <button
                      onClick={() => {
                        const list = [...(editFormData as RecordStringUnknown[])];
                        list.push({ degree: "Bằng cấp", institution: "Trường", graduationDate: "2026", honors: [] });
                        setEditFormData(list);
                      }}
                      className="inline-flex items-center gap-1 py-1.5 px-3 rounded-lg border border-primary/20 text-primary text-xs font-bold transition"
                    >
                      <Plus className="h-3.5 w-3.5" /> Thêm học vấn mới
                    </button>

                    <div className="space-y-4">
                      {(editFormData as RecordStringUnknown[]).map((edu: RecordStringUnknown, idx: number) => (
                        <div key={idx} className="p-4 border border-zinc-200 dark:border-zinc-800 rounded-2xl bg-zinc-50/20 dark:bg-zinc-900/30 relative space-y-3">
                          <button
                            onClick={() => {
                              const list = (editFormData as RecordStringUnknown[]).filter((_: unknown, i: number) => i !== idx);
                              setEditFormData(list);
                            }}
                            className="absolute top-4 right-4 h-8 w-8 text-zinc-400 hover:text-red-500 flex items-center justify-center"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                          
                          <div className="grid md:grid-cols-2 gap-4">
                            <div className="space-y-1">
                              <label className="text-xs font-semibold">Bằng cấp / Chứng chỉ</label>
                              <input
                                type="text"
                                value={edu.degree || ""}
                                onChange={e => {
                                  const list = [...(editFormData as RecordStringUnknown[])];
                                  list[idx].degree = e.target.value;
                                  setEditFormData(list);
                                }}
                                className="w-full px-3 py-2 border rounded-xl bg-white dark:bg-zinc-950 text-xs"
                              />
                            </div>
                            <div className="space-y-1">
                              <label className="text-xs font-semibold">Tên trường</label>
                              <input
                                type="text"
                                value={edu.institution || ""}
                                onChange={e => {
                                  const list = [...(editFormData as RecordStringUnknown[])];
                                  list[idx].institution = e.target.value;
                                  setEditFormData(list);
                                }}
                                className="w-full px-3 py-2 border rounded-xl bg-white dark:bg-zinc-955 text-xs"
                              />
                            </div>
                            <div className="space-y-1">
                              <label className="text-xs font-semibold">Năm tốt nghiệp</label>
                              <input
                                type="text"
                                value={edu.graduationDate || ""}
                                onChange={e => {
                                  const list = [...(editFormData as RecordStringUnknown[])];
                                  list[idx].graduationDate = e.target.value;
                                  setEditFormData(list);
                                }}
                                className="w-full px-3 py-2 border rounded-xl bg-white dark:bg-zinc-955 text-xs"
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Array: skills */}
                {editingSection === "technical_skills" && (
                  <div className="space-y-6">
                    <button
                      onClick={() => {
                        const list = [...(editFormData as RecordStringUnknown[])];
                        list.push({ name: "Kỹ năng", category: "Chung", proficiency: "Intermediate" });
                        setEditFormData(list);
                      }}
                      className="inline-flex items-center gap-1 py-1.5 px-3 rounded-lg border border-primary/20 text-primary text-xs font-bold transition"
                    >
                      <Plus className="h-3.5 w-3.5" /> Thêm kỹ năng mới
                    </button>

                    <div className="grid md:grid-cols-2 gap-4">
                      {(editFormData as RecordStringUnknown[]).map((skill: RecordStringUnknown, idx: number) => (
                        <div key={idx} className="p-3 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50/20 dark:bg-zinc-900/30 flex items-center gap-2">
                          <input
                            type="text"
                            value={skill.name || ""}
                            onChange={e => {
                              const list = [...(editFormData as RecordStringUnknown[])];
                              list[idx].name = e.target.value;
                              setEditFormData(list);
                            }}
                            className="flex-1 px-2.5 py-1.5 rounded-lg border bg-white dark:bg-zinc-950 text-xs font-bold"
                            placeholder="Tên kỹ năng"
                          />
                          <select
                            value={skill.proficiency || "Intermediate"}
                            onChange={e => {
                              const list = [...(editFormData as RecordStringUnknown[])];
                              list[idx].proficiency = e.target.value;
                              setEditFormData(list);
                            }}
                            className="px-2 py-1.5 rounded-lg border bg-white dark:bg-zinc-955 text-xs font-semibold"
                          >
                            <option value="Beginner">Cơ bản</option>
                            <option value="Intermediate">Trung bình</option>
                            <option value="Advanced">Nâng cao</option>
                            <option value="Expert">Chuyên gia</option>
                          </select>
                          <button
                            onClick={() => {
                              const list = (editFormData as RecordStringUnknown[]).filter((_: unknown, i: number) => i !== idx);
                              setEditFormData(list);
                            }}
                            className="h-8 w-8 text-zinc-400 hover:text-red-500 flex items-center justify-center shrink-0"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Array: certifications */}
                {editingSection === "certifications" && (
                  <div className="space-y-6">
                    <button
                      onClick={() => {
                        const list = [...(editFormData as RecordStringUnknown[])];
                        list.push({ name: "Chứng chỉ mới", issuer: "Tổ chức cấp", issueDate: "2024", expiryDate: "", credentialId: "", verificationUrl: "" });
                        setEditFormData(list);
                      }}
                      className="inline-flex items-center gap-1 py-1.5 px-3 rounded-lg border border-primary/20 text-primary text-xs font-bold transition duration-200 cursor-pointer"
                    >
                      <Plus className="h-3.5 w-3.5" /> Thêm chứng chỉ mới
                    </button>

                    <div className="space-y-4">
                      {(editFormData as RecordStringUnknown[]).map((c: RecordStringUnknown, idx: number) => (
                        <div key={idx} className="p-4 border border-zinc-200 dark:border-zinc-800 rounded-2xl bg-zinc-50/20 dark:bg-zinc-900/30 relative space-y-3">
                          <button
                            onClick={() => {
                              const list = (editFormData as RecordStringUnknown[]).filter((_: unknown, i: number) => i !== idx);
                              setEditFormData(list);
                            }}
                            className="absolute top-4 right-4 h-8 w-8 text-zinc-400 hover:text-red-500 flex items-center justify-center cursor-pointer"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                          
                          <div className="grid md:grid-cols-2 gap-4">
                            <div className="space-y-1">
                              <label className="text-xs font-semibold">Tên chứng chỉ</label>
                              <input
                                type="text"
                                value={c.name || ""}
                                onChange={e => {
                                  const list = [...(editFormData as RecordStringUnknown[])];
                                  list[idx].name = e.target.value;
                                  setEditFormData(list);
                                }}
                                className="w-full px-3 py-2 border rounded-xl bg-white dark:bg-zinc-955 text-xs"
                              />
                            </div>
                            <div className="space-y-1">
                              <label className="text-xs font-semibold">Tổ chức cấp</label>
                              <input
                                type="text"
                                value={c.issuer || ""}
                                onChange={e => {
                                  const list = [...(editFormData as RecordStringUnknown[])];
                                  list[idx].issuer = e.target.value;
                                  setEditFormData(list);
                                }}
                                className="w-full px-3 py-2 border rounded-xl bg-white dark:bg-zinc-955 text-xs"
                              />
                            </div>
                            <div className="space-y-1">
                              <label className="text-xs font-semibold">Ngày cấp</label>
                              <input
                                type="text"
                                value={c.issueDate || ""}
                                onChange={e => {
                                  const list = [...(editFormData as RecordStringUnknown[])];
                                  list[idx].issueDate = e.target.value;
                                  setEditFormData(list);
                                }}
                                className="w-full px-3 py-2 border rounded-xl bg-white dark:bg-zinc-955 text-xs"
                              />
                            </div>
                            <div className="space-y-1">
                              <label className="text-xs font-semibold">Liên kết xác minh</label>
                              <input
                                type="text"
                                value={c.verificationUrl || ""}
                                onChange={e => {
                                  const list = [...(editFormData as RecordStringUnknown[])];
                                  list[idx].verificationUrl = e.target.value;
                                  setEditFormData(list);
                                }}
                                className="w-full px-3 py-2 border rounded-xl bg-white dark:bg-zinc-955 text-xs"
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Array: projects */}
                {editingSection === "projects" && (
                  <div className="space-y-6">
                    <button
                      onClick={() => {
                        const list = [...(editFormData as RecordStringUnknown[])];
                        list.push({ name: "Dự án mới", description: "Mô tả dự án...", technologies: [], url: "", startDate: "2024", endDate: "" });
                        setEditFormData(list);
                      }}
                      className="inline-flex items-center gap-1 py-1.5 px-3 rounded-lg border border-primary/20 text-primary text-xs font-bold transition duration-200 cursor-pointer"
                    >
                      <Plus className="h-3.5 w-3.5" /> Thêm dự án mới
                    </button>

                    <div className="space-y-4">
                      {(editFormData as RecordStringUnknown[]).map((proj: RecordStringUnknown, idx: number) => (
                        <div key={idx} className="p-4 border border-zinc-200 dark:border-zinc-800 rounded-2xl bg-zinc-50/20 dark:bg-zinc-900/30 relative space-y-3">
                          <button
                            onClick={() => {
                              const list = (editFormData as RecordStringUnknown[]).filter((_: unknown, i: number) => i !== idx);
                              setEditFormData(list);
                            }}
                            className="absolute top-4 right-4 h-8 w-8 text-zinc-400 hover:text-red-500 flex items-center justify-center cursor-pointer"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                          
                          <div className="grid md:grid-cols-2 gap-4">
                            <div className="space-y-1">
                              <label className="text-xs font-semibold">Tên dự án</label>
                              <input
                                type="text"
                                value={proj.name || ""}
                                onChange={e => {
                                  const list = [...(editFormData as RecordStringUnknown[])];
                                  list[idx].name = e.target.value;
                                  setEditFormData(list);
                                }}
                                className="w-full px-3 py-2 border rounded-xl bg-white dark:bg-zinc-950 text-xs"
                              />
                            </div>
                            <div className="space-y-1">
                              <label className="text-xs font-semibold">Liên kết dự án</label>
                              <input
                                type="text"
                                value={proj.url || ""}
                                onChange={e => {
                                  const list = [...(editFormData as RecordStringUnknown[])];
                                  list[idx].url = e.target.value;
                                  setEditFormData(list);
                                }}
                                className="w-full px-3 py-2 border rounded-xl bg-white dark:bg-zinc-955 text-xs"
                              />
                            </div>
                            <div className="space-y-1">
                              <label className="text-xs font-semibold">Năm bắt đầu</label>
                              <input
                                type="text"
                                value={proj.startDate || ""}
                                onChange={e => {
                                  const list = [...(editFormData as RecordStringUnknown[])];
                                  list[idx].startDate = e.target.value;
                                  setEditFormData(list);
                                }}
                                className="w-full px-3 py-2 border rounded-xl bg-white dark:bg-zinc-955 text-xs"
                              />
                            </div>
                            <div className="space-y-1">
                              <label className="text-xs font-semibold">Năm kết thúc</label>
                              <input
                                type="text"
                                value={proj.endDate || ""}
                                onChange={e => {
                                  const list = [...(editFormData as RecordStringUnknown[])];
                                  list[idx].endDate = e.target.value;
                                  setEditFormData(list);
                                }}
                                className="w-full px-3 py-2 border rounded-xl bg-white dark:bg-zinc-955 text-xs"
                              />
                            </div>
                            <div className="space-y-1 md:col-span-2">
                              <label className="text-xs font-semibold">Mô tả dự án</label>
                              <textarea
                                rows={3}
                                value={proj.description || ""}
                                onChange={e => {
                                  const list = [...(editFormData as RecordStringUnknown[])];
                                  list[idx].description = e.target.value;
                                  setEditFormData(list);
                                }}
                                className="w-full px-3 py-2 border rounded-xl bg-white dark:bg-zinc-955 text-xs"
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Editor action buttons */}
              <div className="pt-4 border-t border-zinc-100 dark:border-zinc-800 flex items-center gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => { setEditingSection(null); setEditFormData(null); }}
                  className="px-4 py-2 rounded-xl border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-50 text-sm font-bold text-zinc-700 dark:text-zinc-300 transition"
                >
                  Hủy bỏ
                </button>
                <button
                  type="button"
                  onClick={saveProfileSection}
                  className="px-5 py-2.5 rounded-xl bg-primary text-white hover:bg-primary/95 text-sm font-black shadow-md transition"
                >
                  Lưu thay đổi
                </button>
              </div>
            </div>
          )}

        </div>

      </main>
      
    </div>
  );
}

// Simple internal logger helper to bypass global linter issues
