<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import apiService from './services/api.js'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const isLoading = ref(false)
    const currentUser = ref(null)

    const isAuthenticated = computed(() => {
      return !!currentUser.value
    })

    const checkAuthStatus = async () => {
      try {
        const userData = localStorage.getItem('user')
        if (userData) {
          currentUser.value = JSON.parse(userData)
          // Verify with server
          const response = await apiService.getCurrentUser()
          if (response.success) {
            currentUser.value = response.user
            localStorage.setItem('user', JSON.stringify(response.user))
          }
        }
      } catch (error) {
        console.error('Auth check failed:', error)
        currentUser.value = null
        localStorage.removeItem('user')
        if (route.meta.requiresAuth) {
          router.push('/login')
        }
      }
    }

    const logout = async () => {
      try {
        isLoading.value = true
        await apiService.logout()
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        currentUser.value = null
        localStorage.removeItem('user')
        sessionStorage.removeItem('user')
        isLoading.value = false
        router.push('/login')
      }
    }

    onMounted(() => {
      checkAuthStatus()
    })

    return {
      isLoading,
      currentUser,
      isAuthenticated,
      logout
    }
  }
}
</script>

<template>
  <div id="app">
    <!-- Navigation Bar (only show when authenticated) -->
    <nav v-if="isAuthenticated" class="navbar navbar-expand-lg navbar-dark bg-primary">
      <div class="container-fluid">
        <router-link class="navbar-brand" to="/dashboard">
          <i class="fas fa-hospital"></i>
          Hospital Admin System
        </router-link>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/dashboard" active-class="active">
                <i class="fas fa-tachometer-alt"></i> แดชบอร์ด
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/departments" active-class="active">
                <i class="fas fa-building"></i> แผนก
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/contacts" active-class="active">
                <i class="fas fa-address-book"></i> รายชื่อติดต่อ
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/cases" active-class="active">
                <i class="fas fa-user-injured"></i> เคสผู้ป่วย
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/backups" active-class="active">
                <i class="fas fa-database"></i> สำรองข้อมูล
              </router-link>
            </li>
          </ul>
          
          <ul class="navbar-nav">
            <li class="nav-item dropdown" v-if="currentUser">
              <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                <i class="fas fa-user"></i> {{ currentUser.username }}
              </a>
              <ul class="dropdown-menu">
                <li><a class="dropdown-item" href="#" @click="logout">
                  <i class="fas fa-sign-out-alt"></i> ออกจากระบบ
                </a></li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- Loading Overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </div>
</template>

<style>
/* Global Styles */
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding: 0;
}

/* Navigation Styles */
.navbar-brand {
  font-weight: bold;
  font-size: 1.25rem;
}

.navbar-nav .nav-link {
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  margin: 0 0.25rem;
  transition: all 0.3s ease;
}

.navbar-nav .nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.navbar-nav .nav-link.active {
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: bold;
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-overlay .spinner-border {
  width: 3rem;
  height: 3rem;
}

/* Utility Classes */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .navbar-nav .nav-link {
    margin: 0.25rem 0;
  }
  
  .main-content {
    padding: 1rem;
  }
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
