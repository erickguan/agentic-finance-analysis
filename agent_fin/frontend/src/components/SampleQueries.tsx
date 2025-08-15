import React, { useState, useEffect } from 'react';
import { apiService, SampleQuery } from '../services/apiService';
import { SparklesIcon } from '@heroicons/react/24/outline';

interface SampleQueriesProps {
  onSelectQuery: (query: string) => void;
}

const SampleQueries: React.FC<SampleQueriesProps> = ({ onSelectQuery }) => {
  const [queries, setQueries] = useState<SampleQuery[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSampleQueries();
  }, []);

  const loadSampleQueries = async () => {
    try {
      const response = await apiService.getSampleQueries();
      setQueries(response.queries);
    } catch (error) {
      console.error('Failed to load sample queries:', error);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      stock_analysis: 'bg-blue-100 text-blue-800',
      sentiment: 'bg-green-100 text-green-800',
      valuation: 'bg-purple-100 text-purple-800',
      investment_advice: 'bg-yellow-100 text-yellow-800',
      financial_health: 'bg-red-100 text-red-800',
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-12 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center space-x-2 mb-4">
        <SparklesIcon className="h-5 w-5 text-yellow-500" />
        <h3 className="text-lg font-semibold">Sample Queries</h3>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {queries.map((query) => (
          <button
            key={query.id}
            onClick={() => onSelectQuery(query.query)}
            className="text-left p-3 border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-blue-300 transition-colors group"
          >
            <div className="flex items-start justify-between mb-2">
              <h4 className="font-medium text-gray-900 group-hover:text-blue-600">
                {query.title}
              </h4>
              <span className={`px-2 py-1 text-xs rounded-full ${getCategoryColor(query.category)}`}>
                {query.category.replace('_', ' ')}
              </span>
            </div>
            <p className="text-sm text-gray-600 italic">
              "{query.query}"
            </p>
          </button>
        ))}
      </div>
    </div>
  );
};

export default SampleQueries;