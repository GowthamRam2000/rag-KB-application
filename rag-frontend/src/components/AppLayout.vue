<template>
  <v-layout class="app-layout">
    <v-navigation-drawer
      v-model="drawer"
      location="left"
      width="280"
      elevation="3"
      :permanent="!mobile"
      :temporary="mobile"
      class="navigation-drawer">
      <div class="drawer-header pa-4">
        <div class="d-flex align-center">
          <v-avatar color="white" size="40" class="mr-3">
            <v-icon color="primary" size="24">mdi-brain</v-icon>
          </v-avatar>
          <div>
            <div class="text-h6 font-weight-bold text-white">RAG App</div>
            <div class="text-caption text-white opacity-80">AI Assistant</div>
          </div>
        </div>
      </div>

      <v-divider></v-divider>
      <v-list nav density="comfortable" class="pa-2">
        <v-list-item
          prepend-icon="mdi-view-dashboard"
          title="Dashboard"
          to="/dashboard"
          rounded="lg"
          class="nav-item mb-1"
          active-class="nav-item-active">
        </v-list-item>

        <v-list-item
          prepend-icon="mdi-information"
          title="About"
          to="/about"
          rounded="lg"
          class="nav-item mb-1"
          active-class="nav-item-active">
        </v-list-item>
      </v-list>
      <div v-if="mobile" class="pa-3 mt-4">
        <v-btn
          block
          color="error"
          variant="outlined"
          prepend-icon="mdi-logout"
          @click="handleLogout"
          rounded="lg"
          class="mobile-logout-btn">
          Quick Logout
        </v-btn>
      </div>
      <template v-if="!mobile" v-slot:append>
        <v-divider class="mb-2"></v-divider>
        <div class="pa-3">
          <v-card variant="tonal" color="primary" rounded="lg" class="pa-3">
            <div class="d-flex align-center mb-2">
              <v-avatar size="32" color="primary" class="mr-2">
                <v-icon color="white" size="18">mdi-account</v-icon>
              </v-avatar>
              <div>
                <div class="text-body-2 font-weight-bold">Welcome back</div>
                <div class="text-caption text-medium-emphasis">User</div>
              </div>
            </div>
            <v-btn
              block
              variant="outlined"
              color="primary"
              size="small"
              prepend-icon="mdi-logout"
              @click="handleLogout"
              rounded="lg">
              Logout
            </v-btn>
          </v-card>
        </div>
      </template>
    </v-navigation-drawer>
    <v-main class="main-content">
      <v-app-bar
        v-if="mobile"
        elevation="2"
        color="primary"
        height="56"
        class="mobile-app-bar"
        fixed>
        <v-app-bar-nav-icon @click="toggleDrawer"></v-app-bar-nav-icon>
        <v-toolbar-title class="text-h6 font-weight-bold">
          <v-icon class="mr-2" size="20">mdi-brain</v-icon>
          RAG App
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-chip
          color="white"
          variant="flat"
          size="small"
          class="mr-2">
          <v-icon start size="12">mdi-message-text</v-icon>
          {{ authStore.queriesRemaining }}
        </v-chip>
        <v-btn
          icon
          variant="text"
          @click="handleLogout"
          class="ml-1">
          <v-icon color="white">mdi-logout</v-icon>
        </v-btn>
      </v-app-bar>
      <div :class="mobile ? 'mobile-content' : 'desktop-content'">
        <router-view />
      </div>
    </v-main>
    <v-dialog v-model="showLogoutDialog" max-width="400" persistent>
      <v-card rounded="lg">
        <v-card-title class="text-h6 pa-4">
          <v-icon class="mr-2" color="warning">mdi-logout</v-icon>
          Confirm Logout
        </v-card-title>
        <v-card-text class="pa-4 pt-0">
          Are you sure you want to logout? You will need to sign in again to access your documents.
        </v-card-text>
        <v-card-actions class="pa-4 pt-0">
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="showLogoutDialog = false">
            Cancel
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            @click="confirmLogout">
            Logout
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-overlay
      v-if="mobile && drawer"
      class="mobile-drawer-overlay"
      :model-value="true"
      @click="drawer = false"
      scrim="rgba(0,0,0,0.3)"
      z-index="1005">
    </v-overlay>
  </v-layout>
</template>

<script setup>
import { ref, computed, provide, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { RouterView } from 'vue-router'
import { useDisplay } from 'vuetify'

const { mobile } = useDisplay()
const authStore = useAuthStore()
const drawer = ref(!mobile.value)
const showLogoutDialog = ref(false)
const isDrawerOpen = computed(() => mobile.value && drawer.value)
const toggleDrawer = () => {
  drawer.value = !drawer.value
}
provide('drawerState', {
  isOpen: isDrawerOpen,
  toggle: toggleDrawer,
  drawer: drawer
})
const handleLogout = () => {
  showLogoutDialog.value = true
}

const confirmLogout = () => {
  authStore.logout()
  showLogoutDialog.value = false
  if (mobile.value) {
    drawer.value = false
  }
}
watch(mobile, (newMobile) => {
  drawer.value = !newMobile
}, { immediate: true })
watch(isDrawerOpen, (isOpen) => {
  if (isOpen && mobile.value) {
    document.body.classList.add('drawer-open')
  } else {
    document.body.classList.remove('drawer-open')
  }
})
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
}

.navigation-drawer {
  border-right: 1px solid rgba(0,0,0,0.12);
  z-index: 1006 !important;
}

.drawer-header {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
}

.nav-item {
  margin-bottom: 4px;
  transition: all 0.2s ease;
}

.nav-item:hover {
  background-color: rgba(25, 118, 210, 0.08);
  transform: translateX(4px);
}

.nav-item-active {
  background-color: rgba(25, 118, 210, 0.12) !important;
  color: #1976d2 !important;
  border-left: 3px solid #1976d2;
}

.nav-item-active .v-list-item__prepend .v-icon {
  color: #1976d2 !important;
}

.main-content {
  background-color: #fafafa;
  min-height: 100vh;
}

.mobile-app-bar {
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%) !important;
  position: fixed !important;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1005 !important;
}

.mobile-content {
  padding-top: 56px; 
}

.desktop-content {
  padding-top: 0;
}

.mobile-logout-btn {
  transition: all 0.2s ease;
}

.mobile-logout-btn:hover {
  transform: translateY(-1px);
}
.mobile-drawer-overlay {
  z-index: 1005 !important;
  pointer-events: auto !important;
}
.v-btn {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.v-btn:hover {
  transform: translateY(-1px);
}
@media (max-width: 1024px) {
  .navigation-drawer {
    width: 260px;
  }
}

@media (max-width: 768px) {
  .navigation-drawer {
    width: 100vw;
    max-width: 100vw;
  }

  .drawer-header {
    padding: 12px 16px;
    padding-top: calc(12px + env(safe-area-inset-top));
  }

  .drawer-header .text-h6 {
    font-size: 1.1rem;
  }
  .navigation-drawer.v-navigation-drawer--temporary {
    z-index: 1006 !important;
  }
}

@supports (-webkit-touch-callout: none) {
  .mobile-app-bar {
    height: calc(56px + env(safe-area-inset-top));
    padding-top: env(safe-area-inset-top);
  }

  .mobile-content {
    padding-top: calc(56px + env(safe-area-inset-top));
  }

  .drawer-header {
    padding-top: calc(16px + env(safe-area-inset-top));
  }
}
.v-overlay--active {
  z-index: 1004;
}
.v-dialog > .v-overlay__content {
  margin: 24px;
}

.v-card {
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
}
.navigation-drawer {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

:global(body.drawer-open) {
  overflow: hidden;
  position: fixed;
  width: 100%;
}
.v-app-bar {
  z-index: 1005 !important;
}

.v-navigation-drawer {
  z-index: 1006 !important;
}

.mobile-drawer-overlay {
  z-index: 1005 !important;
}

:global(.mobile-stats-wrapper) {
  z-index: 1003 !important;
}

:global(.mobile-nav-wrapper) {
  z-index: 1004 !important;
}
</style>
