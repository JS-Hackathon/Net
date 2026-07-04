"use client";

import React, { useState } from "react";

interface JobFiltersProps {
  onFilterChange: (filters: { query: string }) => void;
}

export const JobFilters: React.FC<JobFiltersProps> = ({ onFilterChange }) => {
  const [query, setQuery] = useState("Python Developer");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onFilterChange({ query });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm flex flex-col md:flex-row gap-3">
      <div className="flex-1">
        <input
          type="text"
          placeholder="Nhập chức danh, kỹ năng hoặc công ty..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
        />
      </div>
      <button
        type="submit"
        className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-all"
      >
        Tìm kiếm
      </button>
    </form>
  );
};
