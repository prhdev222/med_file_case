<script>
import { ref, reactive, onMounted } from 'vue'
import apiService from '../services/api.js'

export default {
  name: 'Dashboard',
  setup() {
    const isLoading = ref(false)
    const isLoadingActivities = ref(false)
    const lastBackupTime = ref('')
    
    const stats = reactive({
      departments: 0,
      contacts: 0,
      cases: 0,
      today_cases: 0
    })
    
    const activities = ref([])

    const loadStats = async () => {
      try {
        const response = await apiService.getDashboardStats()
        if (response.success) {
          Object.assign(stats, response.stats)
        }
      } catch (error) {
        console.error('Failed to load stats:', error)
      }
    }

    const loadActivities = async () => {
      isLoadingActivities.value = true
      try {
        const response = await apiService.getRecentActivities()
        if (response.success) {
          activities.value = response.activities
        }
      } catch (error) {
        console.error('Failed to load activities:', error)
      } finally {
        isLoadingActivities.value = false
      }
    }

    const refreshData = async () => {
      isLoading.value = true
      try {
        await Promise.all([
          loadStats(),
          loadActivities()
        ])
      } finally {
        isLoading.value = false
      }
    }

    const getActivityIcon = (type) => {
      const icons = {
        'create': 'fas fa-plus',
        'update': 'fas fa-edit',
        'delete': 'fas fa-trash',
        'login': 'fas fa-sign-in-alt',
        'logout': 'fas fa-sign-out-alt',
        'backup': 'fas fa-database'
      }
      return icons[type] || 'fas fa-info'
    }

    const getActivityIconClass = (type) => {
      const classes = {
        'create': 'activity-icon-success',
        'update': 'activity-icon-warning',
        'delete': 'activity-icon-danger',
        'login': 'activity-icon-info',
        'logout': 'activity-icon-secondary',
        'backup': 'activity-icon-primary'
      }
      return classes[type] || 'activity-icon-info'
    }

    const formatDateTime = (timestamp) => {
      if (!timestamp) return ''
      const date = new Date(timestamp)
      return date.toLocaleString('th-TH', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(() => {
      refreshData()
      // Set up auto-refresh every 5 minutes
      const interval = setInterval(refreshData, 5 * 60 * 1000)
      
      // Cleanup interval on unmount
      return () => clearInterval(interval)
    })

    return {
      isLoading,
      isLoadingActivities,
      stats,
      activities,
      lastBackupTime,
      refreshData,
      getActivityIcon,
      getActivityIconClass,
      formatDateTime
    }
  }
}
</script>

<template>
  <div class="dashboard">
    <!-- Page Header -->
    <div class="page-header">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col">
            <h1 class="page-title">
              <i class="fas fa-tachometer-alt"></i>
              แดชบอร์ด
            </h1>
            <p class="page-subtitle">ภาพรวมระบบจัดการโรงพยาบาล</p>
          </div>
          <div class="col-auto">
            <button class="btn btn-primary" @click="refreshData" :disabled="isLoading">
              <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
              รีเฟรช
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="container-fluid">
      <div class="row g-4 mb-4">
        <div class="col-xl-3 col-md-6">
          <div class="stats-card stats-primary">
            <div class="stats-icon">
              <i class="fas fa-building"></i>
            </div>
            <div class="stats-content">
              <h3 class="stats-number">{{ stats.departments || 0 }}</h3>
              <p class="stats-label">แผนก</p>
            </div>
          </div>
        </div>
        
        <div class="col-xl-3 col-md-6">
          <div class="stats-card stats-success">
            <div class="stats-icon">
              <i class="fas fa-address-book"></i>
            </div>
            <div class="stats-content">
              <h3 class="stats-number">{{ stats.contacts || 0 }}</h3>
              <p class="stats-label">รายชื่อติดต่อ</p>
            </div>
          </div>
        </div>
        
        <div class="col-xl-3 col-md-6">
          <div class="stats-card stats-warning">
            <div class="stats-icon">
              <i class="fas fa-user-injured"></i>
            </div>
            <div class="stats-content">
              <h3 class="stats-number">{{ stats.cases || 0 }}</h3>
              <p class="stats-label">เคสผู้ป่วย</p>
            </div>
          </div>
        </div>
        
        <div class="col-xl-3 col-md-6">
          <div class="stats-card stats-info">
            <div class="stats-icon">
              <i class="fas fa-calendar-day"></i>
            </div>
            <div class="stats-content">
              <h3 class="stats-number">{{ stats.today_cases || 0 }}</h3>
              <p class="stats-label">เคสวันนี้</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent Activities -->
      <div class="row">
        <div class="col-12">
          <div class="activity-card">
            <div class="activity-header">
              <h5 class="activity-title">
                <i class="fas fa-history"></i>
                กิจกรรมล่าสุด
              </h5>
            </div>
            <div class="activity-body">
              <div v-if="isLoading" class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">กำลังโหลด...</span>
                </div>
              </div>
              
              <div v-else-if="activities.length === 0" class="text-center py-4 text-muted">
                <i class="fas fa-inbox fa-3x mb-3"></i>
                <p>ไม่มีกิจกรรมล่าสุด</p>
              </div>
              
              <div v-else class="activity-list">
                <div 
                  v-for="activity in activities" 
                  :key="activity.id" 
                  class="activity-item"
                >
                  <div class="activity-icon" :class="getActivityIconClass(activity.type)">
                    <i :class="getActivityIcon(activity.type)"></i>
                  </div>
                  <div class="activity-content">
                    <div class="activity-text">{{ activity.description }}</div>
                    <div class="activity-time">{{ formatDateTime(activity.created_at) }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  min-height: 100vh;
  background-color: #f8fafc;
}

/* Page Header */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem 0;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.page-title i {
  margin-right: 0.75rem;
  color: rgba(255, 255, 255, 0.9);
}

.page-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 0;
}

/* Statistics Cards */
.stats-card {
  background: white;
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 1rem;
  height: 100%;
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
}

.stats-primary .stats-icon {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stats-success .stats-icon {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stats-warning .stats-icon {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stats-info .stats-icon {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.stats-content {
  flex: 1;
}

.stats-number {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.stats-label {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 0;
  font-weight: 500;
}

/* Activity Card */
.activity-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.activity-header {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  padding: 1.5rem;
  color: white;
}

.activity-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0;
}

.activity-title i {
  margin-right: 0.5rem;
}

.activity-body {
  padding: 1.5rem;
}

.activity-list {
  max-height: 400px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  color: white;
  flex-shrink: 0;
}

.activity-icon-success {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.activity-icon-warning {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.activity-icon-danger {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
}

.activity-icon-info {
  background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
}

.activity-icon-secondary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.activity-icon-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 0.25rem;
}

.activity-time {
  font-size: 0.875rem;
  color: #6b7280;
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-header {
    padding: 1.5rem 0;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .stats-card {
    padding: 1rem;
  }
  
  .stats-number {
    font-size: 1.5rem;
  }
}
</style>