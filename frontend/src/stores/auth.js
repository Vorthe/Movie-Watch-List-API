import { ref, computed } from 'vue'

const token = ref(localStorage.getItem('access_token') || '')
const username = ref(localStorage.getItem('username') || '')

function decodeJwtPayload(jwt) {
  try {
    const part = jwt.split('.')[1]
    if (!part) return null
    const base64 = part.replace(/-/g, '+').replace(/_/g, '/')
    const padded = base64 + '='.repeat((4 - (base64.length % 4)) % 4)
    return JSON.parse(atob(padded))
  } catch {
    return null
  }
}

export function useAuth() {
  const isAuthenticated = computed(() => !!token.value)

  const role = computed(() => {
    if (!token.value) return null
    const payload = decodeJwtPayload(token.value)
    return payload?.role || null
  })

  const isAdmin = computed(() => role.value === 'admin')

  function setSession(newToken, newUsername) {
    token.value = newToken
    username.value = newUsername
    localStorage.setItem('access_token', newToken)
    localStorage.setItem('username', newUsername)
  }

  function clearSession() {
    token.value = ''
    username.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('username')
  }

  return {
    token,
    username,
    role,
    isAdmin,
    isAuthenticated,
    setSession,
    clearSession,
  }
}
