<template>
  <div class="container mt-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2><i class="fas fa-database me-2"></i>สำรองข้อมูลความรู้</h2>
          <div>
            <button @click="exportData" class="btn btn-success me-2" :disabled="loading">
              <i class="fas fa-download me-2"></i>ส่งออกข้อมูล
            </button>
            <router-link to="/admin/knowledge" class="btn btn-secondary">
              <i class="fas fa-arrow-left me-2"></i>กลับไปหน้าบทความความรู้
            </router-link>
          </div>
        </div>

        <!-- สถิติ -->
        <div class="row mb-4">
          <div class="col-md-3">
            <div class="card bg-primary text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between">
                  <div>
                    <h4 class="mb-0">{{ totalKnowledge }}</h4>
                    <p class="mb-0">บทความความรู้ทั้งหมด</p>
                  </div>
                  <div class="align-self-center">
                    <i class="fas fa-book fa-2x"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-info text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between">
                  <div>
                    <h4 class="mb-0">{{ knowledgeWithImages }}</h4>
                    <p class="mb-0">บทความที่มีรูปภาพ</p>
                  </div>
                  <div class="align-self-center">
                    <i class="fas fa-image fa-2x"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-warning text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between">
                  <div>
                    <h4 class="mb-0">{{ knowledgeWithLinks }}</h4>
                    <p class="mb-0">บทความที่มีลิงก์</p>
                  </div>
                  <div class="align-self-center">
                    <i class="fas fa-link fa-2x"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="card bg-success text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between">
                  <div>
                    <h4 class="mb-0">{{ lastBackupDate }}</h4>
                    <p class="mb-0">สำรองข้อมูลล่าสุด</p>
                  </div>
                  <div class="align-self-center">
                    <i class="fas fa-calendar fa-2x"></i>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ตารางข้อมูล -->
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0"><i class="fas fa-list me-2"></i>รายการบทความความรู้ทั้งหมด</h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">กำลังโหลด...</span>
              </div>
            </div>
            
            <div v-else-if="knowledgeList.length === 0" class="text-center py-4">
              <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
              <p class="text-muted">ไม่มีข้อมูลบทความความรู้</p>
            </div>
            
            <div v-else class="table-responsive">
              <table class="table table-striped table-hover">
                <thead class="table-dark">
                  <tr>
                    <th scope="col">#</th>
                    <th scope="col">หัวข้อ</th>
                    <th scope="col">รูปภาพ/ลิงก์</th>
                    <th scope="col">หน่วยงาน</th>
                    <th scope="col">วันที่สร้าง</th>
                    <th scope="col">วันที่อัปเดต</th>
                    <th scope="col">การจัดการ</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in knowledgeList" :key="item.id">
                    <th scope="row">{{ index + 1 }}</th>
                    <td>
                      <strong>{{ item.title }}</strong>
                      <br>
                      <small class="text-muted">{{ truncateText(item.content, 50) }}</small>
                    </td>
                    <td>
                      <div v-if="item.image_path">
                        <img 
                          :src="getImageUrl(item.image_path)" 
                          alt="Knowledge Image" 
                          class="img-thumbnail cursor-pointer" 
                          style="width: 60px; height: 60px; object-fit: cover;"
                          @click="showImageModal(getImageUrl(item.image_path))"
                        >
                      </div>
                      <div v-else-if="item.external_link">
                        <a :href="item.external_link" target="_blank" class="btn btn-sm btn-outline-primary">
                          <i :class="getLinkIcon(item.link_type)" class="me-1"></i>
                          {{ getLinkTypeText(item.link_type) }}
                        </a>
                      </div>
                      <div v-else>
                        <span class="text-muted">-</span>
                      </div>
                    </td>
                    <td>
                      <span class="badge bg-secondary">{{ item.department_name }}</span>
                    </td>
                    <td>{{ formatDate(item.created_at) }}</td>
                    <td>{{ formatDate(item.updated_at) }}</td>
                    <td>
                      <div class="btn-group" role="group">
                        <router-link 
                          :to="`/admin/knowledge/edit/${item.id}`" 
                          class="btn btn-sm btn-outline-warning"
                          title="แก้ไข"
                        >
                          <i class="fas fa-edit"></i>
                        </router-link>
                        <button 
                          @click="confirmDelete(item)" 
                          class="btn btn-sm btn-outline-danger"
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
          </div>
        </div>
      </div>
    </div>

    <!-- Modal แสดงรูปภาพ -->
    <div class="modal fade" id="imageModal" tabindex="-1" aria-labelledby="imageModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="imageModalLabel">รูปภาพ</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body text-center">
            <img :src="selectedImage" alt="Knowledge Image" class="img-fluid">
          </div>
        </div>
      </div>
    </div>

    <!-- Modal ยืนยันการลบ -->
    <div class="modal fade" id="deleteModal" tabindex="-1" aria-labelledby="deleteModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="deleteModalLabel">ยืนยันการลบ</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>คุณต้องการลบบทความความรู้ "<strong>{{ itemToDelete?.title }}</strong>" หรือไม่?</p>
            <p class="text-danger"><i class="fas fa-exclamation-triangle me-2"></i>การดำเนินการนี้ไม่สามารถยกเลิกได้</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ยกเลิก</button>
            <button type="button" class="btn btn-danger" @click="deleteKnowledge" :disabled="deleting">
              <span v-if="deleting">กำลังลบ...</span>
              <span v-else><i class="fas fa-trash me-2"></i>ลบ</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import apiService from '../services/apiService'

export default {
  name: 'KnowledgeBackup',
  setup() {
    const loading = ref(true)
    const deleting = ref(false)
    const knowledgeList = ref([])
    const selectedImage = ref('')
    const itemToDelete = ref(null)

    // คำนวณสถิติ
    const totalKnowledge = computed(() => knowledgeList.value.length)
    const knowledgeWithImages = computed(() => 
      knowledgeList.value.filter(item => item.image_path).length
    )
    const knowledgeWithLinks = computed(() => 
      knowledgeList.value.filter(item => item.external_link).length
    )
    const lastBackupDate = computed(() => {
      const today = new Date()
      return today.toLocaleDateString('th-TH', {
        day: 'numeric',
        month: 'short'
      })
    })

    // ดึงข้อมูลความรู้
    const fetchKnowledge = async () => {
      try {
        loading.value = true
        const response = await apiService.get('/admin/knowledge')
        knowledgeList.value = response.data
      } catch (error) {
        console.error('Error fetching knowledge:', error)
        showToast('เกิดข้อผิดพลาดในการดึงข้อมูลความรู้', 'error')
      } finally {
        loading.value = false
      }
    }

    // ส่งออกข้อมูล
    const exportData = async () => {
      try {
        loading.value = true
        const response = await apiService.get('/admin/knowledge/export', {
          responseType: 'blob'
        })
        
        // สร้างลิงก์ดาวน์โหลด
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `knowledge_backup_${new Date().toISOString().split('T')[0]}.xlsx`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        window.URL.revokeObjectURL(url)
        
        showToast('ส่งออกข้อมูลเรียบร้อยแล้ว', 'success')
      } catch (error) {
        console.error('Error exporting data:', error)
        showToast('เกิดข้อผิดพลาดในการส่งออกข้อมูล', 'error')
      } finally {
        loading.value = false
      }
    }

    // แสดง Modal รูปภาพ
    const showImageModal = (imageUrl) => {
      selectedImage.value = imageUrl
      const modal = new bootstrap.Modal(document.getElementById('imageModal'))
      modal.show()
    }

    // ยืนยันการลบ
    const confirmDelete = (item) => {
      itemToDelete.value = item
      const modal = new bootstrap.Modal(document.getElementById('deleteModal'))
      modal.show()
    }

    // ลบความรู้
    const deleteKnowledge = async () => {
      if (!itemToDelete.value) return
      
      try {
        deleting.value = true
        await apiService.delete(`/admin/knowledge/${itemToDelete.value.id}`)
        
        // ลบออกจากรายการ
        knowledgeList.value = knowledgeList.value.filter(
          item => item.id !== itemToDelete.value.id
        )
        
        showToast('ลบบทความความรู้เรียบร้อยแล้ว', 'success')
        
        // ปิด Modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'))
        modal.hide()
        itemToDelete.value = null
      } catch (error) {
        console.error('Error deleting knowledge:', error)
        showToast('เกิดข้อผิดพลาดในการลบบทความความรู้', 'error')
      } finally {
        deleting.value = false
      }
    }

    // สร้าง URL รูปภาพ
    const getImageUrl = (imagePath) => {
      if (!imagePath) return ''
      return `http://localhost:5000/uploads/${imagePath}`
    }

    // ตัดข้อความ
    const truncateText = (text, maxLength) => {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }

    // จัดรูปแบบวันที่
    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleDateString('th-TH', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    // ไอคอนลิงก์
    const getLinkIcon = (linkType) => {
      const icons = {
        youtube: 'fab fa-youtube',
        facebook: 'fab fa-facebook',
        line: 'fab fa-line',
        website: 'fas fa-globe',
        other: 'fas fa-link'
      }
      return icons[linkType] || icons.other
    }

    // ข้อความประเภทลิงก์
    const getLinkTypeText = (linkType) => {
      const types = {
        youtube: 'YouTube',
        facebook: 'Facebook',
        line: 'Line',
        website: 'เว็บไซต์',
        other: 'อื่นๆ'
      }
      return types[linkType] || types.other
    }

    // แสดงข้อความแจ้งเตือน
    const showToast = (message, type = 'info') => {
      const toastContainer = document.querySelector('.toast-container') || createToastContainer()
      const toastId = 'toast-' + Date.now()
      
      const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'} border-0" role="alert" aria-live="assertive" aria-atomic="true">
          <div class="d-flex">
            <div class="toast-body">
              ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
          </div>
        </div>
      `
      
      toastContainer.insertAdjacentHTML('beforeend', toastHtml)
      const toastElement = document.getElementById(toastId)
      const toast = new bootstrap.Toast(toastElement)
      toast.show()
      
      toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove()
      })
    }

    // สร้าง toast container
    const createToastContainer = () => {
      const container = document.createElement('div')
      container.className = 'toast-container position-fixed top-0 end-0 p-3'
      container.style.zIndex = '1055'
      document.body.appendChild(container)
      return container
    }

    onMounted(() => {
      fetchKnowledge()
    })

    return {
      loading,
      deleting,
      knowledgeList,
      selectedImage,
      itemToDelete,
      totalKnowledge,
      knowledgeWithImages,
      knowledgeWithLinks,
      lastBackupDate,
      exportData,
      showImageModal,
      confirmDelete,
      deleteKnowledge,
      getImageUrl,
      truncateText,
      formatDate,
      getLinkIcon,
      getLinkTypeText
    }
  }
}
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.cursor-pointer {
  cursor: pointer;
}

.img-thumbnail {
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  padding: 0.25rem;
  transition: transform 0.2s;
}

.img-thumbnail:hover {
  transform: scale(1.1);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}

.table th {
  border-top: none;
}

.badge {
  font-size: 0.75rem;
}
</style>