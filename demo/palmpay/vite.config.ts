import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwind from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'
export default defineConfig({
  plugins: [react(), tailwind(), VitePWA({
    registerType: 'autoUpdate',
    includeAssets: ['palm-192.png', 'palm-512.png'],
    manifest: { id: '/wallet', name: 'Palm Wallet', short_name: 'Palm Wallet', start_url: '/wallet', display: 'standalone', theme_color: '#f7f8f5', background_color: '#f7f8f5', icons: [192,512].map(size => ({ src: '/palm-'+size+'.png', sizes: size+'x'+size, type: 'image/png' })) },
    workbox: { navigateFallbackDenylist: [/^\/api\//, /^\/ws\//] }
  })],
  server: { proxy: { '/api': 'http://127.0.0.1:8000', '/ws': { target: 'ws://127.0.0.1:8000', ws: true } } }
})
