<script setup>
import { ref, onMounted } from 'vue'
import { listNotifications, markAsRead, markAllAsRead } from '../api/notifications'

const notifications = ref([])
const loading = ref(false)
const error = ref('')
const showUnreadOnly = ref(false)

async function load() {
  loading.value = true
  error.value = ''
  try {
    notifications.value = await listNotifications(showUnreadOnly.value)
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to load notifications.'
  } finally {
    loading.value = false
  }
}

async function handleMarkRead(n) {
  if (n.read) return
  try {
    await markAsRead(n.id)
    n.read = true
  } catch (e) {
    error.value = 'Failed to mark as read.'
  }
}

async function handleMarkAllRead() {
  try {
    await markAllAsRead()
    notifications.value = notifications.value.map((n) => ({ ...n, read: true }))
  } catch (e) {
    error.value = 'Failed to mark all as read.'
  }
}

function toggleFilter() {
  showUnreadOnly.value = !showUnreadOnly.value
  load()
}

function formatDate(iso) {
  return new Date(iso).toLocaleString()
}

onMounted(load)
</script>

<template>
  <div class="notifications-view">
    <div class="header">
      <h1>Notifications</h1>
      <div class="actions">
        <button class="btn-secondary" @click="toggleFilter">
          {{ showUnreadOnly ? 'Show all' : 'Show unread only' }}
        </button>
        <button class="btn-secondary" @click="handleMarkAllRead">Mark all as read</button>
      </div>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="muted">Loading…</p>
    <p v-else-if="notifications.length === 0" class="muted">No notifications.</p>

    <ul v-else class="notif-list">
      <li
        v-for="n in notifications"
        :key="n.id"
        :class="['notif-item', { unread: !n.read }]"
        @click="handleMarkRead(n)"
      >
        <p class="notif-msg">{{ n.message }}</p>
        <div class="notif-meta">
          <span class="notif-date">{{ formatDate(n.created_at) }}</span>
          <span v-if="!n.read" class="unread-dot"></span>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.notifications-view {
  max-width: 800px;
  margin: 0 auto;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
  flex-wrap: wrap;
}
h1 {
  margin: 0;
}
.actions {
  display: flex;
  gap: 0.5rem;
}
.btn-secondary {
  background: #334155;
  color: #e2e8f0;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
}
.btn-secondary:hover {
  background: #475569;
}
.notif-list {
  list-style: none;
  margin: 0;
  padding: 0;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 8px;
  overflow: hidden;
}
.notif-item {
  padding: 1rem 1.2rem;
  border-bottom: 1px solid #334155;
  cursor: pointer;
}
.notif-item:last-child {
  border-bottom: none;
}
.notif-item:hover {
  background: #0f172a;
}
.notif-item.unread {
  background: #1e3a5f;
}
.notif-msg {
  margin: 0 0 0.4rem 0;
  color: #e2e8f0;
}
.notif-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.notif-date {
  color: #94a3b8;
  font-size: 0.78rem;
}
.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #60a5fa;
}
.muted {
  color: #94a3b8;
  text-align: center;
  padding: 2rem;
}
.error {
  color: #f87171;
  padding: 0.6rem;
  background: #7f1d1d33;
  border-radius: 6px;
}
</style>
