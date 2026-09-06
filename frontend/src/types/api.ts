import type { AnalysisResult } from "./analysis";

export interface AnalysisOptions {
  include_career_intelligence: boolean;
  include_recommendations: boolean;
  include_xai: boolean;
}

export interface ClientMetadata {
  source: string | null;
  session_id: string | null;
  extra: Record<string, unknown>;
}

export interface ResumeAnalysisRequest {
  options: AnalysisOptions;
  client_metadata: ClientMetadata | null;
}

export interface ResumeJDAnalysisRequest {
  options: AnalysisOptions;
  client_metadata: ClientMetadata | null;
}

export interface AnalysisResponse {
  data: AnalysisResult;
}

export interface AnalysisAcceptedResponse {
  analysis_id: string;
  status: string;
  message: string;
}

export interface DeleteAnalysisResponse {
  analysis_id: string;
  deleted: boolean;
  message: string;
}

export interface ErrorResponse {
  code: string;
  message: string;
  details: unknown;
  field: string | null;
  request_id: string;
}
