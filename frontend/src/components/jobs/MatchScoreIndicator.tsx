"use client";

import React from "react";

interface MatchScoreIndicatorProps {
  score: number;
  size?: "sm" | "md" | "lg";
  showLabel?: boolean;
}

// Color coding: <60 red, 60-80 amber, >80 green.
export const scoreColor = (score: number): string => {
  if (score >= 80) return "#16a34a"; // green-600
  if (score >= 60) return "#d97706"; // amber-600
  return "#dc2626"; // red-600
};

const scoreLabel = (score: number): string => {
  if (score >= 80) return "Rất phù hợp";
  if (score >= 60) return "Phù hợp";
  return "Ít phù hợp";
};

const DIMENSIONS = {
  sm: { box: 56, stroke: 5, font: "text-sm" },
  md: { box: 88, stroke: 7, font: "text-xl" },
  lg: { box: 128, stroke: 9, font: "text-3xl" },
};

export const MatchScoreIndicator: React.FC<MatchScoreIndicatorProps> = ({
  score,
  size = "md",
  showLabel = true,
}) => {
  const dim = DIMENSIONS[size];
  const radius = (dim.box - dim.stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, score));
  const offset = circumference - (clamped / 100) * circumference;
  const color = scoreColor(clamped);

  return (
    <div className="flex flex-col items-center gap-1.5">
      <div className="relative" style={{ width: dim.box, height: dim.box }}>
        <svg width={dim.box} height={dim.box} className="-rotate-90">
          <circle
            cx={dim.box / 2}
            cy={dim.box / 2}
            r={radius}
            fill="none"
            stroke="currentColor"
            strokeWidth={dim.stroke}
            className="text-zinc-200 dark:text-zinc-800"
          />
          <circle
            cx={dim.box / 2}
            cy={dim.box / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={dim.stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: "stroke-dashoffset 0.6s ease" }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`font-extrabold ${dim.font}`} style={{ color }}>
            {Math.round(clamped)}
          </span>
        </div>
      </div>
      {showLabel && (
        <span className="text-[11px] font-bold uppercase tracking-wider" style={{ color }}>
          {scoreLabel(clamped)}
        </span>
      )}
    </div>
  );
};

export default MatchScoreIndicator;
