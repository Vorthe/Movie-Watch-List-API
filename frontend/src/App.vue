<script setup>
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from './stores/auth'
import NotificationBell from './components/NotificationBell.vue'

const router = useRouter()
const route = useRoute()
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
      <div class="nav-links" v-if="isAuthenticated">
        <router-link to="/movies" :class="{ active: route.name === 'movies' }">
          Catalog
        </router-link>
        <router-link to="/schedule" :class="{ active: route.name === 'schedule' }">
          Schedule
        </router-link>
        <router-link to="/notifications" :class="{ active: route.name === 'notifications' }">
          Notifications
        </router-link>
      </div>
      <div class="nav-right" v-if="isAuthenticated">
        <NotificationBell />
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
  gap: 1.5rem;
}
.brand {
  font-size: 1.25rem;
  font-weight: 600;
}
.nav-links {
  display: flex;
  gap: 1.5rem;
  flex: 1;
  justify-content: center;
}
.nav-links a {
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.9rem;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  transition: all 0.15s;
}
.nav-links a:hover {
  color: #e2e8f0;
}
.nav-links a.active {
  color: #60a5fa;
  background: #1e40af33;
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
