<template>
  <v-app>
    <!-- Back Navigation Bar - Mobile & Desktop -->
    <v-app-bar
      color="primary"
      dark
      elevation="2"
      height="64"
      class="back-navigation">
      <v-btn
        icon
        @click="goBackToDashboard"
        class="back-btn">
        <v-icon size="24">mdi-arrow-left</v-icon>
      </v-btn>

      <v-toolbar-title class="text-h6 font-weight-medium">
        <v-icon class="mr-2" size="20">mdi-information</v-icon>
        About RAG Application
      </v-toolbar-title>

      <v-spacer></v-spacer>

      <!-- Desktop Quick Actions -->
      <div v-if="!mobile" class="d-flex ga-2">
        <v-btn
          href="https://rag-frontend-355828630002.us-central1.run.app/dashboard"
          target="_blank"
          variant="outlined"
          color="white"
          size="small">
          <v-icon start size="16">mdi-rocket-launch</v-icon>
          Try Live Demo
        </v-btn>

        <v-btn
          href="https://gowthamram2000.github.io"
          target="_blank"
          variant="text"
          color="white"
          size="small">
          <v-icon start size="16">mdi-account-circle</v-icon>
          Portfolio
        </v-btn>
      </div>
    </v-app-bar>

    <!-- Main Content with proper spacing -->
    <div class="content-wrapper">
      <!-- Hero Section -->
      <div class="hero-section">
        <v-container fluid class="pa-0">
          <div class="hero-content pa-8 text-center">
            <v-avatar size="120" class="mb-6 hero-avatar">
              <v-icon color="white" size="60">mdi-brain</v-icon>
            </v-avatar>

            <h1 class="hero-title text-h2 font-weight-bold text-white mb-4">
              RAG Application
            </h1>
            <p class="hero-subtitle text-h5 text-white opacity-90 mb-6">
              AI-Powered Document Assistant with Retrieval-Augmented Generation
            </p>

            <div class="hero-badges d-flex justify-center flex-wrap ga-3 mb-8">
              <v-chip color="white" variant="flat" size="large" class="px-4">
                <v-icon start>mdi-lightning-bolt</v-icon>
                Fast API
              </v-chip>
              <v-chip color="white" variant="flat" size="large" class="px-4">
                <v-icon start>mdi-vuejs</v-icon>
                Vue.js 3
              </v-chip>
              <v-chip color="white" variant="flat" size="large" class="px-4">
                <v-icon start>mdi-language-python</v-icon>
                Python
              </v-chip>
              <v-chip color="white" variant="flat" size="large" class="px-4">
                <v-icon start>mdi-google-cloud</v-icon>
                Cloud Run
              </v-chip>
            </div>

            <!-- Mobile Quick Actions -->
            <div v-if="mobile" class="d-flex flex-column ga-3 mb-6">
              <v-btn
                href="https://rag-frontend-355828630002.us-central1.run.app/dashboard"
                target="_blank"
                color="orange"
                variant="flat"
                size="large"
                rounded="lg"
                block
                class="clickable-link">
                <v-icon start>mdi-rocket-launch</v-icon>
                Try Live Demo
              </v-btn>

              <v-btn
                href="https://gowthamram2000.github.io"
                target="_blank"
                color="white"
                variant="outlined"
                size="large"
                rounded="lg"
                block
                class="clickable-link">
                <v-icon start>mdi-account-circle</v-icon>
                View Personal Portfolio
              </v-btn>
            </div>

            <!-- Desktop Portfolio Button -->
            <v-btn
              v-if="!mobile"
              href="https://gowthamram2000.github.io"
              target="_blank"
              color="orange"
              variant="flat"
              size="large"
              rounded="lg"
              class="hero-cta clickable-link">
              <v-icon start>mdi-account-circle</v-icon>
              View Personal Portfolio
            </v-btn>
          </div>
        </v-container>
      </div>

      <!-- Floating Back Button for Mobile (Additional Option) -->
      <v-fab
        v-if="mobile"
        icon="mdi-arrow-left"
        color="primary"
        size="56"
        class="floating-back-btn"
        @click="goBackToDashboard">
      </v-fab>

      <v-container fluid :class="mobile ? 'pa-4' : 'pa-8'">
        <!-- Quick Dashboard Access Card -->
        <v-row class="mb-6">
          <v-col cols="12">
            <v-card
              elevation="3"
              rounded="lg"
              class="dashboard-access-card pa-4"
              color="primary"
              dark>
              <div class="d-flex align-center justify-space-between">
                <div>
                  <h3 class="text-h6 font-weight-bold mb-2">
                    <v-icon class="mr-2">mdi-view-dashboard</v-icon>
                    Ready to get started?
                  </h3>
                  <p class="text-body-2 mb-0 opacity-90">
                    Go back to the dashboard to upload documents and start chatting with AI
                  </p>
                </div>
                <v-btn
                  @click="goBackToDashboard"
                  color="white"
                  variant="flat"
                  size="large"
                  rounded="lg"
                  class="ml-4">
                  <v-icon start>mdi-arrow-left</v-icon>
                  {{ mobile ? 'Dashboard' : 'Back to Dashboard' }}
                </v-btn>
              </div>
            </v-card>
          </v-col>
        </v-row>

        <!-- Project Overview -->
        <v-row class="mb-8">
          <v-col cols="12">
            <v-card elevation="3" rounded="lg" class="pa-6">
              <div class="d-flex align-center mb-4">
                <v-icon color="primary" size="32" class="mr-3">mdi-information</v-icon>
                <h2 class="text-h4 font-weight-bold text-primary">Project Overview</h2>
              </div>

              <p class="text-h6 text-medium-emphasis mb-4 body-text">
                Created by <strong>Gowtham Ram M</strong> as a open source personal project to demonstrate modern web development skills and AI integration capabilities.
              </p>

              <p class="text-body-1 mb-4 body-text">
                This Retrieval-Augmented Generation (RAG) application combines the power of modern web technologies with Gen AI to create an intelligent document assistant. Users can upload documents and ask natural language questions, receiving contextually relevant answers powered by Google's Gemini 2.0 Flash Lite model. Most useful when utilising as KB document bot
              </p>
              <p class="text-body-1 mb-4 body-text">
                <Strong> I really apologize for the rate limits! This App is invite-only because, honestly, I don't want to wake up one fine day to a LUDICROUS cloud bill . AI inference is incredibly expensive</Strong>
              </p>

              <div class="d-flex flex-wrap ga-4">
                <v-chip color="success" variant="tonal" size="large">
                  <v-icon start>mdi-check-circle</v-icon>
                  Production Ready
                </v-chip>
                <v-chip color="info" variant="tonal" size="large">
                  <v-icon start>mdi-responsive</v-icon>
                  Mobile Optimized
                </v-chip>
                <v-chip color="warning" variant="tonal" size="large">
                  <v-icon start>mdi-security</v-icon>
                  Secure & Scalable
                </v-chip>
              </div>
            </v-card>
          </v-col>
        </v-row>

        <!-- Technology Stack -->
        <v-row class="mb-8">
          <v-col cols="12">
            <h2 class="text-h4 font-weight-bold text-primary mb-6 text-center">
              <v-icon class="mr-3" size="36">mdi-code-tags</v-icon>
              Technology Stack
            </h2>
          </v-col>

          <v-col cols="12" md="6" lg="3">
            <v-card elevation="3" rounded="lg" class="tech-card pa-6 text-center h-100">
              <v-avatar color="success" size="64" class="mb-4">
                <v-icon color="white" size="32">mdi-application-brackets</v-icon>
              </v-avatar>
              <h3 class="text-h6 font-weight-bold mb-2">Frontend</h3>
              <v-chip color="success" variant="tonal" size="small" class="mb-2">Vue.js 3</v-chip>
              <v-chip color="success" variant="tonal" size="small" class="mb-2">Vuetify</v-chip>
              <v-chip color="success" variant="tonal" size="small">Composition API</v-chip>
            </v-card>
          </v-col>

          <v-col cols="12" md="6" lg="3">
            <v-card elevation="3" rounded="lg" class="tech-card pa-6 text-center h-100">
              <v-avatar color="info" size="64" class="mb-4">
                <v-icon color="white" size="32">mdi-server</v-icon>
              </v-avatar>
              <h3 class="text-h6 font-weight-bold mb-2">Backend</h3>
              <v-chip color="info" variant="tonal" size="small" class="mb-2">FastAPI</v-chip>
              <v-chip color="info" variant="tonal" size="small" class="mb-2">Python</v-chip>
              <v-chip color="info" variant="tonal" size="small">Async/Await</v-chip>
            </v-card>
          </v-col>

          <v-col cols="12" md="6" lg="3">
            <v-card elevation="3" rounded="lg" class="tech-card pa-6 text-center h-100">
              <v-avatar color="warning" size="64" class="mb-4">
                <v-icon color="white" size="32">mdi-database</v-icon>
              </v-avatar>
              <h3 class="text-h6 font-weight-bold mb-2">Database</h3>
              <v-chip color="warning" variant="tonal" size="small" class="mb-2">PostgreSQL</v-chip>
              <v-chip color="warning" variant="tonal" size="small" class="mb-2">Vector Storage</v-chip>
              <v-chip color="warning" variant="tonal" size="small">pgvector</v-chip>
            </v-card>
          </v-col>

          <v-col cols="12" md="6" lg="3">
            <v-card elevation="3" rounded="lg" class="tech-card pa-6 text-center h-100">
              <v-avatar color="error" size="64" class="mb-4">
                <v-icon color="white" size="32">mdi-google-cloud</v-icon>
              </v-avatar>
              <h3 class="text-h6 font-weight-bold mb-2">AI & Cloud</h3>
              <v-chip color="error" variant="tonal" size="small" class="mb-2">Gemini 2.0</v-chip>
              <v-chip color="error" variant="tonal" size="small" class="mb-2">Cloud Run</v-chip>
              <v-chip color="error" variant="tonal" size="small">Vector Search</v-chip>
            </v-card>
          </v-col>
        </v-row>

        <!-- Key Features -->
        <v-row class="mb-8">
          <v-col cols="12">
            <h2 class="text-h4 font-weight-bold text-primary mb-6 text-center">
              <v-icon class="mr-3" size="36">mdi-star</v-icon>
              Key Features
            </h2>
          </v-col>

          <v-col cols="12" md="6" lg="4" v-for="feature in features" :key="feature.title">
            <v-card elevation="3" rounded="lg" class="feature-card pa-6 h-100">
              <v-icon :color="feature.color" size="48" class="mb-4">{{ feature.icon }}</v-icon>
              <h3 class="text-h6 font-weight-bold mb-3">{{ feature.title }}</h3>
              <p class="text-body-2 body-text">{{ feature.description }}</p>
            </v-card>
          </v-col>
        </v-row>

        <!-- System Architecture -->
        <v-row class="mb-8">
          <v-col cols="12">
            <v-card elevation="3" rounded="lg" class="pa-6">
              <div class="d-flex align-center mb-6">
                <v-icon color="primary" size="32" class="mr-3">mdi-chart-tree</v-icon>
                <h2 class="text-h4 font-weight-bold text-primary">System Architecture</h2>
              </div>

              <div class="architecture-diagram mb-6">
                <v-row dense class="architecture-flow">
                  <v-col cols="12" class="text-center mb-3">
                    <v-chip color="primary" variant="flat" size="x-large" class="px-8 py-4">
                      <v-icon start size="24">mdi-account-group</v-icon>
                      <span class="text-h6">Users (Web/Mobile)</span>
                    </v-chip>
                  </v-col>
                  <v-col cols="12" class="text-center mb-3">
                    <div class="flow-arrow">
                      <v-icon color="primary" size="40">mdi-arrow-down-thick</v-icon>
                      <div class="flow-label">HTTP Requests</div>
                    </div>
                  </v-col>
                  <v-col cols="12" class="text-center mb-3">
                    <v-card variant="tonal" color="success" rounded="lg" class="pa-4 arch-component">
                      <v-icon color="success" size="56" class="mb-3">mdi-vuejs</v-icon>
                      <div class="text-h5 font-weight-bold">Vue.js Frontend</div>
                      <div class="text-body-1">Vuetify UI • Responsive Design</div>
                    </v-card>
                  </v-col>
                  <v-col cols="12" class="text-center mb-3">
                    <div class="flow-arrow">
                      <div class="bidirectional-arrow">
                        <v-icon color="info" size="32">mdi-arrow-up-thick</v-icon>
                        <v-icon color="info" size="32">mdi-arrow-down-thick</v-icon>
                      </div>
                      <div class="flow-label">REST API Calls</div>
                    </div>
                  </v-col>
                  <v-col cols="12" class="text-center mb-3">
                    <v-card variant="tonal" color="info" rounded="lg" class="pa-4 arch-component">
                      <v-icon color="info" size="56" class="mb-3">mdi-api</v-icon>
                      <div class="text-h5 font-weight-bold">FastAPI Backend</div>
                      <div class="text-body-1">Authentication • Document Processing • RAG Pipeline</div>
                    </v-card>
                  </v-col>
                  <v-col cols="12" class="text-center mb-3">
                    <div class="flow-arrow">
                      <v-icon color="warning" size="40">mdi-arrow-down-thick</v-icon>
                      <div class="flow-label">Deployed on</div>
                    </div>
                  </v-col>
                  <v-col cols="12" class="text-center mb-4">
                    <v-card variant="tonal" color="warning" rounded="lg" class="pa-4 arch-component">
                      <v-icon color="warning" size="56" class="mb-3">mdi-google-cloud</v-icon>
                      <div class="text-h5 font-weight-bold">Google Cloud Run</div>
                      <div class="text-body-1">Serverless • Auto-scaling • HTTPS</div>
                    </v-card>
                  </v-col>
                  <v-col cols="12" class="text-center mb-3">
                    <div class="flow-split">
                      <div class="split-arrow left-arrow">
                        <v-icon color="error" size="32">mdi-arrow-down-left-bold</v-icon>
                        <div class="flow-label">Data Storage</div>
                      </div>
                      <div class="split-arrow right-arrow">
                        <v-icon color="purple" size="32">mdi-arrow-down-right-bold</v-icon>
                        <div class="flow-label">AI Processing</div>
                      </div>
                    </div>
                  </v-col>
                  <v-col cols="12" md="6" class="text-center mb-4">
                    <v-card variant="tonal" color="error" rounded="lg" class="pa-4 arch-component">
                      <v-icon color="error" size="56" class="mb-3">mdi-database</v-icon>
                      <div class="text-h5 font-weight-bold">PostgreSQL + pgvector</div>
                      <div class="text-body-1">Document Storage • Vector Embeddings • Semantic Search</div>
                    </v-card>
                  </v-col>
                  <v-col cols="12" md="6" class="text-center mb-4">
                    <v-card variant="tonal" color="purple" rounded="lg" class="pa-4 arch-component">
                      <v-icon color="purple" size="56" class="mb-3">mdi-brain</v-icon>
                      <div class="text-h5 font-weight-bold">Gemini 2.0 Flash Lite</div>
                      <div class="text-body-1">Text Generation • Context Understanding • RAG Responses</div>
                    </v-card>
                  </v-col>
                </v-row>
                <div class="architecture-legend mt-6 pa-4">
                  <h4 class="text-h6 font-weight-bold mb-4 text-center">Data Flow Legend</h4>
                  <div class="d-flex flex-wrap justify-center ga-3">
                    <v-chip color="primary" variant="outlined" size="small">
                      <v-icon start>mdi-arrow-down</v-icon>
                      User Requests
                    </v-chip>
                    <v-chip color="success" variant="outlined" size="small">
                      <v-icon start>mdi-arrow-up-down</v-icon>
                      API Communication
                    </v-chip>
                    <v-chip color="info" variant="outlined" size="small">
                      <v-icon start>mdi-cloud</v-icon>
                      Cloud Deployment
                    </v-chip>
                    <v-chip color="warning" variant="outlined" size="small">
                      <v-icon start>mdi-database-arrow-right</v-icon>
                      Data Storage
                    </v-chip>
                    <v-chip color="error" variant="outlined" size="small">
                      <v-icon start>mdi-brain</v-icon>
                      AI Processing
                    </v-chip>
                  </div>
                </div>
              </div>
            </v-card>
          </v-col>
        </v-row>

        <!-- Project Stats -->
        <v-row class="mb-8">
          <v-col cols="12">
            <h2 class="text-h4 font-weight-bold text-primary mb-6 text-center">
              <v-icon class="mr-3" size="36">mdi-chart-line</v-icon>
              Project Highlights
            </h2>
          </v-col>

          <v-col cols="6" md="3" v-for="stat in stats" :key="stat.label">
            <v-card elevation="3" rounded="lg" class="stat-card pa-6 text-center h-100">
              <div class="text-h3 font-weight-bold" :class="`text-${stat.color}`">{{ stat.value }}</div>
              <div class="text-body-2 text-medium-emphasis body-text">{{ stat.label }}</div>
            </v-card>
          </v-col>
        </v-row>

        <!-- Developer Section -->
        <v-row class="mb-8">
          <v-col cols="12">
            <v-card elevation="3" rounded="lg" class="developer-card pa-8">
              <v-row align="center">
                <v-col cols="12" md="8">
                  <div class="d-flex align-center mb-4">
                    <v-avatar color="primary" size="64" class="mr-4">
                      <v-icon color="white" size="32">mdi-account-circle</v-icon>
                    </v-avatar>
                    <div>
                      <h2 class="text-h4 font-weight-bold text-primary">Gowtham Ram</h2>
                      <p class="text-h6 text-medium-emphasis mb-0 body-text">Full-Stack Developer & AI Enthusiast</p>
                    </div>
                  </div>

                  <p class="text-body-1 mb-4 body-text">
                    Passionate about creating solutions that reduce my workload. This RAG application showcases modern web development practices combined with advanced GenAI capabilities.
                  </p>

                  <div class="d-flex flex-wrap ga-3">
                    <v-chip color="primary" variant="outlined">
                      <v-icon start>mdi-vuejs</v-icon>
                      Vue.js
                    </v-chip>
                    <v-chip color="success" variant="outlined">
                      <v-icon start>mdi-language-python</v-icon>
                      Python Developer
                    </v-chip>
                    <v-chip color="info" variant="outlined">
                      <v-icon start>mdi-brain</v-icon>
                      GenAI Integration
                    </v-chip>
                    <v-chip color="warning" variant="outlined">
                      <v-icon start>mdi-cloud</v-icon>
                      Cloud Architecture
                    </v-chip>
                  </div>
                </v-col>

                <v-col cols="12" md="4" class="text-center">
                  <v-btn
                    href="https://gowthamram2000.github.io"
                    target="_blank"
                    color="orange"
                    variant="flat"
                    size="x-large"
                    rounded="lg"
                    block
                    class="mb-4 clickable-link">
                    <v-icon start>mdi-web</v-icon>
                    View Personal Portfolio
                  </v-btn>

                  <v-btn
                    href="https://github.com/gowthamram2000"
                    target="_blank"
                    color="grey"
                    variant="outlined"
                    size="large"
                    rounded="lg"
                    block
                    class="clickable-link">
                    <v-icon start>mdi-github</v-icon>
                    GitHub Profile
                  </v-btn>
                </v-col>
              </v-row>
            </v-card>
          </v-col>
        </v-row>

        <!-- Final Call to Action -->
        <v-row class="mb-8">
          <v-col cols="12">
            <v-card
              elevation="3"
              rounded="lg"
              class="cta-card pa-8 text-center"
              color="primary"
              dark>
              <h3 class="text-h4 font-weight-bold mb-4">
                Ready to Experience RAG Technology?
              </h3>
              <p class="text-h6 mb-6 opacity-90">
                Upload your documents and start having intelligent conversations with AI
              </p>
              <div class="d-flex flex-wrap justify-center ga-4">
                <v-btn
                  @click="goBackToDashboard"
                  color="white"
                  variant="flat"
                  size="x-large"
                  rounded="lg"
                  class="px-8">
                  <v-icon start>mdi-rocket-launch</v-icon>
                  Go to Dashboard
                </v-btn>

                <v-btn
                  href="https://rag-frontend-355828630002.us-central1.run.app/dashboard"
                  target="_blank"
                  color="orange"
                  variant="flat"
                  size="x-large"
                  rounded="lg"
                  class="px-8">
                  <v-icon start>mdi-open-in-new</v-icon>
                  Try Live Demo
                </v-btn>
              </div>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </div>

    <!-- Footer -->
    <div class="footer-section pa-6 text-center">
      <div class="text-body-2 text-medium-emphasis body-text">
        Built with ❤️ using Vue.js, FastAPI, Python & Cloud • © 2025 Gowtham Ram
      </div>
    </div>
  </v-app>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useDisplay } from 'vuetify'
import { useRouter } from 'vue-router'

const { mobile } = useDisplay()
const router = useRouter()

// Navigation methods
const goBackToDashboard = () => {
  router.push('/dashboard')
}

const features = ref([
  {
    title: "Document Upload & Processing",
    description: "Support for PDF and DOCX files with intelligent text extraction and preprocessing.",
    icon: "mdi-file-upload",
    color: "primary"
  },
  {
    title: "AI-Powered Q&A",
    description: "Ask natural language questions and get contextually relevant answers from your documents.",
    icon: "mdi-chat-question",
    color: "success"
  },
  {
    title: "Vector Search",
    description: "Advanced semantic search using vector embeddings for accurate information retrieval.",
    icon: "mdi-vector-triangle",
    color: "info"
  },
  {
    title: "Real-time Chat",
    description: "Interactive chat interface with message history and source citations.",
    icon: "mdi-message-text",
    color: "warning"
  },
  {
    title: "Mobile Responsive",
    description: "Optimized for all devices with a modern, touch-friendly interface.",
    icon: "mdi-responsive",
    color: "error"
  },
  {
    title: "Secure & Scalable",
    description: "Built with security best practices and deployed on Google Cloud for reliability.",
    icon: "mdi-security",
    color: "purple"
  }
])

const stats = ref([
  { value: "100%", label: "Mobile Responsive", color: "primary" },
  { value: "2.0", label: "Gemini Flash Lite", color: "success" },
  { value: "3", label: "Vue.js Version", color: "info" },
  { value: "∞", label: "Scalability", color: "warning" }
])
</script>

<style scoped>
/* Content wrapper to account for app bar */
.content-wrapper {
  padding-top: 64px; /* Height of app bar */
}

/* Back Navigation Styles */
.back-navigation {
  position: fixed !important;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1010;
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%) !important;
}

.back-btn {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.back-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: translateX(-2px);
}

/* Floating Back Button */
.floating-back-btn {
  position: fixed !important;
  bottom: 24px;
  left: 24px;
  z-index: 1005;
  box-shadow: 0 8px 24px rgba(25, 118, 210, 0.3);
}

/* Dashboard Access Card */
.dashboard-access-card {
  border: 2px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

/* CTA Card */
.cta-card {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%) !important;
  border: 2px solid rgba(255, 255, 255, 0.1);
}

/* Enhanced font sizes */
.body-text {
  font-size: 1.2em !important;
  line-height: 1.6 !important;
}

.text-body-1.body-text {
  font-size: 1.2rem !important;
}

.text-body-2.body-text {
  font-size: 1.08rem !important;
}

.text-h6.body-text {
  font-size: 1.44rem !important;
}

/* Clickable Link Styling */
.clickable-link {
  cursor: pointer !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.clickable-link:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: 0 8px 25px rgba(255, 152, 0, 0.4) !important;
  text-decoration: none;
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 50%, #0d47a1 100%);
  min-height: 60vh;
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  opacity: 0.3;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-avatar {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.hero-title {
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.hero-subtitle {
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

.hero-badges .v-chip {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.hero-cta {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Architecture Diagram */
.architecture-diagram {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-radius: 16px;
  padding: 32px;
  border: 1px solid rgba(25, 118, 210, 0.1);
}

.architecture-flow {
  position: relative;
}

.arch-component {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid rgba(0, 0, 0, 0.05);
}

.arch-component:hover {
  transform: translateY(-4px) scale(1.02);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
}

.flow-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin: 16px 0;
}

.flow-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.7);
  background: white;
  padding: 4px 12px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.bidirectional-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: -8px;
}

.flow-split {
  display: flex;
  justify-content: space-around;
  align-items: center;
  position: relative;
  margin: 20px 0;
}

.split-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.architecture-legend {
  background: rgba(25, 118, 210, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(25, 118, 210, 0.1);
}

/* Card Styles */
.v-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.v-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
}

.tech-card:hover {
  transform: translateY(-8px) scale(1.02);
}

.feature-card:hover {
  transform: translateY(-6px);
}

.stat-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
}

.stat-card:hover {
  transform: translateY(-4px) scale(1.05);
}

.developer-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border: 2px solid #e3f2fd;
}

/* Footer */
.footer-section {
  background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%);
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

/* Mobile Responsive Design */
@media (max-width: 768px) {
  .content-wrapper {
    padding-top: 64px;
  }

  .hero-section {
    min-height: 50vh;
  }

  .hero-title {
    font-size: 2.5rem !important;
  }

  .hero-subtitle {
    font-size: 1.25rem !important;
  }

  .hero-badges {
    justify-content: center;
  }

  .hero-badges .v-chip {
    margin: 4px;
  }

  .architecture-diagram {
    padding: 20px;
  }

  .flow-split {
    flex-direction: column;
    gap: 16px;
  }

  .arch-component {
    margin-bottom: 16px;
  }

  .body-text {
    font-size: 1.1em !important;
  }

  .dashboard-access-card .d-flex {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }

  .dashboard-access-card .ml-4 {
    margin-left: 0 !important;
    margin-top: 16px;
  }
}

/* Enhanced animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.v-card {
  animation: fadeInUp 0.6s ease-out;
}

.v-btn {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.v-btn:hover {
  transform: translateY(-1px);
}

.v-chip {
  transition: all 0.2s ease;
}

.v-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.flow-arrow .v-icon {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.clickable-link.v-btn--variant-flat {
  background-color: #ff9800 !important;
  color: white !important;
}

.clickable-link.v-btn--variant-outlined {
  border-color: #ff9800 !important;
  color: #ff9800 !important;
}

.clickable-link.v-btn--variant-outlined:hover {
  background-color: #ff9800 !important;
  color: white !important;
}

.back-btn:focus-visible,
.floating-back-btn:focus-visible {
  outline: 2px solid white;
  outline-offset: 2px;
}
</style>
