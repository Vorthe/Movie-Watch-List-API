<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login as loginApi } from '../api/auth'
import { useAuth } from '../stores/auth'

const router = useRouter()
const { setSession } = useAuth()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    const data = await loginApi(username.value, password.value)
    setSession(data.access_token, username.value)
    router.push({ name: 'movies' })
  } catch (e) {
    if (e.response?.status === 401) {
      error.value = 'Invalid username or password.'
    } else {
      error.value = e.response?.data?.detail || 'Login failed. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-wrap">
    <form class="login-card" @submit.prevent="handleLogin">
      <h1>Sign In</h1>
      <p class="subtitle">Movie Watch List</p>

      <label>
        Username
        <input v-model="username" type="text" required autocomplete="username" />
      </label>

      <label>
        Password
        <input v-model="password" type="password" required autocomplete="current-password" />
      </label>

      <p v-if="error" class="error">{{ error }}</p>

      <button type="submit" :disabled="loading">
        {{ loading ? 'Signing in…' : 'Sign In' }}
      </button>

      <p class="footer">
        No account?
        <router-link to="/signup">Create one</router-link>
      </p>
    </form>
  </div>
</template>

<style scoped>
.login-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}
.login-card {
  background: #1e293b;
  padding: 2rem;
  border-radius: 12px;
  width: 100%;
  max-width: 380px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border: 1px solid #334155;
}
h1 {
  margin: 0;
  font-size: 1.5rem;
}
.subtitle {
  margin: 0 0 0.5rem 0;
  color: #94a3b8;
  font-size: 0.9rem;
}
label {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.9rem;
  color: #cbd5e1;
}
input {
  padding: 0.6rem 0.8rem;
  border-radius: 6px;
  border: 1px solid #475569;
  background: #0f172a;
  color: #e2e8f0;
  font-size: 0.95rem;
}
input:focus {
  outline: none;
  border-color: #3b82f6;
}
button {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.7rem;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  margin-top: 0.5rem;
}
button:hover:not(:disabled) {
  background: #2563eb;
}
button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.error {
  color: #f87171;
  font-size: 0.9rem;
  margin: 0;
  padding: 0.5rem;
  background: #7f1d1d33;
  border-radius: 6px;
}
.footer {
  font-size: 0.85rem;
  color: #94a3b8;
  text-align: center;
  margin: 0.5rem 0 0 0;
}
.footer a {
  color: #60a5fa;
}
</style>
