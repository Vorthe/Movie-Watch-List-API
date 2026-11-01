import { ref, computed } from 'vue'

const token = ref(localStorage.getItem('access_token') || '')
const username = ref(localStorage.getItem('username') || '')

export function useAuth() {
  const isAuthenticated = computed(() => !!token.value)

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

  return { token, username, isAuthenticated, setSession, clearSession }
}