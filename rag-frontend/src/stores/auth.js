import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import router from '@/router'

const API_URL = 'backend url'
const setAuthHeader = (token) => {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

export const chatContainerRef = ref(null)

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null,
    documents: [],
    chatHistory: [],
    error: null,
    loading: false,
    snackbar: {
      show: false,
      text: '',
      color: '',
      timeout: 3000,
    },
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    queriesRemaining: (state) => (state.user ? 10 - state.user.query_count : 10),
    uploadsRemaining: (state) => (state.user ? 5 - state.user.pdf_upload_count : 5),
  },
  actions: {
    async fetchUserProfile() {
        if (!this.token) return;
        this.loading = true;
        try {
            const response = await axios.get(`${API_URL}/users/me`);
            this.user = response.data;
        } catch (err) {
            console.error("Failed to fetch user profile, logging out.", err);
            this.logout();
        } finally {
            this.loading = false;
        }
    },
    async login(username, password) {
      this.loading = true; this.error = null;
      try {
        const params = new URLSearchParams();
        params.append('username', username);
        params.append('password', password);
        const response = await axios.post(`${API_URL}/login`, params);
        this.token = response.data.access_token;
        localStorage.setItem('token', this.token);
        setAuthHeader(this.token);
        await this.fetchUserProfile();
        router.push('/dashboard');
      } catch (err) {
        this.error = err.response?.data?.detail || 'An error occurred during login.';
      } finally {
        this.loading = false;
      }
    },
    logout() {
      this.token = null; this.user = null; this.documents = []; this.chatHistory = [];
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      router.push('/login');
    },
    async uploadDocument(file) {
        this.loading = true; this.error = null;
        const formData = new FormData();
        formData.append('file', file);
        try {
            await axios.post(`${API_URL}/documents/upload`, formData);
            this.snackbar.show = true;
            this.snackbar.text = 'File uploaded successfully!';
            this.snackbar.color = 'success';
            await this.fetchUserProfile();
            await this.fetchDocuments();
        } catch (err) {
            this.error = err.response?.data?.detail || 'File upload failed.';
            this.snackbar.show = true;
            this.snackbar.text = this.error;
            this.snackbar.color = 'error';
        } finally {
            this.loading = false;
        }
    },
    async askQuery(question) {
        this.loading = true; this.error = null;
        this.chatHistory.push({ author: 'user', content: question });
        try {
            const response = await axios.post(`${API_URL}/query`, { question });
            this.chatHistory.push({ author: 'ai', content: response.data.answer, sources: response.data.source_documents });
            this.scrollToChatBottom();
            await this.fetchUserProfile();
        } catch (err) {
            const errorContent = err.response?.data?.detail || 'Failed to get an answer.';
            this.chatHistory.push({ author: 'ai', content: `Sorry, an error occurred: ${errorContent}` });
            this.error = errorContent;
            this.snackbar.show = true;
            this.snackbar.text = errorContent;
            this.snackbar.color = 'error';
        } finally {
            this.loading = false;
        }
    },
    scrollToChatBottom() {
        if (chatContainerRef.value) {
            setTimeout(() => {
                chatContainerRef.value.scrollTop = chatContainerRef.value.scrollHeight;
            }, 100);
        }
    },
    async register(username, password, inviteCode) {
      this.loading = true; this.error = null;
      try {
        await axios.post(`${API_URL}/register`, { username, password, invite_code: inviteCode });
        await this.login(username, password);
      } catch (err) {
        this.error = err.response?.data?.detail || 'Registration failed.';
      } finally {
        this.loading = false;
      }
    },
    async fetchDocuments() {
      if (!this.token) return;
      this.loading = true;
      try {
        const response = await axios.get(`${API_URL}/documents`);
        this.documents = response.data;
      } catch (err) {
        this.error = 'Failed to fetch documents.';
      } finally {
        this.loading = false;
      }
    },
    async deleteDocument(docId) {
        this.loading = true; this.error = null;
        try {
            await axios.delete(`${API_URL}/documents/${docId}`);
            this.snackbar.show = true;
            this.snackbar.text = 'Document deleted successfully!';
            this.snackbar.color = 'success';
            await this.fetchDocuments();
            await this.fetchUserProfile();
        } catch (err) {
            this.error = err.response?.data?.detail || 'Failed to delete document.';
            // Show error snackbar
            this.snackbar.show = true;
            this.snackbar.text = this.error;
            this.snackbar.color = 'error';
        } finally {
            this.loading = false;
        }
    },
  },
});
