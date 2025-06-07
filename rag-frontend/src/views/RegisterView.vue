<template>
  <v-container fluid class="fill-height register-container">
    <v-row align="center" justify="center" class="fill-height">
      <v-col cols="12" sm="8" md="6" lg="4" xl="3">
        <v-card class="register-card elevation-3" rounded="lg">
          <div class="register-header">
            <div class="header-content">
              <div class="icon-container mb-4">
                <v-icon size="48" color="secondary" class="header-icon">mdi-account-plus</v-icon>
              </div>
              <h1 class="text-h4 font-weight-regular text-secondary mb-2">Join Us</h1>
              <p class="text-body-1 text-medium-emphasis">Create your RAG Application account</p>
            </div>
          </div>
          <v-card-text class="pa-6 form-section">
            <div class="mb-4 text-center">
              <v-chip
                color="warning"
                variant="tonal"
                size="default"
                prepend-icon="mdi-information"
                class="invite-chip"
                rounded="lg"
              >
                Invite code required to register
              </v-chip>
            </div>

            <v-form @submit.prevent="handleRegister" class="register-form">
              <div class="mb-4">
                <v-text-field
                  v-model="username"
                  label="Username"
                  prepend-inner-icon="mdi-account-outline"
                  variant="outlined"
                  required
                  density="default"
                  color="secondary"
                  class="material-input"
                  hide-details="auto"
                  rounded="lg"
                  clearable
                ></v-text-field>
              </div>
              <div class="mb-4">
                <v-text-field
                  v-model="password"
                  label="Password"
                  prepend-inner-icon="mdi-lock-outline"
                  variant="outlined"
                  type="password"
                  required
                  density="default"
                  color="secondary"
                  class="material-input"
                  hide-details="auto"
                  rounded="lg"
                ></v-text-field>
              </div>
              <div class="mb-4">
                <v-text-field
                  v-model="inviteCode"
                  label="Invite Code"
                  prepend-inner-icon="mdi-ticket-confirmation-outline"
                  variant="outlined"
                  required
                  density="default"
                  color="secondary"
                  class="material-input invite-code-input"
                  hide-details="auto"
                  rounded="lg"
                  clearable
                >
                  <template v-slot:append-inner>
                    <v-tooltip text="Paste your invite code here" location="bottom">
                      <template v-slot:activator="{ props }">
                        <v-icon
                          v-bind="props"
                          color="secondary"
                          size="small"
                          class="help-icon"
                        >
                          mdi-help-circle-outline
                        </v-icon>
                      </template>
                    </v-tooltip>
                  </template>
                </v-text-field>
              </div>

              <!-- Error Alert -->
              <v-alert
                v-if="authStore.error"
                type="error"
                variant="tonal"
                class="mb-4 material-alert"
                rounded="lg"
                border="start"
                border-color="error"
                closable
              >
                <template v-slot:prepend>
                  <v-icon>mdi-alert-circle</v-icon>
                </template>
                {{ authStore.error }}
              </v-alert>
              <v-btn
                :loading="authStore.loading"
                type="submit"
                color="secondary"
                block
                size="large"
                class="material-btn text-button font-weight-medium mt-2"
                elevation="2"
                rounded="lg"
                style="height: 48px; text-transform: none;"
              >
                <template v-slot:prepend>
                  <v-icon>mdi-account-plus</v-icon>
                </template>
                Create Account
              </v-btn>
            </v-form>
          </v-card-text>
          <v-divider class="mx-6 mb-4"></v-divider>
          <v-card-actions class="justify-center pa-6 pt-0">
            <div class="text-center w-100">
              <p class="text-body-2 text-medium-emphasis mb-3">
                Already have an account?
              </p>
              <router-link
                to="/login"
                class="login-link text-decoration-none d-block"
              >
                <v-btn
                  variant="outlined"
                  color="secondary"
                  class="font-weight-medium"
                  block
                  rounded="lg"
                  style="height: 40px; text-transform: none;"
                  size="default"
                >
                  Sign in here
                  <template v-slot:append>
                    <v-icon size="small">mdi-arrow-right</v-icon>
                  </template>
                </v-btn>
              </router-link>
            </div>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { RouterLink } from 'vue-router'

const username = ref('')
const password = ref('')
const inviteCode = ref('')
const authStore = useAuthStore()

const handleRegister = () => {
  authStore.register(username.value, password.value, inviteCode.value)
}
</script>

<style scoped>
.register-container {
  background: #fafafa;
  min-height: 100vh;
}

.register-card {
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.12);
  max-width: 400px;
  transition: box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.register-card:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15) !important;
}

.register-header {
  background: #ffffff;
  padding: 32px 24px 24px;
  text-align: center;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.header-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.icon-container {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 80px;
  height: 80px;
  background: rgba(156, 39, 176, 0.08);
  border-radius: 50%;
  border: 1px solid rgba(156, 39, 176, 0.2);
}

.header-icon {
  opacity: 0.87;
}

.form-section {
  background: #ffffff;
}

.invite-chip {
  font-weight: 500;
  background: rgba(245, 124, 0, 0.08) !important;
  color: rgba(0, 0, 0, 0.87) !important;
  border: 1px solid rgba(245, 124, 0, 0.2);
}

.material-input {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.material-input:deep(.v-field) {
  background: #ffffff;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.material-input:deep(.v-field--focused) {
  background: rgba(156, 39, 176, 0.04);
}

.material-input:deep(.v-field__outline) {
  border-color: rgba(0, 0, 0, 0.38);
}

.material-input:deep(.v-field--focused .v-field__outline) {
  border-color: rgb(156, 39, 176);
  border-width: 2px;
}

.material-input:deep(.v-field__prepend-inner .v-icon) {
  opacity: 0.6;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.material-input:deep(.v-field--focused .v-field__prepend-inner .v-icon) {
  opacity: 0.87;
  color: rgb(156, 39, 176);
}

.material-input:deep(.v-label) {
  color: rgba(0, 0, 0, 0.6);
  font-weight: 400;
}

.material-input:deep(.v-field--focused .v-label) {
  color: rgb(156, 39, 176);
}

.invite-code-input:deep(.v-field) {
  border: 2px solid rgba(156, 39, 176, 0.2);
  background: rgba(156, 39, 176, 0.02);
}

.invite-code-input:deep(.v-field--focused) {
  border-color: rgb(156, 39, 176);
  background: rgba(156, 39, 176, 0.04);
}

.help-icon {
  opacity: 0.6;
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.help-icon:hover {
  opacity: 0.87;
}

.material-btn {
  background: rgb(156, 39, 176) !important;
  color: white !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  letter-spacing: 0.5px;
}

.material-btn:hover {
  box-shadow: 0 4px 8px rgba(156, 39, 176, 0.3) !important;
}

.material-btn:active {
  box-shadow: 0 2px 4px rgba(156, 39, 176, 0.4) !important;
}

.material-alert {
  border-radius: 8px !important;
  animation: slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: rgba(211, 47, 47, 0.04) !important;
  border-left: 4px solid rgb(211, 47, 47) !important;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-link:deep(.v-btn) {
  border: 1px solid rgba(156, 39, 176, 0.5);
  color: rgb(156, 39, 176);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.login-link:hover:deep(.v-btn) {
  border-color: rgb(156, 39, 176);
  background: rgba(156, 39, 176, 0.04);
}

.login-link:active:deep(.v-btn) {
  background: rgba(156, 39, 176, 0.08);
}

/* Typography following Material Design */
.text-h4 {
  font-family: 'Roboto', sans-serif;
  font-size: 2.125rem;
  font-weight: 400;
  line-height: 1.235;
  letter-spacing: 0.00735em;
}

.text-body-1 {
  font-family: 'Roboto', sans-serif;
  font-size: 1rem;
  font-weight: 400;
  line-height: 1.5;
  letter-spacing: 0.00938em;
}

.text-body-2 {
  font-family: 'Roboto', sans-serif;
  font-size: 0.875rem;
  font-weight: 400;
  line-height: 1.43;
  letter-spacing: 0.01071em;
}

.text-button {
  font-family: 'Roboto', sans-serif;
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1.75;
  letter-spacing: 0.02857em;
  text-transform: uppercase;
}

/* Responsive adjustments */
@media (max-width: 960px) {
  .register-header {
    padding: 24px 20px 20px;
  }

  .icon-container {
    width: 72px;
    height: 72px;
  }

  .header-icon {
    font-size: 40px !important;
  }
}

@media (max-width: 600px) {
  .register-header {
    padding: 20px 16px 16px;
  }

  .register-card {
    margin: 16px;
    border-radius: 12px !important;
  }

  .form-section {
    padding: 20px !important;
  }

  .icon-container {
    width: 64px;
    height: 64px;
    margin-bottom: 16px !important;
  }

  .header-icon {
    font-size: 32px !important;
  }

  .text-h4 {
    font-size: 1.75rem;
  }

  .invite-chip {
    font-size: 0.8125rem;
  }
}

.material-input:deep(.v-field--focused) {
  outline: none;
}

.material-btn:focus-visible {
  outline: 2px solid rgb(156, 39, 176);
  outline-offset: 2px;
}

.login-link:deep(.v-btn:focus-visible) {
  outline: 2px solid rgb(156, 39, 176);
  outline-offset: 2px;
}

.text-secondary {
  color: rgba(0, 0, 0, 0.87) !important;
}

.text-medium-emphasis {
  color: rgba(0, 0, 0, 0.6) !important;
}
</style>
