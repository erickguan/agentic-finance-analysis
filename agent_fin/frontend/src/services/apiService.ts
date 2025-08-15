import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface AnalysisRequest {
  query: string;
  depth?: string;
}

export interface AnalysisResponse {
  analysis_id: string;
  status: string;
  symbol?: string;
  results?: any;
  error?: string;
  timestamp: string;
}

export interface SystemStatus {
  status: string;
  agents: Record<string, string>;
  config: Record<string, any>;
}

export interface SampleQuery {
  id: string;
  title: string;
  query: string;
  category: string;
}

class ApiService {
  async startAnalysis(query: string, depth: string = 'Standard Analysis'): Promise<AnalysisResponse> {
    const response = await api.post<AnalysisResponse>('/analyze', {
      query,
      depth
    });
    return response.data;
  }

  async getAnalysis(analysisId: string): Promise<AnalysisResponse> {
    const response = await api.get<AnalysisResponse>(`/analyze/${analysisId}`);
    return response.data;
  }

  async getAnalyses(): Promise<{ analyses: any[] }> {
    const response = await api.get('/analyses');
    return response.data;
  }

  async deleteAnalysis(analysisId: string): Promise<void> {
    await api.delete(`/analyze/${analysisId}`);
  }

  async getSystemStatus(): Promise<SystemStatus> {
    const response = await api.get<SystemStatus>('/status');
    return response.data;
  }

  async getSampleQueries(): Promise<{ queries: SampleQuery[] }> {
    const response = await api.get('/sample-queries');
    return response.data;
  }

  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await api.get('/health');
    return response.data;
  }

  // Polling function for real-time updates
  async pollAnalysis(
    analysisId: string, 
    onUpdate: (analysis: AnalysisResponse) => void,
    intervalMs: number = 2000
  ): Promise<() => void> {
    const poll = async () => {
      try {
        const analysis = await this.getAnalysis(analysisId);
        onUpdate(analysis);
        
        // Stop polling if analysis is completed or failed
        if (analysis.status === 'completed' || analysis.status === 'failed') {
          clearInterval(intervalId);
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    };

    // Start polling
    const intervalId = setInterval(poll, intervalMs);
    
    // Initial poll
    poll();
    
    // Return cleanup function
    return () => clearInterval(intervalId);
  }
}

export const apiService = new ApiService();