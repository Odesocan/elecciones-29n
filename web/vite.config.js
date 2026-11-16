import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Servidor local del boceto: npm run dev → http://127.0.0.1:5173
// (o desde la raíz del proyecto: python3 maestro.py servir)
export default defineConfig({
  plugins: [react()],
  // La configuración vive en ../config (compartida con el pipeline):
  // el servidor de desarrollo tiene que poder leerla.
  server: { fs: { allow: ['..'] } },
});
