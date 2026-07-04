"use client";

import React, { useState } from "react";
import { CheckCircle2, AlertCircle, HelpCircle, XCircle, ChevronDown, ChevronUp, AlertTriangle } from "lucide-react";
import { RequirementMatchResult } from "@/lib/services/matching";

interface RequirementMatrixViewProps {
  matrix: RequirementMatchResult[];
}

export const RequirementMatrixView: React.FC<RequirementMatrixViewProps> = ({ matrix }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const toggleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "SATISFIED":
        return <CheckCircle2 className="text-emerald-500 w-5 h-5 shrink-0" />;
      case "PARTIAL":
        return <AlertTriangle className="text-amber-500 w-5 h-5 shrink-0" />;
      case "CLARIFICATION":
        return <HelpCircle className="text-blue-500 w-5 h-5 shrink-0" />;
      case "MISSING":
        return <XCircle className="text-rose-500 w-5 h-5 shrink-0" />;
      default:
        return <HelpCircle className="text-gray-400 w-5 h-5 shrink-0" />;
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case "SATISFIED":
        return "bg-emerald-50 text-emerald-700 border-emerald-100";
      case "PARTIAL":
        return "bg-amber-50 text-amber-700 border-amber-100";
      case "CLARIFICATION":
        return "bg-blue-50 text-blue-700 border-blue-100";
      case "MISSING":
        return "bg-rose-50 text-rose-700 border-rose-100";
      default:
        return "bg-gray-50 text-gray-700 border-gray-100";
    }
  };

  const getPriorityBadgeClass = (level: string) => {
    switch (level) {
      case "CRITICAL":
        return "bg-red-50 text-red-800 border-red-200";
      case "HIGH":
        return "bg-orange-50 text-orange-800 border-orange-200";
      case "MEDIUM":
        return "bg-amber-50 text-amber-800 border-amber-100";
      case "LOW":
        return "bg-blue-50 text-blue-800 border-blue-200";
      default:
        return "bg-gray-50 text-gray-800 border-gray-200";
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      <div className="p-5 border-b border-gray-50 bg-gray-50/50">
        <h3 className="font-bold text-gray-900 text-lg">Ma trận So khớp Yêu cầu (Requirement Matrix)</h3>
        <p className="text-sm text-gray-500 font-medium">Chi tiết đánh giá mức độ đáp ứng từng yêu cầu tuyển dụng của JD đối với CV</p>
      </div>

      <div className="divide-y divide-gray-100">
        {matrix.map((item, index) => {
          const isExpanded = expandedIndex === index;
          return (
            <div key={item.requirement_id || index} className="transition-all hover:bg-gray-50/30">
              {/* Accordion Header */}
              <button
                onClick={() => toggleExpand(index)}
                className="w-full p-5 flex items-center justify-between gap-4 text-left cursor-pointer focus:outline-none"
              >
                <div className="flex items-center gap-3 min-w-0">
                  {getStatusIcon(item.status)}
                  <div>
                    <span className="font-semibold text-gray-900 text-sm md:text-base leading-snug line-clamp-1">{item.requirement}</span>
                    <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                      <span className={`px-2 py-0.5 rounded-full text-xxs font-bold border ${getPriorityBadgeClass(item.priority.level)}`}>
                        {item.priority.level}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-xxs font-bold border ${getStatusBadgeClass(item.status)}`}>
                        {item.status}
                      </span>
                      <span className="text-xxs text-gray-400 font-medium">Confidence: {item.confidence * 100}%</span>
                    </div>
                  </div>
                </div>
                <div>
                  {isExpanded ? <ChevronUp className="text-gray-400 w-5 h-5" /> : <ChevronDown className="text-gray-400 w-5 h-5" />}
                </div>
              </button>

              {/* Accordion Content */}
              {isExpanded && (
                <div className="px-5 pb-5 pt-1 bg-gray-50/50 border-t border-gray-50/50 space-y-4 text-sm animate-fade-in">
                  <div>
                    <h4 className="font-bold text-gray-800 text-xs mb-1.5 uppercase tracking-wider">Lý giải chi tiết</h4>
                    <ul className="list-disc pl-4 space-y-1 text-gray-600">
                      {item.reasoning.map((reason, rIdx) => (
                        <li key={rIdx}>{reason}</li>
                      ))}
                    </ul>
                  </div>

                  {item.evidence && item.evidence.length > 0 && (
                    <div>
                      <h4 className="font-bold text-gray-800 text-xs mb-2 uppercase tracking-wider">Bằng chứng từ CV (Evidence)</h4>
                      <div className="space-y-2">
                        {item.evidence.map((ev, evIdx) => (
                          <div key={evIdx} className="bg-white p-3 rounded-lg border border-gray-100 shadow-xxs">
                            <span className="inline-block text-[10px] font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2 py-0.5 rounded mb-1.5">
                              Mục: {ev.section}
                            </span>
                            <p className="text-gray-700 italic text-xs leading-relaxed">"{ev.text}"</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="flex flex-wrap gap-x-6 gap-y-2 pt-3 border-t border-gray-100 text-xs text-gray-500 font-medium">
                    <div>Kỹ năng đối ứng: <span className="font-bold text-gray-800">{item.matched_skill}</span></div>
                    <div>Phương thức match: <span className="font-bold text-gray-800 capitalize">{item.matching_method}</span></div>
                    <div>Đóng góp tổng thể: <span className="font-bold text-gray-800">{(item.contribution * 100).toFixed(0)}%</span></div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
