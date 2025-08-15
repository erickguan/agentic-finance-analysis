import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ClockIcon, 
  CheckCircleIcon, 
  XCircleIcon,
  ArrowPathIcon,
  EyeIcon 
} from '@heroicons/react/24/outline';
import { Analysis } from '../types';

interface AnalysisHistoryProps {
  analyses: Analysis[];
  onRefresh: () => void;
}

const AnalysisHistory: React.FC<AnalysisHistoryProps> = ({ analyses, onRefresh }) => {
  const navigate = useNavigate();

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'processing':
        return <ArrowPathIcon className="h-5 w-5 text-blue-500 animate-spin" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const truncateQuery = (query: string, maxLength: number = 80) => {
    return query.length > maxLength ? `${query.substring(0, maxLength)}...` : query;
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Analysis History</h3>
        <button
          onClick={onRefresh}
          className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
          title="Refresh"
        >
          <ArrowPathIcon className="h-4 w-4" />
        </button>
      </div>

      {analyses.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <ClockIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>No analyses yet. Start your first analysis above!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {analyses.slice(0, 10).map((analysis) => (
            <div
              key={analysis.analysis_id}
              className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-2">
                    {getStatusIcon(analysis.status)}
                    <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(analysis.status)}`}>
                      {analysis.status}
                    </span>
                    {analysis.symbol && (
                      <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full font-medium">
                        {analysis.symbol}
                      </span>
                    )}
                  </div>
                  
                  <p className="text-sm text-gray-900 mb-2">
                    {truncateQuery(analysis.query)}
                  </p>
                  
                  <div className="text-xs text-gray-500">
                    <span>Started: {formatDate(analysis.started_at)}</span>
                    {analysis.completed_at && (
                      <span className="ml-4">
                        Completed: {formatDate(analysis.completed_at)}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex-shrink-0 ml-4">
                  <button
                    onClick={() => navigate(`/analysis/${analysis.analysis_id}`)}
                    className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  >
                    <EyeIcon className="h-4 w-4 mr-1" />
                    View
                  </button>
                </div>
              </div>

              {analysis.error && (
                <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                  Error: {analysis.error}
                </div>
              )}
            </div>
          ))}

          {analyses.length > 10 && (
            <div className="text-center pt-4">
              <p className="text-sm text-gray-500">
                Showing latest 10 analyses ({analyses.length} total)
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AnalysisHistory;