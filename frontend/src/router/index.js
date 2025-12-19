import { createRouter, createWebHistory } from 'vue-router'
import Home from '../components/Home.vue'
import Login from '../components/Login.vue'
import Dashboard from '../components/Dashboard.vue'
import Departments from '../components/Departments.vue'
import Contacts from '../components/Contacts.vue'
import Cases from '../components/Cases.vue'
import Backups from '../components/Backups.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/departments',
    name: 'Departments',
    component: Departments,
    meta: { requiresAuth: true }
  },
  {
      path: '/admin/activities',
      name: 'Activities',
      component: () => import('../components/Activities.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/knowledge',
      name: 'Knowledge',
      component: () => import('../components/Knowledge.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/guidelines',
      name: 'Guidelines',
      component: () => import('../components/Guidelines.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin/users',
      name: 'Users',
      component: () => import('../components/Users.vue'),
      meta: { requiresAuth: true }
    },
  {
    path: '/contacts',
    name: 'Contacts',
    component: Contacts,
    meta: { requiresAuth: true }
  },
  {
    path: '/cases',
    name: 'Cases',
    component: Cases,
    meta: { requiresAuth: true }
  },
  {
    path: '/backups',
    name: 'Backups',
    component: Backups,
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const isAuthenticated = checkAuthStatus()
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    // Redirect to login if route requires authentication and user is not authenticated
    next('/login')
  } else if (to.meta.requiresGuest && isAuthenticated) {
    // Redirect to dashboard if route requires guest and user is authenticated
    next('/dashboard')
  } else {
    next()
  }
})

// Helper function to check authentication status
// This is a simple check - in a real app you might want to verify with the server
function checkAuthStatus() {
  // Check if user data exists in localStorage or sessionStorage
  const userData = localStorage.getItem('user') || sessionStorage.getItem('user')
  return !!userData
}

export default router