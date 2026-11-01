import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../stores/auth'
import LoginView from '../views/LoginView.vue'
import SignupView from '../views/SignupView.vue'
import MoviesView from '../views/MoviesView.vue'

const routes = [
  { path: '/', redirect: '/movies' },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/signup', name: 'signup', component: SignupView },
  { path: '/movies', name: 'movies', component: MoviesView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const { isAuthenticated } = useAuth()
  const publicPages = ['login', 'signup']
  if (!publicPages.includes(to.name) && !isAuthenticated.value) {
    return { name: 'login' }
  }
  if (publicPages.includes(to.name) && isAuthenticated.value) {
    return { name: 'movies' }
  }
})

export default router
