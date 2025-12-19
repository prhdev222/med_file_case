<template>
  <div class="container-fluid">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h2 class="text-primary mb-1">
              <i class="fas fa-users me-2"></i>จัดการข้อมูลผู้ป่วย
            </h2>
            <p class="text-muted mb-0">ระบบจัดการข้อมูลผู้ป่วยและเอกสารที่เกี่ยวข้อง</p>
          </div>
          <router-link to="/admin/add-case" class="btn btn-primary">
            <i class="fas fa-plus me-2"></i>เพิ่มผู้ป่วยใหม่
          </router-link>
        </div>
      </div>
    </div>

    <!-- Search and Stats -->
    <div class="row mb-4">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="fas fa-search me-2"></i>ค้นหาข้อมูลผู้ป่วย
            </h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="searchCases" class="row g-3">
              <div class="col-md-3">
                <label for="searchHN" class="form-label">HN</label>
                <input
                  type="text"
                  class="form-control"
                  id="searchHN"
                  v-model="searchForm.hn"
                  placeholder="ค้นหาด้วย HN"
                />
              </div>
              <div class="col-md-3">
                <label for="searchFirstName" class="form-label">ชื่อ</label>
                <input
                  type="text"
                  class="form-control"
                  id="searchFirstName"
                  v-model="searchForm.firstName"
                  placeholder="ชื่อ"
                />
              </div>
              <div class="col-md-3">
                <label for="searchLastName" class="form-label">นามสกุล</label>
                <input
                  type="text"
                  class="form-control"
                  id="searchLastName"
                  v-model="searchForm.lastName"
                  placeholder="นามสกุล"
                />
              </div>
              <div class="col-md-3">
                <label for="searchDepartment" class="form-label">หน่วยงาน</label>
                <select class="form-select" id="searchDepartment" v-model="searchForm.departmentId">
                  <option value="">ทั้งหมด</option>
                  <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                    {{ dept.name }}
                  </option>
                </select>
              </div>
              <div class="col-md-2">
                <label class="form-label">&nbsp;</label>
                <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                  <i class="fas fa-search me-2"></i>ค้นหา
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card">
          <div class="card-body text-center">
            <h5 class="card-title text-primary">
              <i class="fas fa-chart-bar me-2"></i>สถิติรวม
            </h5>
            <div class="display-6 text-primary">{{ totalCases }}</div>
            <p class="text-muted mb-0">รายการทั้งหมด</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Cases Table -->
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="fas fa-list me-2"></i>รายการผู้ป่วย
              <span v-if="isSearching" class="badge bg-info ms-2">ผลการค้นหา</span>
            </h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">กำลังโหลด...</span>
              </div>
            </div>
            
            <div v-else-if="cases.length > 0">
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>ID</th>
                      <th>HN</th>
                      <th>ชื่อ-นามสกุล</th>
                      <th>หน่วยงาน</th>
                      <th>วันที่</th>
                      <th>หมายเหตุ</th>
                      <th>เอกสาร</th>
                      <th>วันที่สร้าง</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="caseItem in cases" :key="caseItem.id">
                      <td>
                        <span class="badge bg-secondary">#{{ caseItem.id }}</span>
                      </td>
                      <td>
                        <strong class="text-primary">{{ caseItem.hn }}</strong>
                      </td>
                      <td>
                        <div>
                          <strong>{{ caseItem.first_name }}</strong>
                          <br>
                          <small class="text-muted">{{ caseItem.last_name }}</small>
                        </div>
                      </td>
                      <td>
                        <span class="badge bg-info">{{ caseItem.department?.name || 'ไม่ระบุ' }}</span>
                      </td>
                      <td>
                        <span class="text-success">{{ formatDate(caseItem.case_date) }}</span>
                      </td>
                      <td>
                        <span v-if="caseItem.notes" class="text-muted">
                          {{ caseItem.notes.length > 50 ? caseItem.notes.substring(0, 50) + '...' : caseItem.notes }}
                        </span>
                        <span v-else class="text-muted">-</span>
                      </td>
                      <td>
                        <div v-if="caseItem.file_path" class="d-flex align-items-center">
                          <i :class="getFileIcon(caseItem.file_path)" class="me-2"></i>
                          <span class="text-muted">
                            {{ getFileName(caseItem.file_path) }}
                          </span>
                          <button 
                            @click="downloadFile(caseItem.id)" 
                            class="btn btn-sm btn-outline-primary ms-2" 
                            title="ดาวน์โหลด"
                          >
                            <i class="fas fa-download"></i>
                          </button>
                        </div>
                        <div v-else-if="caseItem.external_link" class="d-flex align-items-center">
                          <i class="fas fa-link text-success me-2"></i>
                          <a :href="caseItem.external_link" target="_blank" class="text-success">
                            {{ caseItem.link_type || 'ลิงก์' }}
                          </a>
                        </div>
                        <span v-else class="text-muted">-</span>
                      </td>
                      <td>
                        <small class="text-muted">
                          {{ formatDateTime(caseItem.created_at) }}
                        </small>
                      </td>
                      <td>
                        <div class="btn-group" role="group">
                          <router-link 
                            :to="`/admin/edit-case/${caseItem.id}`" 
                            class="btn btn-sm btn-outline-primary" 
                            title="แก้ไข"
                          >
                            <i class="fas fa-edit"></i>
                          </router-link>
                          <button 
                            type="button" 
                            class="btn btn-sm btn-outline-danger" 
                            @click="confirmDelete(caseItem.id, caseItem.hn)" 
                            title="ลบ"
                          >
                            <i class="fas fa-trash"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Pagination -->
              <nav v-if="pagination.totalPages > 1" aria-label="Page navigation" class="mt-4">
                <ul class="pagination justify-content-center">
                  <li class="page-item" :class="{ disabled: !pagination.hasPrev }">
                    <button 
                      class="page-link" 
                      @click="changePage(pagination.currentPage - 1)"
                      :disabled="!pagination.hasPrev"
                    >
                      <i class="fas fa-chevron-left"></i>
                    </button>
                  </li>
                  
                  <li 
                    v-for="page in getPageNumbers()" 
                    :key="page" 
                    class="page-item" 
                    :class="{ active: page === pagination.currentPage }"
                  >
                    <button 
                      v-if="page !== '...'" 
                      class="page-link" 
                      @click="changePage(page)"
                    >
                      {{ page }}
                    </button>
                    <span v-else class="page-link">...</span>
                  </li>
                  
                  <li class="page-item" :class="{ disabled: !pagination.hasNext }">
                    <button 
                      class="page-link" 
                      @click="changePage(pagination.currentPage + 1)"
                      :disabled="!pagination.hasNext"
                    >
                      <i class="fas fa-chevron-right"></i>
                    </button>
                  </li>
                </ul>
              </nav>
            </div>
            
            <div v-else class="text-center py-5">
              <i class="fas fa-users fa-3x text-muted mb-3"></i>
              <h5 class="text-muted">ไม่พบข้อมูลผู้ป่วย</h5>
              <p class="text-muted">
                <span v-if="isSearching">ลองปรับเงื่อนไขการค้นหาใหม่</span>
                <span v-else>เริ่มต้นเพิ่มผู้ป่วยใหม่ได้เลย</span>
              </p>
              <router-link v-if="!isSearching" to="/admin/add-case" class="btn btn-primary">
                <i class="fas fa-plus me-2"></i>เพิ่มผู้ป่วยใหม่
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Export Section -->
    <div class="row mt-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="fas fa-download me-2"></i>ส่งออกข้อมูล
            </h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="exportCases" class="row g-3">
              <div class="col-md-2">
                <label for="exportStartDate" class="form-label">วันที่เริ่มต้น</label>
                <input 
                  type="date" 
                  class="form-control" 
                  id="exportStartDate" 
                  v-model="exportForm.startDate"
                />
              </div>
              <div class="col-md-2">
                <label for="exportEndDate" class="form-label">วันที่สิ้นสุด</label>
                <input 
                  type="date" 
                  class="form-control" 
                  id="exportEndDate" 
                  v-model="exportForm.endDate"
                />
              </div>
              <div class="col-md-3">
                <label for="exportDepartment" class="form-label">หน่วยงาน</label>
                <select class="form-select" id="exportDepartment" v-model="exportForm.departmentId">
                  <option value="">ทั้งหมด</option>
                  <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                    {{ dept.name }}
                  </option>
                </select>
              </div>
              <div class="col-md-2">
                <label class="form-label">&nbsp;</label>
                <div>
                  <button 
                    type="button" 
                    class="btn btn-primary me-2" 
                    @click="previewExport"
                    :disabled="exportLoading"
                  >
                    <i class="fas fa-search me-1"></i>ค้นหา
                  </button>
                  <button 
                    type="submit" 
                    class="btn btn-success" 
                    :disabled="exportLoading"
                  >
                    <i class="fas fa-file-csv me-1"></i>Export CSV
                  </button>
                </div>
              </div>
            </form>
            
            <!-- Export Preview -->
            <div v-if="showExportPreview" class="mt-3">
              <hr>
              <h6 class="text-primary">
                <i class="fas fa-eye me-2"></i>ตัวอย่างข้อมูลที่จะ Export
              </h6>
              <div class="row">
                <div class="col-md-6">
                  <p><strong>ช่วงวันที่:</strong> {{ exportPreview.dateRange }}</p>
                  <p><strong>หน่วยงาน:</strong> {{ exportPreview.department }}</p>
                  <p><strong>จำนวนรายการ:</strong> 
                    <span class="badge bg-info">{{ exportPreview.count }}</span>
                  </p>
                </div>
                <div class="col-md-6">
                  <p><strong>คอลัมน์ที่จะ Export:</strong></p>
                  <ul class="small text-muted">
                    <li>HN, ชื่อ, นามสกุล</li>
                    <li>หน่วยงาน, วันที่วินิจฉัย, หมายเหตุ</li>
                    <li>เอกสาร</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Delete Confirmation Modal -->
  <div class="modal fade" id="deleteModal" tabindex="-1" ref="deleteModal">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-exclamation-triangle text-danger me-2"></i>ยืนยันการลบ
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <p>คุณต้องการลบข้อมูลผู้ป่วย <strong>{{ deleteTarget.hn }}</strong> ใช่หรือไม่?</p>
          <p class="text-muted small">การดำเนินการนี้ไม่สามารถยกเลิกได้</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            <i class="fas fa-times me-2"></i>ยกเลิก
          </button>
          <button type="button" class="btn btn-danger" @click="deleteCase" :disabled="deleteLoading">
            <i class="fas fa-trash me-2"></i>ลบ
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { Modal } from 'bootstrap'
import apiService from '../services/apiService'

export default {
  name: 'Cases',
  setup() {
    const loading = ref(false)
    const exportLoading = ref(false)
    const deleteLoading = ref(false)
    const cases = ref([])
    const departments = ref([])
    const totalCases = ref(0)
    const showExportPreview = ref(false)
    const deleteModal = ref(null)
    
    const searchForm = reactive({
      hn: '',
      firstName: '',
      lastName: '',
      departmentId: ''
    })
    
    const exportForm = reactive({
      startDate: '',
      endDate: '',
      departmentId: ''
    })
    
    const pagination = reactive({
      currentPage: 1,
      totalPages: 1,
      totalItems: 0,
      itemsPerPage: 20,
      hasPrev: false,
      hasNext: false
    })
    
    const deleteTarget = reactive({
      id: null,
      hn: ''
    })
    
    const exportPreview = reactive({
      dateRange: '',
      department: '',
      count: 0
    })
    
    const isSearching = computed(() => {
      return searchForm.hn || searchForm.firstName || searchForm.lastName || searchForm.departmentId
    })
    
    // Initialize export dates (last 30 days)
    const initializeExportDates = () => {
      const today = new Date()
      const thirtyDaysAgo = new Date(today.getTime() - (30 * 24 * 60 * 60 * 1000))
      
      exportForm.endDate = today.toISOString().split('T')[0]
      exportForm.startDate = thirtyDaysAgo.toISOString().split('T')[0]
    }
    
    const loadCases = async (page = 1) => {
      try {
        loading.value = true
        const params = {
          page,
          per_page: pagination.itemsPerPage,
          ...searchForm
        }
        
        const response = await apiService.getCases(params)
        cases.value = response.items || []
        totalCases.value = response.total || 0
        
        // Update pagination
        pagination.currentPage = response.page || 1
        pagination.totalPages = response.pages || 1
        pagination.totalItems = response.total || 0
        pagination.hasPrev = response.has_prev || false
        pagination.hasNext = response.has_next || false
        
      } catch (error) {
        console.error('Error loading cases:', error)
        showToast('เกิดข้อผิดพลาดในการโหลดข้อมูล', 'error')
      } finally {
        loading.value = false
      }
    }
    
    const loadDepartments = async () => {
      try {
        const response = await apiService.getDepartments()
        departments.value = response || []
      } catch (error) {
        console.error('Error loading departments:', error)
      }
    }
    
    const searchCases = () => {
      pagination.currentPage = 1
      loadCases(1)
    }
    
    const changePage = (page) => {
      if (page >= 1 && page <= pagination.totalPages) {
        loadCases(page)
      }
    }
    
    const getPageNumbers = () => {
      const pages = []
      const current = pagination.currentPage
      const total = pagination.totalPages
      
      if (total <= 7) {
        for (let i = 1; i <= total; i++) {
          pages.push(i)
        }
      } else {
        if (current <= 4) {
          for (let i = 1; i <= 5; i++) pages.push(i)
          pages.push('...')
          pages.push(total)
        } else if (current >= total - 3) {
          pages.push(1)
          pages.push('...')
          for (let i = total - 4; i <= total; i++) pages.push(i)
        } else {
          pages.push(1)
          pages.push('...')
          for (let i = current - 1; i <= current + 1; i++) pages.push(i)
          pages.push('...')
          pages.push(total)
        }
      }
      
      return pages
    }
    
    const confirmDelete = (id, hn) => {
      deleteTarget.id = id
      deleteTarget.hn = hn
      
      const modal = new Modal(deleteModal.value)
      modal.show()
    }
    
    const deleteCase = async () => {
      try {
        deleteLoading.value = true
        await apiService.deleteCase(deleteTarget.id)
        
        const modal = Modal.getInstance(deleteModal.value)
        modal.hide()
        
        showToast('ลบข้อมูลผู้ป่วยเรียบร้อยแล้ว', 'success')
        loadCases(pagination.currentPage)
        
      } catch (error) {
        console.error('Error deleting case:', error)
        showToast('เกิดข้อผิดพลาดในการลบข้อมูล', 'error')
      } finally {
        deleteLoading.value = false
      }
    }
    
    const previewExport = () => {
      // Update preview information
      if (exportForm.startDate && exportForm.endDate) {
        const start = new Date(exportForm.startDate).toLocaleDateString('th-TH')
        const end = new Date(exportForm.endDate).toLocaleDateString('th-TH')
        exportPreview.dateRange = `${start} - ${end}`
      } else {
        exportPreview.dateRange = 'ไม่ระบุ'
      }
      
      if (exportForm.departmentId) {
        const dept = departments.value.find(d => d.id == exportForm.departmentId)
        exportPreview.department = dept ? dept.name : 'ไม่ระบุ'
      } else {
        exportPreview.department = 'ทั้งหมด'
      }
      
      exportPreview.count = totalCases.value
      showExportPreview.value = true
    }
    
    const exportCases = async () => {
      try {
        // Validate dates
        if (exportForm.startDate && exportForm.endDate && exportForm.startDate > exportForm.endDate) {
          showToast('วันที่เริ่มต้นต้องไม่เกินวันที่สิ้นสุด', 'error')
          return
        }
        
        exportLoading.value = true
        const response = await apiService.exportCases(exportForm)
        
        // Create download link
        const url = window.URL.createObjectURL(new Blob([response]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `cases_export_${new Date().toISOString().split('T')[0]}.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
        showToast('ส่งออกข้อมูลเรียบร้อยแล้ว', 'success')
        
      } catch (error) {
        console.error('Error exporting cases:', error)
        showToast('เกิดข้อผิดพลาดในการส่งออกข้อมูล', 'error')
      } finally {
        exportLoading.value = false
      }
    }
    
    const downloadFile = async (caseId) => {
      try {
        const response = await apiService.downloadCaseFile(caseId)
        // Handle file download
        const url = window.URL.createObjectURL(new Blob([response]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `case_${caseId}_file`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
      } catch (error) {
        console.error('Error downloading file:', error)
        showToast('เกิดข้อผิดพลาดในการดาวน์โหลดไฟล์', 'error')
      }
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('th-TH')
    }
    
    const formatDateTime = (dateString) => {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleString('th-TH')
    }
    
    const getFileIcon = (filePath) => {
      if (!filePath) return 'fas fa-file text-primary'
      const extension = filePath.toLowerCase().split('.').pop()
      if (extension === 'pdf') return 'fas fa-file-pdf text-danger'
      return 'fas fa-file text-primary'
    }
    
    const getFileName = (filePath) => {
      if (!filePath) return ''
      const fileName = filePath.split('/').pop()
      return fileName.length > 20 ? fileName.substring(0, 20) + '...' : fileName
    }
    
    const showToast = (message, type = 'success') => {
      // Create toast notification
      const event = new CustomEvent('show-toast', {
        detail: { message, type }
      })
      window.dispatchEvent(event)
    }
    
    onMounted(() => {
      loadCases()
      loadDepartments()
      initializeExportDates()
      previewExport()
    })
    
    return {
      loading,
      exportLoading,
      deleteLoading,
      cases,
      departments,
      totalCases,
      searchForm,
      exportForm,
      pagination,
      deleteTarget,
      exportPreview,
      showExportPreview,
      isSearching,
      deleteModal,
      searchCases,
      changePage,
      getPageNumbers,
      confirmDelete,
      deleteCase,
      previewExport,
      exportCases,
      downloadFile,
      formatDate,
      formatDateTime,
      getFileIcon,
      getFileName
    }
  }
}
</script>

<style scoped>
.table th {
  border-top: none;
  font-weight: 600;
  color: #495057;
}

.badge {
  font-size: 0.75em;
}

.btn-group .btn {
  border-radius: 0.25rem;
}

.btn-group .btn:not(:last-child) {
  margin-right: 0.25rem;
}

.pagination .page-link {
  color: #0d6efd;
}

.pagination .page-item.active .page-link {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.display-6 {
  font-size: 2.5rem;
  font-weight: 600;
}
</style>