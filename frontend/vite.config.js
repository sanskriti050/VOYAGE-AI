import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { cors: true },
  build: {
    // Ensure UTF-8 encoding in output so ₹ and other symbols render correctly
    charset: 'utf8',
  },
})
