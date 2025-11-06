import { contextBridge, ipcRenderer } from 'electron';

// This exposes specific, typed functions to the renderer process.
// This is more secure than a generic 'invoke' function.
contextBridge.exposeInMainWorld('electronAPI', {
  // Audio file management
  saveAudio: (args: { url: string; filename?: string }) =>
    ipcRenderer.invoke('save-audio', args),

  // API Key encryption using Electron safeStorage
  encryptApiKey: (plainKey: string): Promise<string | { error: string }> =>
    ipcRenderer.invoke('encrypt-api-key', plainKey),

  decryptApiKey: (encryptedKey: string): Promise<string | { error: string }> =>
    ipcRenderer.invoke('decrypt-api-key', encryptedKey),

  isEncryptionAvailable: (): Promise<boolean> =>
    ipcRenderer.invoke('is-encryption-available'),

  // STEP 10: Backend port management
  // Returns the port number that the backend is running on (8000-8050)
  getBackendPort: (): Promise<number> =>
    ipcRenderer.invoke('get-backend-port'),

  // STEP 30: Navigation event listener
  // Allows renderer to listen for navigation commands from main process (e.g., menu items)
  onNavigateToSettings: (callback: () => void) => {
    const listener = () => callback();
    ipcRenderer.on('navigate-to-settings', listener);
    
    // Return cleanup function to remove listener
    return () => {
      ipcRenderer.removeListener('navigate-to-settings', listener);
    };
  },
});
