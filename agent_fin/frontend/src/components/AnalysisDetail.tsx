import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeftIcon, 
  ArrowPathIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  DocumentTextIcon,
  ChartBarIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import { apiService, AnalysisResponse } from '../services/apiService';

const AnalysisDetail: React.FC = () => {
  const { analysisId } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  const loadAnalysis = async () => {
    if (!analysisId) return;
    
    try {
      setError(null);
      const response = await apiService.getAnalysis(analysisId);
      setAnalysis(response);
    } catch (err) {
      setError('Failed to load analysis');
      console.error('Failed to load analysis:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="h-6 w-6 text-green-500" />;
      case 'failed':
        return <XCircleIcon className="h-6 w-6 text-red-500" />;
      case 'processing':
        return <ArrowPathIcon className="h-6 w-6 text-blue-500 animate-spin" />;
      default:
        return <ClockIcon className="h-6 w-6 text-gray-500" />;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  useEffect(() => {
    if (analysisId) {
      loadAnalysis();
      
      // Set up polling for real-time updates
      let cleanupFn: (() => void) | null = null;
      
      apiService.pollAnalysis(analysisId, (updatedAnalysis) => {
        setAnalysis(updatedAnalysis);
        setLoading(false);
      }).then((cleanup) => {
        cleanupFn = cleanup;
      });

      return () => {
        if (cleanupFn) cleanupFn();
      };
    }
  }, [analysisId, loadAnalysis]);

  if (loading && !analysis) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-4 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="max-w-6xl mx-auto">
        <button
          onClick={() => navigate('/')}
          className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 mb-6"
        >
          <ArrowLeftIcon className="h-4 w-4" />
          <span>Back to Dashboard</span>
        </button>
        
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <XCircleIcon className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Analysis Not Found</h2>
          <p className="text-gray-600 mb-4">{error || 'The requested analysis could not be found.'}</p>
          <button
            onClick={loadAnalysis}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', name: 'Overview', icon: DocumentTextIcon },
    { id: 'research', name: 'Research', icon: MagnifyingGlassIcon },
    { id: 'analysis', name: 'Analysis', icon: ChartBarIcon },
  ];

  return (
    <div className="max-w-6xl mx-auto">
      {/* Navigation */}
      <button
        onClick={() => navigate('/')}
        className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 mb-6"
      >
        <ArrowLeftIcon className="h-4 w-4" />
        <span>Back to Dashboard</span>
      </button>

      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              {getStatusIcon(analysis.status)}
              <h1 className="text-2xl font-bold text-gray-900">
                Analysis: {analysis.symbol || 'Processing...'}
              </h1>
            </div>
            <p className="text-gray-600 mb-2">"{analysis.results?.user_query || 'Unknown query'}"</p>
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span>Status: <span className="font-medium">{analysis.status}</span></span>
              <span>Updated: {formatTimestamp(analysis.timestamp)}</span>
            </div>
          </div>
          
          <button
            onClick={loadAnalysis}
            className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md"
            title="Refresh"
          >
            <ArrowPathIcon className="h-5 w-5" />
          </button>
        </div>

        {analysis.error && (
          <div className="bg-red-50 border border-red-200 rounded p-4">
            <h3 className="font-medium text-red-800 mb-2">Error</h3>
            <p className="text-red-700">{analysis.error}</p>
          </div>
        )}

        {analysis.results?.final_response && (
          <div className="bg-blue-50 border border-blue-200 rounded p-4">
            <h3 className="font-medium text-blue-800 mb-2">Executive Summary</h3>
            <p className="text-blue-700">{analysis.results.final_response}</p>
          </div>
        )}
      </div>

      {/* Tabs */}
      {analysis.results && (
        <div className="bg-white rounded-lg shadow-md">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{tab.name}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'overview' && (
              <OverviewTab results={analysis.results} />
            )}
            {activeTab === 'research' && (
              <ResearchTab research={analysis.results.research_results} />
            )}
            {activeTab === 'analysis' && (
              <AnalysisTab analysisData={analysis.results.analysis_results} />
            )}
          </div>
        </div>
      )}
    </div>
  );
};

// Tab Components
const OverviewTab: React.FC<{ results: any }> = ({ results }) => (
  <div className="space-y-6">
    <div>
      <h3 className="text-lg font-semibold mb-4">Key Information</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Symbol</div>
          <div className="text-lg font-semibold">{results.symbol || 'N/A'}</div>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Status</div>
          <div className="text-lg font-semibold">{results.status || 'N/A'}</div>
        </div>
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="text-sm text-gray-600">Processed</div>
          <div className="text-lg font-semibold">
            {results.processing_timestamp ? 
              new Date(results.processing_timestamp).toLocaleDateString() : 'N/A'}
          </div>
        </div>
      </div>
    </div>

    {results.research_results?.research_findings && (
      <div>
        <h3 className="text-lg font-semibold mb-4">Research Summary</h3>
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-blue-900">{results.research_results.research_findings}</p>
        </div>
      </div>
    )}

    {results.analysis_results?.analysis_findings && (
      <div>
        <h3 className="text-lg font-semibold mb-4">Analysis Summary</h3>
        <div className="bg-green-50 p-4 rounded-lg">
          <p className="text-green-900">{results.analysis_results.analysis_findings}</p>
        </div>
      </div>
    )}
  </div>
);

const ResearchTab: React.FC<{ research: any }> = ({ research }) => {
  if (!research) {
    return <div className="text-gray-500">No research data available</div>;
  }

  return (
    <div className="space-y-6">
      {research.research_findings && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Research Findings</h3>
          <div className="prose max-w-none">
            <p>{research.research_findings}</p>
          </div>
        </div>
      )}

      {research.sources_used && research.sources_used.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Data Sources</h3>
          <div className="flex flex-wrap gap-2">
            {research.sources_used.map((source: string, index: number) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
              >
                {source.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </span>
            ))}
          </div>
        </div>
      )}

      {research.data_quality_assessment && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Data Quality Assessment</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Completeness Score</div>
              <div className="text-2xl font-semibold">
                {(research.data_quality_assessment.completeness_score * 100).toFixed(0)}%
              </div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Source Diversity</div>
              <div className="text-2xl font-semibold">
                {research.data_quality_assessment.source_diversity}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const AnalysisTab: React.FC<{ analysisData: any }> = ({ analysisData }) => {
  if (!analysisData) {
    return <div className="text-gray-500">No analysis data available</div>;
  }

  return (
    <div className="space-y-6">
      {analysisData.analysis_findings && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Analysis Findings</h3>
          <div className="prose max-w-none">
            <p>{analysisData.analysis_findings}</p>
          </div>
        </div>
      )}

      {analysisData.metrics_calculated && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Calculated Metrics</h3>
          <div className="space-y-4">
            {Object.entries(analysisData.metrics_calculated).map(([category, metrics]: [string, any]) => (
              <div key={category}>
                <h4 className="font-medium text-gray-900 mb-2 capitalize">
                  {category.replace('_', ' ')}
                </h4>
                <div className="space-y-2">
                  {Array.isArray(metrics) && metrics.map((metric: any, index: number) => (
                    <div key={index} className="bg-gray-50 p-3 rounded">
                      <div className="font-medium">{metric.tool}</div>
                      <div className="text-sm text-gray-600 mt-1">
                        {typeof metric.result === 'string' ? 
                          metric.result.substring(0, 200) + (metric.result.length > 200 ? '...' : '') :
                          JSON.stringify(metric.result).substring(0, 200) + '...'
                        }
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {analysisData.confidence_assessment && (
        <div>
          <h3 className="text-lg font-semibold mb-4">Confidence Assessment</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Overall Confidence</div>
              <div className="text-lg font-semibold capitalize">
                {analysisData.confidence_assessment.overall_confidence}
              </div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Analysis Completeness</div>
              <div className="text-lg font-semibold">
                {(analysisData.confidence_assessment.analysis_completeness * 100).toFixed(0)}%
              </div>
            </div>
          </div>
          
          {analysisData.confidence_assessment.limiting_factors && 
           analysisData.confidence_assessment.limiting_factors.length > 0 && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded">
              <h4 className="font-medium text-yellow-800 mb-2">Limiting Factors</h4>
              <ul className="text-yellow-700 text-sm">
                {analysisData.confidence_assessment.limiting_factors.map((factor: string, index: number) => (
                  <li key={index}>• {factor}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AnalysisDetail;