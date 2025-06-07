// src/main.js

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import { useAuthStore } from './stores/auth'
import axios from 'axios' // Import axios here
import 'vuetify/styles' // Ensure Vuetify styles are imported


const app = createApp(App)
const pinia = createPinia()

// 1. Tell the app to use Pinia. The store is now active.
app.use(pinia)

// 2. Now that the store is active, we can use it.
const authStore = useAuthStore()

// 3. Check for an existing token and initialize the app state.
if (authStore.token) {
  // Set the authorization header for all future axios requests
  axios.defaults.headers.common['Authorization'] = `Bearer ${authStore.token}`;
  // Fetch the user's profile to get their latest data
  authStore.fetchUserProfile();
}

// 4. Use other plugins and mount the app.
app.use(router)
app.use(vuetify)
app.mount('#app')
