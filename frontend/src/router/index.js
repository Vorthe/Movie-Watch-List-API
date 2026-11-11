import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../stores/auth'
import LoginView from '../views/LoginView.vue'
import SignupView from '../views/SignupView.vue'
import MoviesView from '../views/MoviesView.vue'
import NotificationsView from '../views/NotificationsView.vue'
import ScheduleView from '../views/ScheduleView.vue'
import AdminView from '../views/AdminView.vue'

const routes = [
  { path: '/', redirect: '/movies' },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/signup', name: 'signup', component: SignupView },
  { path: '/movies', name: 'movies', component: MoviesView },
  {
    path: '/notifications',
    name: 'notifications',
    component: NotificationsView,
  },
  { path: '/schedule', name: 'schedule', component: ScheduleView },
  {
    path: '/admin',
    name: 'admin',
    component: AdminView,
    meta: { requiresAdmin: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const { isAuthenticated, isAdmin } = useAuth()
  const publicPages = ['login', 'signup']

  if (!publicPages.includes(to.name) && !isAuthenticated.value) {
    return { name: 'login' }
  }
  if (publicPages.includes(to.name) && isAuthenticated.value) {
    return { name: 'movies' }
  }
  if (to.meta.requiresAdmin && !isAdmin.value) {
    return { name: 'movies' }
  }
})

export default router
