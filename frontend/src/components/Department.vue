<template>
  <div>
    <!-- Breadcrumb -->
    <div class="row">
      <div class="col-12">
        <nav aria-label="breadcrumb">
          <ol class="breadcrumb">
            <li class="breadcrumb-item">
              <router-link to="/">หน้าแรก</router-link>
            </li>
            <li class="breadcrumb-item active">{{ department?.name }}</li>
          </ol>
        </nav>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">กำลังโหลด...</span>
      </div>
    </div>

    <!-- Department Header -->
    <div v-else-if="department" class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-body text-center">
            <h1 class="display-5 text-primary">
              <i :class="getDepartmentIcon(department.code)" v-if="!isKidneyDept(department.code)"></i>
              <img v-else src="/static/images/kidney.svg" alt="หน่วยไตเรื้อรัง" 
                   style="width: 60px; height: 60px; object-fit: contain; margin-right: 1rem;">
              {{ department.name }}
            </h1>
            <p class="lead">{{ department.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <ul class="nav nav-tabs" id="departmentTabs" role="tablist">
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          :class="{ active: activeTab === 'guidelines' }"
          @click="activeTab = 'guidelines'"
          type="button"
        >
          <i class="fas fa-file-medical me-2"></i>Guidelines
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          :class="{ active: activeTab === 'knowledge' }"
          @click="activeTab = 'knowledge'"
          type="button"
        >
          <i class="fas fa-book-medical me-2"></i>ความรู้
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          :class="{ active: activeTab === 'activities' }"
          @click="activeTab = 'activities'"
          type="button"
        >
          <i class="fas fa-calendar-alt me-2"></i>กิจกรรม
        </button>
      </li>
      <li class="nav-item" role="presentation">
        <button 
          class="nav-link" 
          :class="{ active: activeTab === 'contact' }"
          @click="activeTab = 'contact'"
          type="button"
        >
          <i class="fas fa-address-book me-2"></i>ติดต่อ
        </button>
      </li>
    </ul>

    <!-- Tab Content -->
    <div class="tab-content" id="departmentTabContent">
      <!-- Guidelines Tab -->
      <div v-show="activeTab === 'guidelines'" class="tab-pane fade show active">
        <div class="card mt-3">
          <div class="card-header">
            <h5 class="mb-0"><i class="fas fa-file-medical me-2"></i>ไฟล์ Guidelines</h5>
          </div>
          <div class="card-body">
            <div v-if="guidelines.length > 0" class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>ชื่อไฟล์</th>
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
                      <i :class="guideline.external_link ? 'fas fa-link me-2 text-primary' : 'fas fa-file-pdf me-2 text-danger'"></i>
                      {{ guideline.title }}
                    </td>
                    <td>
                      <span v-if="guideline.external_link" class="badge bg-success">
                        {{ guideline.link_type || 'External Link' }}
                      </span>
                      <span v-else class="badge bg-info">ไฟล์</span>
                    </td>
                    <td>
                      <a v-if="guideline.external_link" :href="guideline.external_link" target="_blank" class="text-primary">
                        <i class="fas fa-external-link-alt me-1"></i>เปิดลิงก์
                      </a>
                      <span v-else>{{ formatFileSize(guideline.file_size) }} MB</span>
                    </td>
                    <td>{{ formatDate(guideline.upload_date) }}</td>
                    <td>{{ guideline.description || '-' }}</td>
                    <td>
                      <a v-if="guideline.external_link" 
                         :href="guideline.external_link" 
                         target="_blank" 
                         class="btn btn-sm btn-primary">
                        <i class="fas fa-external-link-alt me-1"></i>เปิดลิงก์
                      </a>
                      <a v-else 
                         :href="`/api/download/guideline/${guideline.id}`" 
                         class="btn btn-sm btn-primary">
                        <i class="fas fa-download me-1"></i>ดาวน์โหลด
                      </a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="text-center py-4">
              <i class="fas fa-file-medical fa-3x text-muted mb-3"></i>
              <p class="text-muted">ยังไม่มีไฟล์ guidelines สำหรับหน่วยงานนี้</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Knowledge Tab -->
      <div v-show="activeTab === 'knowledge'" class="tab-pane fade">
        <div class="card mt-3">
          <div class="card-header">
            <h5 class="mb-0"><i class="fas fa-book-medical me-2"></i>ความรู้และข้อมูลเฉพาะทาง</h5>
          </div>
          <div class="card-body">
            <div v-if="knowledge.length > 0">
              <div v-for="item in knowledge" :key="item.id" class="knowledge-item mb-4 p-3 border rounded">
                <div class="row">
                  <div class="col-md-8">
                    <h6 class="text-primary">{{ item.title }}</h6>
                    <div class="text-muted small mb-2">
                      <i class="fas fa-calendar me-1"></i>อัปเดตเมื่อ: {{ formatDateTime(item.updated_at) }}
                    </div>
                    <div class="knowledge-content" v-html="item.content"></div>
                  </div>
                  <div class="col-md-4">
                    <div v-if="item.image_path" class="text-center">
                      <img :src="getImageUrl(item.image_path)" 
                           alt="รูปภาพ" 
                           class="img-fluid rounded" 
                           style="max-width: 200px; cursor: pointer;"
                           @click="showImageModal(getImageUrl(item.image_path), item.title)">
                      <br><small class="text-muted">คลิกเพื่อดูใหญ่</small>
                    </div>
                    <div v-else-if="item.external_link" class="text-center">
                      <a :href="item.external_link" target="_blank" class="btn btn-outline-primary">
                        <i class="fas fa-external-link-alt me-1"></i>
                        {{ getLinkTypeLabel(item.link_type) }}
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-4">
              <i class="fas fa-book-medical fa-3x text-muted mb-3"></i>
              <p class="text-muted">ยังไม่มีข้อมูลความรู้สำหรับหน่วยงานนี้</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Activities Tab -->
      <div v-show="activeTab === 'activities'" class="tab-pane fade">
        <div class="card mt-3">
          <div class="card-header">
            <h5 class="mb-0"><i class="fas fa-calendar-alt me-2"></i>กิจกรรมของหน่วยงาน</h5>
          </div>
          <div class="card-body">
            <div v-if="activities.length > 0" class="row">
              <div v-for="activity in activities" :key="activity.id" class="col-md-6 mb-3">
                <div class="card h-100">
                  <img v-if="activity.image_path" 
                       :src="getImageUrl(activity.image_path)" 
                       class="card-img-top" 
                       alt="รูปภาพกิจกรรม" 
                       style="height: 200px; object-fit: cover; cursor: pointer;"
                       @click="showImageModal(getImageUrl(activity.image_path), activity.title)">
                  <div class="card-body">
                    <h6 class="card-title text-primary">{{ activity.title }}</h6>
                    <p class="card-text">{{ activity.description }}</p>
                    <div v-if="activity.activity_date" class="text-muted small">
                      <i class="fas fa-calendar me-1"></i>{{ formatDate(activity.activity_date) }}
                    </div>
                    <div v-if="activity.external_link" class="mt-2">
                      <a :href="activity.external_link" target="_blank" class="btn btn-sm btn-outline-primary">
                        <i class="fas fa-external-link-alt me-1"></i>
                        {{ getLinkTypeLabel(activity.link_type) }}
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-4">
              <i class="fas fa-calendar-alt fa-3x text-muted mb-3"></i>
              <p class="text-muted">ยังไม่มีข้อมูลกิจกรรมสำหรับหน่วยงานนี้</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Contact Tab -->
      <div v-show="activeTab === 'contact'" class="tab-pane fade">
        <div class="card mt-3">
          <div class="card-header">
            <h5 class="mb-0"><i class="fas fa-address-book me-2"></i>ข้อมูลการติดต่อ</h5>
          </div>
          <div class="card-body">
            <div v-if="contacts.length > 0">
              <div v-for="contact in contacts" :key="contact.id" class="row">
                <div v-if="contact.line_id" class="col-md-6 mb-3">
                  <div class="d-flex align-items-center">
                    <i class="fab fa-line fa-2x text-success me-3"></i>
                    <div>
                      <strong>LINE ID:</strong><br>
                      {{ contact.line_id }}
                    </div>
                  </div>
                </div>
                
                <div v-if="contact.email" class="col-md-6 mb-3">
                  <div class="d-flex align-items-center">
                    <i class="fas fa-envelope fa-2x text-primary me-3"></i>
                    <div>
                      <strong>อีเมล:</strong><br>
                      <a :href="`mailto:${contact.email}`">{{ contact.email }}</a>
                    </div>
                  </div>
                </div>
                
                <div v-if="contact.phone" class="col-md-6 mb-3">
                  <div class="d-flex align-items-center">
                    <i class="fas fa-phone fa-2x text-success me-3"></i>
                    <div>
                      <strong>เบอร์โทร:</strong><br>
                      <a :href="`tel:${contact.phone}`">{{ contact.phone }}</a>
                    </div>
                  </div>
                </div>
                
                <div v-if="contact.other_contact" class="col-12 mb-3">
                  <div class="d-flex align-items-start">
                    <i class="fas fa-info-circle fa-2x text-info me-3 mt-1"></i>
                    <div>
                      <strong>ข้อมูลเพิ่มเติม:</strong><br>
                      {{ contact.other_contact }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-4">
              <i class="fas fa-address-book fa-3x text-muted mb-3"></i>
              <p class="text-muted">ยังไม่มีข้อมูลการติดต่อสำหรับหน่วยงานนี้</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Image Modal -->
    <div class="modal fade" id="imageModal" tabindex="-1" aria-labelledby="imageModalLabel" aria-hidden="true" ref="imageModal">
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
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import apiService from '../services/apiService'
import { Modal } from 'bootstrap'

export default {
  name: 'Department',
  setup() {
    const route = useRoute()
    const department = ref(null)
    const guidelines = ref([])
    const knowledge = ref([])
    const activities = ref([])
    const contacts = ref([])
    const loading = ref(true)
    const activeTab = ref('guidelines')
    const modalImageSrc = ref('')
    const modalImageTitle = ref('')
    const imageModal = ref(null)

    const departmentId = computed(() => route.params.id)

    const getDepartmentIcon = (code) => {
      const iconMap = {
        'DM': 'fas fa-syringe me-3',
        'COPD': 'fas fa-lungs me-3',
        'UGIB': 'fas fa-tint me-3',
        'STEMI_NSTEMI': 'fas fa-heartbeat me-3',
        'STROKE': 'fas fa-brain me-3',
        'TB': 'fas fa-bacteria me-3',
        'CHEMO': 'fas fa-pills me-3',
        'HTN': 'fas fa-heart-pulse me-3',
        'SEPSIS': 'fas fa-virus me-3',
        'RHEUMATO': 'fas fa-bone me-3',
        'OBESITY': 'fas fa-weight me-3'
      }
      return iconMap[code] || 'fas fa-hospital me-3'
    }

    const isKidneyDept = (code) => {
      return code === 'CKD'
    }

    const formatFileSize = (bytes) => {
      return (bytes / 1024 / 1024).toFixed(2)
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('th-TH')
    }

    const formatDateTime = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleString('th-TH')
    }

    const getImageUrl = (imagePath) => {
      return `/api/storage/${imagePath.replace('storage/', '')}`
    }

    const getLinkTypeLabel = (linkType) => {
      const labels = {
        'youtube': 'YouTube',
        'facebook': 'Facebook',
        'line': 'Line',
        'registration': 'ลงทะเบียน'
      }
      return labels[linkType] || 'ลิงก์'
    }

    const showImageModal = (imageSrc, title) => {
      modalImageSrc.value = imageSrc
      modalImageTitle.value = title
      const modal = new Modal(imageModal.value)
      modal.show()
    }

    const fetchDepartmentData = async () => {
      try {
        loading.value = true
        const [deptResponse, guidelinesResponse, knowledgeResponse, activitiesResponse, contactsResponse] = await Promise.all([
          apiService.get(`/api/departments/${departmentId.value}`),
          apiService.get(`/api/departments/${departmentId.value}/guidelines`),
          apiService.get(`/api/departments/${departmentId.value}/knowledge`),
          apiService.get(`/api/departments/${departmentId.value}/activities`),
          apiService.get(`/api/departments/${departmentId.value}/contacts`)
        ])
        
        department.value = deptResponse.data
        guidelines.value = guidelinesResponse.data
        knowledge.value = knowledgeResponse.data
        activities.value = activitiesResponse.data
        contacts.value = contactsResponse.data
      } catch (error) {
        console.error('Error fetching department data:', error)
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchDepartmentData()
    })

    return {
      department,
      guidelines,
      knowledge,
      activities,
      contacts,
      loading,
      activeTab,
      modalImageSrc,
      modalImageTitle,
      imageModal,
      getDepartmentIcon,
      isKidneyDept,
      formatFileSize,
      formatDate,
      formatDateTime,
      getImageUrl,
      getLinkTypeLabel,
      showImageModal
    }
  }
}
</script>

<style scoped>
.knowledge-item {
  transition: box-shadow 0.2s ease-in-out;
}

.knowledge-item:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.nav-link {
  cursor: pointer;
}

.card-img-top {
  transition: transform 0.2s ease-in-out;
}

.card-img-top:hover {
  transform: scale(1.05);
}
</style>