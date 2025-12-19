<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="card-title mb-0">
              <i class="fas fa-plus me-2"></i>เพิ่มกิจกรรมใหม่
            </h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="submitForm">
              <div class="row">
                <div class="col-md-6">
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
                        {{ dept.name }}
                      </option>
                    </select>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="title" class="form-label">หัวข้อกิจกรรม <span class="text-danger">*</span></label>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="title" 
                      v-model="formData.title" 
                      required 
                      maxlength="200"
                    >
                  </div>
                </div>
              </div>

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="activity_date" class="form-label">วันที่กิจกรรม <span class="text-danger">*</span></label>
                    <input 
                      type="date" 
                      class="form-control" 
                      id="activity_date" 
                      v-model="formData.activity_date" 
                      required
                    >
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">ประเภทการอัปโหลด <span class="text-danger">*</span></label>
                    <div class="d-flex gap-3">
                      <div class="form-check">
                        <input 
                          class="form-check-input" 
                          type="radio" 
                          name="upload_type" 
                          id="data_only" 
                          value="data" 
                          v-model="formData.upload_type"
                        >
                        <label class="form-check-label" for="data_only">
                          เฉพาะข้อมูล
                        </label>
                      </div>
                      <div class="form-check">
                        <input 
                          class="form-check-input" 
                          type="radio" 
                          name="upload_type" 
                          id="with_image" 
                          value="image" 
                          v-model="formData.upload_type"
                        >
                        <label class="form-check-label" for="with_image">
                          รูปภาพ
                        </label>
                      </div>
                      <div class="form-check">
                        <input 
                          class="form-check-input" 
                          type="radio" 
                          name="upload_type" 
                          id="with_link" 
                          value="link" 
                          v-model="formData.upload_type"
                        >
                        <label class="form-check-label" for="with_link">
                          ลิงก์ภายนอก
                        </label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label for="description" class="form-label">คำอธิบาย</label>
                <textarea 
                  class="form-control" 
                  id="description" 
                  v-model="formData.description" 
                  rows="4" 
                  maxlength="300" 
                  @input="updateCharCount"
                ></textarea>
                <div class="form-text">
                  จำนวนตัวอักษร: <span :style="{ color: charCountColor }">{{ charCount }}</span>/300
                </div>
              </div>

              <!-- Image Upload Section -->
              <div v-if="formData.upload_type === 'image'" class="mb-3">
                <label for="image" class="form-label">อัปโหลดรูปภาพ</label>
                <input 
                  type="file" 
                  class="form-control" 
                  id="image" 
                  @change="handleImageUpload" 
                  accept="image/*"
                >
                <div class="form-text">รองรับไฟล์: JPG, PNG, GIF (ขนาดไม่เกิน 5MB)</div>
                <div v-if="imagePreview" class="mt-2">
                  <img :src="imagePreview" alt="Preview" class="img-thumbnail" style="max-width: 200px;">
                </div>
              </div>

              <!-- External Link Section -->
              <div v-if="formData.upload_type === 'link'" class="mb-3">
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
                      <option value="registration">ลงทะเบียน</option>
                      <option value="other">อื่นๆ</option>
                    </select>
                  </div>
                </div>
              </div>

              <div class="d-flex justify-content-between">
                <router-link to="/admin/activities" class="btn btn-secondary">
                  <i class="fas fa-times me-2"></i>ยกเลิก
                </router-link>
                <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
                  <i class="fas fa-save me-2"></i>
                  {{ isSubmitting ? 'กำลังบันทึก...' : 'บันทึก' }}
                </button>
              </div>
            </form>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../services/apiService'

export default {
  name: 'AddActivity',
  setup() {
    const router = useRouter()
    const departments = ref([])
    const isSubmitting = ref(false)
    const imagePreview = ref(null)
    const toastElement = ref(null)
    const toastTitle = ref('')
    const toastMessage = ref('')

    const formData = reactive({
      department_id: '',
      title: '',
      activity_date: new Date().toISOString().split('T')[0],
      upload_type: 'data',
      description: '',
      image: null,
      external_link: '',
      link_type: 'website'
    })

    const charCount = computed(() => formData.description.length)
    const charCountColor = computed(() => {
      const remaining = 300 - charCount.value
      if (remaining < 30) return 'red'
      if (remaining < 60) return 'orange'
      return 'inherit'
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

    const handleImageUpload = (event) => {
      const file = event.target.files[0]
      if (file) {
        if (file.size > 5 * 1024 * 1024) {
          showToast('ข้อผิดพลาด', 'ขนาดไฟล์ต้องไม่เกิน 5MB')
          event.target.value = ''
          return
        }
        
        formData.image = file
        
        const reader = new FileReader()
        reader.onload = (e) => {
          imagePreview.value = e.target.result
        }
        reader.readAsDataURL(file)
      }
    }

    const updateCharCount = () => {
      // This is handled by the computed property
    }

    const submitForm = async () => {
      if (isSubmitting.value) return
      
      isSubmitting.value = true
      
      try {
        const submitData = new FormData()
        submitData.append('department_id', formData.department_id)
        submitData.append('title', formData.title)
        submitData.append('activity_date', formData.activity_date)
        submitData.append('upload_type', formData.upload_type)
        submitData.append('description', formData.description)
        
        if (formData.upload_type === 'image' && formData.image) {
          submitData.append('image', formData.image)
        } else if (formData.upload_type === 'link') {
          submitData.append('external_link', formData.external_link)
          submitData.append('link_type', formData.link_type)
        }
        
        await apiService.post('/api/admin/activities', submitData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        showToast('สำเร็จ', 'เพิ่มกิจกรรมเรียบร้อยแล้ว')
        
        setTimeout(() => {
          router.push('/admin/activities')
        }, 1500)
        
      } catch (error) {
        console.error('Error creating activity:', error)
        const errorMessage = error.response?.data?.message || 'เกิดข้อผิดพลาดในการเพิ่มกิจกรรม'
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
      imagePreview,
      charCount,
      charCountColor,
      toastElement,
      toastTitle,
      toastMessage,
      handleImageUpload,
      updateCharCount,
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

.img-thumbnail {
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  padding: 0.25rem;
}

.toast {
  min-width: 300px;
}
</style>