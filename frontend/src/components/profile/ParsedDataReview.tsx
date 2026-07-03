"use client";

import React, { useState } from "react";
import { 
  Check, 
  X, 
  AlertTriangle, 
  Plus, 
  Trash2, 
  Briefcase, 
  GraduationCap, 
  Wrench, 
  Award,
  User 
} from "lucide-react";
import { ResumeAnalysis } from "@/lib/services/analysis";
import { ConfidenceIndicator } from "./ConfidenceIndicator";

interface ParsedDataReviewProps {
  analysis: ResumeAnalysis;
  onApprove: (corrections: Record<string, any>) => void;
  onCancel: () => void;
}

export const ParsedDataReview: React.FC<ParsedDataReviewProps> = ({
  analysis,
  onApprove,
  onCancel,
}) => {
  const [editedData, setEditedData] = useState<any>(JSON.parse(JSON.stringify(analysis.parsedData || {})));
  const [corrections, setCorrections] = useState<Record<string, any>>({});
  const [activeTab, setActiveTab] = useState<"personal" | "experience" | "education" | "skills" | "certs">("personal");

  const updateField = (path: string, value: any) => {
    // Update local edited state
    const newData = { ...editedData };
    const parts = path.split(".");
    let curr = newData;
    for (let i = 0; i < parts.length - 1; i++) {
      const part = parts[i];
      if (part.match(/^\d+$/)) {
        curr = curr[parseInt(part)];
      } else {
        curr = curr[part];
      }
    }
    
    const last = parts[parts.length - 1];
    if (last.match(/^\d+$/)) {
      curr[parseInt(last)] = value;
    } else {
      curr[last] = value;
    }
    
    setEditedData(newData);

    // Track correction path
    setCorrections(prev => ({
      ...prev,
      [path]: value
    }));
  };

  const handleSave = () => {
    onApprove(corrections);
  };

  const addExperience = () => {
    const newExp = {
      title: "Chức danh công việc",
      company: "Tên công ty",
      location: "",
      start_date: "2024",
      end_date: "",
      is_current: false,
      description: "Mô tả công việc...",
      key_achievements: [],
      technologies_used: []
    };
    const list = [...(editedData.work_experience || [])];
    list.push(newExp);
    updateField("work_experience", list);
  };

  const removeExperience = (idx: number) => {
    const list = (editedData.work_experience || []).filter((_: any, i: number) => i !== idx);
    updateField("work_experience", list);
  };

  const addEducation = () => {
    const newEdu = {
      degree: "Bằng cấp/Khóa học",
      field_of_study: "Ngành học",
      institution: "Tên trường",
      location: "",
      graduation_date: "2026",
      gpa: ""
    };
    const list = [...(editedData.education || [])];
    list.push(newEdu);
    updateField("education", list);
  };

  const removeEducation = (idx: number) => {
    const list = (editedData.education || []).filter((_: any, i: number) => i !== idx);
    updateField("education", list);
  };

  const addSkill = () => {
    const newSkill = { name: "Kỹ năng mới", category: "Chung", proficiency: "Intermediate" };
    const list = [...(editedData.technical_skills || [])];
    list.push(newSkill);
    updateField("technical_skills", list);
  };

  const removeSkill = (idx: number) => {
    const list = (editedData.technical_skills || []).filter((_: any, i: number) => i !== idx);
    updateField("technical_skills", list);
  };

  const addCert = () => {
    const newCert = { name: "Chứng chỉ mới", issuer: "Tổ chức cấp", issue_date: "", credential_id: "" };
    const list = [...(editedData.certifications || [])];
    list.push(newCert);
    updateField("certifications", list);
  };

  const removeCert = (idx: number) => {
    const list = (editedData.certifications || []).filter((_: any, i: number) => i !== idx);
    updateField("certifications", list);
  };

  return (
    <div className="border border-zinc-200 dark:border-zinc-800 rounded-3xl bg-white dark:bg-zinc-900 shadow-sm overflow-hidden flex flex-col md:flex-row min-h-[600px]">
      
      {/* Sidebar Tabs */}
      <div className="w-full md:w-64 border-r border-zinc-100 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/40 p-4 shrink-0 flex flex-row md:flex-col gap-1.5 overflow-x-auto md:overflow-x-visible">
        <button
          onClick={() => setActiveTab("personal")}
          className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition shrink-0 w-max md:w-full ${
            activeTab === "personal"
              ? "bg-primary text-white"
              : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/80"
          }`}
        >
          <User className="h-4 w-4" /> Thông tin cá nhân
        </button>
        <button
          onClick={() => setActiveTab("experience")}
          className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition shrink-0 w-max md:w-full ${
            activeTab === "experience"
              ? "bg-primary text-white"
              : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/80"
          }`}
        >
          <Briefcase className="h-4 w-4" /> Kinh nghiệm làm việc
        </button>
        <button
          onClick={() => setActiveTab("education")}
          className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition shrink-0 w-max md:w-full ${
            activeTab === "education"
              ? "bg-primary text-white"
              : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/80"
          }`}
        >
          <GraduationCap className="h-4 w-4" /> Học vấn học thuật
        </button>
        <button
          onClick={() => setActiveTab("skills")}
          className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition shrink-0 w-max md:w-full ${
            activeTab === "skills"
              ? "bg-primary text-white"
              : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/80"
          }`}
        >
          <Wrench className="h-4 w-4" /> Kỹ năng chuyên môn
        </button>
        <button
          onClick={() => setActiveTab("certs")}
          className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-bold transition shrink-0 w-max md:w-full ${
            activeTab === "certs"
              ? "bg-primary text-white"
              : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-100 dark:hover:bg-zinc-800/80"
          }`}
        >
          <Award className="h-4 w-4" /> Chứng chỉ & Khác
        </button>

        <div className="hidden md:block mt-auto pt-6 border-t border-zinc-200/80 dark:border-zinc-800">
          <ConfidenceIndicator score={analysis.confidenceScore || 0} />
        </div>
      </div>

      {/* Main Review Area */}
      <div className="flex-1 flex flex-col justify-between min-w-0">
        <div className="p-6 md:p-8 space-y-6 overflow-y-auto max-h-[500px]">
          
          {/* TAB: Personal Info */}
          {activeTab === "personal" && (
            <div className="space-y-4">
              <h3 className="font-extrabold text-base md:text-lg text-zinc-900 dark:text-white pb-3 border-b border-zinc-100 dark:border-zinc-800 flex items-center gap-2">
                <User className="h-5 w-5 text-primary" /> Thông tin cá nhân trích xuất
              </h3>
              
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-black uppercase text-zinc-400 dark:text-zinc-500 tracking-wider">Họ và tên</label>
                  <input
                    type="text"
                    value={editedData.personal_info?.full_name || ""}
                    onChange={e => updateField("personal_info.full_name", e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-sm focus:border-primary focus:ring-1 focus:ring-primary/20 transition"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-black uppercase text-zinc-400 dark:text-zinc-500 tracking-wider">Email liên hệ</label>
                  <input
                    type="email"
                    value={editedData.personal_info?.email || ""}
                    onChange={e => updateField("personal_info.email", e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-sm focus:border-primary focus:ring-1 focus:ring-primary/20 transition"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-black uppercase text-zinc-400 dark:text-zinc-500 tracking-wider">Số điện thoại</label>
                  <input
                    type="text"
                    value={editedData.personal_info?.phone || ""}
                    onChange={e => updateField("personal_info.phone", e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-sm focus:border-primary focus:ring-1 focus:ring-primary/20 transition"
                  />
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-black uppercase text-zinc-400 dark:text-zinc-500 tracking-wider">Địa chỉ sinh sống</label>
                  <input
                    type="text"
                    value={editedData.personal_info?.location || ""}
                    onChange={e => updateField("personal_info.location", e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-sm focus:border-primary focus:ring-1 focus:ring-primary/20 transition"
                  />
                </div>

                <div className="space-y-1 md:col-span-2">
                  <label className="text-xs font-black uppercase text-zinc-400 dark:text-zinc-500 tracking-wider">Tóm tắt tiểu sử chuyên môn</label>
                  <textarea
                    rows={4}
                    value={editedData.professional_summary || ""}
                    onChange={e => updateField("professional_summary", e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-sm focus:border-primary focus:ring-1 focus:ring-primary/20 transition"
                  />
                </div>
              </div>
            </div>
          )}

          {/* TAB: Experience */}
          {activeTab === "experience" && (
            <div className="space-y-6">
              <div className="flex justify-between items-center pb-3 border-b border-zinc-100 dark:border-zinc-800">
                <h3 className="font-extrabold text-base md:text-lg text-zinc-900 dark:text-white flex items-center gap-2">
                  <Briefcase className="h-5 w-5 text-primary" /> Kinh nghiệm làm việc trích xuất
                </h3>
                <button
                  onClick={addExperience}
                  className="inline-flex items-center gap-1 py-1.5 px-3 rounded-lg border border-primary/20 text-primary hover:bg-primary/5 text-xs font-bold transition"
                >
                  <Plus className="h-3.5 w-3.5" /> Thêm mới
                </button>
              </div>

              <div className="space-y-4">
                {(editedData.work_experience || []).map((exp: any, idx: number) => (
                  <div key={idx} className="p-4 border border-zinc-200 dark:border-zinc-800 rounded-2xl bg-zinc-50/20 dark:bg-zinc-900/30 space-y-4 relative group">
                    <button
                      onClick={() => removeExperience(idx)}
                      className="absolute top-4 right-4 h-8 w-8 rounded-lg text-zinc-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 flex items-center justify-center transition"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="text-[10px] font-black uppercase text-zinc-400 tracking-wider">Chức danh / Vị trí</label>
                        <input
                          type="text"
                          value={exp.title || ""}
                          onChange={e => updateField(`work_experience.${idx}.title`, e.target.value)}
                          className="w-full px-3 py-2 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-xs focus:border-primary transition"
                        />
                      </div>
                      
                      <div className="space-y-1">
                        <label className="text-[10px] font-black uppercase text-zinc-400 tracking-wider">Tên công ty</label>
                        <input
                          type="text"
                          value={exp.company || ""}
                          onChange={e => updateField(`work_experience.${idx}.company`, e.target.value)}
                          className="w-full px-3 py-2 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-xs focus:border-primary transition"
                        />
                      </div>

                      <div className="space-y-1">
                        <label className="text-[10px] font-black uppercase text-zinc-400 tracking-wider">Thời gian bắt đầu</label>
                        <input
                          type="text"
                          value={exp.start_date || ""}
                          onChange={e => updateField(`work_experience.${idx}.start_date`, e.target.value)}
                          className="w-full px-3 py-2 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-xs focus:border-primary transition"
                        />
                      </div>

                      <div className="space-y-1">
                        <label className="text-[10px] font-black uppercase text-zinc-400 tracking-wider">Thời gian kết thúc</label>
                        <input
                          type="text"
                          value={exp.end_date || ""}
                          onChange={e => updateField(`work_experience.${idx}.end_date`, e.target.value)}
                          className="w-full px-3 py-2 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-xs focus:border-primary transition"
                        />
                      </div>

                      <div className="space-y-1 md:col-span-2">
                        <label className="text-[10px] font-black uppercase text-zinc-400 tracking-wider">Mô tả chi tiết và thành tựu</label>
                        <textarea
                          rows={3}
                          value={exp.description || ""}
                          onChange={e => updateField(`work_experience.${idx}.description`, e.target.value)}
                          className="w-full px-3 py-2 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-xs focus:border-primary transition"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB: Education */}
          {activeTab === "education" && (
            <div className="space-y-6">
              <div className="flex justify-between items-center pb-3 border-b border-zinc-100 dark:border-zinc-800">
                <h3 className="font-extrabold text-base md:text-lg text-zinc-900 dark:text-white flex items-center gap-2">
                  <GraduationCap className="h-5 w-5 text-primary" /> Học vấn trích xuất
                </h3>
                <button
                  onClick={addEducation}
                  className="inline-flex items-center gap-1 py-1.5 px-3 rounded-lg border border-primary/20 text-primary hover:bg-primary/5 text-xs font-bold transition"
                >
                  <Plus className="h-3.5 w-3.5" /> Thêm mới
                </button>
              </div>

              <div className="space-y-4">
                {(editedData.education || []).map((edu: any, idx: number) => (
                  <div key={idx} className="p-4 border border-zinc-200 dark:border-zinc-800 rounded-2xl bg-zinc-50/20 dark:bg-zinc-900/30 space-y-4 relative group">
                    <button
                      onClick={() => removeEducation(idx)}
                      className="absolute top-4 right-4 h-8 w-8 rounded-lg text-zinc-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 flex items-center justify-center transition"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="text-[10px] font-black uppercase text-zinc-400 tracking-wider">Trường học</label>
                        <input
                          type="text"
                          value={edu.institution || ""}
                          onChange={e => updateField(`education.${idx}.institution`, e.target.value)}
                          className="w-full px-3 py-2 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-xs focus:border-primary transition"
                        />
                      </div>
                      
                      <div className="space-y-1">
                        <label className="text-[10px] font-black uppercase text-zinc-400 tracking-wider">Bằng cấp</label>
                        <input
                          type="text"
                          value={edu.degree || ""}
                          onChange={e => updateField(`education.${idx}.degree`, e.target.value)}
                          className="w-full px-3 py-2 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-xs focus:border-primary transition"
                        />
                      </div>

                      <div className="space-y-1">
                        <label className="text-[10px] font-black uppercase text-zinc-400 tracking-wider">Chuyên ngành</label>
                        <input
                          type="text"
                          value={edu.field_of_study || ""}
                          onChange={e => updateField(`education.${idx}.field_of_study`, e.target.value)}
                          className="w-full px-3 py-2 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-xs focus:border-primary transition"
                        />
                      </div>

                      <div className="space-y-1">
                        <label className="text-[10px] font-black uppercase text-zinc-400 tracking-wider">Năm tốt nghiệp</label>
                        <input
                          type="text"
                          value={edu.graduation_date || ""}
                          onChange={e => updateField(`education.${idx}.graduation_date`, e.target.value)}
                          className="w-full px-3 py-2 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-xs focus:border-primary transition"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB: Skills */}
          {activeTab === "skills" && (
            <div className="space-y-6">
              <div className="flex justify-between items-center pb-3 border-b border-zinc-100 dark:border-zinc-800">
                <h3 className="font-extrabold text-base md:text-lg text-zinc-900 dark:text-white flex items-center gap-2">
                  <Wrench className="h-5 w-5 text-primary" /> Kỹ năng chuyên môn trích xuất
                </h3>
                <button
                  onClick={addSkill}
                  className="inline-flex items-center gap-1 py-1.5 px-3 rounded-lg border border-primary/20 text-primary hover:bg-primary/5 text-xs font-bold transition"
                >
                  <Plus className="h-3.5 w-3.5" /> Thêm mới
                </button>
              </div>

              <div className="grid md:grid-cols-2 gap-3.5">
                {(editedData.technical_skills || []).map((skill: any, idx: number) => (
                  <div key={idx} className="p-3 border border-zinc-200 dark:border-zinc-800 rounded-xl bg-zinc-50/20 dark:bg-zinc-900/30 flex items-center gap-3 relative group">
                    <div className="flex-1 min-w-0 grid grid-cols-2 gap-2">
                      <input
                        type="text"
                        value={skill.name || ""}
                        onChange={e => {
                          const list = [...editedData.technical_skills];
                          list[idx].name = e.target.value;
                          updateField("technical_skills", list);
                        }}
                        className="px-2.5 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-xs"
                        placeholder="Tên kỹ năng"
                      />
                      <select
                        value={skill.proficiency || "Intermediate"}
                        onChange={e => {
                          const list = [...editedData.technical_skills];
                          list[idx].proficiency = e.target.value;
                          updateField("technical_skills", list);
                        }}
                        className="px-2 py-1.5 rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-xs"
                      >
                        <option value="Beginner">Cơ bản</option>
                        <option value="Intermediate">Trung bình</option>
                        <option value="Advanced">Nâng cao</option>
                        <option value="Expert">Chuyên gia</option>
                      </select>
                    </div>

                    <button
                      onClick={() => removeSkill(idx)}
                      className="h-8 w-8 rounded-lg text-zinc-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 flex items-center justify-center transition shrink-0"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB: Certifications */}
          {activeTab === "certs" && (
            <div className="space-y-6">
              <div className="flex justify-between items-center pb-3 border-b border-zinc-100 dark:border-zinc-800">
                <h3 className="font-extrabold text-base md:text-lg text-zinc-900 dark:text-white flex items-center gap-2">
                  <Award className="h-5 w-5 text-primary" /> Chứng chỉ và thành tựu trích xuất
                </h3>
                <button
                  onClick={addCert}
                  className="inline-flex items-center gap-1 py-1.5 px-3 rounded-lg border border-primary/20 text-primary hover:bg-primary/5 text-xs font-bold transition"
                >
                  <Plus className="h-3.5 w-3.5" /> Thêm mới
                </button>
              </div>

              <div className="space-y-4">
                {(editedData.certifications || []).map((cert: any, idx: number) => (
                  <div key={idx} className="p-4 border border-zinc-200 dark:border-zinc-800 rounded-2xl bg-zinc-50/20 dark:bg-zinc-900/30 space-y-4 relative group">
                    <button
                      onClick={() => removeCert(idx)}
                      className="absolute top-4 right-4 h-8 w-8 rounded-lg text-zinc-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/20 flex items-center justify-center transition"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="space-y-1">
                        <label className="text-[10px] font-black uppercase text-zinc-400 tracking-wider">Tên chứng chỉ</label>
                        <input
                          type="text"
                          value={cert.name || ""}
                          onChange={e => updateField(`certifications.${idx}.name`, e.target.value)}
                          className="w-full px-3 py-2 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-xs focus:border-primary transition"
                        />
                      </div>
                      
                      <div className="space-y-1">
                        <label className="text-[10px] font-black uppercase text-zinc-400 tracking-wider">Tổ chức cấp</label>
                        <input
                          type="text"
                          value={cert.issuer || ""}
                          onChange={e => updateField(`certifications.${idx}.issuer`, e.target.value)}
                          className="w-full px-3 py-2 rounded-xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-950 font-bold text-xs focus:border-primary transition"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

        {/* Action Panel Footer */}
        <div className="p-6 border-t border-zinc-100 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-900/20 flex flex-col md:flex-row items-center justify-between gap-4">
          <span className="text-xs text-muted-foreground font-medium flex items-center gap-1.5">
            <AlertTriangle className="h-3.5 w-3.5 text-amber-500" />
            Vui lòng rà soát kỹ lưỡng trước khi lưu kết quả vào hồ sơ ứng viên của bạn.
          </span>
          
          <div className="flex items-center gap-2.5 w-full md:w-auto">
            <button
              onClick={onCancel}
              className="flex-1 md:flex-none inline-flex justify-center items-center gap-1.5 px-4.5 py-2.5 rounded-xl border border-zinc-200 dark:border-zinc-800 hover:bg-zinc-100 dark:hover:bg-zinc-800 text-sm font-bold text-zinc-700 dark:text-zinc-300 transition"
            >
              <X className="h-4 w-4" /> Hủy bỏ
            </button>
            <button
              onClick={handleSave}
              className="flex-1 md:flex-none inline-flex justify-center items-center gap-1.5 px-6 py-2.5 rounded-xl bg-primary text-white hover:bg-primary/95 text-sm font-black shadow-md shadow-primary/10 transition"
            >
              <Check className="h-4 w-4" /> Đồng bộ & Lưu hồ sơ
            </button>
          </div>
        </div>

      </div>

    </div>
  );
};
