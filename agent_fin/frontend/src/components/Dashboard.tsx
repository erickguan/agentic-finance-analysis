import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import QueryForm from './QueryForm';
import SampleQueries from './SampleQueries';
import AnalysisHistory from './AnalysisHistory';
import SystemStatus from './SystemStatus';
import { apiService } from '../services/apiService';
import { Analysis } from '../types';

const Dashboard: React.FC = () => {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    loadAnalyses();
  }, []);

  const loadAnalyses = async () => {
    try {
      const response = await apiService.getAnalyses();
      setAnalyses(response.analyses);
    } catch (error) {
      console.error('Failed to load analyses:', error);
    }
  };

  const handleNewAnalysis = async (query: string, depth: string) => {
    setLoading(true);
    try {
      const response = await apiService.startAnalysis(query, depth);
      navigate(`/analysis/${response.analysis_id}`);
    } catch (error) {
      console.error('Failed to start analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSampleQuery = (query: string) => {
    handleNewAnalysis(query, 'Standard Analysis');
  };

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Welcome to Financial Analysis AI
        </h2>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Get comprehensive stock analysis powered by advanced AI agents. 
          Our system combines research, technical analysis, and market sentiment 
          to provide actionable insights.
        </p>
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column - Query Interface */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-xl font-semibold mb-4">New Analysis</h3>
            <QueryForm 
              onSubmit={handleNewAnalysis} 
              loading={loading}
            />
          </div>

          <SampleQueries onSelectQuery={handleSampleQuery} />
          
          <AnalysisHistory 
            analyses={analyses} 
            onRefresh={loadAnalyses}
          />
        </div>

        {/* Right Column - System Info */}
        <div className="space-y-6">
          <SystemStatus />
          
          {/* Quick Stats */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">Quick Stats</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Analyses:</span>
                <span className="font-medium">{analyses.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Completed:</span>
                <span className="font-medium text-green-600">
                  {analyses.filter(a => a.status === 'completed').length}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">In Progress:</span>
                <span className="font-medium text-blue-600">
                  {analyses.filter(a => a.status === 'processing').length}
                </span>
              </div>
            </div>
          </div>

          {/* Agent Overview */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">AI Agents</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                <div>
                  <div className="font-medium">Research Agent</div>
                  <div className="text-sm text-gray-600">Data collection & research</div>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <div>
                  <div className="font-medium">Analysis Agent</div>
                  <div className="text-sm text-gray-600">Technical & fundamental analysis</div>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                <div>
                  <div className="font-medium">Master Agent</div>
                  <div className="text-sm text-gray-600">Orchestration & synthesis</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;