<template>
  <div class="container mt-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2><i class="fas fa-book me-2"></i>จัดการความรู้</h2>
          <router-link to="/admin/dashboard" class="btn btn-secondary">
            <i class="fas fa-arrow-left me-2"></i>กลับไปหน้าแดชบอร์ด
          </router-link>
        </div>

        <!-- สถิติ -->
        <div class="row mb-4">
          <div class="col-md-3">
            <div class="card bg-primary text-white">
              <div class="card-body">
                <h5 class="card-title">จำนวนความรู้ทั้งหมด</h5>
                <h2>{{ knowledgeList.length }}</h2>
              </div>
            </div>
          </div>
        </div>

        <!-- ตารางความรู้ -->
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0"><i class="fas fa-list me-2"></i>รายการความรู้</h5>
          </div>
          <div class="card-body">
            <div v-if="knowledgeList.length > 0">
              <div class="table-responsive">
                <table class="table table-striped table-hover">
                  <thead class="table-dark">
                    <tr>
                      <th>ลำดับ</th>
                      <th>หัวข้อ</th>
                      <th>รูปภาพ/ลิงก์</th>
                      <th>หน่วยงาน</th>
                      <th>วันที่สร้าง</th>
                      <th>วันที่อัปเดต</th>
                      <th>การจัดการ</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, index) in knowledgeList" :key="item.id">
                      <td>{{ index + 1 }}</td>
                      <td>
                        <strong>{{ item.title }}</strong>
                        <br v-if="item.content">
                        <small v-if="item.content" class="text-muted">
                          {{ truncateText(item.content, 100) }}
                        </small>
                      </td>
                      <td>
                        <div v-if="item.image_path" class="text-center">
                          <img 
                            :src="getImageUrl(item.image_path)" 
                            alt="รูปภาพ" 
                            class="img-thumbnail" 
                            style="max-width: 80px; cursor: pointer;"
                            @click="showImageModal(getImageUrl(item.image_path), item.title)"
                          >
                          <br><small class="text-muted">คลิกเพื่อดูใหญ่</small>
                        </div>
                        <div v-else-if="item.external_link" class="text-center">
                          <a :href="item.external_link" target="_blank" class="btn btn-sm btn-outline-primary">
                            <i class="fas fa-external-link-alt"></i>
                            {{ getLinkTypeLabel(item.link_type) }}
                          </a>
                        </div>
                        <span v-else class="text-muted">ไม่มี</span>
                      </td>
                      <td>
                        <span class="badge bg-info">{{ item.department?.name || 'ไม่ระบุ' }}</span>
                      </td>
                      <td>{{ formatDate(item.created_at) }}</td>
                      <td>{{ formatDate(item.updated_at) }}</td>
                      <td>
                        <div class="btn-group" role="group">
                          <router-link 
                            :to="`/admin/knowledge/edit/${item.id}`" 
                            class="btn btn-sm btn-outline-primary"
                          >
                            <i class="fas fa-edit"></i>
                          </router-link>
                          <button 
                            type="button" 
                            class="btn btn-sm btn-outline-danger" 
                            @click="confirmDelete(item.id)"
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
            <div v-else class="text-center py-5">
              <i class="fas fa-book fa-3x text-muted mb-3"></i>
              <h5 class="text-muted">ยังไม่มีข้อมูลความรู้</h5>
              <p class="text-muted">คลิกปุ่มด้านล่างเพื่อเพิ่มความรู้ใหม่</p>
            </div>
          </div>
        </div>

        <!-- ปุ่มเพิ่มความรู้ใหม่ -->
        <div class="text-center mt-4">
          <router-link to="/admin/knowledge/add" class="btn btn-success btn-lg">
            <i class="fas fa-plus me-2"></i>เพิ่มความรู้ใหม่
          </router-link>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal สำหรับแสดงรูปภาพใหญ่ -->
  <div class="modal fade" id="imageModal" tabindex="-1" aria-labelledby="imageModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="imageModalLabel">{{ modalImageTitle }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body text-center">
          <img :src="modalImageSrc" alt="รูปภาพ" class="img-fluid">
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ปิด</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal ยืนยันการลบ -->
  <div class="modal fade" id="deleteModal" tabindex="-1" aria-labelledby="deleteModalLabel" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="deleteModalLabel">ยืนยันการลบ</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          คุณแน่ใจหรือไม่ที่จะลบความรู้นี้?
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">ยกเลิก</button>
          <button type="button" class="btn btn-danger" @click="deleteKnowledge">ลบ</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { Modal } from 'bootstrap'
import apiService from '../services/apiService'

export default {
  name: 'Knowledge',
  setup() {
    const knowledgeList = ref([])
    const loading = ref(false)
    const modalImageSrc = ref('')
    const modalImageTitle = ref('')
    const deleteId = ref(null)

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

    // ลบความรู้
    const deleteKnowledge = async () => {
      try {
        await apiService.delete(`/admin/knowledge/${deleteId.value}`)
        knowledgeList.value = knowledgeList.value.filter(item => item.id !== deleteId.value)
        showToast('ลบความรู้เรียบร้อยแล้ว', 'success')
        
        // ปิด modal
        const modal = Modal.getInstance(document.getElementById('deleteModal'))
        modal.hide()
      } catch (error) {
        console.error('Error deleting knowledge:', error)
        showToast('เกิดข้อผิดพลาดในการลบความรู้', 'error')
      }
    }

    // ยืนยันการลบ
    const confirmDelete = (id) => {
      deleteId.value = id
      const modal = new Modal(document.getElementById('deleteModal'))
      modal.show()
    }

    // แสดง modal รูปภาพ
    const showImageModal = (imageSrc, title) => {
      modalImageSrc.value = imageSrc
      modalImageTitle.value = title
      const modal = new Modal(document.getElementById('imageModal'))
      modal.show()
    }

    // ตัดข้อความ
    const truncateText = (text, maxLength) => {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    }

    // จัดรูปแบบวันที่
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

    // สร้าง URL รูปภาพ
    const getImageUrl = (imagePath) => {
      if (!imagePath) return ''
      return `${import.meta.env.VITE_API_BASE_URL}/storage/${imagePath.replace('storage/', '')}`
    }

    // ป้ายกำกับประเภทลิงก์
    const getLinkTypeLabel = (linkType) => {
      const labels = {
        youtube: 'YouTube',
        facebook: 'Facebook',
        line: 'Line',
        website: 'เว็บไซต์',
        other: 'ลิงก์'
      }
      return labels[linkType] || 'ลิงก์'
    }

    // แสดงข้อความแจ้งเตือน
    const showToast = (message, type = 'info') => {
      // สร้าง toast element
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
      
      // ลบ toast หลังจากซ่อน
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
      knowledgeList,
      loading,
      modalImageSrc,
      modalImageTitle,
      fetchKnowledge,
      deleteKnowledge,
      confirmDelete,
      showImageModal,
      truncateText,
      formatDate,
      getImageUrl,
      getLinkTypeLabel
    }
  }
}
</script>

<style scoped>
.img-thumbnail {
  transition: transform 0.2s;
}

.img-thumbnail:hover {
  transform: scale(1.1);
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.table th {
  border-top: none;
}

.btn-group .btn {
  margin-right: 0.25rem;
}

.btn-group .btn:last-child {
  margin-right: 0;
}
</style>