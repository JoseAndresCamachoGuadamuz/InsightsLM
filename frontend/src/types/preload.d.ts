/**
 * This interface defines the functions exposed from the preload script via the contextBridge.
 * It ensures that our React code knows the exact signature of the functions it can call.
 */
export interface ElectronAPI {
  // Audio file management
  saveAudio: (args: { url: string; filename?: string }) =>
    Promise<{ success: boolean; error?: string; filePath?: string }>;

  // API Key encryption using Electron safeStorage (Steps 1-3)
  encryptApiKey: (plainKey: string) => Promise<string | { error: string }>;
  decryptApiKey: (encryptedKey: string) => Promise<string | { error: string }>;
  isEncryptionAvailable: () => Promise<boolean>;

  // STEP 10: Backend port management
  // Returns the port number that the backend is running on (8000-8050)
  getBackendPort: () => Promise<number>;

  // STEP 30: Navigation event listener
  // Allows renderer to listen for navigation commands from main process (e.g., File > Settings menu)
  // Returns a cleanup function to remove the listener
  onNavigateToSettings: (callback: () => void) => () => void;
}

/**
 * This extends the global 'window' object in TypeScript's scope.
 * It tells TypeScript that 'window' will have a property named 'electronAPI'
 * with the shape defined by our ElectronAPI interface.
 */
declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}

// This empty export is required to treat this file as a module.
export {};
