<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="card-title mb-0">
              <i class="fas fa-edit me-2"></i>แก้ไขกิจกรรม
            </h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">กำลังโหลด...</span>
              </div>
            </div>
            
            <form v-else @submit.prevent="submitForm">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="department_name" class="form-label">หน่วยงาน</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="department_name" 
                      :value="activity.department_name" 
                      readonly
                    >
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
                
                <!-- Current Image -->
                <div v-if="activity.image_filename && !newImagePreview" class="mb-2">
                  <p class="form-text">รูปภาพปัจจุบัน:</p>
                  <img 
                    :src="getImageUrl(activity.image_filename)" 
                    alt="Current image" 
                    class="img-thumbnail" 
                    style="max-width: 200px;"
                  >
                </div>
                
                <input 
                  type="file" 
                  class="form-control" 
                  id="image" 
                  @change="handleImageUpload" 
                  accept="image/*"
                >
                <div class="form-text">รองรับไฟล์: JPG, PNG, GIF (ขนาดไม่เกิน 5MB)</div>
                
                <!-- New Image Preview -->
                <div v-if="newImagePreview" class="mt-2">
                  <p class="form-text">รูปภาพใหม่:</p>
                  <img :src="newImagePreview" alt="New preview" class="img-thumbnail" style="max-width: 200px;">
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

              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">วันที่สร้าง</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      :value="formatDateTime(activity.created_at)" 
                      readonly
                    >
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="mb-3">
                    <label class="form-label">วันที่อัปเดตล่าสุด</label>
                    <input 
                      type="text" 
                      class="form-control" 
                      :value="activity.updated_at ? formatDateTime(activity.updated_at) : 'ไม่เคยอัปเดต'" 
                      readonly
                    >
                  </div>
                </div>
              </div>

              <div class="d-flex justify-content-between">
                <router-link to="/admin/activities" class="btn btn-secondary">
                  <i class="fas fa-times me-2"></i>ยกเลิก
                </router-link>
                <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
                  <i class="fas fa-save me-2"></i>
                  {{ isSubmitting ? 'กำลังบันทึก...' : 'บันทึกการเปลี่ยนแปลง' }}
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
import { useRouter, useRoute } from 'vue-router'
import apiService from '../services/apiService'

export default {
  name: 'EditActivity',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const loading = ref(true)
    const isSubmitting = ref(false)
    const newImagePreview = ref(null)
    const toastElement = ref(null)
    const toastTitle = ref('')
    const toastMessage = ref('')
    
    const activity = ref({})
    
    const formData = reactive({
      title: '',
      activity_date: '',
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

    const fetchActivity = async () => {
      try {
        const activityId = route.params.id
        const response = await apiService.get(`/api/admin/activities/${activityId}`)
        activity.value = response.data
        
        // Populate form data
        formData.title = activity.value.title || ''
        formData.activity_date = activity.value.activity_date || ''
        formData.upload_type = activity.value.upload_type || 'data'
        formData.description = activity.value.description || ''
        formData.external_link = activity.value.external_link || ''
        formData.link_type = activity.value.link_type || 'website'
        
        loading.value = false
      } catch (error) {
        console.error('Error fetching activity:', error)
        showToast('ข้อผิดพลาด', 'ไม่สามารถโหลดข้อมูลกิจกรรมได้')
        loading.value = false
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
          newImagePreview.value = e.target.result
        }
        reader.readAsDataURL(file)
      }
    }

    const updateCharCount = () => {
      // This is handled by the computed property
    }

    const getImageUrl = (filename) => {
      return `/storage/activities/${filename}`
    }

    const formatDateTime = (dateString) => {
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

    const submitForm = async () => {
      if (isSubmitting.value) return
      
      isSubmitting.value = true
      
      try {
        const submitData = new FormData()
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
        
        const activityId = route.params.id
        await apiService.put(`/api/admin/activities/${activityId}`, submitData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        showToast('สำเร็จ', 'อัปเดตกิจกรรมเรียบร้อยแล้ว')
        
        setTimeout(() => {
          router.push('/admin/activities')
        }, 1500)
        
      } catch (error) {
        console.error('Error updating activity:', error)
        const errorMessage = error.response?.data?.message || 'เกิดข้อผิดพลาดในการอัปเดตกิจกรรม'
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
      fetchActivity()
    })

    return {
      loading,
      activity,
      formData,
      isSubmitting,
      newImagePreview,
      charCount,
      charCountColor,
      toastElement,
      toastTitle,
      toastMessage,
      handleImageUpload,
      updateCharCount,
      getImageUrl,
      formatDateTime,
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

.spinner-border {
  width: 3rem;
  height: 3rem;
}
</style>