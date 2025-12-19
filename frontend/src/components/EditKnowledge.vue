<template>
  <div class="container mt-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2><i class="fas fa-edit me-2"></i>แก้ไขบทความความรู้</h2>
          <router-link to="/admin/knowledge" class="btn btn-secondary">
            <i class="fas fa-arrow-left me-2"></i>กลับไปหน้าบทความความรู้
          </router-link>
        </div>

        <div v-if="loading" class="text-center">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">กำลังโหลด...</span>
          </div>
        </div>

        <div v-else-if="knowledge" class="card">
          <div class="card-header">
            <h5 class="mb-0"><i class="fas fa-edit me-2"></i>แก้ไขข้อมูลบทความความรู้</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="submitForm">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="department_id" class="form-label">หน่วยงาน *</label>
                    <select 
                      class="form-select" 
                      id="department_id" 
                      v-model="formData.department_id" 
                      required
                    >
                      <option value="">เลือกหน่วยงาน</option>
                      <option 
                        v-for="dept in departments" 
                        :key="dept.id" 
                        :value="dept.id"
                      >
                        {{ dept.name }}
                      </option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="title" class="form-label">หัวข้อ *</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="title" 
                      v-model="formData.title" 
                      required
                    >
                  </div>
                </div>
              </div>
              
              <div class="mb-3">
                <label for="content" class="form-label">เนื้อหา *</label>
                <textarea 
                  class="form-control" 
                  id="content" 
                  v-model="formData.content" 
                  rows="4" 
                  maxlength="500" 
                  required 
                  placeholder="เนื้อหาบทความความรู้ (สูงสุด 500 ตัวอักษร)"
                  @input="updateCharCount"
                ></textarea>
                <div class="form-text">
                  <span :style="{ color: getCharCountColor() }">{{ charCount }}</span>/500 ตัวอักษร
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">ประเภทการอัปโหลด</label>
                <div class="form-check">
                  <input 
                    class="form-check-input" 
                    type="radio" 
                    id="content_only" 
                    value="content" 
                    v-model="uploadType"
                  >
                  <label class="form-check-label" for="content_only">
                    เฉพาะเนื้อหา
                  </label>
                </div>
                <div class="form-check">
                  <input 
                    class="form-check-input" 
                    type="radio" 
                    id="image_upload" 
                    value="image" 
                    v-model="uploadType"
                  >
                  <label class="form-check-label" for="image_upload">
                    อัปโหลดรูปภาพ
                  </label>
                </div>
                <div class="form-check">
                  <input 
                    class="form-check-input" 
                    type="radio" 
                    id="external_link" 
                    value="link" 
                    v-model="uploadType"
                  >
                  <label class="form-check-label" for="external_link">
                    ลิงก์ภายนอก
                  </label>
                </div>
              </div>

              <!-- ส่วนรูปภาพ -->
              <div v-if="uploadType === 'image'" class="mb-3">
                <label for="image" class="form-label">รูปภาพ</label>
                
                <!-- แสดงรูปภาพปัจจุบัน -->
                <div v-if="knowledge.image_path" class="mb-2">
                  <p class="text-muted mb-1">รูปภาพปัจจุบัน:</p>
                  <img 
                    :src="getImageUrl(knowledge.image_path)" 
                    alt="Current image" 
                    class="img-thumbnail" 
                    style="max-width: 200px; max-height: 200px;"
                  >
                </div>
                
                <input 
                  type="file" 
                  class="form-control" 
                  id="image" 
                  @change="handleFileChange" 
                  accept="image/*"
                >
                <div class="form-text">รองรับไฟล์รูปภาพ: JPG, PNG, GIF (สูงสุด 5MB) - เลือกไฟล์ใหม่เพื่อเปลี่ยนรูปภาพ</div>
              </div>

              <!-- ส่วนลิงก์ภายนอก -->
              <div v-if="uploadType === 'link'" class="mb-3">
                <div class="row">
                  <div class="col-md-6">
                    <label for="external_link" class="form-label">ลิงก์ภายนอก</label>
                    <input 
                      type="url" 
                      class="form-control" 
                      id="external_link" 
                      v-model="formData.external_link" 
                      placeholder="https://example.com"
                    >
                  </div>
                  <div class="col-md-6">
                    <label for="link_type" class="form-label">ประเภทลิงก์</label>
                    <select class="form-select" id="link_type" v-model="formData.link_type">
                      <option value="website">เว็บไซต์</option>
                      <option value="youtube">YouTube</option>
                      <option value="facebook">Facebook</option>
                      <option value="line">Line</option>
                      <option value="other">อื่นๆ</option>
                    </select>
                  </div>
                </div>
              </div>

              <!-- ข้อมูลวันที่ -->
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">วันที่สร้าง</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    :value="formatDate(knowledge.created_at)" 
                    readonly
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label">วันที่อัปเดตล่าสุด</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    :value="formatDate(knowledge.updated_at)" 
                    readonly
                  >
                </div>
              </div>

              <div class="d-flex justify-content-between">
                <router-link to="/admin/knowledge" class="btn btn-secondary">
                  <i class="fas fa-times me-2"></i>ยกเลิก
                </router-link>
                <button type="submit" class="btn btn-primary" :disabled="saving">
                  <i class="fas fa-save me-2"></i>
                  <span v-if="saving">กำลังบันทึก...</span>
                  <span v-else>บันทึกการเปลี่ยนแปลง</span>
                </button>
              </div>
            </form>
          </div>
        </div>

        <div v-else class="alert alert-danger">
          <i class="fas fa-exclamation-triangle me-2"></i>
          ไม่พบข้อมูลบทความความรู้ที่ต้องการแก้ไข
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import apiService from '../services/apiService'

export default {
  name: 'EditKnowledge',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const loading = ref(true)
    const saving = ref(false)
    const knowledge = ref(null)
    const departments = ref([])
    const uploadType = ref('content')
    const selectedFile = ref(null)
    
    const formData = ref({
      department_id: '',
      title: '',
      content: '',
      external_link: '',
      link_type: 'website'
    })

    // คำนวณจำนวนตัวอักษร
    const charCount = computed(() => {
      return formData.value.content.length
    })

    // อัปเดตจำนวนตัวอักษร
    const updateCharCount = () => {
      // ฟังก์ชันนี้จะถูกเรียกโดยอัตโนมัติเมื่อ content เปลี่ยน
    }

    // สีของตัวนับตัวอักษร
    const getCharCountColor = () => {
      const remaining = 500 - charCount.value
      if (remaining < 50) return 'red'
      if (remaining < 100) return 'orange'
      return 'inherit'
    }

    // จัดการการเปลี่ยนไฟล์
    const handleFileChange = (event) => {
      const file = event.target.files[0]
      if (file) {
        // ตรวจสอบขนาดไฟล์ (5MB)
        if (file.size > 5 * 1024 * 1024) {
          showToast('ขนาดไฟล์ต้องไม่เกิน 5MB', 'error')
          event.target.value = ''
          return
        }
        selectedFile.value = file
      }
    }

    // สร้าง URL รูปภาพ
    const getImageUrl = (imagePath) => {
      if (!imagePath) return ''
      return `http://localhost:5000/uploads/${imagePath}`
    }

    // จัดรูปแบบวันที่
    const formatDate = (dateString) => {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleDateString('th-TH', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // ดึงข้อมูลหน่วยงาน
    const fetchDepartments = async () => {
      try {
        const response = await apiService.get('/admin/departments')
        departments.value = response.data
      } catch (error) {
        console.error('Error fetching departments:', error)
        showToast('เกิดข้อผิดพลาดในการดึงข้อมูลหน่วยงาน', 'error')
      }
    }

    // ดึงข้อมูลความรู้
    const fetchKnowledge = async () => {
      try {
        const knowledgeId = route.params.id
        const response = await apiService.get(`/admin/knowledge/${knowledgeId}`)
        knowledge.value = response.data
        
        // ตั้งค่าข้อมูลในฟอร์ม
        formData.value = {
          department_id: knowledge.value.department_id,
          title: knowledge.value.title,
          content: knowledge.value.content,
          external_link: knowledge.value.external_link || '',
          link_type: knowledge.value.link_type || 'website'
        }
        
        // กำหนดประเภทการอัปโหลด
        if (knowledge.value.image_path) {
          uploadType.value = 'image'
        } else if (knowledge.value.external_link) {
          uploadType.value = 'link'
        } else {
          uploadType.value = 'content'
        }
        
      } catch (error) {
        console.error('Error fetching knowledge:', error)
        showToast('เกิดข้อผิดพลาดในการดึงข้อมูลบทความความรู้', 'error')
      } finally {
        loading.value = false
      }
    }

    // ส่งฟอร์ม
    const submitForm = async () => {
      try {
        saving.value = true
        
        const formDataToSend = new FormData()
        formDataToSend.append('department_id', formData.value.department_id)
        formDataToSend.append('title', formData.value.title)
        formDataToSend.append('content', formData.value.content)
        formDataToSend.append('upload_type', uploadType.value)
        
        if (uploadType.value === 'image' && selectedFile.value) {
          formDataToSend.append('image', selectedFile.value)
        } else if (uploadType.value === 'link') {
          formDataToSend.append('external_link', formData.value.external_link)
          formDataToSend.append('link_type', formData.value.link_type)
        }

        const knowledgeId = route.params.id
        await apiService.put(`/admin/knowledge/${knowledgeId}`, formDataToSend, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        showToast('แก้ไขบทความความรู้เรียบร้อยแล้ว', 'success')
        router.push('/admin/knowledge')
      } catch (error) {
        console.error('Error updating knowledge:', error)
        showToast('เกิดข้อผิดพลาดในการแก้ไขบทความความรู้', 'error')
      } finally {
        saving.value = false
      }
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

    onMounted(async () => {
      await Promise.all([fetchDepartments(), fetchKnowledge()])
    })

    return {
      knowledge,
      formData,
      departments,
      uploadType,
      loading,
      saving,
      charCount,
      updateCharCount,
      getCharCountColor,
      handleFileChange,
      getImageUrl,
      formatDate,
      submitForm
    }
  }
}
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.form-check {
  margin-bottom: 0.5rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

textarea {
  resize: vertical;
}

.form-text {
  font-size: 0.875rem;
}

.img-thumbnail {
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  padding: 0.25rem;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
}
</style>