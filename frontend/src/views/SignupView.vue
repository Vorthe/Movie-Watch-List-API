<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api/client'

const router = useRouter()

const form = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  phone_number: '',
})
const loading = ref(false)
const error = ref('')

async function handleSignup() {
  error.value = ''
  loading.value = true
  try {
    await api.post('/auth/', {
      ...form.value,
      role: 'user', // hardcoded — backend allows any role (known issue #8)
    })
    router.push({ name: 'login', query: { registered: '1' } })
  } catch (e) {
    const detail = e.response?.data?.detail
    if (Array.isArray(detail)) {
      error.value = detail.map((d) => `${d.loc?.join('.')}: ${d.msg}`).join('; ')
    } else {
      error.value = detail || 'Signup failed. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="signup-wrap">
    <form class="signup-card" @submit.prevent="handleSignup">
      <h1>Create Account</h1>
      <p class="subtitle">Movie Watch List</p>

      <div class="grid-2">
        <label>
          First name
          <input v-model="form.first_name" type="text" required />
        </label>
        <label>
          Last name
          <input v-model="form.last_name" type="text" required />
        </label>
      </div>

      <label>
        Username
        <input v-model="form.username" type="text" required autocomplete="username" />
      </label>

      <label>
        Email
        <input v-model="form.email" type="email" required autocomplete="email" />
      </label>

      <label>
        Phone number (10-12 digits)
        <input
          v-model="form.phone_number"
          type="tel"
          required
          minlength="10"
          maxlength="12"
          pattern="[0-9]{10,12}"
        />
      </label>

      <label>
        Password (min 8 chars)
        <input
          v-model="form.password"
          type="password"
          required
          minlength="8"
          autocomplete="new-password"
        />
      </label>

      <p v-if="error" class="error">{{ error }}</p>

      <button type="submit" :disabled="loading">
        {{ loading ? 'Creating…' : 'Create Account' }}
      </button>

      <p class="footer">
        Already have an account?
        <router-link to="/login">Sign in</router-link>
      </p>
    </form>
  </div>
</template>

<style scoped>
.signup-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
}
.signup-card {
  background: #1e293b;
  padding: 2rem;
  border-radius: 12px;
  width: 100%;
  max-width: 460px;
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
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
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.7rem;
}
label {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.85rem;
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
  margin-top: 0.3rem;
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
  font-size: 0.85rem;
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
