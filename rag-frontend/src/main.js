
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import vuetify from './plugins/vuetify'
import { useAuthStore } from './stores/auth'
import axios from 'axios' 
import 'vuetify/styles' 


const app = createApp(App)
const pinia = createPinia()
app.use(pinia)

const authStore = useAuthStore()
if (authStore.token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${authStore.token}`;
  authStore.fetchUserProfile();
}
app.use(router)
app.use(vuetify)
app.mount('#app')
