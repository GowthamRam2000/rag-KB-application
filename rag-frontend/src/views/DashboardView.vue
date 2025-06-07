<template>
  <v-app>
    <!-- Page Header - Hidden on mobile since we have app bar -->
    <div v-if="!mobile" class="page-header pa-6 bg-white elevation-1 mb-4">
      <div class="d-flex align-center justify-space-between">
        <div>
          <h1 class="text-h4 font-weight-bold text-primary mb-2">
            <v-icon class="mr-3" size="36">mdi-brain</v-icon>
            RAG Application
          </h1>
          <p class="text-h6 text-medium-emphasis mb-0">AI-Powered Document Assistant</p>
        </div>

        <!-- Quick Stats -->
        <div class="d-flex ga-4">
          <v-card variant="tonal" color="success" class="pa-3 text-center" min-width="120">
            <div class="text-h5 font-weight-bold">{{ authStore.uploadsRemaining }}</div>
            <div class="text-caption">Uploads Left</div>
          </v-card>
          <v-card variant="tonal" color="info" class="pa-3 text-center" min-width="120">
            <div class="text-h5 font-weight-bold">{{ authStore.queriesRemaining }}</div>
            <div class="text-caption">Queries Left</div>
          </v-card>
          <v-card variant="tonal" color="primary" class="pa-3 text-center" min-width="120">
            <div class="text-h5 font-weight-bold">{{ authStore.documents.length }}</div>
            <div class="text-caption">Documents</div>
          </v-card>
        </div>
      </div>

      <!-- Desktop Navigation Links -->
      <div class="mt-4">
        <v-btn-group variant="outlined" class="nav-buttons">
          <v-btn
            :color="$route.name === 'dashboard' ? 'primary' : 'default'"
            :variant="$route.name === 'dashboard' ? 'flat' : 'outlined'"
            prepend-icon="mdi-view-dashboard"
            to="/dashboard">
            Dashboard
          </v-btn>
          <v-btn
            :color="$route.name === 'about' ? 'primary' : 'default'"
            :variant="$route.name === 'about' ? 'flat' : 'outlined'"
            prepend-icon="mdi-information"
            to="/about">
            About
          </v-btn>
        </v-btn-group>
      </div>
    </div>

    <!-- Mobile Quick Navigation - Hide when drawer is open -->
    <div v-if="mobile && !isDrawerOpen"
         class="mobile-nav-wrapper"
         :key="`mobile-nav-${mobileNavKey}`">
      <div class="mobile-nav pa-2">
        <v-chip-group mandatory class="d-flex justify-center">
          <v-chip
            :color="$route.name === 'dashboard' ? 'primary' : 'default'"
            :variant="$route.name === 'dashboard' ? 'flat' : 'outlined'"
            size="small"
            to="/dashboard">
            <v-icon start>mdi-view-dashboard</v-icon>
            Dashboard
          </v-chip>
          <v-chip
            :color="$route.name === 'about' ? 'primary' : 'default'"
            :variant="$route.name === 'about' ? 'flat' : 'outlined'"
            size="small"
            to="/about">
            <v-icon start>mdi-information</v-icon>
            About
          </v-chip>
        </v-chip-group>
      </div>
    </div>

    <!-- Mobile Stats Cards - Hide when drawer is open -->
    <div v-if="mobile && !isDrawerOpen"
         class="mobile-stats-wrapper"
         :key="`mobile-stats-${mobileStatsKey}`">
      <div class="mobile-stats pa-3">
        <v-row dense>
          <v-col cols="4">
            <v-card variant="tonal" color="success" class="pa-2 text-center mobile-stat-card">
              <div class="text-subtitle-1 font-weight-bold">{{ authStore.uploadsRemaining }}</div>
              <div class="text-caption">Uploads Left</div>
            </v-card>
          </v-col>
          <v-col cols="4">
            <v-card variant="tonal" color="info" class="pa-2 text-center mobile-stat-card">
              <div class="text-subtitle-1 font-weight-bold">{{ authStore.queriesRemaining }}</div>
              <div class="text-caption">Queries Left</div>
            </v-card>
          </v-col>
          <v-col cols="4">
            <v-card variant="tonal" color="primary" class="pa-2 text-center mobile-stat-card">
              <div class="text-subtitle-1 font-weight-bold">{{ authStore.documents.length }}</div>
              <div class="text-caption">Documents</div>
            </v-card>
          </v-col>
        </v-row>
      </div>
    </div>

    <!-- Main Content -->
    <v-container fluid :class="mobile ? 'pa-2 mobile-container' : 'pa-6'">
      <v-row>
        <!-- Left Sidebar -->
        <v-col cols="12" md="4" lg="3">
          <!-- Upload Section -->
          <v-card elevation="3" class="mb-4" rounded="lg">
            <v-card-title class="upload-header text-h6 text-white py-4">
              <v-icon class="mr-2">mdi-cloud-upload</v-icon>
              Upload Documents
            </v-card-title>

            <v-card-text class="pa-4">
              <input type="file" ref="fileInput" @change="handleFileSelected" hidden accept=".pdf,.docx"/>

              <!-- Clean Drop Zone -->
              <v-card
                :class="['drop-zone pa-6 text-center', {
                  'border-success': selectedFile,
                  'border-primary': isDragOver && !selectedFile
                }]"
                variant="outlined"
                :color="selectedFile ? 'success' : isDragOver ? 'primary' : ''"
                @click="triggerFileInput"
                @dragover.prevent="isDragOver = true"
                @dragleave.prevent="isDragOver = false"
                @drop.prevent="handleDrop"
                rounded="lg">

                <v-icon
                  :color="selectedFile ? 'success' : 'primary'"
                  size="48"
                  class="mb-3">
                  {{ selectedFile ? 'mdi-file-check' : 'mdi-cloud-upload-outline' }}
                </v-icon>

                <div class="text-body-1 font-weight-medium mb-1">
                  {{ selectedFile ? 'File Ready' : 'Drop file or click to browse' }}
                </div>
                <div class="text-body-2 text-medium-emphasis">
                  {{ selectedFile ? selectedFile.name : 'PDF or DOCX only' }}
                </div>
              </v-card>

              <div v-if="selectedFile" class="mt-3">
                <v-chip closable @click:close="clearFileSelection" color="success" variant="flat">
                  <v-icon start>mdi-file-document</v-icon>
                  {{ truncateFilename(selectedFile.name, 25) }}
                </v-chip>
              </div>

              <v-btn
                block
                color="primary"
                class="mt-4"
                size="large"
                rounded="lg"
                :disabled="!selectedFile || authStore.loading || authStore.uploadsRemaining <= 0"
                @click="handleUpload">
                <v-icon start>mdi-upload</v-icon>
                Upload Document
              </v-btn>

              <div class="text-center mt-3">
                <v-chip
                  :color="authStore.uploadsRemaining > 0 ? 'success' : 'warning'"
                  variant="tonal"
                  size="small">
                  <v-icon start size="16">mdi-counter</v-icon>
                  {{ authStore.uploadsRemaining }} uploads remaining
                </v-chip>
              </div>
            </v-card-text>
          </v-card>

          <!-- Documents List -->
          <v-card elevation="3" rounded="lg">
            <v-card-title class="documents-header text-h6 text-white py-4">
              <v-icon class="mr-2">mdi-folder-multiple</v-icon>
              Your Documents
              <v-spacer></v-spacer>
              <v-chip color="white" variant="flat" size="small">
                {{ authStore.documents.length }}
              </v-chip>
            </v-card-title>

            <v-card-text class="pa-0" :style="mobile ? 'max-height: 300px; overflow-y: auto;' : 'max-height: 400px; overflow-y: auto;'">
              <v-list v-if="authStore.documents.length > 0" lines="one">
                <v-list-item
                  v-for="doc in authStore.documents"
                  :key="doc.id"
                  class="px-4 py-2">

                  <template v-slot:prepend>
                    <v-avatar color="primary" variant="tonal" size="36">
                      <v-icon>mdi-file-document</v-icon>
                    </v-avatar>
                  </template>

                  <v-list-item-title class="text-body-1">
                    {{ truncateFilename(doc.filename, mobile ? 20 : 30) }}
                  </v-list-item-title>

                  <template v-slot:append>
                    <v-btn
                      icon="mdi-delete"
                      variant="text"
                      color="error"
                      size="small"
                      @click="handleDelete(doc.id)">
                    </v-btn>
                  </template>
                </v-list-item>
              </v-list>

              <div v-else class="text-center pa-8">
                <v-icon size="64" color="grey" class="mb-3">mdi-file-upload-outline</v-icon>
                <div class="text-h6 font-weight-medium mb-2">No documents yet</div>
                <div class="text-body-2 text-medium-emphasis">Upload your first document to get started</div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Chat Interface -->
        <v-col cols="12" md="8" lg="9">
          <v-card elevation="3" class="chat-card" rounded="lg">
            <v-card-title class="chat-header text-h6 text-white py-4">
              <v-icon class="mr-2">mdi-chat-question</v-icon>
              AI Assistant
              <v-spacer></v-spacer>
              <v-chip
                :color="authStore.queriesRemaining > 0 ? 'success' : 'warning'"
                variant="flat"
                size="small">
                <v-icon start size="16">mdi-message-text</v-icon>
                {{ authStore.queriesRemaining }} queries remaining
              </v-chip>
            </v-card-title>

            <!-- Chat Messages -->
            <v-card-text class="pa-0 chat-messages-container">
              <div v-if="authStore.chatHistory.length === 0" class="empty-chat pa-8 text-center">
                <v-icon size="80" color="primary" class="mb-4">mdi-chat-question-outline</v-icon>
                <div class="text-h5 font-weight-medium mb-2">Ready to help!</div>
                <div class="text-body-1 text-medium-emphasis">Ask me anything about your uploaded documents.</div>
              </div>

              <div v-else class="messages-container pa-4" ref="chatContainer">
                <div
                  v-for="(message, index) in authStore.chatHistory"
                  :key="index"
                  :class="['message-wrapper mb-4', message.author === 'user' ? 'user-message' : 'ai-message']">

                  <v-card
                    :class="['message-bubble', message.author === 'user' ? (mobile ? 'ml-4' : 'ml-8') : (mobile ? 'mr-4' : 'mr-8')]"
                    :color="message.author === 'user' ? 'primary' : 'grey-lighten-4'"
                    elevation="2"
                    rounded="xl">

                    <v-card-text class="pa-4">
                      <div class="d-flex align-center mb-2">
                        <v-avatar
                          :color="message.author === 'user' ? 'white' : 'primary'"
                          size="32"
                          class="mr-3">
                          <v-icon
                            size="18"
                            :color="message.author === 'user' ? 'primary' : 'white'">
                            {{ message.author === 'user' ? 'mdi-account' : 'mdi-robot-happy' }}
                          </v-icon>
                        </v-avatar>
                        <span class="text-body-2 font-weight-bold">
                          {{ message.author === 'user' ? 'You' : 'AI Assistant' }}
                        </span>
                      </div>

                      <div
                        v-html="renderMarkdown(message.content)"
                        :class="['message-content', message.author === 'user' ? 'text-white' : 'text-black']">
                      </div>

                      <div v-if="message.author === 'ai' && message.sources" class="mt-3">
                        <div class="text-caption font-weight-bold mb-2">Sources:</div>
                        <div class="d-flex flex-wrap ga-1">
                          <v-chip
                            v-for="doc in message.sources"
                            :key="doc"
                            size="x-small"
                            color="primary"
                            variant="tonal">
                            <v-icon start size="12">mdi-file-document</v-icon>
                            {{ truncateFilename(doc, 15) }}
                          </v-chip>
                        </div>
                      </div>
                    </v-card-text>
                  </v-card>
                </div>
              </div>
            </v-card-text>

            <!-- Input Area -->
            <v-divider></v-divider>
            <v-card-actions class="pa-4 bg-white">
              <v-textarea
                v-model="userQuestion"
                label="Ask me anything about your documents..."
                variant="outlined"
                :rows="mobile ? 1 : 2"
                auto-grow
                :max-rows="mobile ? 3 : 4"
                rounded="lg"
                :disabled="authStore.loading || authStore.queriesRemaining <= 0"
                @keydown.enter.exact.prevent="handleQuery"
                hide-details
                class="flex-grow-1 mr-3">
              </v-textarea>
              <v-btn
                color="primary"
                icon
                size="large"
                rounded="lg"
                elevation="2"
                :disabled="!userQuestion.trim() || authStore.loading || authStore.queriesRemaining <= 0"
                @click="handleQuery">
                <v-icon>mdi-send</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- Snackbar -->
    <v-snackbar
      v-model="authStore.snackbar.show"
      :timeout="authStore.snackbar.timeout"
      :color="authStore.snackbar.color"
      location="top right">
      {{ authStore.snackbar.text }}
      <template v-slot:actions>
        <v-btn variant="text" @click="authStore.snackbar.show = false">Close</v-btn>
      </template>
    </v-snackbar>

    <!-- Error Alert -->
    <v-alert
      v-if="authStore.error"
      type="error"
      closable
      class="ma-4"
      @click:close="authStore.error = null">
      {{ authStore.error }}
    </v-alert>

    <!-- Modern Loading Overlay -->
    <v-overlay
      :model-value="authStore.loading"
      class="d-flex align-center justify-center"
      persistent
      scrim="black"
      opacity="0.7">
      <v-card class="pa-8 text-center" elevation="12" rounded="xl" width="320">
        <v-progress-circular
          indeterminate
          color="primary"
          size="72"
          width="6"
          class="mb-4">
        </v-progress-circular>

        <div class="text-h6 font-weight-bold mb-2">Processing...</div>
        <div class="text-body-2 text-medium-emphasis">
          Please wait while we process your request
        </div>
      </v-card>
    </v-overlay>
  </v-app>
</template>

<script setup>
import { ref, onMounted, watch, nextTick, computed, inject } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useDisplay } from 'vuetify';
import { useRoute } from 'vue-router';
import MarkdownIt from 'markdown-it';

const authStore = useAuthStore();
const { mobile } = useDisplay();
const route = useRoute();
const md = new MarkdownIt();

// Inject drawer state from App Layout
const drawerState = inject('drawerState', {
  isOpen: ref(false),
  toggle: () => {},
  drawer: ref(false)
});
const isDrawerOpen = drawerState.isOpen;

const fileInput = ref(null);
const selectedFile = ref(null);
const userQuestion = ref('');
const chatContainer = ref(null);
const isDragOver = ref(false);

// Computed properties for forcing re-renders
const mobileStatsKey = computed(() => {
  return `${authStore.uploadsRemaining}-${authStore.queriesRemaining}-${authStore.documents.length}-${isDrawerOpen.value}`;
});

const mobileNavKey = computed(() => {
  return `${route.name}-${isDrawerOpen.value}`;
});

onMounted(() => {
  authStore.fetchDocuments();
});

// Watch for chat history changes
watch(() => authStore.chatHistory, () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
  });
}, { deep: true });

// Watch for mobile stats changes and drawer state
watch([
  () => authStore.uploadsRemaining,
  () => authStore.queriesRemaining,
  () => authStore.documents.length,
  isDrawerOpen
], () => {
  if (mobile.value) {
    // Force reactivity update on mobile
    nextTick(() => {
      console.log('Mobile stats updated:', {
        uploads: authStore.uploadsRemaining,
        queries: authStore.queriesRemaining,
        docs: authStore.documents.length,
        drawerOpen: isDrawerOpen.value
      });
    });
  }
}, { immediate: true, deep: true });

const triggerFileInput = () => fileInput.value.click();

const handleFileSelected = (event) => {
  const files = event.target.files;
  if (files && files.length > 0) {
    selectedFile.value = files[0];
  }
};

const handleDrop = (event) => {
  isDragOver.value = false;
  const files = event.dataTransfer.files;
  if (files && files.length > 0) {
    selectedFile.value = files[0];
  }
};

const clearFileSelection = () => {
  selectedFile.value = null;
  if (fileInput.value) fileInput.value.value = '';
};

const handleUpload = async () => {
  if (selectedFile.value) {
    await authStore.uploadDocument(selectedFile.value);
    clearFileSelection();
  }
};

const handleDelete = async (docId) => {
  if (confirm('Are you sure you want to delete this document?')) {
    await authStore.deleteDocument(docId);
  }
};

const handleQuery = async () => {
  if (userQuestion.value.trim() && authStore.queriesRemaining > 0) {
    await authStore.askQuery(userQuestion.value);
    userQuestion.value = '';
  }
};

const renderMarkdown = (text) => md.render(text || '');

const truncateFilename = (filename, maxLength) => {
  return filename.length > maxLength ? filename.substring(0, maxLength) + '...' : filename;
};
</script>

<style scoped>
.page-header {
  border-bottom: 1px solid rgba(0,0,0,0.1);
}

/* Navigation Buttons */
.nav-buttons {
  display: flex;
  gap: 8px;
}

.nav-buttons .v-btn {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-buttons .v-btn:hover {
  transform: translateY(-1px);
}

/* Mobile Navigation */
.mobile-nav-wrapper {
  position: sticky;
  top: 56px;
  z-index: 1004;
  background: white;
  border-bottom: 1px solid rgba(0,0,0,0.1);
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  transform: translateZ(0);
}

.mobile-nav {
  background: white;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Mobile Stats Styling */
.mobile-stats-wrapper {
  position: sticky;
  top: calc(56px + 48px); /* App bar + mobile nav */
  z-index: 1003;
  background: white;
  border-bottom: 1px solid rgba(0,0,0,0.1);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transform: translateZ(0);
  -webkit-transform: translateZ(0);
  will-change: transform;
}

.mobile-stats {
  background: white;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.mobile-stat-card {
  min-height: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  transition: all 0.2s ease;
}

.mobile-stat-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.mobile-container {
  margin-top: 0;
  padding-top: 12px !important;
}

/* Header Colors */
.upload-header {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%) !important;
}

.documents-header {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%) !important;
}

.chat-header {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%) !important;
}

.chat-card {
  height: calc(100vh - 280px);
  display: flex;
  flex-direction: column;
}

.chat-messages-container {
  flex: 1;
  overflow: hidden;
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
}

.messages-container {
  height: 100%;
  overflow-y: auto;
  max-height: calc(100vh - 400px);
}

.empty-chat {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
}

.message-wrapper {
  display: flex;
}

.user-message {
  justify-content: flex-end;
}

.ai-message {
  justify-content: flex-start;
}

.message-bubble {
  max-width: calc(100% - 64px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.message-bubble:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.drop-zone {
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-width: 2px !important;
  border-style: dashed !important;
}

.drop-zone:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.message-content :deep(p) {
  margin-bottom: 8px;
}

.message-content :deep(p):last-child {
  margin-bottom: 0;
}

/* Enhanced scrollbar */
.messages-container::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #c1c1c1 0%, #a1a1a1 100%);
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #a1a1a1 0%, #818181 100%);
}

/* Material Design shadows */
.v-card {
  box-shadow: 0 2px 4px rgba(0,0,0,0.1), 0 8px 16px rgba(0,0,0,0.1);
}

/* Modern Material Design button styles */
.v-btn {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.v-btn:hover {
  transform: translateY(-1px);
}

/* Mobile Responsive Design */
@media (max-width: 768px) {
  .mobile-nav-wrapper {
    top: 56px;
    position: sticky;
  }

  .mobile-stats-wrapper {
    top: calc(56px + 48px); /* App bar + mobile nav */
    position: sticky;
  }

  .chat-card {
    height: calc(100vh - 360px); /* Account for mobile nav + stats */
  }

  .messages-container {
    max-height: calc(100vh - 480px); /* Account for mobile nav + stats */
  }

  .message-bubble {
    max-width: calc(100% - 32px);
  }

  .page-header .d-flex {
    flex-direction: column;
    align-items: flex-start !important;
    gap: 16px;
  }

  .page-header .d-flex .d-flex {
    flex-direction: row;
    width: 100%;
    justify-content: space-between;
  }
}

/* Enhanced iOS Safari support */
@supports (-webkit-touch-callout: none) {
  .mobile-nav-wrapper {
    top: calc(56px + env(safe-area-inset-top));
  }

  .mobile-stats-wrapper {
    top: calc(56px + 48px + env(safe-area-inset-top));
    -webkit-backface-visibility: hidden;
    backface-visibility: hidden;
  }
}

/* Ensure proper z-index stacking order */
.v-app-bar {
  z-index: 1005;
}

.v-navigation-drawer {
  z-index: 1006;
}

.mobile-nav-wrapper {
  z-index: 1004;
}

.mobile-stats-wrapper {
  z-index: 1003;
}

/* Enhanced visual hierarchy */
.v-card-title {
  color: white;
}

/* Prevent content shift when drawer opens */
.v-container {
  transition: none;
}

/* Smooth animations */
.mobile-nav-wrapper, .mobile-stats-wrapper {
  transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1),
              transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Loading state improvements */
.v-overlay {
  z-index: 2000;
}

/* Focus and accessibility improvements */
.drop-zone:focus-visible {
  outline: 2px solid #1976d2;
  outline-offset: 2px;
}

.v-btn:focus-visible {
  outline: 2px solid #1976d2;
  outline-offset: 2px;
}

/* Active route styling */
.v-chip[href]:hover,
.v-btn[href]:hover {
  text-decoration: none;
}
</style>
