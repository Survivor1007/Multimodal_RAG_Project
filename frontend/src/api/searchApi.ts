import { apiClient } from "./client";
import {
  type SearchRequest,
  type SearchResponse,
  type RAGRequest,
  type RAGResponse,
  type DocumentItem,
  type DocumentChunksResponse,
  type AnalyticsData,
} from "../types/search";

export const searchApi = {
  async search(payload: SearchRequest): Promise<SearchResponse> {
    const response = await apiClient.post<SearchResponse>(
      "v1/search/search",
      payload
    );
    return response.data;
  },

  async rag(payload: RAGRequest): Promise<RAGResponse> {
    const response = await apiClient.post<RAGResponse>(
      "v1/rag/rag",
      payload
    );
    return response.data;
  },

  async getDocuments(): Promise<{ total_documents: number; documents: DocumentItem[] }> {
    const response = await apiClient.get("v1/documents/list");
    return response.data;
  },

  async getDocumentChunks(docId: number): Promise<DocumentChunksResponse> {
    const response = await apiClient.get(`v1/documents/${docId}/chunks`);
    return response.data;
  },

  async deleteDocument(docId: number): Promise<{ message: string }> {
    const response = await apiClient.delete(`v1/documents/${docId}`);
    return response.data;
  },

  async getTelemetry(): Promise<any> {
    const response = await apiClient.get("v1/analytics/telemetry");
    return response.data;
  },

  async getEvalBenchmark(): Promise<AnalyticsData> {
    const response = await apiClient.get("v1/analytics/eval-benchmark");
    return response.data;
  },
};
