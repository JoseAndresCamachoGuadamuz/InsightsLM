// frontend/src/services/api.ts

import axios from 'axios';

// --- INTERFACES ---
export interface Template {
  id: number;
  name: string;
  prompt_text: string;
  language: string;
}

export interface Config {
  data_storage_path: string;
  default_model: string;
  api_keys: {
    openai: string;
    anthropic: string;
    google: string;
  };
}

// REQUIREMENT 5.5: New interfaces for API testing functionality
export interface ApiTestResult {
  success: boolean;
  message: string;
  provider: string;
  error?: string;
}

export interface AllApiStatusResponse {
  status: string;
  results: {
    [provider: string]: ApiTestResult;
  };
  summary: {
    total_providers: number;
    working_providers: number;
    failed_providers: number;
  };
}

// STEP 3: New interfaces for model discovery
export interface ModelInfo {
  key: string;
  label: string;
  provider: string;
  model_id?: string;
}

export interface ModelsResponse {
  models: ModelInfo[];
  count: number;
  provider?: string;
  providers?: {
    [key: string]: number;
  };
  error?: string;
}

// STEP 10: Dynamic backend port support
// Create an Axios client with default port 8000 (will be updated on app startup)
const apiClient = axios.create({ baseURL: 'http://127.0.0.1:8000' });

/**
 * STEP 10: Update the backend port for all API calls
 * This should be called once during app initialization after the backend starts
 * @param port - The port number the backend is running on (8000-8050)
 */
export const setBackendPort = (port: number): void => {
  const newBaseURL = `http://127.0.0.1:${port}`;
  apiClient.defaults.baseURL = newBaseURL;
  console.log(`[API] Backend port updated to: ${port} (${newBaseURL})`);
};

/**
 * STEP 10: Get the current backend URL
 * Useful for debugging and status display
 */
export const getBackendUrl = (): string => {
  return apiClient.defaults.baseURL || 'http://127.0.0.1:8000';
};

// --- Transcription Endpoints ---
export const uploadAndTranscribe = (
  file: File, 
  onProgress?: (progressEvent: { loaded: number; total?: number }) => void
) => {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.post('/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (onProgress) {
        onProgress({
          loaded: progressEvent.loaded,
          total: progressEvent.total
        });
      }
    },
  });
};

// FIXED: Add alias for backward compatibility with App.tsx
export const uploadFile = uploadAndTranscribe;

export const transcribeFromUrl = (url: string) => { 
  return apiClient.post('/download/', { url }); 
};

// FIXED: Add alias for backward compatibility with App.tsx
export const transcribeUrl = transcribeFromUrl;

// --- Analysis Endpoints ---
export const getSummary = (sourceId: number, model_key: string) => { 
  return apiClient.post(`/summarize/`, { source_id: sourceId, model_key }); 
};

// FIXED: Add alias for backward compatibility with App.tsx
export const summarize = getSummary;

export const postQuery = (sourceId: number, queryText: string, model_key: string) => {
  return apiClient.post('/query/', { source_id: sourceId, query_text: queryText, model_key: model_key });
};

export const getAudioOverview = (sourceId: number, model_key: string) => { 
  return apiClient.post('/audio-overview/', { source_id: sourceId, model_key }); 
};

// --- TEMPLATE & REPORT ENDPOINTS ---
export const getTemplates = () => { 
  return apiClient.get<Template[]>('/templates/'); 
};

export const createTemplate = (name: string, prompt_text: string, language: string) => {
  return apiClient.post<Template>('/templates/', { name, prompt_text, language });
};

// FIXED: Updated signature to match App.tsx usage (4 parameters)
export const updateTemplate = (id: number, name: string, prompt_text: string, language: string) => {
  return apiClient.put<Template>(`/templates/${id}`, { name, prompt_text, language });
};

export const deleteTemplate = (templateId: number) => { 
  return apiClient.delete(`/templates/${templateId}`); 
};

export const deleteAllTemplates = () => { 
  return apiClient.delete('/templates/'); 
};

export const runReport = (sourceId: number, templateId: number, model_key: string) => {
  return apiClient.post('/report/', { source_id: sourceId, template_id: templateId, model_key });
};

// --- REQUIREMENT 5.4: API Testing Endpoints ---
/**
 * Test API connection for a specific provider
 */
export const testApiConnection = async (provider: string): Promise<{ data: ApiTestResult }> => {
  const response = await apiClient.post(`/test-api/${provider}`);
  return response;
};

/**
 * Get status of all API providers at once
 */
export const getAllApiStatus = async (): Promise<{ data: AllApiStatusResponse }> => {
  const response = await apiClient.get('/test-api/status');
  return response;
};

// --- STEP 3: MODEL DISCOVERY ENDPOINTS ---

/**
 * Get available Ollama models installed locally
 * @returns Promise with models response containing Ollama models
 */
export const getOllamaModels = async (): Promise<{ data: ModelsResponse }> => {
  const response = await apiClient.get<ModelsResponse>('/models/ollama');
  return response;
};

/**
 * Get available OpenAI models based on user's API key
 * @returns Promise with models response containing OpenAI models
 */
export const getOpenAIModels = async (): Promise<{ data: ModelsResponse }> => {
  const response = await apiClient.get<ModelsResponse>('/models/openai');
  return response;
};

/**
 * Get available Anthropic Claude models
 * @returns Promise with models response containing Anthropic models
 */
export const getAnthropicModels = async (): Promise<{ data: ModelsResponse }> => {
  const response = await apiClient.get<ModelsResponse>('/models/anthropic');
  return response;
};

/**
 * Get available Google Gemini models based on user's API key
 * @returns Promise with models response containing Google models
 */
export const getGoogleModels = async (): Promise<{ data: ModelsResponse }> => {
  const response = await apiClient.get<ModelsResponse>('/models/google');
  return response;
};

/**
 * Get all available models from all providers
 * This is the main function used to populate model dropdowns
 * @returns Promise with models response containing all available models
 */
export const getAllModels = async (): Promise<{ data: ModelsResponse }> => {
  const response = await apiClient.get<ModelsResponse>('/models/all');
  return response;
};

// --- CONFIGURATION ENDPOINTS ---
export const getConfig = () => { 
  return apiClient.get<Config>('/config/'); 
};

export const updateConfig = (config: Config) => { 
  return apiClient.put('/config/', config); 
};

// --- EXPORT ENDPOINT ---
// FIXED: Completely rewrote to match backend schema and App.tsx usage
export const exportContent = (exportData: {
  source_id: number;
  content_type: 'transcript' | 'summary' | 'overview' | 'report';
  format: 'txt' | 'md';
  model_key: string;
  template_id?: number;
  content?: string;
}) => {
  // Debug logging to help diagnose issues
  console.log('API exportContent called with:', exportData);
  
  return apiClient.post('/export/', exportData, {
    responseType: 'blob',
  });
};