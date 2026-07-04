"use client";

import React, { useEffect, useState } from "react";

interface MatchScoreDialProps {
  score: number;
}

export const MatchScoreDial: React.FC<MatchScoreDialProps> = ({ score }) => {
  const [offset, setOffset] = useState(251.2); // Circumference for r=40
  const circumference = 251.2;

  useEffect(() => {
    // Animate the progress bar
    const progressOffset = circumference - (score / 100) * circumference;
    const timer = setTimeout(() => {
      setOffset(progressOffset);
    }, 100);
    return () => clearTimeout(timer);
  }, [score]);

  // Color selection
  const getColor = (val: number) => {
    if (val < 40) return "stroke-red-500 text-red-600";
    if (val < 70) return "stroke-amber-500 text-amber-600";
    return "stroke-emerald-500 text-emerald-600";
  };

  const getBgColor = (val: number) => {
    if (val < 40) return "bg-red-50 text-red-700 border-red-100";
    if (val < 70) return "bg-amber-50 text-amber-700 border-amber-100";
    return "bg-emerald-50 text-emerald-700 border-emerald-100";
  };

  const statusText = (val: number) => {
    if (val < 40) return "Cần bổ sung nhiều";
    if (val < 70) return "Khá phù hợp";
    return "Rất phù hợp";
  };

  return (
    <div className="flex flex-col items-center justify-center p-6 bg-white border border-gray-100 rounded-2xl shadow-sm">
      <div className="relative flex items-center justify-center w-36 h-36">
        <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
          {/* Background circle */}
          <circle
            className="stroke-gray-100"
            strokeWidth="8"
            fill="transparent"
            r="40"
            cx="50"
            cy="50"
          />
          {/* Progress circle */}
          <circle
            className={`transition-all duration-1000 ease-out ${getColor(score).split(" ")[0]}`}
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            fill="transparent"
            r="40"
            cx="50"
            cy="50"
          />
        </svg>
        <div className="absolute flex flex-col items-center justify-center">
          <span className="text-3xl font-bold text-gray-900">{score}%</span>
          <span className="text-xs text-gray-400 font-semibold tracking-wider uppercase">Match Score</span>
        </div>
      </div>
      <div className={`mt-4 px-4 py-1.5 rounded-full text-xs font-bold border ${getBgColor(score)}`}>
        {statusText(score)}
      </div>
    </div>
  );
};
