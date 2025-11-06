import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  // Configuration for the Renderer Process (React UI)
  plugins: [react()],
});