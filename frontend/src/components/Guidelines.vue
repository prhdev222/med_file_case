<template>
  <div class="container mt-4">
    <div class="row">
      <div class="col-12">
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/admin/dashboard">แดชบอร์ด</router-link>
            </li>
            <li class="breadcrumb-item active">จัดการ Guidelines</li>
          </ol>
        </nav>
      </div>
    </div>

    <div class="row mb-4">
      <div class="col-md-8">
        <h1 class="mb-0">
          <i class="fas fa-file-medical me-2"></i>จัดการ Guidelines
        </h1>
      </div>
      <div class="col-md-4 text-end">
        <router-link to="/admin/guidelines/add" class="btn btn-primary">
          <i class="fas fa-plus me-2"></i>เพิ่ม Guidelines ใหม่
        </router-link>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <h5 class="mb-0"><i class="fas fa-list me-2"></i>รายการ Guidelines ทั้งหมด</h5>
      </div>
      <div class="card-body">
        <div v-if="guidelines.length > 0">
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>ชื่อไฟล์</th>
                  <th>หน่วยงาน</th>
                  <th>ประเภท</th>
                  <th>ขนาด/ลิงก์</th>
                  <th>วันที่อัปโหลด</th>
                  <th>คำอธิบาย</th>
                  <th>การดำเนินการ</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="guideline in guidelines" :key="guideline.id">
                  <td>
                    <i v-if="guideline.external_link" class="fas fa-link me-2 text-primary"></i>
                    <i v-else class="fas fa-file-pdf me-2 text-danger"></i>
                    {{ guideline.title }}
                  </td>
                  <td>
                    <span class="badge bg-primary">{{ guideline.department?.code || 'N/A' }}</span>
                    {{ guideline.department?.name || 'ไม่ระบุ' }}
                  </td>
                  <td>
                    <span v-if="guideline.external_link" class="badge bg-success">
                      {{ guideline.link_type || 'External Link' }}
                    </span>
                    <span v-else class="badge bg-info">ไฟล์</span>
                  </td>
                  <td>
                    <a v-if="guideline.external_link" 
                       :href="guideline.external_link" 
                       target="_blank" 
                       class="text-primary">
                      <i class="fas fa-external-link-alt me-1"></i>เปิดลิงก์
                    </a>
                    <span v-else>
                      {{ formatFileSize(guideline.file_size) }} MB
                    </span>
                  </td>
                  <td>{{ formatDate(guideline.upload_date) }}</td>
                  <td>{{ guideline.description || '-' }}</td>
                  <td>
                    <div class="btn-group" role="group">
                      <a v-if="guideline.external_link" 
                         :href="guideline.external_link" 
                         target="_blank" 
                         class="btn btn-sm btn-outline-primary">
                        <i class="fas fa-external-link-alt"></i>
                      </a>
                      <a v-else 
                         :href="getDownloadUrl(guideline.id)" 
                         class="btn btn-sm btn-outline-primary">
                        <i class="fas fa-download"></i>
                      </a>
                      <router-link :to="`/admin/guidelines/edit/${guideline.id}`" 
                                   class="btn btn-sm btn-outline-warning">
                        <i class="fas fa-edit"></i>
                      </router-link>
                      <button type="button" 
                              class="btn btn-sm btn-outline-danger" 
                              @click="deleteGuideline(guideline.id)">
                        <i class="fas fa-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div v-else class="text-center py-5">
          <i class="fas fa-file-medical fa-3x text-muted mb-3"></i>
          <h5 class="text-muted">ยังไม่มีไฟล์ Guidelines</h5>
          <p class="text-muted">เริ่มต้นโดยการเพิ่มไฟล์ Guidelines ใหม่</p>
          <router-link to="/admin/guidelines/add" class="btn btn-primary">
            <i class="fas fa-plus me-2"></i>เพิ่ม Guidelines แรก
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import apiService from '../services/apiService'

export default {
  name: 'Guidelines',
  setup() {
    const guidelines = ref([])
    const loading = ref(true)
    const error = ref(null)

    const fetchGuidelines = async () => {
      try {
        loading.value = true
        const response = await apiService.getGuidelines()
        guidelines.value = response.data || response
      } catch (err) {
        console.error('Error fetching guidelines:', err)
        error.value = 'เกิดข้อผิดพลาดในการโหลดข้อมูล Guidelines'
      } finally {
        loading.value = false
      }
    }

    const deleteGuideline = async (id) => {
      if (confirm('คุณแน่ใจหรือไม่ที่จะลบ guideline นี้?')) {
        try {
          await apiService.deleteGuideline(id)
          await fetchGuidelines() // Refresh the list
        } catch (err) {
          console.error('Error deleting guideline:', err)
          alert('เกิดข้อผิดพลาดในการลบ guideline')
        }
      }
    }

    const getDownloadUrl = (guidelineId) => {
      return `${apiService.baseURL}/download/guideline/${guidelineId}`
    }

    const formatFileSize = (bytes) => {
      if (!bytes) return '0'
      return (bytes / 1024 / 1024).toFixed(2)
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('th-TH', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(() => {
      fetchGuidelines()
    })

    return {
      guidelines,
      loading,
      error,
      deleteGuideline,
      getDownloadUrl,
      formatFileSize,
      formatDate
    }
  }
}
</script>

<style scoped>
.badge {
  font-size: 0.8em;
}

.btn-group .btn {
  margin: 0 2px;
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.breadcrumb-item a {
  text-decoration: none;
}

.breadcrumb-item a:hover {
  text-decoration: underline;
}
</style>