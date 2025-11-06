/**
 * log.ts - Cross-terminal logging utility for Electron
 * 
 * Handles line-ending differences between Windows and Unix terminals:
 * - PowerShell/cmd.exe expect CRLF (\r\n)
 * - WSL/bash/Unix terminals expect LF (\n)
 * 
 * Detection is based on the TERM environment variable:
 * - TERM set → Unix terminal (use \n)
 * - TERM not set → Windows terminal (use \r\n)
 */

/**
 * Detect terminal type based on environment variables
 * 
 * Uses multiple indicators with fallback:
 * 1. TERM variable (primary) - Set in Unix/WSL terminals, not in PowerShell
 * 2. WSL_DISTRO_NAME (backup) - Set when running in WSL
 * 3. SHELL variable (backup) - Set in Unix shells
 * 
 * @returns 'unix' for LF line endings, 'windows' for CRLF line endings
 */
function detectTerminalType(): 'unix' | 'windows' {
  // Primary detection: TERM variable
  // Unix/WSL terminals set TERM (e.g., 'xterm-256color')
  // PowerShell/cmd.exe do not set TERM
  if (process.env.TERM) {
    return 'unix';
  }
  
  // Backup detection: WSL-specific variables
  // If running in WSL, use Unix line endings
  if (process.env.WSL_DISTRO_NAME || process.env.WSL_INTEROP) {
    return 'unix';
  }
  
  // Backup detection: SHELL variable
  // Unix shells set SHELL (e.g., '/bin/bash')
  if (process.env.SHELL) {
    return 'unix';
  }
  
  // Default: Windows terminal
  return 'windows';
}

// Detect terminal type once at module load
const terminalType = detectTerminalType();
const EOL = terminalType === 'unix' ? '\n' : '\r\n';

/**
 * Log information message to stdout
 * Automatically uses correct line endings for the terminal
 * 
 * @param args - Arguments to log (will be stringified if objects)
 */
export function logInfo(...args: unknown[]): void {
  const message = args
    .map(arg => (typeof arg === 'object' ? JSON.stringify(arg) : String(arg)))
    .join(' ');
  
  // Convert any embedded newlines to platform-appropriate format
  const normalized = message.replace(/\r?\n/g, EOL);
  
  // Write with explicit line ending
  process.stdout.write(normalized + EOL);
}

/**
 * Log error message to stderr
 * Automatically uses correct line endings for the terminal
 * 
 * @param args - Arguments to log (will be stringified if objects)
 */
export function logError(...args: unknown[]): void {
  const message = args
    .map(arg => (typeof arg === 'object' ? JSON.stringify(arg) : String(arg)))
    .join(' ');
  
  // Convert any embedded newlines to platform-appropriate format
  const normalized = message.replace(/\r?\n/g, EOL);
  
  // Write with explicit line ending
  process.stderr.write(normalized + EOL);
}

/**
 * Log a line for backend output (same as logInfo but explicit name)
 * Use this for backend stdout/stderr output to maintain consistency
 * 
 * @param args - Arguments to log
 */
export function logLine(...args: unknown[]): void {
  logInfo(...args);
}

/**
 * Get current line ending being used
 * Useful for debugging or conditional logic
 * 
 * @returns Current line ending string
 */
export function getEOL(): string {
  return EOL;
}

/**
 * Get detected terminal type
 * Useful for debugging
 * 
 * @returns Terminal type ('unix' or 'windows')
 */
export function getTerminalType(): 'unix' | 'windows' {
  return terminalType;
}

// Log detection info at startup (for debugging)
// This helps verify the detection is working correctly
if (process.env.DEBUG_TERMINAL_DETECTION) {
  process.stdout.write(`[log.ts] Terminal type detected: ${terminalType}\n`);
  process.stdout.write(`[log.ts] Using line ending: ${EOL === '\n' ? 'LF (\\n)' : 'CRLF (\\r\\n)'}\n`);
}
