// vite.config.js

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vuetify from 'vite-plugin-vuetify' // Import the Vuetify plugin

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vuetify({
      autoImport: true, // Automatically import all components
    }),
  ],
  define: { 'process.env': {} },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
})
