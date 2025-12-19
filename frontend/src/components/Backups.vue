<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const backups = ref([])
const loading = ref(true)
const showModal = ref(false)
const backupInProgress = ref(false)
const restoreInProgress = ref(false)
const selectedBackup = ref(null)

const formData = ref({
  name: '',
  description: '',
  include_files: true,
  include_database: true,
  compress: true
})

const sortedBackups = computed(() => {
  return backups.value.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getStatusClass = (status) => {
  switch (status) {
    case 'completed': return 'bg-success'
    case 'failed': return 'bg-danger'
    case 'in_progress': return 'bg-warning'
    default: return 'bg-secondary'
  }
}

const getStatusLabel = (status) => {
  switch (status) {
    case 'completed': return 'สำเร็จ'
    case 'failed': return 'ล้มเหลว'
    case 'in_progress': return 'กำลังดำเนินการ'
    default: return 'ไม่ทราบสถานะ'
  }
}

const loadBackups = async () => {
  try {
    const response = await axios.get('/api/backups')
    backups.value = response.data
  } catch (error) {
    console.error('Error loading backups:', error)
  } finally {
    loading.value = false
  }
}

const openModal = () => {
  formData.value = {
    name: `Backup_${new Date().toISOString().split('T')[0]}_${new Date().toTimeString().split(' ')[0].replace(/:/g, '')}`,
    description: '',
    include_files: true,
    include_database: true,
    compress: true
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const createBackup = async () => {
  backupInProgress.value = true
  try {
    await axios.post('/api/backups', formData.value)
    closeModal()
    loadBackups()
  } catch (error) {
    console.error('Error creating backup:', error)
    alert('เกิดข้อผิดพลาดในการสร้างสำรองข้อมูล')
  } finally {
    backupInProgress.value = false
  }
}

const downloadBackup = async (backup) => {
  try {
    const response = await axios.get(`/api/backups/${backup.id}/download`, {
      responseType: 'blob'
    })
    
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', backup.filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error downloading backup:', error)
    alert('เกิดข้อผิดพลาดในการดาวน์โหลดไฟล์สำรอง')
  }
}

const restoreBackup = async (backup) => {
  if (!confirm(`คุณแน่ใจหรือไม่ที่จะคืนค่าข้อมูลจากไฟล์สำรอง "${backup.name}"?\n\nการดำเนินการนี้จะเขียนทับข้อมูลปัจจุบันทั้งหมด`)) {
    return
  }
  
  restoreInProgress.value = true
  selectedBackup.value = backup
  
  try {
    await axios.post(`/api/backups/${backup.id}/restore`)
    alert('คืนค่าข้อมูลสำเร็จ')
    loadBackups()
  } catch (error) {
    console.error('Error restoring backup:', error)
    alert('เกิดข้อผิดพลาดในการคืนค่าข้อมูล')
  } finally {
    restoreInProgress.value = false
    selectedBackup.value = null
  }
}

const deleteBackup = async (backup) => {
  if (!confirm(`คุณแน่ใจหรือไม่ที่จะลบไฟล์สำรอง "${backup.name}"?`)) {
    return
  }
  
  try {
    await axios.delete(`/api/backups/${backup.id}`)
    loadBackups()
  } catch (error) {
    console.error('Error deleting backup:', error)
    alert('เกิดข้อผิดพลาดในการลบไฟล์สำรอง')
  }
}

const refreshBackups = () => {
  loading.value = true
  loadBackups()
}

onMounted(() => {
  loadBackups()
})
</script>

<template>
  <div class="backups">
    <div class="container-fluid">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h1 class="h3 mb-0">
                <i class="bi bi-shield-check me-2"></i>
                จัดการสำรองข้อมูล
              </h1>
              <p class="text-muted">สำรองและคืนค่าข้อมูลระบบ</p>
            </div>
            <div class="btn-group" role="group">
              <button 
                class="btn btn-outline-secondary"
                @click="refreshBackups()"
                :disabled="loading"
              >
                <i class="bi bi-arrow-clockwise me-2"></i>
                รีเฟรช
              </button>
              <button 
                class="btn btn-primary"
                @click="openModal()"
                :disabled="backupInProgress"
              >
                <span v-if="backupInProgress" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-plus-circle me-2"></i>
                {{ backupInProgress ? 'กำลังสำรอง...' : 'สำรองข้อมูลใหม่' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="row mb-4" v-if="!loading">
        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-primary shadow h-100 py-2">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">
                    ไฟล์สำรองทั้งหมด
                  </div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    {{ backups.length }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="bi bi-archive-fill fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-success shadow h-100 py-2">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-success text-uppercase mb-1">
                    สำรองสำเร็จ
                  </div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    {{ backups.filter(b => b.status === 'completed').length }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="bi bi-check-circle-fill fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-warning shadow h-100 py-2">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">
                    ขนาดรวม
                  </div>
                  <div class="h5 mb-0 font-weight-bold text-gray-800">
                    {{ formatFileSize(backups.reduce((sum, b) => sum + (b.file_size || 0), 0)) }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="bi bi-hdd-fill fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="col-xl-3 col-md-6 mb-4">
          <div class="card border-left-info shadow h-100 py-2">
            <div class="card-body">
              <div class="row no-gutters align-items-center">
                <div class="col mr-2">
                  <div class="text-xs font-weight-bold text-info text-uppercase mb-1">
                    สำรองล่าสุด
                  </div>
                  <div class="h6 mb-0 font-weight-bold text-gray-800">
                    {{ backups.length > 0 ? new Date(sortedBackups[0].created_at).toLocaleDateString('th-TH') : 'ไม่มี' }}
                  </div>
                </div>
                <div class="col-auto">
                  <i class="bi bi-clock-fill fa-2x text-gray-300"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div class="row" v-if="loading">
        <div class="col-12 text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">กำลังโหลด...</span>
          </div>
          <p class="mt-2 text-muted">กำลังโหลดข้อมูลสำรอง...</p>
        </div>
      </div>

      <!-- Backups Table -->
      <div class="row" v-if="!loading">
        <div class="col-12">
          <div class="card shadow">
            <div class="card-header">
              <h6 class="m-0 font-weight-bold text-primary">
                <i class="bi bi-list-ul me-2"></i>
                รายการไฟล์สำรอง
              </h6>
            </div>
            <div class="card-body">
              <div class="table-responsive" v-if="sortedBackups.length > 0">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>ชื่อไฟล์สำรอง</th>
                      <th>คำอธิบาย</th>
                      <th>ขนาดไฟล์</th>
                      <th>สถานะ</th>
                      <th>วันที่สร้าง</th>
                      <th class="text-center">จัดการ</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="backup in sortedBackups" :key="backup.id">
                      <td>
                        <div class="d-flex align-items-center">
                          <i class="bi bi-file-earmark-zip me-2 text-primary"></i>
                          <div>
                            <strong>{{ backup.name }}</strong>
                            <br>
                            <small class="text-muted">{{ backup.filename }}</small>
                          </div>
                        </div>
                      </td>
                      <td>
                        <div class="description-cell">
                          {{ backup.description || '-' }}
                        </div>
                      </td>
                      <td>
                        <span class="badge bg-info">{{ formatFileSize(backup.file_size || 0) }}</span>
                      </td>
                      <td>
                        <span class="badge" :class="getStatusClass(backup.status)">
                          {{ getStatusLabel(backup.status) }}
                        </span>
                      </td>
                      <td>
                        <div>
                          {{ new Date(backup.created_at).toLocaleDateString('th-TH') }}
                          <br>
                          <small class="text-muted">
                            {{ new Date(backup.created_at).toLocaleTimeString('th-TH') }}
                          </small>
                        </div>
                      </td>
                      <td class="text-center">
                        <div class="btn-group btn-group-sm" role="group">
                          <button 
                            class="btn btn-outline-success"
                            @click="downloadBackup(backup)"
                            title="ดาวน์โหลด"
                            :disabled="backup.status !== 'completed'"
                          >
                            <i class="bi bi-download"></i>
                          </button>
                          <button 
                            class="btn btn-outline-warning"
                            @click="restoreBackup(backup)"
                            title="คืนค่าข้อมูล"
                            :disabled="backup.status !== 'completed' || restoreInProgress"
                          >
                            <span v-if="restoreInProgress && selectedBackup?.id === backup.id" class="spinner-border spinner-border-sm"></span>
                            <i v-else class="bi bi-arrow-clockwise"></i>
                          </button>
                          <button 
                            class="btn btn-outline-danger"
                            @click="deleteBackup(backup)"
                            title="ลบ"
                            :disabled="restoreInProgress"
                          >
                            <i class="bi bi-trash"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <!-- Empty State -->
              <div v-else class="text-center py-5">
                <i class="bi bi-archive display-4 text-muted"></i>
                <h4 class="mt-3 text-muted">ไม่มีไฟล์สำรอง</h4>
                <p class="text-muted">เริ่มต้นโดยการสร้างไฟล์สำรองแรก</p>
                <button class="btn btn-primary" @click="openModal()">
                  <i class="bi bi-plus-circle me-2"></i>
                  สำรองข้อมูลแรก
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div class="modal fade" :class="{ show: showModal }" :style="{ display: showModal ? 'block' : 'none' }" v-if="showModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-shield-plus me-2"></i>
              สร้างไฟล์สำรองใหม่
            </h5>
            <button type="button" class="btn-close" @click="closeModal()"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="createBackup()">
              <div class="mb-3">
                <label for="name" class="form-label">ชื่อไฟล์สำรอง *</label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="name" 
                  v-model="formData.name" 
                  required
                >
              </div>
              
              <div class="mb-3">
                <label for="description" class="form-label">คำอธิบาย</label>
                <textarea 
                  class="form-control" 
                  id="description" 
                  rows="3" 
                  v-model="formData.description"
                  placeholder="อธิบายเหตุผลในการสำรองข้อมูลครั้งนี้"
                ></textarea>
              </div>
              
              <div class="mb-3">
                <label class="form-label">ตัวเลือกการสำรอง</label>
                <div class="form-check">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    id="include_database" 
                    v-model="formData.include_database"
                  >
                  <label class="form-check-label" for="include_database">
                    <i class="bi bi-database me-2"></i>
                    รวมฐานข้อมูล
                  </label>
                </div>
                <div class="form-check">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    id="include_files" 
                    v-model="formData.include_files"
                  >
                  <label class="form-check-label" for="include_files">
                    <i class="bi bi-folder me-2"></i>
                    รวมไฟล์ระบบ
                  </label>
                </div>
                <div class="form-check">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    id="compress" 
                    v-model="formData.compress"
                  >
                  <label class="form-check-label" for="compress">
                    <i class="bi bi-file-zip me-2"></i>
                    บีบอัดไฟล์
                  </label>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal()" :disabled="backupInProgress">
              ยกเลิก
            </button>
            <button type="button" class="btn btn-primary" @click="createBackup()" :disabled="backupInProgress">
              <span v-if="backupInProgress" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-shield-check me-2"></i>
              {{ backupInProgress ? 'กำลังสำรอง...' : 'เริ่มสำรองข้อมูล' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade" :class="{ show: showModal }" v-if="showModal"></div>
  </div>
</template>

<style scoped>
.border-left-primary {
  border-left: 0.25rem solid #4e73df !important;
}

.border-left-success {
  border-left: 0.25rem solid #1cc88a !important;
}

.border-left-info {
  border-left: 0.25rem solid #36b9cc !important;
}

.border-left-warning {
  border-left: 0.25rem solid #f6c23e !important;
}

.text-xs {
  font-size: 0.7rem;
}

.text-gray-300 {
  color: #dddfeb !important;
}

.text-gray-800 {
  color: #5a5c69 !important;
}

.fa-2x {
  font-size: 2em;
}

.description-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.modal {
  z-index: 1050;
}

.modal-backdrop {
  z-index: 1040;
}

.table th {
  border-top: none;
  font-weight: 600;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
}

.card {
  border-radius: 0.35rem;
}

.shadow {
  box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15) !important;
}
</style>