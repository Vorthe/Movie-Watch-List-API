import api from './client'

export async function listNotifications(unreadOnly = false) {
  const { data } = await api.get('/notifications/', {
    params: unreadOnly ? { unread_only: true } : {},
  })
  return data
}

export async function getUnreadCount() {
  const { data } = await api.get('/notifications/unread-count')
  return data.unread_count
}

export async function markAsRead(notificationId) {
  await api.patch(`/notifications/${notificationId}/read`)
}

export async function markAllAsRead() {
  await api.post('/notifications/read-all')
}
