export interface Analysis {
  analysis_id: string;
  query: string;
  status: 'processing' | 'completed' | 'failed';
  symbol?: string;
  results?: AnalysisResults;
  error?: string;
  started_at: string;
  completed_at?: string;
}

export interface AnalysisResults {
  status: string;
  symbol: string;
  user_query: string;
  final_response?: string;
  research_results?: ResearchResults;
  analysis_results?: AnalysisData;
  processing_timestamp?: string;
}

export interface ResearchResults {
  research_findings: string;
  sources_used: string[];
  data_quality_assessment?: {
    completeness_score: number;
    source_diversity: number;
  };
}

export interface AnalysisData {
  analysis_findings: string;
  metrics_calculated?: {
    technical_metrics?: MetricResult[];
    fundamental_metrics?: MetricResult[];
    sentiment_metrics?: MetricResult[];
  };
  confidence_assessment?: {
    overall_confidence: string;
    analysis_completeness: number;
    limiting_factors?: string[];
  };
}

export interface MetricResult {
  tool: string;
  result: any;
  timestamp?: string;
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