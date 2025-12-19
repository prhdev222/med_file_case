<template>
  <div class="container mt-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2><i class="fas fa-calendar-alt me-2"></i>จัดการกิจกรรม</h2>
          <router-link to="/admin/dashboard" class="btn btn-secondary">
            <i class="fas fa-arrow-left me-2"></i>กลับไปหน้าแดชบอร์ด
          </router-link>
        </div>

        <!-- สถิติ -->
        <div class="row mb-4">
          <div class="col-md-3">
            <div class="card bg-success text-white">
              <div class="card-body">
                <h5 class="card-title">จำนวนกิจกรรมทั้งหมด</h5>
                <h2>{{ activities.length }}</h2>
              </div>
            </div>
          </div>
        </div>

        <!-- ตารางกิจกรรม -->
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0"><i class="fas fa-list me-2"></i>รายการกิจกรรม</h5>
          </div>
          <div class="card-body">
            <div v-if="activities.length > 0" class="table-responsive">
              <table class="table table-striped table-hover">
                <thead class="table-dark">
                  <tr>
                    <th>ลำดับ</th>
                    <th>ชื่อกิจกรรม</th>
                    <th>รูปภาพ/ลิงก์</th>
                    <th>หน่วยงาน</th>
                    <th>รายละเอียด</th>
                    <th>วันที่กิจกรรม</th>
                    <th>วันที่สร้าง</th>
                    <th>การจัดการ</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(activity, index) in activities" :key="activity.id">
                    <td>{{ index + 1 }}</td>
                    <td>
                      <strong>{{ activity.title }}</strong>
                    </td>
                    <td>
                      <div v-if="activity.image_path" class="text-center">
                        <img :src="getImageUrl(activity.image_path)" 
                             alt="รูปภาพ" class="img-thumbnail" 
                             style="max-width: 80px; cursor: pointer;"
                             @click="showImageModal(getImageUrl(activity.image_path), activity.title)">
                        <br><small class="text-muted">คลิกเพื่อดูใหญ่</small>
                      </div>
                      <div v-else-if="activity.external_link" class="text-center">
                        <a :href="activity.external_link" target="_blank" class="btn btn-sm btn-outline-primary">
                          <i class="fas fa-external-link-alt"></i>
                          {{ getLinkTypeText(activity.link_type) }}
                        </a>
                      </div>
                      <span v-else class="text-muted">ไม่มี</span>
                    </td>
                    <td>
                      <span class="badge bg-info">{{ activity.department?.name || 'ไม่ระบุ' }}</span>
                    </td>
                    <td>
                      <span v-if="activity.description">
                        {{ activity.description.length > 100 ? activity.description.substring(0, 100) + '...' : activity.description }}
                      </span>
                      <span v-else class="text-muted">ไม่มีรายละเอียด</span>
                    </td>
                    <td>
                      <span v-if="activity.activity_date">
                        {{ formatDate(activity.activity_date) }}
                      </span>
                      <span v-else class="text-muted">ไม่ระบุ</span>
                    </td>
                    <td>{{ formatDateTime(activity.created_at) }}</td>
                    <td>
                      <div class="btn-group" role="group">
                        <router-link :to="`/admin/activities/edit/${activity.id}`" 
                                   class="btn btn-sm btn-outline-primary">
                          <i class="fas fa-edit"></i>
                        </router-link>
                        <button type="button" class="btn btn-sm btn-outline-danger" 
                                @click="deleteActivity(activity.id)">
                          <i class="fas fa-trash"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-center py-5">
              <i class="fas fa-calendar-alt fa-3x text-muted mb-3"></i>
              <h5 class="text-muted">ยังไม่มีข้อมูลกิจกรรม</h5>
              <p class="text-muted">คลิกปุ่มด้านล่างเพื่อเพิ่มกิจกรรมใหม่</p>
            </div>
          </div>
        </div>

        <!-- ปุ่มเพิ่มกิจกรรมใหม่ -->
        <div class="text-center mt-4">
          <router-link to="/admin/activities/add" class="btn btn-success btn-lg">
            <i class="fas fa-plus me-2"></i>เพิ่มกิจกรรมใหม่
          </router-link>
        </div>
      </div>
    </div>

    <!-- Modal สำหรับแสดงรูปภาพใหญ่ -->
    <div class="modal fade" id="imageModal" tabindex="-1" aria-labelledby="imageModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="imageModalLabel">{{ modalTitle }}</h5>
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
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import apiService from '../services/apiService.js'

export default {
  name: 'Activities',
  setup() {
    const activities = ref([])
    const loading = ref(false)
    const error = ref('')
    const modalImageSrc = ref('')
    const modalTitle = ref('')

    const fetchActivities = async () => {
      try {
        loading.value = true
        error.value = ''
        const response = await apiService.getActivities()
        activities.value = response.activities || []
      } catch (err) {
        console.error('Error fetching activities:', err)
        error.value = 'เกิดข้อผิดพลาดในการโหลดข้อมูลกิจกรรม'
      } finally {
        loading.value = false
      }
    }

    const deleteActivity = async (id) => {
      if (confirm('คุณแน่ใจหรือไม่ที่จะลบกิจกรรมนี้?')) {
        try {
          await apiService.deleteActivity(id)
          await fetchActivities() // Refresh the list
        } catch (err) {
          console.error('Error deleting activity:', err)
          alert('เกิดข้อผิดพลาดในการลบกิจกรรม')
        }
      }
    }

    const showImageModal = (imageSrc, title) => {
      modalImageSrc.value = imageSrc
      modalTitle.value = title
      const modal = new bootstrap.Modal(document.getElementById('imageModal'))
      modal.show()
    }

    const getImageUrl = (imagePath) => {
      if (!imagePath) return ''
      // Remove 'storage/' prefix if present
      const cleanPath = imagePath.replace('storage/', '')
      return `${apiService.baseURL}/storage/${cleanPath}`
    }

    const getLinkTypeText = (linkType) => {
      const types = {
        'youtube': 'YouTube',
        'facebook': 'Facebook',
        'line': 'Line',
        'registration': 'ลงทะเบียน'
      }
      return types[linkType] || 'ลิงก์'
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('th-TH')
    }

    const formatDateTime = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('th-TH')
    }

    onMounted(() => {
      fetchActivities()
    })

    return {
      activities,
      loading,
      error,
      modalImageSrc,
      modalTitle,
      deleteActivity,
      showImageModal,
      getImageUrl,
      getLinkTypeText,
      formatDate,
      formatDateTime
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

.badge {
  font-size: 0.8em;
}

.btn-group .btn {
  margin: 0 2px;
}
</style>