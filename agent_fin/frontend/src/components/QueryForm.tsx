import React, { useState } from 'react';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

interface QueryFormProps {
  onSubmit: (query: string, depth: string) => void;
  loading: boolean;
}

const QueryForm: React.FC<QueryFormProps> = ({ onSubmit, loading }) => {
  const [query, setQuery] = useState('');
  const [depth, setDepth] = useState('Standard Analysis');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query.trim(), depth);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
          Ask about any stock:
        </label>
        <textarea
          id="query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g., 'Analyze Apple stock' or 'What's the outlook for TSLA?'"
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={loading}
        />
      </div>

      <div>
        <label htmlFor="depth" className="block text-sm font-medium text-gray-700 mb-2">
          Analysis Depth:
        </label>
        <select
          id="depth"
          value={depth}
          onChange={(e) => setDepth(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={loading}
        >
          <option value="Quick Overview">Quick Overview</option>
          <option value="Standard Analysis">Standard Analysis</option>
          <option value="Comprehensive Deep Dive">Comprehensive Deep Dive</option>
        </select>
      </div>

      <button
        type="submit"
        disabled={!query.trim() || loading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
      >
        {loading ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span>Analyzing...</span>
          </>
        ) : (
          <>
            <MagnifyingGlassIcon className="h-4 w-4" />
            <span>Analyze</span>
          </>
        )}
      </button>
    </form>
  );
};

export default QueryForm;