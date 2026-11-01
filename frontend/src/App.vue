<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from './stores/auth'

const router = useRouter()
const { username, isAuthenticated, clearSession } = useAuth()

function logout() {
  clearSession()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="app">
    <nav class="navbar">
      <div class="brand">🎬 Movie Watch List</div>
      <div class="nav-right" v-if="isAuthenticated">
        <span class="user">👤 {{ username }}</span>
        <button class="btn-logout" @click="logout">Logout</button>
      </div>
    </nav>
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  background: #0f172a;
  color: #e2e8f0;
}
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: #1e293b;
  border-bottom: 1px solid #334155;
}
.brand {
  font-size: 1.25rem;
  font-weight: 600;
}
.nav-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.user {
  color: #cbd5e1;
}
.btn-logout {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}
.btn-logout:hover {
  background: #dc2626;
}
.content {
  padding: 2rem;
}
</style>
