import React, { useState, useEffect, useRef } from 'react';
import { 
  transcribeFromUrl, 
  uploadAndTranscribe, 
  getSummary, 
  getAudioOverview, 
  postQuery, 
  getTemplates, 
  createTemplate, 
  updateTemplate, 
  deleteTemplate, 
  deleteAllTemplates, 
  runReport, 
  Template,
  getConfig,
  updateConfig,
  Config,
  exportContent,
  testApiConnection,
  getAllApiStatus,
  ApiTestResult,
  setBackendPort,
  getBackendUrl,
  getAllModels,      // STEP 4: Dynamic model loading
  ModelInfo          // STEP 4: Model info interface
} from './services/api';
import { AxiosError } from 'axios';
import './index.css';

// --- Type Definitions ---
type Status = 'idle' | 'uploading' | 'transcribing' | 'success' | 'error' | 'downloading';
type View = 'transcript' | 'chat' | 'summary' | 'overview' | 'reports' | 'settings';
interface Citation { text: string; start_time: number; end_time: number; source_id: number; }
interface ChatMessage { sender: 'user' | 'ai'; text: string; citations?: Citation[]; }
type ReportResults = { [key: number]: string };
type RunningReports = Set<number>;

// --- Helper Functions ---
const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};

// --- Constants ---
const modelOptions = [
  { value: 'ollama_mistral', label: 'Ollama: Mistral' },
  { value: 'ollama_llama3', label: 'Ollama: Llama 3' },
  { value: 'claude_3_5_sonnet', label: 'Anthropic: Claude 3.5 Sonnet' },
  { value: 'openai_gpt5', label: 'OpenAI: GPT-5' },
  { value: 'gemini_1_5_pro', label: 'Google: Gemini 1.5 Pro' },
];
const languageOptions = ["English", "Spanish", "French", "German", "Does Not Apply"];

function App() {
  // --- State Management ---
  const [sourceId, setSourceId] = useState<number | null>(null);
  const [transcription, setTranscription] = useState('');
  const [status, setStatus] = useState<Status>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [currentView, setCurrentView] = useState<View>('transcript');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [query, setQuery] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [summary, setSummary] = useState('');
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [urlInput, setUrlInput] = useState('');
  const [selectedModel, setSelectedModel] = useState<string>(modelOptions[0].value);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isGeneratingAudio, setIsGeneratingAudio] = useState(false);
  const [overviewText, setOverviewText] = useState('');
  const [templates, setTemplates] = useState<Template[]>([]);
  const [showTemplateForm, setShowTemplateForm] = useState(false);
  const [newTemplateName, setNewTemplateName] = useState('');
  const [newTemplatePrompt, setNewTemplatePrompt] = useState('');
  const [newTemplateLanguage, setNewTemplateLanguage] = useState<string>(languageOptions[0]);
  const [runningReports, setRunningReports] = useState<RunningReports>(new Set());
  const [reportResults, setReportResults] = useState<ReportResults>({});
  const [editingTemplateId, setEditingTemplateId] = useState<number | null>(null);
  const [hiddenResults, setHiddenResults] = useState<Set<number>>(new Set());
  const [config, setConfig] = useState<Config | null>(null);
  const [configStatus, setConfigStatus] = useState('');
  const [exportingState, setExportingState] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(false); // REQUIREMENT 1: Added loading state
  const [isDragging, setIsDragging] = useState(false); // NEW: Drag & drop state
  
  // STEP 2: Toast notification state
  const [toastMessage, setToastMessage] = useState<string>('');
  const [showToast, setShowToast] = useState<boolean>(false);
  
  // REQUIREMENT 5.5: API Testing State
  const [testingStatus, setTestingStatus] = useState<{[key: string]: 'idle' | 'testing' | 'success' | 'error'}>({});
  const [testResults, setTestResults] = useState<{[key: string]: ApiTestResult | null}>({});
  const statusTimeoutsRef = useRef<{[key: string]: NodeJS.Timeout}>({}); // Changed to ref to avoid stale closures
  const [isTestingAll, setIsTestingAll] = useState(false);

  // STEP 7: Password visibility state
  const [showPasswords, setShowPasswords] = useState<{[key: string]: boolean}>({
    openai: false,
    anthropic: false,
    google: false
  });

  // STEP 9: Backend connection state
  const [backendConnected, setBackendConnected] = useState<boolean>(false);
  const [isCheckingConnection, setIsCheckingConnection] = useState<boolean>(false);
  const [connectionError, setConnectionError] = useState<string>('');

  // STEP 10: Backend port state
  const [backendPort, setBackendPortState] = useState<number>(8000);

  // STEP 4: Dynamic model loading state
  const [availableModels, setAvailableModels] = useState<ModelInfo[]>([]);
  const [modelsLoading, setModelsLoading] = useState<boolean>(false);
  const [modelsError, setModelsError] = useState<string>('');

  // REQUIREMENT 4: Prompt storage states
  const [chatPrompts, setChatPrompts] = useState<string[]>([]);
  const [summaryPrompt, setSummaryPrompt] = useState<string>("");
  const [overviewPrompt, setOverviewPrompt] = useState<string>("");
  const [reportPrompts, setReportPrompts] = useState<{[key: number]: string}>({});
  const [showPromptModal, setShowPromptModal] = useState<boolean>(false);
  const [currentPromptContent, setCurrentPromptContent] = useState<string>("");

  // BUG FIX: Refs for focus management
  const chatInputRef = useRef<HTMLInputElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null); // NEW: Ref for hidden file input

  // --- Effects ---
  useEffect(() => {
    handleFetchTemplates();
    handleFetchConfig();
    fetchAvailableModels();  // STEP 4: Fetch models on startup
  }, []);

  // Cleanup timeouts on unmount to prevent memory leaks
  useEffect(() => {
    return () => {
      // Ref always has current value, so this will properly clear all active timeouts
      Object.values(statusTimeoutsRef.current).forEach(timeout => clearTimeout(timeout));
      statusTimeoutsRef.current = {}; // Clear all references
    };
  }, []); // Empty array = only cleanup on unmount

  // STEP 9: Check backend connection on mount
  useEffect(() => {
    checkBackendHealth();
  }, []);

  // STEP 10: Initialize backend port from Electron
  useEffect(() => {
    const initializeBackendPort = async () => {
      try {
        const port = await window.electronAPI.getBackendPort();
        console.log('[App] Backend port from Electron:', port);
        setBackendPortState(port);
        setBackendPort(port); // Update API client
      } catch (error) {
        console.error('[App] Failed to get backend port, using default 8000:', error);
        // Keep default port 8000
      }
    };
    
    initializeBackendPort();
  }, []);

  // STEP 30: Listen for navigate-to-settings IPC event from File > Settings menu
  useEffect(() => {
    // Check if electronAPI is available (only in Electron environment)
    if (window.electronAPI && window.electronAPI.onNavigateToSettings) {
      console.log('[App] Setting up navigate-to-settings listener');
      
      // Register listener - onNavigateToSettings returns a cleanup function
      const cleanup = window.electronAPI.onNavigateToSettings(() => {
        console.log('[App] Received navigate-to-settings event from menu');
        setCurrentView('settings');
      });
      
      // Cleanup on unmount
      return cleanup;
    } else {
      console.log('[App] electronAPI.onNavigateToSettings not available (web mode)');
    }
  }, []);

  // REQUIREMENT 4: Model name mapping function
  const getModelDisplayName = (modelKey: string): string => {
    const modelNames: { [key: string]: string } = {
      'ollama_mistral': 'Ollama Mistral 7B',
      'ollama_llama3': 'Ollama Llama 3',
      'openai_gpt4': 'OpenAI GPT-4',
      'openai_gpt4o': 'OpenAI GPT-4o',
      'claude_sonnet': 'Anthropic Claude Sonnet 3.5',
      'claude_3_5_sonnet': 'Anthropic Claude 3.5 Sonnet',
      'claude_opus': 'Anthropic Claude Opus 3',
      'openai_gpt5': 'OpenAI GPT-5',
      'gemini_1_5_pro': 'Google Gemini 1.5 Pro',
      'gemini_1_5_flash': 'Google Gemini 1.5 Flash'
    };
    return modelNames[modelKey] || modelKey;
  };

  // REQUIREMENT 4: Format prompt for display with template
  const formatPromptForDisplay = (
    prompt: string, 
    modelKey: string, 
    timestamp: Date,
    type: 'summary' | 'overview' | 'chat' | 'report' = 'summary',
    language?: string,
    userQuestion?: string
  ): string => {
    const modelName = getModelDisplayName(modelKey);
    
    // Format timestamp as "Month DD, YYYY, HH:MM AM/PM"
    const formattedDate = timestamp.toLocaleDateString('en-US', { 
      month: 'long', 
      day: 'numeric', 
      year: 'numeric' 
    });
    const formattedTime = timestamp.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit', 
      hour12: true 
    });
    const formattedTimestamp = `${formattedDate}, ${formattedTime}`;

    // Determine title based on type
    const titles = {
      summary: 'SUMMARY GENERATION PROMPT',
      overview: 'AUDIO OVERVIEW PROMPT',
      chat: 'CHAT QUERY PROMPT',
      report: 'CUSTOM REPORT PROMPT'
    };
    const title = titles[type];

    // Extract system instructions and question for chat
    let systemInstruction = prompt;
    let extractedQuestion = userQuestion;
    
    // Special handling for chat prompts
    if (type === 'chat') {
      // Extract system instruction (before CONTEXT:)
      const contextMatch = prompt.match(/^(.*?)(?:\n\s*CONTEXT:|CONTEXT:)/s);
      if (contextMatch) {
        systemInstruction = contextMatch[1].trim();
      }
      
      // Extract question (after QUESTION:) if not provided
      if (!extractedQuestion) {
        const questionMatch = prompt.match(/QUESTION:\s*\n?(.*?)$/s);
        if (questionMatch) {
          extractedQuestion = questionMatch[1].trim();
        }
      }
    } else {
      // For non-chat: Extract just the system instruction part (before context/transcript)
      const splitMarkers = ['---\n', '\n---\n', '\nContext:', '\nCONTEXT:', '\n\nTranscription:', '\n\nContext chunks:'];
      for (const marker of splitMarkers) {
        const parts = prompt.split(marker);
        if (parts.length > 1) {
          systemInstruction = parts[0].trim();
          break;
        }
      }
    }

    // Determine omission note based on type
    const omissionNotes = {
      summary: '[Transcript content omitted for brevity]',
      overview: '[Transcript content omitted for brevity]',
      chat: '[Context chunks omitted for brevity]',
      report: '[Transcript content omitted for brevity]'
    };
    const omissionNote = omissionNotes[type];

    // Build the formatted prompt
    let formatted = `=== ${title} ===

Model: ${modelName}
Generated: ${formattedTimestamp}

--- Prompt Sent to AI ---

${systemInstruction}`;

    // Add language for reports if provided
    if (type === 'report' && language) {
      formatted += `\n\nLanguage: ${language}`;
    }

    // Add user question for chat
    if (type === 'chat' && extractedQuestion) {
      formatted += `\n\nQUESTION:\n${extractedQuestion}`;
    }

    // Add omission note
    formatted += `\n\n${omissionNote}`;

    formatted += `\n\n--- End of Prompt ---`;

    return formatted;
  };


  // BUG FIX: Enhanced modal close handler with focus restoration
  const handleClosePromptModal = () => {
    setShowPromptModal(false);
    
    // Restore focus to the previously focused element
    // Use setTimeout to ensure the modal is fully unmounted before focusing
    setTimeout(() => {
      if (previousFocusRef.current) {
        previousFocusRef.current.focus();
        previousFocusRef.current = null;
      } else if (currentView === 'chat' && chatInputRef.current) {
        // Fallback: if we're in chat view, focus the chat input
        chatInputRef.current.focus();
      }
    }, 0);
  };

  // BUG FIX: Enhanced modal open handler with focus capture
  const handleOpenPromptModal = (promptContent: string) => {
    // Capture the currently focused element before opening modal
    previousFocusRef.current = document.activeElement as HTMLElement;
    setCurrentPromptContent(promptContent);
    setShowPromptModal(true);
  };
  // --- Core Logic Functions ---
  // REQUIREMENT 2: Updated resetState function
  const resetState = () => {
    setErrorMessage(''); setUploadProgress(0); setTranscription('');
    setChatMessages([]); setSourceId(null); setSummary('');
    setAudioUrl(null); setOverviewText(''); setReportResults({});
    setIsLoading(false); // REQUIREMENT 1: Reset loading state
    
    // REQUIREMENT 2: Add missing chat state resets
    setIsThinking(false);  // Clear thinking state that disables input
    setQuery('');          // Clear chat input text
    
    // REQUIREMENT 4: Clear all prompt states
    setChatPrompts([]);
    setSummaryPrompt('');
    setOverviewPrompt('');
    setReportPrompts({});
    
    // REQUIREMENT 2: Don't force tab switch - preserve user's current view
    // REMOVED: setCurrentView('transcript'); 
    // Let user stay on their current tab after reset
  };

  // STEP 2: Toast notification helper functions
  const showToastNotification = (message: string) => {
    setToastMessage(message);
    setShowToast(true);
  };

  const closeToast = () => {
    setShowToast(false);
    setToastMessage('');
  };

  // STEP 4: Fetch available models from backend
  const fetchAvailableModels = async () => {
    setModelsLoading(true);
    setModelsError('');
    
    try {
      console.log('[App] Fetching available models...');
      const response = await getAllModels();
      const models = response.data.models;
      const providerErrors = response.data.provider_errors; // STEP 6C-3: Get provider errors from backend
      const providers = response.data.providers || {};
      
      if (models && models.length > 0) {
        setAvailableModels(models);
        console.log(`[App] Loaded ${models.length} models from ${Object.keys(providers).length} providers`);
        
        // STEP 6C-3: Display provider-specific errors if any exist
        if (providerErrors && Object.keys(providerErrors).length > 0) {
          const errorMessages: string[] = [];
          
          // Build error message for each failing provider
          Object.entries(providerErrors).forEach(([provider, error]) => {
            const providerName = provider.charAt(0).toUpperCase() + provider.slice(1);
            errorMessages.push(`${providerName}: ${error}`);
          });
          
          // Build working providers summary
          const workingProviders: string[] = [];
          Object.entries(providers).forEach(([provider, count]) => {
            const providerName = provider.charAt(0).toUpperCase() + provider.slice(1);
            workingProviders.push(`${providerName} (${count})`);
          });
          
          // Combine into user-friendly message
          let message = '⚠️ Some AI providers are unavailable: ';
          message += errorMessages.join(' • ');
          
          if (workingProviders.length > 0) {
            message += ` | ✅ Working: ${workingProviders.join(', ')}`;
          }
          
          showToastNotification(message);
          console.log('[App] Provider errors:', providerErrors);
        }
        
        // If current selected model is not in available models, select first available
        const currentModelExists = models.some(m => m.key === selectedModel);
        if (!currentModelExists && models.length > 0) {
          console.log(`[App] Current model '${selectedModel}' not available, switching to '${models[0].key}'`);
          setSelectedModel(models[0].key);
        }
      } else {
        // No models available - check if we have provider errors to show
        if (providerErrors && Object.keys(providerErrors).length > 0) {
          // STEP 6C-3: Show specific errors when no models available
          const errorMessages: string[] = [];
          
          Object.entries(providerErrors).forEach(([provider, error]) => {
            const providerName = provider.charAt(0).toUpperCase() + provider.slice(1);
            errorMessages.push(`${providerName}: ${error}`);
          });
          
          const message = '⚠️ No AI models available. ' + errorMessages.join(' • ');
          showToastNotification(message);
          console.log('[App] No models available. Provider errors:', providerErrors);
        } else {
          // Generic error if no specific provider errors
          showToastNotification('No AI models available. Please configure API keys in Settings or install Ollama.');
          console.warn('[App] No models available and no provider errors reported');
        }
        
        setModelsError('No AI models available. Please configure API keys in Settings or install Ollama.');
        setAvailableModels([]);
      }
    } catch (error) {
      console.error('[App] Failed to fetch models:', error);
      setModelsError('Unable to fetch models. Please check your connection.');
      // Keep any existing models as fallback
      if (availableModels.length === 0) {
        // Only show error toast if we have NO models at all
        showToastNotification('Unable to load AI models. Please check your settings.');
      }
    } finally {
      setModelsLoading(false);
    }
  };

  const processSuccessfulTranscription = (response: any) => {
    setTranscription(response.data.transcription);
    setSourceId(response.data.source_id);
    setStatus('success');
    setIsLoading(false); // REQUIREMENT 1: Clear loading state on success
  };

  const handleError = (err: unknown) => {
    let message = 'An unknown error occurred.';
    
    // STEP 9: Check if this is a connection error
    const isConnectionError = (
      err instanceof AxiosError && 
      (err.code === 'ERR_NETWORK' || 
       err.code === 'ECONNREFUSED' ||
       err.message?.includes('Network Error') ||
       err.message?.includes('ERR_CONNECTION_REFUSED'))
    );
    
    // STEP 9: Don't show generic error for connection issues - Step 9 UI handles it
    if (isConnectionError) {
      console.warn('Backend connection error detected - will be handled by Step 9 UI');
      setBackendConnected(false);
      setConnectionError('Cannot connect to backend server');
      setStatus('idle'); // Reset to idle instead of error
      return; // Exit early, don't show generic error
    }
    
    if (err instanceof AxiosError && err.response?.data?.detail) {
      const detail = err.response.data.detail;
      if (Array.isArray(detail)) {
        message = detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join('; ');
      } else {
        message = String(detail);
      }
    }
    console.error('API Error:', err);
    
    // STEP 2: Show toast notification instead of inline error
    showToastNotification(message);
    
    // Keep old error message for now (will remove in Step 4)
    setErrorMessage(message);
    setStatus('error');
    setIsSummarizing(false);
    setIsGeneratingAudio(false);
    setIsThinking(false);
    setRunningReports(new Set());
    setExportingState(new Set());
    setIsLoading(false); // REQUIREMENT 1: Clear loading state on error
  };

  // STEP 4B - PHASE 1: API error handler with yt-dlp detection
  const handleApiError = (err: unknown) => {
    let message = 'An unknown error occurred.';
    
    if (err instanceof AxiosError && err.response?.data?.detail) {
      const detail = err.response.data.detail;
      
      // MSG-020: Check for yt-dlp 403 errors
      if (typeof detail === 'string' && detail.includes('403') && detail.includes('yt-dlp')) {
        message = 'Cannot download video. The video might be restricted or require yt-dlp or a new version of yt-dlp. Please install or update yt-dlp and restart the application.';
      } else if (Array.isArray(detail)) {
        message = detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join('; ');
      } else {
        // Strip ANSI color codes from backend error messages
        message = String(detail).replace(/\x1b\[[0-9;]*m/g, '');
      }
    }
    
    console.error('API Error:', err);
    showToastNotification(message);
    setErrorMessage(message);
    setStatus('error');
    setIsSummarizing(false);
    setIsGeneratingAudio(false);
    setIsThinking(false);
    setRunningReports(new Set());
    setExportingState(new Set());
    setIsLoading(false);
  };

  // --- Event Handlers ---
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      resetState(); 
      setIsLoading(true); // REQUIREMENT 1: Set loading IMMEDIATELY when file selected
      setStatus('uploading');
      uploadAndTranscribe(event.target.files[0], (progressEvent) => {
        // API sends object { loaded, total }, convert to percentage
        if (progressEvent.total && progressEvent.total > 0) {
          const percentage = (progressEvent.loaded / progressEvent.total) * 100;
          setUploadProgress(percentage);
        }
      })
        .then(processSuccessfulTranscription).catch(err => handleApiError(err));
    }
  };

  // NEW: Drag & Drop Handlers
  const handleDragEnter = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      resetState();
      setIsLoading(true);
      setStatus('uploading');
      uploadAndTranscribe(file, (progressEvent) => {
        // API sends object { loaded, total }, convert to percentage
        if (progressEvent.total && progressEvent.total > 0) {
          const percentage = (progressEvent.loaded / progressEvent.total) * 100;
          setUploadProgress(percentage);
        }
      })
        .then(processSuccessfulTranscription).catch(err => handleApiError(err));
    }
  };

  const handleChooseFileClick = () => {
    fileInputRef.current?.click();
  };

  const handleUrlSubmit = async () => {
    if (!urlInput.trim()) return;
    resetState(); 
    setIsLoading(true); // REQUIREMENT 1: Set loading IMMEDIATELY when Go clicked
    setStatus('downloading');
    try {
      const response = await transcribeFromUrl(urlInput);
      processSuccessfulTranscription(response);
    } catch (err) { handleApiError(err); }
  };

  const handleSummarize = async () => {
    if (!sourceId) return;
    setIsSummarizing(true); setSummary(''); setErrorMessage('');
    setCurrentView('summary');
    try {
      const response = await getSummary(sourceId, selectedModel);
      setSummary(response.data.summary);
      // REQUIREMENT 4: Store the prompt from API response
      if (response.data.prompt) {
        setSummaryPrompt(response.data.prompt);
      }
    } catch (err) { handleError(err); }
    finally { setIsSummarizing(false); }
  };

  const handleCreateAudioOverview = async () => {
    if (!sourceId) return;
    setIsGeneratingAudio(true); setOverviewText(''); setAudioUrl(null);
    setErrorMessage(''); setCurrentView('overview');
    try {
      const response = await getAudioOverview(sourceId, selectedModel);
      setOverviewText(response.data.summary_text);
      const fullAudioUrl = `http://127.0.0.1:8000${response.data.audio_url}`;
      setAudioUrl(fullAudioUrl);
      // REQUIREMENT 4: Store the prompt from API response
      if (response.data.prompt) {
        setOverviewPrompt(response.data.prompt);
      }
    } catch (err) { handleError(err); }
    finally { setIsGeneratingAudio(false); }
  };

  // REQUIREMENT 2: Updated handleQuerySubmit function
  const handleQuerySubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    // REQUIREMENT 2: Defensive programming - ensure clean state
    if (!query.trim() || !sourceId) {
      console.warn('Cannot submit query: missing query text or source ID');
      return;
    }
    
    if (isThinking) {
      console.warn('Cannot submit query: already processing');
      return;
    }
    
    const newUserMessage: ChatMessage = { sender: 'user', text: query };
    setChatMessages(prev => [...prev, newUserMessage]);
    setQuery('');
    setIsThinking(true);
    
    try {
      const response = await postQuery(sourceId, query, selectedModel);
      const aiMessage: ChatMessage = { 
        sender: 'ai', 
        text: response.data.answer, 
        citations: response.data.citations 
      };
      setChatMessages(prev => [...prev, aiMessage]);
      
      // REQUIREMENT 4: Store the prompt from API response
      if (response.data.prompt) {
        setChatPrompts(prev => [...prev, response.data.prompt]);
      }
    } catch (err) { 
      handleError(err); 
    } finally { 
      // REQUIREMENT 2: Ensure isThinking is always cleared
      setIsThinking(false);
      
      // REQUIREMENT 2: Restore input focus after query completion
      setTimeout(() => {
        const chatInput = document.querySelector('.chat-input-form input') as HTMLInputElement;
        if (chatInput && currentView === 'chat') {
          chatInput.focus();
        }
      }, 100);
    }
  };

  const handleFetchTemplates = async () => {
    try {
      const response = await getTemplates();
      setTemplates(response.data);
    } catch (err) { handleError(err); }
  };

  const handleSaveTemplate = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!newTemplateName.trim() || !newTemplatePrompt.trim()) return;
    try {
      if (editingTemplateId) {
        await updateTemplate(editingTemplateId, { name: newTemplateName, prompt_text: newTemplatePrompt, language: newTemplateLanguage });
      } else {
        await createTemplate(newTemplateName, newTemplatePrompt, newTemplateLanguage);
      }
      setNewTemplateName(''); setNewTemplatePrompt(''); setEditingTemplateId(null);
      setNewTemplateLanguage(languageOptions[0]); setShowTemplateForm(false);
      handleFetchTemplates();
    } catch (err) { handleError(err); }
  };

  const handleEditTemplate = (template: Template) => {
    setEditingTemplateId(template.id);
    setNewTemplateName(template.name);
    setNewTemplatePrompt(template.prompt_text);
    setNewTemplateLanguage(template.language);
    setShowTemplateForm(true);
  };

  const handleCancelEdit = () => {
    setEditingTemplateId(null);
    setNewTemplateName('');
    setNewTemplatePrompt('');
    setNewTemplateLanguage(languageOptions[0]);
    setShowTemplateForm(false);
  };

  const handleDeleteTemplate = async (templateId: number) => {
    if (!window.confirm("Delete this template? (Generated results will not be affected)")) return; // MSG-007
    try {
      await deleteTemplate(templateId);
      handleFetchTemplates();
    } catch (err) { handleError(err); }
  };

  const handleDeleteAllTemplates = async () => {
    if (!window.confirm("Delete ALL templates? This action cannot be undone.")) return; // MSG-008
    try {
      await deleteAllTemplates();
      handleFetchTemplates();
    } catch (err) { handleError(err); }
  };

  const handleRunReport = async (templateId: number) => {
    if (!sourceId) return;
    setRunningReports(prev => new Set(prev).add(templateId));
    setErrorMessage('');
    try {
      const response = await runReport(sourceId, templateId, selectedModel);
      setReportResults(prev => ({ ...prev, [templateId]: response.data.report_text }));
      // REQUIREMENT 4: Store the prompt from API response
      if (response.data.prompt) {
        setReportPrompts(prev => ({ ...prev, [templateId]: response.data.prompt }));
      }
    } catch (err) { handleError(err); }
    finally {
      setRunningReports(prev => {
        const next = new Set(prev);
        next.delete(templateId);
        return next;
      });
    }
  };

  const handleClearReport = (templateId: number) => {
    setReportResults(prev => {
      const next = { ...prev };
      delete next[templateId];
      return next;
    });
    // REQUIREMENT 4: Also clear the stored prompt
    setReportPrompts(prev => {
      const next = { ...prev };
      delete next[templateId];
      return next;
    });
  };

  const handleClearAllReports = () => {
    setReportResults({});
    // REQUIREMENT 4: Also clear all stored prompts
    setReportPrompts({});
  };

  const handleToggleResultVisibility = (templateId: number) => {
    setHiddenResults(prev => {
      const next = new Set(prev);
      if (next.has(templateId)) {
        next.delete(templateId);
      } else {
        next.add(templateId);
      }
      return next;
    });
  };

  const handleFetchConfig = async () => {
    try {
      const response = await getConfig();
      setConfig(response.data);
      setSelectedModel(response.data.default_model);
    } catch (err) { handleError(err); }
  };

  const handleConfigChange = (field: keyof Config | `api_keys.${keyof Config['api_keys']}`, value: string) => {
    setConfig(prevConfig => {
      if (!prevConfig) return null;
      const newConfig = JSON.parse(JSON.stringify(prevConfig));
      if (field.startsWith('api_keys.')) {
        const key = field.split('.')[1] as keyof Config['api_keys'];
        newConfig.api_keys[key] = value;
      } else {
        (newConfig as any)[field] = value;
      }
      return newConfig;
    });
  };

  const handleConfigSave = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!config) return;
    try {
      await updateConfig(config);
      setConfigStatus('Settings saved successfully!');
      setSelectedModel(config.default_model);
      fetchAvailableModels();  // STEP 4: Refresh models after saving API keys
      setTimeout(() => setConfigStatus(''), 3000);
    } catch (err) {
      handleError(err);
      setConfigStatus('Failed to save settings.');
    }
  };

  // STEP 7: Toggle password visibility
  const togglePasswordVisibility = (provider: string) => {
    setShowPasswords(prev => ({
      ...prev,
      [provider]: !prev[provider]
    }));
  };

  // STEP 9: Check backend health
  const checkBackendHealth = async () => {
    setIsCheckingConnection(true);
    try {
      const response = await fetch(`http://127.0.0.1:${backendPort}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(3000) // 3 second timeout
      });
      
      if (response.ok) {
        setBackendConnected(true);
        setConnectionError('');
        
        // STEP 9: Refetch data after successful reconnection
        handleFetchConfig();
        handleFetchTemplates();
        fetchAvailableModels();  // STEP 4: Refresh models after reconnection
        
        return true;
      } else {
        throw new Error('Backend returned non-OK status');
      }
    } catch (error) {
      setBackendConnected(false);
      setConnectionError('Cannot connect to backend server');
      return false;
    } finally {
      setIsCheckingConnection(false);
    }
  };

  // REQUIREMENT 5.5: API Testing Handler Functions
  const handleTestConnection = async (provider: string) => {
    // Clear existing timeout for this provider if any (using ref for current value)
    if (statusTimeoutsRef.current[provider]) {
      clearTimeout(statusTimeoutsRef.current[provider]);
      delete statusTimeoutsRef.current[provider]; // Clean up reference
    }
    
    setTestingStatus(prev => ({ ...prev, [provider]: 'testing' }));
    setTestResults(prev => ({ ...prev, [provider]: null }));
    
    try {
      const response = await testApiConnection(provider);
      setTestResults(prev => ({ ...prev, [provider]: response.data }));
      setTestingStatus(prev => ({ ...prev, [provider]: response.data.success ? 'success' : 'error' }));
      
      // Set timeout to clear status after 15 seconds
      const timeoutId = setTimeout(() => {
        setTestingStatus(prev => {
          const newStatus = { ...prev };
          delete newStatus[provider];
          return newStatus;
        });
        setTestResults(prev => {
          const newResults = { ...prev };
          delete newResults[provider];
          return newResults;
        });
        // Clean up timeout reference when it fires
        delete statusTimeoutsRef.current[provider];
      }, 15000); // 15 seconds
      
      // Store timeout directly in ref (immediate, no async batching)
      statusTimeoutsRef.current[provider] = timeoutId;
      
    } catch (err) {
      const errorResult: ApiTestResult = {
        success: false,
        message: `Connection test failed: ${err instanceof Error ? err.message : 'Unknown error'}`,
        provider,
        error: err instanceof Error ? err.message : 'Unknown error'
      };
      setTestResults(prev => ({ ...prev, [provider]: errorResult }));
      setTestingStatus(prev => ({ ...prev, [provider]: 'error' }));
      
      // Set timeout for error status too
      const timeoutId = setTimeout(() => {
        setTestingStatus(prev => {
          const newStatus = { ...prev };
          delete newStatus[provider];
          return newStatus;
        });
        setTestResults(prev => {
          const newResults = { ...prev };
          delete newResults[provider];
          return newResults;
        });
        // Clean up timeout reference when it fires
        delete statusTimeoutsRef.current[provider];
      }, 15000); // 15 seconds
      
      // Store timeout directly in ref (immediate, no async batching)
      statusTimeoutsRef.current[provider] = timeoutId;
    }
  };

  const handleTestAllConnections = async () => {
    const providers = ['ollama', 'openai', 'anthropic', 'google'];
    
    // Clear any existing timeouts for all providers before starting (using ref for current values)
    providers.forEach(provider => {
      if (statusTimeoutsRef.current[provider]) {
        clearTimeout(statusTimeoutsRef.current[provider]);
        delete statusTimeoutsRef.current[provider]; // Clean up reference
      }
    });
    
    // Set flag to indicate "Test All" was clicked
    setIsTestingAll(true);
    
    // Set all to testing
    const testingState = providers.reduce((acc, provider) => {
      acc[provider] = 'testing';
      return acc;
    }, {} as {[key: string]: 'idle' | 'testing' | 'success' | 'error'});
    setTestingStatus(testingState);
    
    try {
      const response = await getAllApiStatus();
      const results = response.data.results;
      
      // Update individual results
      setTestResults(results);
      
      // Update status for each provider
      const newStatus = providers.reduce((acc, provider) => {
        acc[provider] = results[provider]?.success ? 'success' : 'error';
        return acc;
      }, {} as {[key: string]: 'idle' | 'testing' | 'success' | 'error'});
      setTestingStatus(newStatus);
      
      // Set timeouts to auto-hide status after 15 seconds for each provider
      providers.forEach(provider => {
        const timeoutId = setTimeout(() => {
          setTestingStatus(prev => {
            const updated = { ...prev };
            delete updated[provider];
            return updated;
          });
          setTestResults(prev => {
            const updated = { ...prev };
            delete updated[provider];
            return updated;
          });
          // Clean up timeout reference when it fires
          delete statusTimeoutsRef.current[provider];
        }, 15000); // 15 seconds
        
        // Store timeout directly in ref (immediate, no async batching)
        statusTimeoutsRef.current[provider] = timeoutId;
      });
      
      // Clear flag when done
      setIsTestingAll(false);
      
    } catch (err) {
      // Set all to error on failure
      const errorState = providers.reduce((acc, provider) => {
        acc[provider] = 'error';
        return acc;
      }, {} as {[key: string]: 'idle' | 'testing' | 'success' | 'error'});
      setTestingStatus(errorState);
      
      // Set timeouts to auto-hide error status after 15 seconds for each provider
      providers.forEach(provider => {
        const timeoutId = setTimeout(() => {
          setTestingStatus(prev => {
            const updated = { ...prev };
            delete updated[provider];
            return updated;
          });
          setTestResults(prev => {
            const updated = { ...prev };
            delete updated[provider];
            return updated;
          });
          // Clean up timeout reference when it fires
          delete statusTimeoutsRef.current[provider];
        }, 15000); // 15 seconds
        
        // Store timeout directly in ref (immediate, no async batching)
        statusTimeoutsRef.current[provider] = timeoutId;
      });
      
      handleError(err);
      
      // Clear flag even on error
      setIsTestingAll(false);
    }
  };

  const getStatusIcon = (provider: string) => {
    const status = testingStatus[provider] || 'idle';
    switch (status) {
      case 'testing': return '⏳';
      case 'success': return '✅';
      case 'error': return '❌';
      default: return '';
    }
  };

  const getStatusText = (provider: string) => {
    const status = testingStatus[provider] || 'idle';
    const result = testResults[provider];
    
    if (status === 'testing') return 'Testing...';
    if (status === 'success') return 'Working';
    if (status === 'error' && result) return result.message;
    return '';
  };

  // REQUIREMENT 2: Updated handleClearAndResetAll function
  const handleClearAndResetAll = (): boolean => {
    if (!window.confirm("Clear all content? This will remove the transcription, summary, overview, reports, and chat history. This action cannot be undone.")) { // MSG-009
      return false; // User cancelled
    }
    
    // Store current view to restore after reset
    const currentViewBeforeReset = currentView;
    
    // Clear URL input
    setUrlInput('');
    
    // Reset file input
    const fileInput = document.getElementById('file-upload') as HTMLInputElement;
    if (fileInput) fileInput.value = '';
    
    // Reset all content state
    resetState();
    
    // REQUIREMENT 2: Restore the view user was on
    setCurrentView(currentViewBeforeReset);
    
    // REQUIREMENT 2: If user was on chat tab, restore input focus after React re-renders
    if (currentViewBeforeReset === 'chat') {
      setTimeout(() => {
        const chatInput = document.querySelector('.chat-input-form input') as HTMLInputElement;
        if (chatInput) {
          chatInput.focus();
        }
      }, 100); // Small delay to ensure React has re-rendered
    }
    
    return true; // Reset completed successfully
  };

  // FIXED: Model change handler with reset - checks if reset was successful
  const handleModelChange = (newModel: string) => {
    if (sourceId) {
      // First confirmation: warn about content loss
      if (!window.confirm("Change AI model? This will clear all current content.")) { // MSG-010
        return; // Path 1: User cancelled - keep current model
      }
      
      // Second confirmation: in handleClearAndResetAll
      const resetSuccessful = handleClearAndResetAll();
      
      if (!resetSuccessful) {
        return; // Path 3: User cancelled second dialog - keep current model
      }
      // Path 2: Both confirmations accepted - model will change below
    }
    
    setSelectedModel(newModel); // Only reached if no content OR reset successful
  };

  const handleExport = async (
    contentType: 'transcript' | 'summary' | 'overview' | 'report',
    format: 'txt' | 'md',
    templateId?: number
  ) => {
    if (!sourceId) return;
    const exportKey = `${contentType}-${format}-${templateId || sourceId}`;
    setExportingState(prev => new Set(prev).add(exportKey));
    
    try {
      // Get the displayed content based on content type
      let displayedContent: string | undefined = undefined;
      
      switch (contentType) {
        case 'transcript':
          displayedContent = transcription || undefined;
          break;
        case 'summary':
          displayedContent = summary || undefined;
          break;
        case 'overview':
          displayedContent = overviewText || undefined;
          break;
        case 'report':
          if (templateId) {
            displayedContent = reportResults[templateId] || undefined;
          }
          break;
      }
      
      // Build request body - only include fields with values
      const requestBody: {
        source_id: number;
        content_type: string;
        format: string;
        model_key: string;
        template_id?: number;
        content?: string;
      } = {
        source_id: sourceId,
        content_type: contentType,
        format: format,
        model_key: selectedModel,
      };
      
      // Only include optional fields if they have values
      if (templateId !== undefined) {
        requestBody.template_id = templateId;
      }
      if (displayedContent) {
        requestBody.content = displayedContent;
      }
      
      console.log('Export request:', requestBody);
      
      const response = await exportContent(requestBody);
      
      // Determine MIME type based on format
      const mimeType = format === 'md' ? 'text/markdown' : 'text/plain';
      
      // Create Blob with proper MIME type
      const url = window.URL.createObjectURL(new Blob([response.data], { type: mimeType }));
      const link = document.createElement('a');
      link.href = url;
      
      // Parse filename from Content-Disposition header
      const disposition = response.headers['content-disposition'];
      let filename = `export.${format}`;
      if (disposition && disposition.indexOf('attachment') !== -1) {
        const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
        const matches = filenameRegex.exec(disposition);
        if (matches != null && matches[1]) {
          filename = matches[1].replace(/['"]/g, '');
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export error:', err);
      handleError(err);
    } finally {
      setExportingState(prev => {
        const next = new Set(prev);
        next.delete(exportKey);
        return next;
      });
    }
  };

  const handleSaveAudio = async () => {
    if (!audioUrl) return;
    const exportKey = 'audio-save';
    setExportingState(prev => new Set(prev).add(exportKey));
    try {
      const filename = audioUrl.substring(audioUrl.lastIndexOf('/') + 1);
      const result = await (window as any).electronAPI.saveAudio({ url: audioUrl, filename });
      if (!result.success) {
        console.error("Save audio failed:", result.error);
        // MSG-001: Ensure proper punctuation
        const errorMsg = result.error.trim();
        const punctuatedError = errorMsg.match(/[.!?]$/) ? errorMsg : `${errorMsg}.`;
        showToastNotification(`Unable to save audio file. ${punctuatedError}`);
      } else {
        console.log("Audio saved successfully to:", result.filePath);
      }
    } catch (err) {
      console.error("IPC Error:", err);
      showToastNotification("Unable to save the audio file. Please try again."); // MSG-002
    } finally {
      setExportingState(prev => {
        const next = new Set(prev);
        next.delete(exportKey);
        return next;
      });
    }
  };

  return (
    <>
      {/* STEP 2: Toast Notification */}
      {showToast && (
        <div className="toast-notification">
          <div className="toast-content">
            <span className="toast-icon">⚠️</span>
            <span className="toast-message">{toastMessage}</span>
            <button className="toast-close" onClick={closeToast}>×</button>
          </div>
        </div>
      )}

      <div className="container">
      <div className="sidebar">
        {/* BOX 1: Header (NO label) */}
        <div className="sidebar-box">
          <h1>InsightsLM</h1>
        </div>

        {/* BOX 2: AI Model (WITH label) */}
        <fieldset className="sidebar-box">
          <legend>AI Model</legend>
          <select 
            className="model-select-full"
            value={selectedModel} 
            onChange={(e) => handleModelChange(e.target.value)}
            disabled={modelsLoading}
          >
            {modelsLoading ? (
              <option>Loading models...</option>
            ) : availableModels.length > 0 ? (
              availableModels.map(model => (
                <option key={model.key} value={model.key}>
                  {model.label}
                </option>
              ))
            ) : (
              <option value="">No models available</option>
            )}
          </select>
        </fieldset>

        {/* BOX 3: File Input (WITH label) */}
        <fieldset className="sidebar-box">
          <legend>File Input</legend>
          
          {/* Drag & Drop Zone */}
          <div 
            className={`drop-zone ${isDragging ? 'dragging' : ''}`}
            onDragEnter={handleDragEnter}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <p>📁 Drag & drop files here</p>
          </div>

          {/* Choose File Button */}
          <button 
            className="choose-file-btn" 
            onClick={handleChooseFileClick}
            disabled={status === 'downloading' || status === 'uploading'}
          >
            Choose File
          </button>
          <input 
            ref={fileInputRef}
            type="file" 
            onChange={handleFileChange} 
            disabled={status === 'downloading' || status === 'uploading'}
            style={{ display: 'none' }}
          />

          {/* URL Input Section */}
          <div className="url-input-box">
            <input 
              type="text" 
              value={urlInput} 
              onChange={(e) => setUrlInput(e.target.value)} 
              placeholder="Enter video or audio URL" 
              disabled={status === 'downloading' || status === 'uploading'} 
            />
            <button 
              onClick={handleUrlSubmit} 
              disabled={status === 'downloading' || status === 'uploading'}
            >
              Go
            </button>
          </div>
        </fieldset>

        {/* BOX 4: Progress (NO label, CONDITIONAL) */}
        {(status === 'uploading' || status === 'downloading') && (
          <div className="sidebar-box">
            {status === 'uploading' && (
              <>
                <div className="progress-bar-container">
                  <div className="progress-bar" style={{ width: `${typeof uploadProgress === 'number' && isFinite(uploadProgress) ? uploadProgress : 0}%` }} />
                  <div className="progress-text">{Math.round(typeof uploadProgress === 'number' && isFinite(uploadProgress) ? uploadProgress : 0)}%</div>
                </div>
                <p className="status-message">
                  {uploadProgress < 100 ? "Uploading file..." : "Waiting for transcript..."}
                </p>
              </>
            )}
            {status === 'downloading' && (
              <p className="status-message">Downloading & Processing...</p>
            )}
          </div>
        )}

        {/* BOX 5: Actions (WITH label, CONDITIONAL) */}
        {sourceId && (
          <fieldset className="sidebar-box">
            <legend>Actions</legend>
            <div className="actions">
              <button onClick={handleSummarize} disabled={isSummarizing}>
                {isSummarizing ? 'Summarizing...' : 'Generate Summary'}
              </button>
              <button onClick={handleCreateAudioOverview} disabled={isGeneratingAudio}>
                {isGeneratingAudio ? 'Generating Audio...' : 'Create Audio Overview'}
              </button>
              <button 
                onClick={handleClearAndResetAll}
                className="reset-button"
              >
                Clear & Reset All
              </button>
            </div>
          </fieldset>
        )}
      </div>

      <div className="main-content">
        <div className="view-switcher">
          <button onClick={() => setCurrentView('transcript')} className={currentView === 'transcript' ? 'active' : ''}>Transcript</button>
          <button onClick={() => setCurrentView('chat')} className={currentView === 'chat' ? 'active' : ''}>Chat</button>
          <button onClick={() => setCurrentView('summary')} className={currentView === 'summary' ? 'active' : ''}>Summary</button>
          <button onClick={() => setCurrentView('overview')} className={currentView === 'overview' ? 'active' : ''}>Overview</button>
          <button onClick={() => setCurrentView('reports')} className={currentView === 'reports' ? 'active' : ''}>Reports</button>
          <button onClick={() => setCurrentView('settings')} className={currentView === 'settings' ? 'active' : ''}>Settings</button>
        </div>

        {currentView === 'settings' && (
          <div className="settings-content">
            <div className="settings-header">
              <h2>Settings</h2>
              {/* STEP 9: Connection Status Indicator */}
              <div className={`connection-status ${backendConnected ? 'connected' : 'disconnected'}`}>
                <span className="status-dot"></span>
                <span className="status-text">
                  Backend: {isCheckingConnection ? 'Checking...' : (backendConnected ? `Connected on port ${backendPort}` : 'Disconnected')}
                </span>
              </div>
            </div>

            {/* STEP 9: Backend Error Message */}
            {!backendConnected && connectionError && (
              <div className="backend-error-message">
                <div className="error-icon">⚠️</div>
                <div className="error-content">
                  <h3>Backend Server Not Running</h3>
                  <p>Start the backend to use InsightsLM:</p>
                  
                  <div className="error-section">
                    <strong>🚀 Quick Start (Recommended):</strong>
                    <code>cd ~/InsightsLM && ./start-insightslm.sh</code>
                  </div>
                  
                  <div className="error-section">
                    <strong>📖 Manual Start:</strong>
                    <ol>
                      <li>cd ~/InsightsLM/backend</li>
                      <li>source venv/bin/activate</li>
                      <li>uvicorn main:app --reload --host 0.0.0.0 --port 8000</li>
                    </ol>
                  </div>
                  
                  <button 
                    type="button"
                    className="retry-connection-btn"
                    onClick={checkBackendHealth}
                    disabled={isCheckingConnection}
                  >
                    {isCheckingConnection ? 'Checking...' : 'Retry Connection'}
                  </button>
                </div>
              </div>
            )}

            {config ? (
              <form className="settings-form" onSubmit={handleConfigSave}>
                <div className="form-group">
                  <label htmlFor="default-model-select">Default AI Model</label>
                  <select 
                    id="default-model-select" 
                    value={config.default_model} 
                    onChange={(e) => handleConfigChange('default_model', e.target.value)}
                    disabled={modelsLoading}
                  >
                    {modelsLoading ? (
                      <option>Loading models...</option>
                    ) : availableModels.length > 0 ? (
                      availableModels.map(model => (
                        <option key={model.key} value={model.key}>{model.label}</option>
                      ))
                    ) : (
                      <option value="">No models available</option>
                    )}
                  </select>
                </div>

                <div className="api-section">
                  <div className="api-section-header">
                    <h3>API Keys</h3>
                    <button 
                      type="button" 
                      className="secondary-action"
                      onClick={handleTestAllConnections}
                      disabled={Object.values(testingStatus).some(status => status === 'testing')}
                    >
                      {isTestingAll ? 'Testing All...' : 'Test All Connections'}
                    </button>
                  </div>

                  {/* STEP 5: Security Notice Banner */}
                  <div className="security-notice">
                    <span className="security-icon">🔒</span>
                    <span className="security-text">
                      API keys are encrypted using your system's secure storage
                    </span>
                  </div>

                  {/* Ollama Section */}
                  <div className="form-group api-key-group">
                    <label htmlFor="ollama-status">Ollama (Local)</label>
                    <div className="api-test-row">
                      <span className="api-status-display">Local installation - no key required</span>
                      <button 
                        type="button"
                        className="test-connection-btn"
                        onClick={() => handleTestConnection('ollama')}
                        disabled={testingStatus['ollama'] === 'testing'}
                      >
                        {testingStatus['ollama'] === 'testing' ? 'Testing...' : 'Test Connection'}
                      </button>
                      <span className="status-indicator">
                        {getStatusIcon('ollama')} {getStatusText('ollama')}
                      </span>
                    </div>
                  </div>

                  {/* OpenAI Section */}
                  <div className="form-group api-key-group">
                    <label htmlFor="openai-key">
                      OpenAI API Key
                      <a 
                        href="https://platform.openai.com/api-keys" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="help-link"
                        title="Get your OpenAI API key"
                      >
                        ❓
                      </a>
                    </label>
                    <div className="api-test-row">
                      <div className="password-input-wrapper">
                        <input 
                          id="openai-key" 
                          type={showPasswords.openai ? "text" : "password"}
                          value={config.api_keys.openai} 
                          onChange={(e) => handleConfigChange('api_keys.openai', e.target.value)} 
                          placeholder="sk-..." 
                        />
                        <button
                          type="button"
                          className="password-toggle-btn"
                          onClick={() => togglePasswordVisibility('openai')}
                          title={showPasswords.openai ? "Hide API key" : "Show API key"}
                        >
                          {showPasswords.openai ? '👁️' : '👁️‍🗨️'}
                        </button>
                      </div>
                      <button 
                        type="button"
                        className="test-connection-btn"
                        onClick={() => handleTestConnection('openai')}
                        disabled={testingStatus['openai'] === 'testing' || !config.api_keys.openai.trim()}
                        title={!config.api_keys.openai.trim() ? 'Enter API key first' : 'Test OpenAI connection'}
                      >
                        {testingStatus['openai'] === 'testing' ? 'Testing...' : 'Test Connection'}
                      </button>
                      <span className="status-indicator">
                        {getStatusIcon('openai')} {getStatusText('openai')}
                      </span>
                    </div>
                  </div>

                  {/* Anthropic Section */}
                  <div className="form-group api-key-group">
                    <label htmlFor="anthropic-key">
                      Anthropic API Key
                      <a 
                        href="https://console.anthropic.com/settings/keys" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="help-link"
                        title="Get your Anthropic API key"
                      >
                        ❓
                      </a>
                    </label>
                    <div className="api-test-row">
                      <div className="password-input-wrapper">
                        <input 
                          id="anthropic-key" 
                          type={showPasswords.anthropic ? "text" : "password"}
                          value={config.api_keys.anthropic} 
                          onChange={(e) => handleConfigChange('api_keys.anthropic', e.target.value)} 
                          placeholder="sk-ant-..." 
                        />
                        <button
                          type="button"
                          className="password-toggle-btn"
                          onClick={() => togglePasswordVisibility('anthropic')}
                          title={showPasswords.anthropic ? "Hide API key" : "Show API key"}
                        >
                          {showPasswords.anthropic ? '👁️' : '👁️‍🗨️'}
                        </button>
                      </div>
                      <button 
                        type="button"
                        className="test-connection-btn"
                        onClick={() => handleTestConnection('anthropic')}
                        disabled={testingStatus['anthropic'] === 'testing' || !config.api_keys.anthropic.trim()}
                        title={!config.api_keys.anthropic.trim() ? 'Enter API key first' : 'Test Anthropic connection'}
                      >
                        {testingStatus['anthropic'] === 'testing' ? 'Testing...' : 'Test Connection'}
                      </button>
                      <span className="status-indicator">
                        {getStatusIcon('anthropic')} {getStatusText('anthropic')}
                      </span>
                    </div>
                  </div>

                  {/* Google Section */}
                  <div className="form-group api-key-group">
                    <label htmlFor="google-key">
                      Google Gemini API Key
                      <a 
                        href="https://makersuite.google.com/app/apikey" 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="help-link"
                        title="Get your Google Gemini API key"
                      >
                        ❓
                      </a>
                    </label>
                    <div className="api-test-row">
                      <div className="password-input-wrapper">
                        <input 
                          id="google-key" 
                          type={showPasswords.google ? "text" : "password"}
                          value={config.api_keys.google} 
                          onChange={(e) => handleConfigChange('api_keys.google', e.target.value)} 
                          placeholder="AIza..." 
                        />
                        <button
                          type="button"
                          className="password-toggle-btn"
                          onClick={() => togglePasswordVisibility('google')}
                          title={showPasswords.google ? "Hide API key" : "Show API key"}
                        >
                          {showPasswords.google ? '👁️' : '👁️‍🗨️'}
                        </button>
                      </div>
                      <button 
                        type="button"
                        className="test-connection-btn"
                        onClick={() => handleTestConnection('google')}
                        disabled={testingStatus['google'] === 'testing' || !config.api_keys.google.trim()}
                        title={!config.api_keys.google.trim() ? 'Enter API key first' : 'Test Google Gemini connection'}
                      >
                        {testingStatus['google'] === 'testing' ? 'Testing...' : 'Test Connection'}
                      </button>
                      <span className="status-indicator">
                        {getStatusIcon('google')} {getStatusText('google')}
                      </span>
                    </div>
                  </div>
                </div>

                <h3>Data Storage</h3>
                <div className="form-group">
                  <label htmlFor="data-path">Data Storage Path (Read-only)</label>
                  <input 
                    id="data-path" 
                    type="text" 
                    value={config.data_storage_path} 
                    readOnly 
                    disabled 
                  />
                  <small>⚠️ This path contains all your data (transcripts, embeddings, and encrypted API keys). It's set on first launch and cannot be changed to prevent data loss.</small>
                </div>

                <div className="form-actions">
                  <button type="submit" className="primary-action">Save Settings</button>
                  {configStatus && <span className="config-status">{configStatus}</span>}
                </div>
              </form>
            ) : (
              <p>Loading settings...</p>
            )}
          </div>
        )}

        {sourceId ? (
          <>
            {currentView === 'transcript' && (
              <div className="results-box">
                <div className="tab-header">
                  <h2>Transcription</h2>
                  <div className="header-actions">
                    <button className="secondary-action" onClick={() => handleExport('transcript', 'txt')} disabled={exportingState.has(`transcript-txt-${sourceId}`)}>
                      {exportingState.has(`transcript-txt-${sourceId}`) ? 'Exporting...' : 'Export as .txt'}
                    </button>
                    <button className="secondary-action" onClick={() => handleExport('transcript', 'md')} disabled={exportingState.has(`transcript-md-${sourceId}`)}>
                      {exportingState.has(`transcript-md-${sourceId}`) ? 'Exporting...' : 'Export as .md'}
                    </button>
                  </div>
                </div>
                <textarea value={transcription} readOnly />
              </div>
            )}

            {currentView === 'summary' && (
              <div className="summary-content">
                <div className="tab-header">
                  <h2>Summary</h2>
                  <div className="header-actions">
                    <button 
                      className="secondary-action" 
                      onClick={() => {
                        if (summaryPrompt) {
                          const formattedPrompt = formatPromptForDisplay(summaryPrompt, selectedModel, new Date(), 'summary');
                          setCurrentPromptContent(formattedPrompt);
                          setShowPromptModal(true);
                        } else {
                          showToastNotification('No prompt available yet. Please generate a summary first.'); // MSG-003
                        }
                      }}
                    >
                      View Prompt
                    </button>
                    {summary && !isSummarizing && (
                      <>
                        <button className="secondary-action" onClick={() => handleExport('summary', 'txt')} disabled={exportingState.has(`summary-txt-${sourceId}`)}>
                          {exportingState.has(`summary-txt-${sourceId}`) ? 'Exporting...' : 'Export as .txt'}
                        </button>
                        <button className="secondary-action" onClick={() => handleExport('summary', 'md')} disabled={exportingState.has(`summary-md-${sourceId}`)}>
                          {exportingState.has(`summary-md-${sourceId}`) ? 'Exporting...' : 'Export as .md'}
                        </button>
                      </>
                    )}
                  </div>
                </div>
                {isSummarizing && <p>Generating summary...</p>}
                {!isSummarizing && errorMessage && <p className="error">{errorMessage}</p>}
                <p className="summary-text">{summary}</p>
              </div>
            )}

            {currentView === 'overview' && (
              <div className="overview-content">
                <div className="tab-header">
                  <h2>Audio Overview</h2>
                </div>
                {isGeneratingAudio && <p>Generating overview and audio...</p>}
                {!isGeneratingAudio && errorMessage && <p className="error">{errorMessage}</p>}
                {audioUrl && (
                  <div className="audio-player-box">
                    <audio 
                      key={audioUrl} 
                      controls 
                      src={audioUrl}
                      onLoadedMetadata={(e) => {
                        try {
                          // Safely validate and reset audio position
                          if (e?.target && e.target instanceof HTMLAudioElement) {
                            const audio = e.target;
                            // Only reset if not already at start
                            if (audio.currentTime !== 0 && !isNaN(audio.duration)) {
                              audio.currentTime = 0;
                            }
                          }
                        } catch (error) {
                          console.warn('Error resetting audio position:', error);
                          // Non-critical error - audio still playable
                        }
                      }}
                    >
                      Your browser does not support the audio element.
                    </audio>
                  </div>
                )}
                <div className="export-actions">
                  <button 
                    className="secondary-action" 
                    onClick={() => {
                      if (overviewPrompt) {
                        const formattedPrompt = formatPromptForDisplay(overviewPrompt, selectedModel, new Date(), 'overview');
                        setCurrentPromptContent(formattedPrompt);
                        setShowPromptModal(true);
                      } else {
                        showToastNotification('No prompt available yet. Please generate an overview first.'); // MSG-004
                      }
                    }}
                  >
                    View Prompt
                  </button>
                  {overviewText && (
                    <>
                      <button className="secondary-action" onClick={handleSaveAudio} disabled={exportingState.has('audio-save')}>
                        {exportingState.has('audio-save') ? 'Saving...' : 'Save Audio As...'}
                      </button>
                      <button className="secondary-action" onClick={() => handleExport('overview', 'txt')} disabled={exportingState.has(`overview-txt-${sourceId}`)}>
                        {exportingState.has(`overview-txt-${sourceId}`) ? 'Exporting...' : 'Export as .txt'}
                      </button>
                      <button className="secondary-action" onClick={() => handleExport('overview', 'md')} disabled={exportingState.has(`overview-md-${sourceId}`)}>
                        {exportingState.has(`overview-md-${sourceId}`) ? 'Exporting...' : 'Export as .md'}
                      </button>
                    </>
                  )}
                </div>
                {overviewText && (
                  <>
                    <hr />
                    <p className="summary-text">{overviewText}</p>
                  </>
                )}
              </div>
            )}

            {currentView === 'chat' && (
              <div className="chat-container">
                <div className="chat-messages">
                  {chatMessages.map((msg, index) => (
                    <div key={index} className={`message-wrapper ${msg.sender}`}>
                      <div className="message"><p>{msg.text}</p></div>
                      {msg.sender === 'ai' && msg.citations && msg.citations.length > 0 && (
                        <div className="citations-container">
                          <h5>Sources:</h5>
                          {msg.citations.map((citation, cIndex) => (
                            <div key={cIndex} className="citation-card">
                              <span className="citation-time">{formatTime(citation.start_time)}</span>
                              <p className="citation-text">"{citation.text}"</p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                  {isThinking && (<div className="message-wrapper ai"><div className="message"><p>Thinking...</p></div></div>)}
                </div>
                {chatPrompts.length > 0 && (
                  <div style={{ padding: '0.5rem 1rem', borderTop: '1px solid #dee2e6' }}>
                    <button 
                      className="secondary-action"
                      onClick={() => {
                        const lastPrompt = chatPrompts[chatPrompts.length - 1];
                        const formattedPrompt = formatPromptForDisplay(lastPrompt, selectedModel, new Date(), 'chat');
                        handleOpenPromptModal(formattedPrompt);
                      }}
                    >
                      View Last Prompt
                    </button>
                  </div>
                )}
                <form onSubmit={handleQuerySubmit} className="chat-input-form">
                  <input ref={chatInputRef} type="text" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Ask a question..." disabled={isThinking} />
                  <button type="submit" disabled={isThinking}>Send</button>
                </form>
              </div>
            )}

            {currentView === 'reports' && (
              <div className="reports-content">
                <h2>Custom Reports</h2>
                <div className="reports-actions">
                  <button className="primary-action" onClick={() => setShowTemplateForm(prev => !prev)}>{showTemplateForm ? 'Cancel' : 'Add New Template'}</button>
                  <button className="secondary-action" onClick={handleClearAllReports} disabled={Object.keys(reportResults).length === 0}>Clear All Results</button>
                  <button className="delete-button" onClick={handleDeleteAllTemplates}>Delete All Templates</button>
                </div>
                {showTemplateForm && (
                  <form onSubmit={handleSaveTemplate} className="template-form">
                    <h3>{editingTemplateId ? 'Edit Report Template' : 'New Report Template'}</h3>
                    <input type="text" placeholder="Template Name" value={newTemplateName} onChange={e => setNewTemplateName(e.target.value)} required />
                    <textarea placeholder="Enter your prompt here..." value={newTemplatePrompt} onChange={e => setNewTemplatePrompt(e.target.value)} required />
                    <label htmlFor="language-select">Report Language:</label>
                    <select id="language-select" value={newTemplateLanguage} onChange={e => setNewTemplateLanguage(e.target.value)}>
                      {languageOptions.map(lang => <option key={lang} value={lang}>{lang}</option>)}
                    </select>
                    <button type="submit">{editingTemplateId ? 'Update Template' : 'Save Template'}</button>
                    {editingTemplateId && <button type="button" className="secondary-action" onClick={handleCancelEdit}>Cancel Edit</button>}
                  </form>
                )}
                <div className="template-list">
                  <h3>Available Templates</h3>
                  {templates.length === 0 && !showTemplateForm && <p>No templates found.</p>}
                  {templates.map(template => (
                    <div key={template.id} className="template-item-container">
                      <div className="template-item">
                        <span>{template.name}</span>
                        <div className="template-item-actions">
                          <button onClick={() => handleRunReport(template.id)} disabled={runningReports.has(template.id)}>{runningReports.has(template.id) ? 'Running...' : 'Run'}</button>
                          <button 
                            className="secondary-action" 
                            onClick={() => {
                              const prompt = reportPrompts[template.id];
                              if (prompt) {
                                const formattedPrompt = formatPromptForDisplay(
                                  prompt, 
                                  selectedModel, 
                                  new Date(), 
                                  'report',
                                  template.language
                                );
                                setCurrentPromptContent(formattedPrompt);
                                setShowPromptModal(true);
                              } else {
                                showToastNotification('No prompt available yet. Please run this report first.'); // MSG-005
                              }
                            }}
                          >
                            View Prompt
                          </button>
                          <button className="secondary-action" onClick={() => handleEditTemplate(template)}>Edit</button>
                          <button className="delete-button" onClick={() => handleDeleteTemplate(template.id)}>Delete</button>
                        </div>
                      </div>
                      {reportResults[template.id] && (
                        <div className="report-result">
                          <div className="report-result-header">
                            <h4>Result for "{template.name}"</h4>
                            <div className="report-result-header-actions">
                              <button className="secondary-action" onClick={() => handleExport('report', 'txt', template.id)} disabled={exportingState.has(`report-txt-${template.id}`)}>
                                {exportingState.has(`report-txt-${template.id}`) ? 'Exporting...' : 'Export as .txt'}
                              </button>
                              <button className="secondary-action" onClick={() => handleExport('report', 'md', template.id)} disabled={exportingState.has(`report-md-${template.id}`)}>
                                {exportingState.has(`report-md-${template.id}`) ? 'Exporting...' : 'Export as .md'}
                              </button>
                              <button className="secondary-action" onClick={() => handleToggleResultVisibility(template.id)}>{hiddenResults.has(template.id) ? 'Show' : 'Hide'}</button>
                              <button className="clear-button" onClick={() => handleClearReport(template.id)}>Clear</button>
                            </div>
                          </div>
                          {!hiddenResults.has(template.id) && <pre>{reportResults[template.id]}</pre>}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        ) : (
          currentView !== 'settings' && (
            <div className="placeholder">
              <p>{isLoading ? 'Loading a Transcript...' : 'Your transcription will appear here once a file is processed.'}</p>
            </div>
          )
        )}
      </div>

      {/* REQUIREMENT 4: Prompt Display Modal */}
      {showPromptModal && (
        <div className="modal-backdrop" onClick={handleClosePromptModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Generated Prompt</h3>
              <button 
                className="modal-close-x" 
                onClick={handleClosePromptModal}
                aria-label="Close modal"
              >
                ×
              </button>
            </div>
            
            <div className="modal-body">
              <pre className="prompt-text">{currentPromptContent}</pre>
            </div>
            
            <div className="modal-footer">
              <button 
                className="btn-copy"
                onClick={() => {
                  navigator.clipboard.writeText(currentPromptContent);
                  showToastNotification('Prompt copied to clipboard!'); // MSG-006
                }}
              >
                Copy to Clipboard
              </button>
              <button 
                className="btn-modal-close"
                onClick={handleClosePromptModal}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
    </>
  );
}

export default App;