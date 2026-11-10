<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { listNotifications, getUnreadCount, markAsRead, markAllAsRead } from '../api/notifications'

const unreadCount = ref(0)
const notifications = ref([])
const isOpen = ref(false)
const loading = ref(false)

let pollTimer = null

async function refreshCount() {
  try {
    unreadCount.value = await getUnreadCount()
  } catch (e) {
    // silent fail - bell should not break the app
  }
}

async function toggleOpen() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    loading.value = true
    try {
      notifications.value = await listNotifications()
    } catch (e) {
      notifications.value = []
    } finally {
      loading.value = false
    }
  }
}

async function handleMarkRead(notification) {
  if (notification.read) return
  try {
    await markAsRead(notification.id)
    notification.read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  } catch (e) {
    // ignore
  }
}

async function handleMarkAllRead() {
  try {
    await markAllAsRead()
    notifications.value = notifications.value.map((n) => ({ ...n, read: true }))
    unreadCount.value = 0
  } catch (e) {
    // ignore
  }
}

function formatDate(iso) {
  const d = new Date(iso)
  return d.toLocaleString()
}

onMounted(() => {
  refreshCount()
  pollTimer = setInterval(refreshCount, 60000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<template>
  <div class="bell-wrap">
    <button class="bell-btn" @click="toggleOpen" :title="'Notifications'">
      <span class="bell-icon">🔔</span>
      <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
    </button>

    <div v-if="isOpen" class="dropdown">
      <div class="dropdown-head">
        <span>Notifications</span>
        <button v-if="unreadCount > 0" class="btn-mark-all" @click="handleMarkAllRead">
          Mark all read
        </button>
      </div>

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
          <span class="notif-date">{{ formatDate(n.created_at) }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.bell-wrap {
  position: relative;
}
.bell-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  position: relative;
  padding: 0.3rem 0.5rem;
  font-size: 1.2rem;
}
.badge {
  position: absolute;
  top: 0;
  right: 0;
  background: #ef4444;
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  border-radius: 999px;
  padding: 0.1rem 0.35rem;
  min-width: 18px;
  text-align: center;
}
.dropdown {
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: 0.5rem;
  width: 340px;
  max-height: 420px;
  overflow-y: auto;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  z-index: 100;
}
.dropdown-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.7rem 1rem;
  border-bottom: 1px solid #334155;
  font-weight: 600;
  font-size: 0.9rem;
}
.btn-mark-all {
  background: transparent;
  color: #60a5fa;
  border: none;
  cursor: pointer;
  font-size: 0.75rem;
}
.btn-mark-all:hover {
  text-decoration: underline;
}
.notif-list {
  list-style: none;
  margin: 0;
  padding: 0;
}
.notif-item {
  padding: 0.7rem 1rem;
  border-bottom: 1px solid #334155;
  cursor: pointer;
  font-size: 0.85rem;
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
  margin: 0 0 0.3rem 0;
  color: #e2e8f0;
}
.notif-date {
  color: #94a3b8;
  font-size: 0.72rem;
}
.muted {
  color: #94a3b8;
  text-align: center;
  font-size: 0.85rem;
  padding: 1rem;
}
</style>
