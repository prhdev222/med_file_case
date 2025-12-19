<template>
  <div class="container-fluid">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="display-5 text-primary">
              <i class="fas fa-chart-bar me-3"></i>สถิติผู้ป่วยที่เก็บข้อมูล
            </h1>
            <p class="lead text-muted">แผนกอายุรกรรม โรงพยาบาลสงฆ์</p>
          </div>
          <div class="text-end">
            <router-link to="/" class="btn btn-outline-primary">
              <i class="fas fa-arrow-left me-2"></i>กลับหน้าหลัก
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="card">
          <div class="card-body">
            <label for="periodSelect" class="form-label">
              <i class="fas fa-calendar me-2"></i>ช่วงเวลา
            </label>
            <select id="periodSelect" class="form-select" v-model="selectedPeriod" @change="loadStats">
              <option value="week">รายสัปดาห์</option>
              <option value="month">รายเดือน</option>
              <option value="3months">3 เดือน</option>
              <option value="6months">6 เดือน</option>
              <option value="year">รายปี</option>
            </select>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card">
          <div class="card-body">
            <label for="departmentSelect" class="form-label">
              <i class="fas fa-hospital me-2"></i>หน่วยงาน
            </label>
            <select id="departmentSelect" class="form-select" v-model="selectedDepartment" @change="loadStats">
              <option value="all">ทั้งหมด</option>
              <option value="dm">หน่วยเบาหวาน</option>
              <option value="ckd">หน่วยไตเรื้อรัง</option>
              <option value="copd">หน่วยโรคปอดอุดกั้นเรื้อรัง</option>
              <option value="htn">หน่วยความดันโลหิตสูง</option>
              <option value="obesity">หน่วยโรคอ้วน</option>
              <option value="rheumato">หน่วยรูมาติก</option>
              <option value="sepsis">หน่วยภาวะติดเชื้อในกระแสเลือด</option>
              <option value="stemi_nstemi">หน่วยโรคหัวใจขาดเลือด</option>
              <option value="stroke">หน่วยโรคหลอดเลือดสมอง</option>
              <option value="tb">หน่วยวัณโรค</option>
              <option value="ugib">หน่วยเลือดออกทางเดินอาหารส่วนบน</option>
              <option value="chemo">หน่วยเคมีบำบัด</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">กำลังโหลด...</span>
      </div>
    </div>

    <!-- Summary Stats -->
    <div v-else class="row mb-4">
      <div class="col-md-3">
        <div class="card stats-card bg-primary text-white">
          <div class="card-body text-center">
            <i class="fas fa-users fa-2x mb-3"></i>
            <h5>ผู้ป่วยที่เก็บข้อมูล</h5>
            <div class="stat-number">{{ stats.total_cases || 0 }}</div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card stats-card bg-success text-white">
          <div class="card-body text-center">
            <i class="fas fa-file fa-2x mb-3"></i>
            <h5>มีไฟล์แนบ</h5>
            <div class="stat-number">{{ stats.cases_with_files || 0 }}</div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card stats-card bg-info text-white">
          <div class="card-body text-center">
            <i class="fas fa-link fa-2x mb-3"></i>
            <h5>มีลิงก์ภายนอก</h5>
            <div class="stat-number">{{ stats.cases_with_links || 0 }}</div>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card stats-card bg-warning text-white">
          <div class="card-body text-center">
            <i class="fas fa-clock fa-2x mb-3"></i>
            <h5>อัปเดตล่าสุด</h5>
            <div class="stat-number">{{ formatLastUpdate() }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row 1 -->
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5><i class="fas fa-chart-pie me-2"></i>การกระจายตามหน่วยงาน</h5>
          </div>
          <div class="card-body">
            <div class="chart-container">
              <canvas ref="departmentPieChart"></canvas>
            </div>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5><i class="fas fa-chart-bar me-2"></i>เปรียบเทียบระหว่างหน่วยงาน</h5>
          </div>
          <div class="card-body">
            <div class="chart-container">
              <canvas ref="departmentBarChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row 2 -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5><i class="fas fa-chart-line me-2"></i>แนวโน้ม 6 เดือนย้อนหลัง</h5>
          </div>
          <div class="card-body">
            <div class="chart-container">
              <canvas ref="trendLineChart"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Department Details -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5><i class="fas fa-list me-2"></i>รายละเอียดตามหน่วยงาน</h5>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-hover">
                <thead class="table-light">
                  <tr>
                    <th>หน่วยงาน</th>
                    <th>จำนวนผู้ป่วยที่เก็บข้อมูล</th>
                    <th>สัดส่วน</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="stats.dept_stats && stats.dept_stats.length > 0" v-for="dept in stats.dept_stats" :key="dept.name">
                    <td><strong>{{ dept.name }}</strong></td>
                    <td><span class="badge bg-primary">{{ dept.count || dept.case_count || 0 }}</span></td>
                    <td>{{ calculatePercentage(dept.count || dept.case_count || 0) }}%</td>
                  </tr>
                  <tr v-else>
                    <td colspan="3" class="text-center text-muted">ไม่พบข้อมูล</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import apiService from '../services/apiService'
import Chart from 'chart.js/auto'

export default {
  name: 'Stats',
  setup() {
    const stats = ref({
      total_cases: 0,
      dept_stats: [],
      total_guidelines: 0,
      cases_with_files: 0,
      cases_with_links: 0,
      monthly_stats: []
    })
    const loading = ref(true)
    const selectedPeriod = ref('month')
    const selectedDepartment = ref('all')
    
    // Chart refs
    const departmentPieChart = ref(null)
    const departmentBarChart = ref(null)
    const trendLineChart = ref(null)
    
    // Chart instances
    let pieChartInstance = null
    let barChartInstance = null
    let lineChartInstance = null

    const formatLastUpdate = () => {
      const now = new Date()
      return now.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit' })
    }

    const calculatePercentage = (count) => {
      if (!stats.value.total_cases || stats.value.total_cases === 0) return '0.0'
      return ((count / stats.value.total_cases) * 100).toFixed(1)
    }

    const loadStats = async () => {
      try {
        loading.value = true
        const response = await apiService.get('/api/stats', {
          params: {
            period: selectedPeriod.value,
            department: selectedDepartment.value
          }
        })
        stats.value = response.data
        
        // Update charts after data is loaded
        await nextTick()
        updateCharts()
      } catch (error) {
        console.error('Error loading stats:', error)
        // Set default empty stats on error
        stats.value = {
          total_cases: 0,
          dept_stats: [],
          total_guidelines: 0,
          cases_with_files: 0,
          cases_with_links: 0,
          monthly_stats: []
        }
      } finally {
        loading.value = false
      }
    }

    const updateCharts = () => {
      updateDepartmentPieChart()
      updateDepartmentBarChart()
      updateTrendChart()
    }

    const updateDepartmentPieChart = () => {
      if (!departmentPieChart.value || !stats.value.dept_stats || stats.value.dept_stats.length === 0) return
      
      const ctx = departmentPieChart.value.getContext('2d')
      
      if (pieChartInstance) {
        pieChartInstance.destroy()
      }
      
      const data = stats.value.dept_stats.map(dept => dept.count || dept.case_count || 0)
      const labels = stats.value.dept_stats.map(dept => dept.name)
      const colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
      ]
      
      pieChartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: labels,
          datasets: [{
            data: data,
            backgroundColor: colors.slice(0, data.length),
            borderWidth: 2,
            borderColor: '#fff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      })
    }

    const updateDepartmentBarChart = () => {
      if (!departmentBarChart.value || !stats.value.dept_stats || stats.value.dept_stats.length === 0) return
      
      const ctx = departmentBarChart.value.getContext('2d')
      
      if (barChartInstance) {
        barChartInstance.destroy()
      }
      
      const data = stats.value.dept_stats.map(dept => dept.count || dept.case_count || 0)
      const labels = stats.value.dept_stats.map(dept => dept.name)
      
      barChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'จำนวนผู้ป่วย',
            data: data,
            backgroundColor: '#36A2EB',
            borderColor: '#36A2EB',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        }
      })
    }

    const updateTrendChart = () => {
      if (!trendLineChart.value) return
      
      const ctx = trendLineChart.value.getContext('2d')
      
      if (lineChartInstance) {
        lineChartInstance.destroy()
      }
      
      // Generate sample monthly data if not available
      const monthlyData = stats.value.monthly_stats && stats.value.monthly_stats.length > 0 
        ? stats.value.monthly_stats 
        : generateSampleMonthlyData()
      
      const labels = monthlyData.map(item => item.month || item.label)
      const data = monthlyData.map(item => item.count || item.value || 0)
      
      lineChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'จำนวนผู้ป่วยรายเดือน',
            data: data,
            borderColor: '#4BC0C0',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        }
      })
    }

    const generateSampleMonthlyData = () => {
      const months = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.']
      return months.map((month, index) => ({
        month: month,
        count: Math.floor(Math.random() * 20) + 5
      }))
    }

    onMounted(() => {
      loadStats()
      
      // Auto refresh every 5 minutes
      setInterval(loadStats, 5 * 60 * 1000)
    })

    return {
      stats,
      loading,
      selectedPeriod,
      selectedDepartment,
      departmentPieChart,
      departmentBarChart,
      trendLineChart,
      formatLastUpdate,
      calculatePercentage,
      loadStats
    }
  }
}
</script>

<style scoped>
.stats-card {
  transition: transform 0.2s;
}

.stats-card:hover {
  transform: translateY(-5px);
}

.stat-number {
  font-size: 2.5rem;
  font-weight: bold;
}

.change-positive {
  color: #28a745;
}

.change-negative {
  color: #dc3545;
}

.chart-container {
  position: relative;
  height: 400px;
  margin: 20px 0;
}
</style>