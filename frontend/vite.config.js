import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // Plotly is ~1.3 MB — isolate so it's cached independently
          plotly: ['plotly.js-cartesian-dist-min', 'react-plotly.js'],
          // React core — stable, cached long-term
          vendor: ['react', 'react-dom', 'react-router-dom'],
        },
      },
    },
  },
})
