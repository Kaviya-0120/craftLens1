import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/voice': 'http://localhost:8000',
      '/image': 'http://localhost:8000',
      '/listing': 'http://localhost:8000',
      '/pricing': 'http://localhost:8000',
      '/consistency': 'http://localhost:8000',
      '/catalogue': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
      '/static': 'http://localhost:8000',
    },
  },
})
