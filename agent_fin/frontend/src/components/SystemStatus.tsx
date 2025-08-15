import React, { useState, useEffect } from 'react';
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  ExclamationTriangleIcon,
  ArrowPathIcon 
} from '@heroicons/react/24/outline';
import { apiService, SystemStatus as SystemStatusType } from '../services/apiService';

const SystemStatus: React.FC = () => {
  const [status, setStatus] = useState<SystemStatusType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkStatus();
    // Check status every 30 seconds
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkStatus = async () => {
    try {
      setError(null);
      const statusResponse = await apiService.getSystemStatus();
      setStatus(statusResponse);
    } catch (err) {
      setError('Unable to connect to API');
      console.error('Status check failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = () => {
    if (loading) return <ArrowPathIcon className="h-5 w-5 text-gray-500 animate-spin" />;
    if (error) return <XCircleIcon className="h-5 w-5 text-red-500" />;
    if (status?.status === 'active') return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
    return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
  };

  const getStatusColor = () => {
    if (error) return 'text-red-600';
    if (status?.status === 'active') return 'text-green-600';
    return 'text-yellow-600';
  };

  const getAgentStatus = (agentName: string) => {
    const agentStatus = status?.agents[agentName];
    if (!agentStatus) return 'unknown';
    return agentStatus;
  };

  const getAgentStatusColor = (agentStatus: string) => {
    switch (agentStatus.toLowerCase()) {
      case 'active':
      case 'ready':
        return 'text-green-600';
      case 'busy':
        return 'text-blue-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">System Status</h3>
        <button
          onClick={checkStatus}
          className="p-1 text-gray-500 hover:text-gray-700 rounded"
          disabled={loading}
        >
          <ArrowPathIcon className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* Overall Status */}
      <div className="flex items-center space-x-2 mb-4">
        {getStatusIcon()}
        <span className={`font-medium ${getStatusColor()}`}>
          {error ? 'System Offline' : status?.status === 'active' ? 'System Online' : 'System Status Unknown'}
        </span>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-3 mb-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {status && (
        <>
          {/* Agent Status */}
          <div className="space-y-3 mb-4">
            <h4 className="text-sm font-medium text-gray-900">Agent Status</h4>
            {Object.entries(status.agents).map(([agentName, agentStatus]) => (
              <div key={agentName} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 capitalize">
                  {agentName.replace('_', ' ')}:
                </span>
                <span className={`text-sm font-medium ${getAgentStatusColor(agentStatus)}`}>
                  {agentStatus}
                </span>
              </div>
            ))}
          </div>

          {/* Configuration */}
          <div className="pt-4 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-900 mb-3">Configuration</h4>
            <div className="space-y-2">
              {Object.entries(status.config).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600 capitalize">
                    {key.replace('_', ' ')}:
                  </span>
                  <span className="text-sm font-mono text-gray-800 truncate ml-2">
                    {typeof value === 'string' ? value : JSON.stringify(value)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Health Status Indicator */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Last Updated:</span>
          <span className="text-gray-800">{new Date().toLocaleTimeString()}</span>
        </div>
      </div>
    </div>
  );
};

export default SystemStatus;