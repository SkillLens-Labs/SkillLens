import type { AnalysisResult } from "../types/analysis";

export type AnalysisStateStatus =
  | "idle"
  | "submitting"
  | "loading"
  | "success"
  | "error";

export interface AnalysisState {
  status: AnalysisStateStatus;
  analysis: AnalysisResult | null;
  error: {
    code: string;
    message: string;
    details: unknown;
    field: string | null;
    request_id: string | null;
  } | null;
  last_request_id: string | null;
}

export const initialAnalysisState: AnalysisState = {
  status: "idle",
  analysis: null,
  error: null,
  last_request_id: null,
};
