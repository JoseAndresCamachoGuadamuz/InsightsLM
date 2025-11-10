import path from 'node:path';
import { app, BrowserWindow, ipcMain, dialog, safeStorage, Menu, shell } from 'electron';
import { net } from 'electron';
import * as fs from 'fs';
import { spawn, ChildProcess } from 'child_process';
import { logInfo, logError, logLine } from './log';

// ===== PLATFORM CONFIGURATION =====
/**
 * Hybrid Architecture Configuration
 * Backend runs in WSL (Python/ML optimized)
 * Frontend runs natively on Windows (Full GPU acceleration)
 */
logInfo('[InsightsLM] Running on native Windows with full hardware acceleration');
logInfo('[InsightsLM] Backend: WSL | Frontend: Native Windows');

// These "magic constants" are provided by the Vite plugin for loading the correct URL/file.
declare const MAIN_WINDOW_VITE_DEV_SERVER_URL: string;
declare const MAIN_WINDOW_VITE_NAME: string;

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (require('electron-squirrel-startup')) {
  app.quit();
}

// ===== STEP 10: BACKEND PROCESS MANAGEMENT =====
/**
 * Global backend process tracking
 * Used to manage the Python backend lifecycle
 */
let backendProcess: ChildProcess | null = null;
let backendPort: number = 8000; // Default port, will be updated after successful start

/**
 * Port configuration for backend fallback
 * Tries ports 8000-8050 (51 ports total)
 */
const PORT_MIN = 8000;
const PORT_MAX = 8050;
const HEALTH_CHECK_MAX_RETRIES = 30; // 30 seconds total
const HEALTH_CHECK_INTERVAL = 1000; // 1 second between checks

/**
 * Try to start the backend on a specific port
 * @param port - Port number to try (8000-8050)
 * @returns Promise<boolean> - true if process spawned successfully
 */
async function tryStartBackendOnPort(port: number): Promise<boolean> {
  return new Promise((resolve) => {
    try {
      logInfo(`[Backend] Attempting to start on port ${port}...`);
      
      // Spawn Python backend via WSL
      // CRITICAL: Must specify Ubuntu distro (not docker-desktop default)
      // CRITICAL: Must run as user (not root) so ~ resolves correctly
      const wslCommand = `cd ~/InsightsLM-new/backend && source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port ${port}`;
      
      // Get WSL username from environment or default to current Windows user
      const wslUser = process.env.WSL_USER || process.env.USERNAME?.toLowerCase() || 'user';
      
      // Use Ubuntu distro explicitly (not docker-desktop)
      // NOTE: Variable named backendProc to avoid conflict with global process object
      const backendProc = spawn('wsl', ['-d', 'Ubuntu', '-u', wslUser, 'bash', '-c', wslCommand], {
        detached: false,
        stdio: ['ignore', 'pipe', 'pipe'], // Proper stdio configuration
        windowsHide: true
      });

      // Line buffering for stdout - accumulate partial lines
      let stdoutBuffer = '';
      
      // Log backend output for debugging
      backendProc.stdout?.on('data', (data) => {
        try {
          const chunk = data?.toString() || '';
          if (!chunk) return;
          
          // Immediately strip ANSI codes from incoming chunk
          const cleanedChunk = chunk.replace(/\x1b\[[0-9;]*[a-zA-Z]/g, '');
          
          // Normalize line endings in the chunk
          const normalizedChunk = cleanedChunk.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
          
          // Add cleaned chunk to buffer
          stdoutBuffer += normalizedChunk;
          
          // Split by newlines
          const lines = stdoutBuffer.split('\n');
          
          // Last element is either empty (if ended with \n) or incomplete line
          const incompleteLine = lines.pop() || '';
          
          // Process all complete lines
          lines.forEach(line => {
            const trimmedLine = line.trim();
            if (trimmedLine.length > 0) {
              const displayLine = trimmedLine.length > 500 
                ? trimmedLine.substring(0, 497) + '...' 
                : trimmedLine;
              // CRITICAL FIX: Use logLine from log module
              // Automatically uses correct line endings (CRLF for PowerShell, LF for WSL)
              logLine(`[Backend:${port}] ${displayLine}`);
            }
          });
          
          // Keep incomplete line in buffer for next iteration
          stdoutBuffer = incompleteLine;
        } catch (error) {
          logError(`[Backend:${port}] Error processing stdout:`, error);
          stdoutBuffer = ''; // Reset buffer on error
        }
      });

      // Line buffering for stderr - accumulate partial lines
      let stderrBuffer = '';

      backendProc.stderr?.on('data', (data) => {
        try {
          const chunk = data?.toString() || '';
          if (!chunk) return;
          
          // Immediately strip ANSI codes from incoming chunk
          const cleanedChunk = chunk.replace(/\x1b\[[0-9;]*[a-zA-Z]/g, '');
          
          // Normalize line endings in the chunk
          const normalizedChunk = cleanedChunk.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
          
          // Add cleaned chunk to buffer
          stderrBuffer += normalizedChunk;
          
          // Split by newlines
          const lines = stderrBuffer.split('\n');
          
          // Last element is either empty (if ended with \n) or incomplete line
          const incompleteLine = lines.pop() || '';
          
          // Process all complete lines
          lines.forEach(line => {
            const trimmedLine = line.trim();
            if (trimmedLine.length > 0) {
              const displayLine = trimmedLine.length > 500 
                ? trimmedLine.substring(0, 497) + '...' 
                : trimmedLine;
              // CRITICAL FIX: Use console.error for stderr
              logLine(`[Backend:${port}] ${displayLine}`);
            }
          });
          
          // Keep incomplete line in buffer for next iteration
          stderrBuffer = incompleteLine;
        } catch (error) {
          logError(`[Backend:${port}] Error processing stderr:`, error);
          stderrBuffer = ''; // Reset buffer on error
        }
      });

      // Handle process exit
      backendProc.on('exit', (code, signal) => {
        logInfo(`[Backend:${port}] Process exited (code: ${code}, signal: ${signal})`);
        if (backendProcess === backendProc) {
          backendProcess = null;
        }
      });

      // Handle spawn errors
      backendProc.on('error', (error) => {
        logError(`[Backend:${port}] Spawn error:`, error);
        resolve(false);
      });

      // If we got here, spawn succeeded (doesn't mean backend is ready yet)
      backendProcess = backendProc;
      resolve(true);

    } catch (error) {
      logError(`[Backend:${port}] Exception during spawn:`, error);
      resolve(false);
    }
  });
}

/**
 * Check if backend is responding on the health endpoint
 * @param port - Port to check
 * @param maxRetries - Maximum number of retry attempts
 * @returns Promise<boolean> - true if backend is healthy
 */
async function checkBackendHealth(port: number, maxRetries: number): Promise<boolean> {
  const healthUrl = `http://127.0.0.1:${port}/health`;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      logInfo(`[Backend:${port}] Health check ${attempt}/${maxRetries}...`);
      
      // Try to fetch health endpoint
      const result = await new Promise<boolean>((resolve) => {
        const request = net.request(healthUrl);
        
        request.on('response', (response) => {
          if (response.statusCode === 200) {
            logInfo(`[Backend:${port}] ✅ Health check passed!`);
            resolve(true);
          } else {
            resolve(false);
          }
        });
        
        request.on('error', (error) => {
          // Expected during startup - backend not ready yet
          resolve(false);
        });
        
        request.end();
      });
      
      if (result) {
        return true;
      }
      
      // Wait before next attempt
      await new Promise(resolve => setTimeout(resolve, HEALTH_CHECK_INTERVAL));
      
    } catch (error) {
      // Continue trying
    }
  }
  
  logError(`[Backend:${port}] ❌ Health check failed after ${maxRetries} attempts`);
  return false;
}

/**
 * Start backend with automatic port fallback
 * Tries ports 8000-8050 until one succeeds
 * @returns Promise with success status, port, and error details
 */
async function startBackendWithFallback(): Promise<{ 
  success: boolean; 
  port?: number; 
  error?: string 
}> {
  logInfo(`[Backend] Starting with port fallback (${PORT_MIN}-${PORT_MAX})...`);
  
  for (let port = PORT_MIN; port <= PORT_MAX; port++) {
    logInfo(`[Backend] Trying port ${port}...`);
    
    // Try to spawn backend on this port
    const spawned = await tryStartBackendOnPort(port);
    
    if (!spawned) {
      logInfo(`[Backend] Port ${port} failed to spawn, trying next...`);
      continue;
    }
    
    // Backend spawned, wait for it to be ready
    const healthy = await checkBackendHealth(port, HEALTH_CHECK_MAX_RETRIES);
    
    if (healthy) {
      logInfo(`[Backend] ✅ Successfully started on port ${port}`);
      backendPort = port;
      return { success: true, port };
    } else {
      // Health check failed, kill this attempt and try next port
      logInfo(`[Backend] Port ${port} health check failed, trying next...`);
      if (backendProcess) {
        backendProcess.kill();
        backendProcess = null;
      }
    }
  }
  
  // All ports failed
  logError(`[Backend] ❌ Failed to start on any port (${PORT_MIN}-${PORT_MAX})`);
  return { 
    success: false, 
    error: `Could not start backend on ports ${PORT_MIN}-${PORT_MAX}.\nAll ports may be in use or WSL may not be available.`
  };
}

/**
 * Create and show loading window during backend initialization
 * @returns BrowserWindow - Loading window instance
 */
function showLoadingWindow(): BrowserWindow {
  const loadingWindow = new BrowserWindow({
    width: 400,
    height: 300,
    frame: false,
    transparent: false,
    resizable: false,
    alwaysOnTop: true,
    center: true,
    backgroundColor: '#1a1a1a',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  // Load inline HTML for loading screen
  const loadingHTML = `
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
          width: 100%; height: 100vh;
          display: flex; flex-direction: column;
          justify-content: center; align-items: center;
          background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
          color: #ffffff;
        }
        .logo {
          font-size: 2rem; font-weight: 700; margin-bottom: 2rem;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .spinner {
          width: 60px; height: 60px; margin: 0 auto 2rem;
          border: 4px solid rgba(102, 126, 234, 0.2);
          border-top: 4px solid #667eea; border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .message { font-size: 1.125rem; color: #e0e0e0; }
        .submessage { font-size: 0.875rem; color: #999; margin-top: 0.5rem; }
      </style>
    </head>
    <body>
      <div class="logo">InsightsLM</div>
      <div class="spinner"></div>
      <div class="message">Starting backend...</div>
      <div class="submessage">This may take a few seconds</div>
    </body>
    </html>
  `;
  
  loadingWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(loadingHTML)}`);
  
  return loadingWindow;
}

/**
 * Show error dialog with Retry/Continue/Quit options
 * @param message - Main error message
 * @param details - Detailed error information
 * @returns Promise<'retry' | 'continue' | 'quit'>
 */
async function showErrorDialog(message: string, details: string): Promise<'retry' | 'continue' | 'quit'> {
  const response = await dialog.showMessageBox({
    type: 'error',
    title: 'InsightsLM Backend Startup Failed',
    message: message,
    detail: details + 
           '\n\n' +
           'Options:\n' +
           '• Retry: Try starting the backend again\n' +
           '• Continue Anyway: Open app (use manual startup script)\n' +
           '• Quit: Close InsightsLM',
    buttons: ['Retry', 'Continue Anyway', 'Quit'],
    defaultId: 0,
    cancelId: 1,
    noLink: true
  });

  if (response.response === 0) return 'retry';
  if (response.response === 1) return 'continue';
  return 'quit';
}

/**
 * Attempt to start backend with retry logic
 * Shows loading screen and handles errors with user feedback
 */
async function startBackendWithRetry(): Promise<boolean> {
  let loadingWindow: BrowserWindow | null = null;
  
  try {
    // Show loading screen
    loadingWindow = showLoadingWindow();
    
    // Try to start backend
    const result = await startBackendWithFallback();
    
    // Close loading window
    if (loadingWindow && !loadingWindow.isDestroyed()) {
      loadingWindow.close();
      loadingWindow = null;
    }
    
    if (result.success) {
      logInfo(`[Backend] ✅ Backend ready on port ${result.port}`);
      return true;
    } else {
      // Backend failed to start - show error dialog
      logError(`[Backend] ❌ Backend failed:`, result.error);
      
      const action = await showErrorDialog(
        'Backend Could Not Start',
        result.error || 'Unknown error occurred during backend startup.'
      );
      
      if (action === 'retry') {
        logInfo('[Backend] User chose to retry...');
        // Recursive retry
        return await startBackendWithRetry();
      } else if (action === 'continue') {
        logInfo('[Backend] User chose to continue without backend...');
        return false; // Continue without backend
      } else {
        logInfo('[Backend] User chose to quit...');
        app.quit();
        return false;
      }
    }
  } catch (error) {
    logError('[Backend] Unexpected error during startup:', error);
    
    // Close loading window if still open
    if (loadingWindow && !loadingWindow.isDestroyed()) {
      loadingWindow.close();
    }
    
    // Show error and let user decide
    const action = await showErrorDialog(
      'Unexpected Error',
      'An unexpected error occurred while starting the backend.\n\n' + String(error)
    );
    
    if (action === 'retry') {
      return await startBackendWithRetry();
    } else if (action === 'continue') {
      return false;
    } else {
      app.quit();
      return false;
    }
  }
}

// ===== MAIN WINDOW CREATION =====
const createWindow = (): void => {
  // Create the browser window with secure webPreferences.
  const mainWindow = new BrowserWindow({
    height: 800,
    width: 1200,
    webPreferences: {
      // FIXED: Preload is in the same directory as main.js after compilation
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  // Load the Vite dev server URL in development, or the local HTML file in production.
  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(MAIN_WINDOW_VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`));
  }

  // STEP 11: Set up application menu
  const menu = createApplicationMenu(mainWindow);
  Menu.setApplicationMenu(menu);
};

// ===== STEP 11: MENU SYSTEM =====
/**
 * Loads package.json data for About dialog and Help menu links
 */
function getPackageInfo(): { name: string; version: string; repository: string; bugs: string; homepage: string } {
  try {
    const packagePath = path.join(__dirname, '../../package.json');
    const packageData = JSON.parse(fs.readFileSync(packagePath, 'utf-8'));
    return {
      name: packageData.productName || packageData.name || 'InsightsLM',
      version: packageData.version || '1.0.0',
      repository: packageData.repository?.url || 'https://github.com/YOUR-ORG/InsightsLM',
      bugs: packageData.bugs?.url || 'https://github.com/YOUR-ORG/InsightsLM/issues',
      homepage: packageData.homepage || 'https://github.com/YOUR-ORG/InsightsLM#readme',
    };
  } catch (error) {
    logError(`Failed to load package.json: ${error instanceof Error ? error.message : String(error)}`);
    return {
      name: 'InsightsLM',
      version: '1.0.0',
      repository: 'https://github.com/YOUR-ORG/InsightsLM',
      bugs: 'https://github.com/YOUR-ORG/InsightsLM/issues',
      homepage: 'https://github.com/YOUR-ORG/InsightsLM#readme',
    };
  }
}

/**
 * Shows the About dialog
 */
function showAboutDialog(mainWindow: BrowserWindow): void {
  const packageInfo = getPackageInfo();
  const electronVersion = process.versions.electron;
  const chromeVersion = process.versions.chrome;
  const nodeVersion = process.versions.node;

  dialog.showMessageBox(mainWindow, {
    type: 'info',
    title: `About ${packageInfo.name}`,
    message: packageInfo.name,
    detail: `Version: ${packageInfo.version}\n\n` +
            `AI-powered audio transcription and analysis application\n\n` +
            `Electron: ${electronVersion}\n` +
            `Chrome: ${chromeVersion}\n` +
            `Node.js: ${nodeVersion}\n\n` +
            `© 2025 InsightsLM Team\n` +
            `Licensed under MIT License`,
    buttons: ['OK'],
  });
}

/**
 * Creates the application menu (platform-aware)
 */
function createApplicationMenu(mainWindow: BrowserWindow): Menu {
  const packageInfo = getPackageInfo();
  const isMac = process.platform === 'darwin';

  const template: Electron.MenuItemConstructorOptions[] = [];

  // macOS: App menu (InsightsLM menu)
  if (isMac) {
    template.push({
      label: packageInfo.name,
      submenu: [
        {
          label: `About ${packageInfo.name}`,
          click: () => showAboutDialog(mainWindow),
        },
        { type: 'separator' },
        {
          label: 'Settings',
          accelerator: 'Cmd+,',
          click: () => {
            mainWindow.webContents.send('navigate-to-settings');
          },
        },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' },
      ],
    });
  }

  // File menu
  template.push({
    label: 'File',
    submenu: [
      // Windows/Linux: Settings in File menu
      ...(!isMac ? [
        {
          label: 'Settings',
          accelerator: 'Ctrl+,',
          click: () => {
            mainWindow.webContents.send('navigate-to-settings');
          },
        },
        { type: 'separator' } as Electron.MenuItemConstructorOptions,
      ] : []),
      {
        label: 'Close Window',
        accelerator: isMac ? 'Cmd+W' : 'Ctrl+W',
        click: () => {
          mainWindow.close();
        },
      },
      ...(!isMac ? [
        { type: 'separator' } as Electron.MenuItemConstructorOptions,
        {
          label: 'Quit',
          accelerator: 'Ctrl+Q',
          click: () => {
            app.quit();
          },
        } as Electron.MenuItemConstructorOptions,
      ] : []),
    ],
  });

  // Edit menu
  template.push({
    label: 'Edit',
    submenu: [
      { role: 'undo' },
      { role: 'redo' },
      { type: 'separator' },
      { role: 'cut' },
      { role: 'copy' },
      { role: 'paste' },
      { role: 'selectAll' },
    ],
  });

  // View menu
  template.push({
    label: 'View',
    submenu: [
      { role: 'reload' },
      { role: 'forceReload' },
      { role: 'toggleDevTools' },
      { type: 'separator' },
      { role: 'resetZoom' },
      { role: 'zoomIn' },
      { role: 'zoomOut' },
      { type: 'separator' },
      { role: 'togglefullscreen' },
    ],
  });

  // Window menu
  template.push({
    label: 'Window',
    submenu: [
      { role: 'minimize' },
      { role: 'close' },
      ...(isMac ? [
        { type: 'separator' } as Electron.MenuItemConstructorOptions,
        { role: 'front' } as Electron.MenuItemConstructorOptions,
      ] : []),
    ],
  });

  // Help menu
  template.push({
    label: 'Help',
    submenu: [
      ...(!isMac ? [
        {
          label: `About ${packageInfo.name}`,
          click: () => showAboutDialog(mainWindow),
        } as Electron.MenuItemConstructorOptions,
        { type: 'separator' } as Electron.MenuItemConstructorOptions,
      ] : []),
      {
        label: 'Documentation',
        click: async () => {
          const wikiUrl = packageInfo.repository.replace(/\.git$/, '') + '/wiki';
          await shell.openExternal(wikiUrl);
        },
      },
      {
        label: 'View on GitHub',
        click: async () => {
          const repoUrl = packageInfo.repository.replace(/\.git$/, '');
          await shell.openExternal(repoUrl);
        },
      },
      { type: 'separator' },
      {
        label: 'Report Issue',
        click: async () => {
          await shell.openExternal(packageInfo.bugs);
        },
      },
    ],
  });

  return Menu.buildFromTemplate(template);
}

// ===== APP LIFECYCLE =====
/**
 * This method is called when Electron has finished initialization.
 * STEP 10: Modified to auto-start backend before creating main window
 */
app.on('ready', async () => {
  // --- Setup IPC Handlers First ---
  
  // Custom IPC Handler for "Save Audio As..."
  ipcMain.handle('save-audio', async (event, { url, filename }) => {
    try {
      // Validate URL
      const parsedUrl = new URL(url);
      if (!['http:', 'https:'].includes(parsedUrl.protocol)) {
        return { success: false, error: 'The audio file cannot be saved. Invalid file location.' }; // MSG-011
      }

      // Sanitize the filename to prevent path traversal
      const safeFilename = (filename ?? 'audio.mp3').replace(/[^\w.-]/g, '_');
      
      // Get the window that sent the request
      const win = BrowserWindow.fromWebContents(event.sender);
      if (!win) {
        return { success: false, error: 'Unable to save file. Please try again.' }; // MSG-012
      }

      // Show native save dialog
      const { canceled, filePath } = await dialog.showSaveDialog(win, {
        title: 'Save Audio File',
        defaultPath: path.join(app.getPath('downloads'), safeFilename),
        filters: [
          { name: 'Audio Files', extensions: ['mp3'] },
          { name: 'All Files', extensions: ['*'] }
        ]
      });

      // User cancelled the dialog
      if (canceled || !filePath) {
        return { success: false, error: 'File save cancelled.' }; // MSG-013
      }

      // Download file from localhost using Electron's net module
      return new Promise<{ success: boolean; error?: string; filePath?: string }>((resolve) => {
        const request = net.request(url);
        const chunks: Buffer[] = [];

        request.on('response', (response) => {
          // Check if response is successful
          if (response.statusCode !== 200 && response.statusCode !== 206) {
            resolve({ 
              success: false, 
              error: `Unable to download audio file. Server error (status: ${response.statusCode}).` // MSG-014
            });
            return;
          }

          response.on('data', (chunk) => {
            chunks.push(Buffer.from(chunk));
          });

          response.on('end', () => {
            try {
              // Write all chunks to file
              const fileBuffer = Buffer.concat(chunks);
              fs.writeFileSync(filePath, fileBuffer);
              resolve({ success: true, filePath });
            } catch (writeError: any) {
              resolve({ 
                success: false, 
                error: `Cannot save file to your computer. ${writeError.message}` // MSG-015
              });
            }
          });

          response.on('error', (error) => {
            resolve({ 
              success: false, 
              error: 'Network error while downloading audio. Please check your connection.' // MSG-016
            });
          });
        });

        request.on('error', (error) => {
          resolve({ 
            success: false, 
            error: 'Cannot download audio file. Please try again.' // MSG-017
          });
        });

        request.end();
      });

    } catch (error: any) {
      logError('Save audio error:', error);
      return { 
        success: false, 
        error: error.message ?? 'An unexpected error occurred. Please try again.' // MSG-018
      };
    }
  });

  // ===== STEP 1.2: SAFESTORAGE IPC HANDLERS =====
  /**
   * Encrypt API Key using Electron safeStorage
   * Uses OS-level encryption (Windows DPAPI, macOS Keychain, Linux libsecret)
   */
  ipcMain.handle('encrypt-api-key', async (event, plainKey: string) => {
    try {
      // Handle empty or null keys
      if (!plainKey || plainKey.trim() === '') {
        return '';
      }

      // Encrypt using safeStorage and convert to base64 for storage
      const encrypted = safeStorage.encryptString(plainKey);
      return encrypted.toString('base64');
    } catch (error: any) {
      logError('API key encryption error:', error);
      return { error: 'Failed to encrypt API key. Please try again.' };
    }
  });

  /**
   * Decrypt API Key using Electron safeStorage
   * Reverses the encryption performed by encrypt-api-key
   */
  ipcMain.handle('decrypt-api-key', async (event, encryptedKey: string) => {
    try {
      // Handle empty or null keys
      if (!encryptedKey || encryptedKey.trim() === '') {
        return '';
      }

      // Convert from base64 back to Buffer and decrypt
      const buffer = Buffer.from(encryptedKey, 'base64');
      return safeStorage.decryptString(buffer);
    } catch (error: any) {
      logError('API key decryption error:', error);
      return { error: 'Failed to decrypt API key. Please re-enter your key.' };
    }
  });

  /**
   * Check if safeStorage encryption is available
   * Returns true if the OS supports secure key storage
   */
  ipcMain.handle('is-encryption-available', async () => {
    try {
      return safeStorage.isEncryptionAvailable();
    } catch (error) {
      // Failsafe: if we can't check, assume it's not available
      logError('Error checking encryption availability:', error);
      return false;
    }
  });

  // ===== STEP 10: NEW IPC HANDLER FOR BACKEND PORT =====
  /**
   * Get the current backend port
   * Frontend uses this to construct API URLs dynamically
   */
  ipcMain.handle('get-backend-port', async () => {
    return backendPort;
  });

  // --- STEP 10: Auto-Start Backend Before Creating Window ---
  logInfo('[App] Backend auto-start DISABLED - using external backend...');
  const backendStarted = false; // DISABLED: await startBackendWithRetry();
  
  if (backendStarted) {
    logInfo(`[App] ✅ Backend ready on port ${backendPort}, creating main window...`);
  } else {
    logInfo('[App] ⚠️ Backend not started, creating window anyway (Step 9 error UI will show)...');
  }
  
  // Create main window (regardless of backend status)
  createWindow();
});

// ===== STEP 10: CLEANUP ON APP QUIT =====
/**
 * Gracefully shut down backend process when app quits
 */
app.on('before-quit', () => {
  logInfo('[App] Shutting down...');
  
  if (backendProcess && !backendProcess.killed) {
    logInfo('[Backend] Stopping backend process...');
    backendProcess.kill('SIGTERM');
    backendProcess = null;
    logInfo('[Backend] ✅ Backend stopped');
  }
});

// Quit when all windows are closed, except on macOS.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
