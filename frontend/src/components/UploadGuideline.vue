<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/admin/dashboard">แดชบอร์ด</router-link>
            </li>
            <li class="breadcrumb-item">
              <router-link to="/admin/guidelines">จัดการ Guidelines</router-link>
            </li>
            <li class="breadcrumb-item active">อัปโหลด Guidelines</li>
          </ol>
        </nav>
      </div>
    </div>

    <div class="row">
      <div class="col-12">
        <h1 class="mb-4">
          <i class="fas fa-upload me-2"></i>อัปโหลดไฟล์ Guidelines
        </h1>
      </div>
    </div>

    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card shadow">
          <div class="card-header bg-primary text-white">
            <h5 class="mb-0"><i class="fas fa-file-medical me-2"></i>ข้อมูลไฟล์</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="submitForm">
              <div class="mb-3">
                <label for="department_id" class="form-label">หน่วยงาน <span class="text-danger">*</span></label>
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
                    {{ dept.name }} ({{ dept.code }})
                  </option>
                </select>
              </div>
              
              <div class="mb-3">
                <label for="title" class="form-label">ชื่อไฟล์ <span class="text-danger">*</span></label>
                <input 
                  type="text" 
                  class="form-control" 
                  id="title" 
                  v-model="formData.title" 
                  required 
                  placeholder="เช่น: แนวทางการรักษาเบาหวาน 2024"
                >
              </div>
              
              <div class="mb-3">
                <label for="description" class="form-label">คำอธิบาย</label>
                <textarea 
                  class="form-control" 
                  id="description" 
                  v-model="formData.description" 
                  rows="3" 
                  placeholder="อธิบายเนื้อหาของไฟล์นี้"
                ></textarea>
              </div>
              
              <!-- ตัวเลือกประเภทการอัปโหลด -->
              <div class="mb-3">
                <label class="form-label">ประเภทการอัปโหลด <span class="text-danger">*</span></label>
                <div class="form-check">
                  <input 
                    class="form-check-input" 
                    type="radio" 
                    name="upload_type" 
                    id="upload_file" 
                    value="file" 
                    v-model="formData.upload_type"
                  >
                  <label class="form-check-label" for="upload_file">
                    <i class="fas fa-file-upload me-2"></i>อัปโหลดไฟล์
                  </label>
                </div>
                <div class="form-check">
                  <input 
                    class="form-check-input" 
                    type="radio" 
                    name="upload_type" 
                    id="upload_link" 
                    value="link" 
                    v-model="formData.upload_type"
                  >
                  <label class="form-check-label" for="upload_link">
                    <i class="fas fa-link me-2"></i>ลิงก์ภายนอก
                  </label>
                </div>
              </div>
              
              <!-- ส่วนอัปโหลดไฟล์ -->
              <div v-if="formData.upload_type === 'file'" class="mb-4">
                <label for="file" class="form-label">ไฟล์ <span class="text-danger">*</span></label>
                <input 
                  type="file" 
                  class="form-control" 
                  id="file" 
                  @change="handleFileUpload"
                  accept=".pdf,.doc,.docx,.ppt,.pptx"
                >
                <div class="form-text">
                  <i class="fas fa-info-circle me-1"></i>
                  รองรับไฟล์: PDF, DOC, DOCX, PPT, PPTX (ขนาดสูงสุด 50MB)
                </div>
                
                <!-- Custom filename input -->
                <div class="mt-3">
                  <label for="custom_filename" class="form-label">
                    <i class="fas fa-edit me-2"></i>ชื่อไฟล์ที่ต้องการ
                  </label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="custom_filename" 
                    v-model="formData.custom_filename" 
                    placeholder="ชื่อไฟล์ที่ต้องการ (ไม่ต้องใส่นามสกุลไฟล์)"
                  >
                  <div class="form-text">
                    ตั้งชื่อไฟล์เอง (ระบบจะเพิ่มนามสกุลไฟล์ให้อัตโนมัติ) หรือปล่อยว่างเพื่อใช้ชื่อไฟล์เดิม
                  </div>
                </div>
              </div>
              
              <!-- ส่วนลิงก์ภายนอก -->
              <div v-if="formData.upload_type === 'link'" class="mb-4">
                <div class="mb-3">
                  <label for="link_type" class="form-label">ประเภทลิงก์</label>
                  <select class="form-select" id="link_type" v-model="formData.link_type">
                    <option value="">เลือกประเภทลิงก์</option>
                    <option value="Google Drive">Google Drive</option>
                    <option value="OneDrive">OneDrive</option>
                    <option value="Dropbox">Dropbox</option>
                    <option value="Website">เว็บไซต์</option>
                    <option value="Other">อื่นๆ</option>
                  </select>
                </div>
                <div class="mb-3">
                  <label for="external_link" class="form-label">ลิงก์ <span class="text-danger">*</span></label>
                  <input 
                    type="url" 
                    class="form-control" 
                    id="external_link" 
                    v-model="formData.external_link" 
                    placeholder="https://drive.google.com/file/d/... หรือ https://example.com/..."
                  >
                  <div class="form-text">
                    <i class="fas fa-info-circle me-1"></i>
                    ใส่ลิงก์ที่สามารถเข้าถึงได้จากภายนอก
                  </div>
                </div>
              </div>
              
              <div class="d-grid gap-2">
                <button type="submit" class="btn btn-primary btn-lg" :disabled="isSubmitting">
                  <i class="fas fa-upload me-2"></i>
                  {{ isSubmitting ? 'กำลังอัปโหลด...' : 'อัปโหลดไฟล์' }}
                </button>
                <router-link to="/admin/guidelines" class="btn btn-outline-secondary">
                  <i class="fas fa-arrow-left me-2"></i>กลับไปหน้าจัดการ Guidelines
                </router-link>
              </div>
            </form>
          </div>
        </div>
        
        <!-- File Upload Guidelines -->
        <div class="card mt-4">
          <div class="card-header bg-info text-white">
            <h6 class="mb-0"><i class="fas fa-info-circle me-2"></i>คำแนะนำการอัปโหลด</h6>
          </div>
          <div class="card-body">
            <ul class="mb-0">
              <li>ไฟล์ต้องมีขนาดไม่เกิน 50MB</li>
              <li>รองรับเฉพาะไฟล์เอกสาร: PDF, DOC, DOCX, PPT, PPTX</li>
              <li>ชื่อไฟล์ควรสื่อความหมายและเข้าใจง่าย</li>
              <li>กรอกคำอธิบายเพื่อให้ผู้ใช้เข้าใจเนื้อหาได้ดีขึ้น</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Toast Notification -->
  <div 
    class="toast-container position-fixed bottom-0 end-0 p-3"
    style="z-index: 1050;"
  >
    <div 
      ref="toastElement"
      class="toast" 
      role="alert" 
      aria-live="assertive" 
      aria-atomic="true"
    >
      <div class="toast-header">
        <strong class="me-auto">{{ toastTitle }}</strong>
        <button 
          type="button" 
          class="btn-close" 
          @click="hideToast" 
          aria-label="Close"
        ></button>
      </div>
      <div class="toast-body">
        {{ toastMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../services/apiService'

export default {
  name: 'UploadGuideline',
  setup() {
    const router = useRouter()
    const departments = ref([])
    const isSubmitting = ref(false)
    const toastElement = ref(null)
    const toastTitle = ref('')
    const toastMessage = ref('')

    const formData = reactive({
      department_id: '',
      title: '',
      description: '',
      upload_type: 'file',
      file: null,
      custom_filename: '',
      link_type: '',
      external_link: ''
    })

    const fetchDepartments = async () => {
      try {
        const response = await apiService.get('/api/departments')
        departments.value = response.data
      } catch (error) {
        console.error('Error fetching departments:', error)
        showToast('ข้อผิดพลาด', 'ไม่สามารถโหลดข้อมูลหน่วยงานได้')
      }
    }

    const handleFileUpload = (event) => {
      const file = event.target.files[0]
      if (file) {
        if (file.size > 50 * 1024 * 1024) {
          showToast('ข้อผิดพลาด', 'ขนาดไฟล์ต้องไม่เกิน 50MB')
          event.target.value = ''
          return
        }
        
        const allowedTypes = ['.pdf', '.doc', '.docx', '.ppt', '.pptx']
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase()
        
        if (!allowedTypes.includes(fileExtension)) {
          showToast('ข้อผิดพลาด', 'รองรับเฉพาะไฟล์ PDF, DOC, DOCX, PPT, PPTX เท่านั้น')
          event.target.value = ''
          return
        }
        
        formData.file = file
      }
    }

    const submitForm = async () => {
      if (isSubmitting.value) return
      
      // Validation
      if (formData.upload_type === 'file' && !formData.file) {
        showToast('ข้อผิดพลาด', 'กรุณาเลือกไฟล์ที่ต้องการอัปโหลด')
        return
      }
      
      if (formData.upload_type === 'link' && !formData.external_link) {
        showToast('ข้อผิดพลาด', 'กรุณากรอกลิงก์ภายนอก')
        return
      }
      
      isSubmitting.value = true
      
      try {
        const submitData = new FormData()
        submitData.append('department_id', formData.department_id)
        submitData.append('title', formData.title)
        submitData.append('description', formData.description)
        submitData.append('upload_type', formData.upload_type)
        
        if (formData.upload_type === 'file') {
          submitData.append('file', formData.file)
          if (formData.custom_filename) {
            submitData.append('custom_filename', formData.custom_filename)
          }
        } else if (formData.upload_type === 'link') {
          submitData.append('external_link', formData.external_link)
          if (formData.link_type) {
            submitData.append('link_type', formData.link_type)
          }
        }
        
        await apiService.post('/api/admin/guidelines', submitData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        showToast('สำเร็จ', 'อัปโหลด Guidelines เรียบร้อยแล้ว')
        
        setTimeout(() => {
          router.push('/admin/guidelines')
        }, 1500)
        
      } catch (error) {
        console.error('Error uploading guideline:', error)
        const errorMessage = error.response?.data?.message || 'เกิดข้อผิดพลาดในการอัปโหลด Guidelines'
        showToast('ข้อผิดพลาด', errorMessage)
      } finally {
        isSubmitting.value = false
      }
    }

    const showToast = (title, message) => {
      toastTitle.value = title
      toastMessage.value = message
      
      if (toastElement.value) {
        const toast = new bootstrap.Toast(toastElement.value)
        toast.show()
      }
    }

    const hideToast = () => {
      if (toastElement.value) {
        const toast = bootstrap.Toast.getInstance(toastElement.value)
        if (toast) {
          toast.hide()
        }
      }
    }

    onMounted(() => {
      fetchDepartments()
    })

    return {
      formData,
      departments,
      isSubmitting,
      toastElement,
      toastTitle,
      toastMessage,
      handleFileUpload,
      submitForm,
      showToast,
      hideToast
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

.toast {
  min-width: 300px;
}

.btn-lg {
  padding: 0.75rem 1.5rem;
  font-size: 1.125rem;
}
</style>