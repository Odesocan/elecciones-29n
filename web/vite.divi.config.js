import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Build para Divi: un único archivo JS (IIFE) con React, D3, la app, su
// CSS y la configuración dentro. Sale a web/dist/; después
// scripts/empaquetar-divi.mjs monta la carpeta divi/ del proyecto.
export default defineConfig({
  plugins: [react()],
  define: { 'process.env.NODE_ENV': '"production"' },
  publicDir: false, // los datos y los logos los copia el empaquetador
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    target: 'es2019',
    lib: {
      entry: 'src/embed.jsx',
      name: 'OdesocanProgramas',
      formats: ['iife'],
      fileName: () => 'odesocan-programas.js',
    },
  },
});
