<script setup>
import { ref, onMounted } from 'vue'
import { apiService } from '../services/apiService'

const departments = ref([])
const isLoading = ref(true)
const showModal = ref(false)
const editingDepartment = ref(null)
const error = ref('')
const success = ref('')
const formData = ref({
  name: '',
  code: '',
  description: ''
})

const loadDepartments = async () => {
  try {
    isLoading.value = true
    error.value = ''
    const response = await apiService.getDepartments()
    departments.value = response.departments || []
  } catch (err) {
    console.error('Error loading departments:', err)
    error.value = 'ไม่สามารถโหลดข้อมูลแผนกได้'
  } finally {
    isLoading.value = false
  }
}

const openModal = (department = null) => {
  editingDepartment.value = department
  error.value = ''
  success.value = ''
  
  if (department) {
    formData.value = {
      name: department.name || '',
      code: department.code || '',
      description: department.description || ''
    }
  } else {
    formData.value = {
      name: '',
      code: '',
      description: ''
    }
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingDepartment.value = null
  error.value = ''
  success.value = ''
}

const saveDepartment = async () => {
  try {
    error.value = ''
    
    if (!formData.value.name.trim() || !formData.value.code.trim()) {
      error.value = 'กรุณากรอกชื่อแผนกและรหัสแผนก'
      return
    }
    
    if (editingDepartment.value) {
      await apiService.updateDepartment(editingDepartment.value.id, formData.value)
      success.value = 'แก้ไขข้อมูลแผนกเรียบร้อยแล้ว'
    } else {
      await apiService.createDepartment(formData.value)
      success.value = 'เพิ่มแผนกใหม่เรียบร้อยแล้ว'
    }
    
    setTimeout(() => {
      closeModal()
      loadDepartments()
    }, 1500)
    
  } catch (err) {
    console.error('Error saving department:', err)
    error.value = err.response?.data?.message || 'เกิดข้อผิดพลาดในการบันทึกข้อมูล'
  }
}

const deleteDepartment = async (id, name) => {
  if (confirm(`คุณแน่ใจหรือไม่ที่จะลบแผนก "${name}"?\n\nการลบจะไม่สามารถกู้คืนได้`)) {
    try {
      await apiService.deleteDepartment(id)
      success.value = 'ลบแผนกเรียบร้อยแล้ว'
      loadDepartments()
      
      setTimeout(() => {
        success.value = ''
      }, 3000)
      
    } catch (err) {
      console.error('Error deleting department:', err)
      error.value = err.response?.data?.message || 'เกิดข้อผิดพลาดในการลบแผนก'
    }
  }
}

const clearMessages = () => {
  error.value = ''
  success.value = ''
}

onMounted(() => {
  loadDepartments()
})
</script>

<template>
  <div class="departments">
    <!-- Page Header -->
    <div class="page-header">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col">
            <h1 class="page-title">
              <i class="fas fa-building"></i>
              จัดการแผนก
            </h1>
            <p class="page-subtitle">จัดการข้อมูลแผนกต่างๆ ในโรงพยาบาล</p>
          </div>
          <div class="col-auto">
            <button 
              class="btn btn-light btn-lg"
              @click="openModal()"
              :disabled="isLoading"
            >
              <i class="fas fa-plus"></i>
              เพิ่มแผนกใหม่
            </button>
          </div>
        </div>
      </div>
    </div>

    <div class="container-fluid">
      <!-- Alert Messages -->
      <div class="row" v-if="error || success">
        <div class="col-12">
          <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-triangle me-2"></i>
            {{ error }}
            <button type="button" class="btn-close" @click="clearMessages()"></button>
          </div>
          <div v-if="success" class="alert alert-success alert-dismissible fade show" role="alert">
            <i class="fas fa-check-circle me-2"></i>
            {{ success }}
            <button type="button" class="btn-close" @click="clearMessages()"></button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div class="row" v-if="isLoading">
        <div class="col-12 text-center py-5">
          <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
            <span class="visually-hidden">กำลังโหลด...</span>
          </div>
          <p class="mt-3 text-muted">กำลังโหลดข้อมูลแผนก...</p>
        </div>
      </div>

      <!-- Departments Grid -->
      <div class="row" v-if="!isLoading">
        <div class="col-xl-4 col-lg-6 col-md-12 mb-4" v-for="department in departments" :key="department.id">
          <div class="department-card">
            <div class="department-header">
              <div class="department-icon">
                <i class="fas fa-hospital"></i>
              </div>
              <div class="department-info">
                <h5 class="department-name">{{ department.name }}</h5>
                <span class="department-code">{{ department.code }}</span>
              </div>
            </div>
            
            <div class="department-body">
              <p class="department-description">
                {{ department.description || 'ไม่มีคำอธิบาย' }}
              </p>
              
              <div class="department-stats">
                <div class="stat-item">
                  <i class="fas fa-file-medical"></i>
                  <span>Guidelines: {{ department.guidelines_count || 0 }}</span>
                </div>
                <div class="stat-item">
                  <i class="fas fa-book"></i>
                  <span>Knowledge: {{ department.knowledge_count || 0 }}</span>
                </div>
                <div class="stat-item">
                  <i class="fas fa-calendar"></i>
                  <span>Activities: {{ department.activities_count || 0 }}</span>
                </div>
              </div>
            </div>
            
            <div class="department-footer">
              <button 
                class="btn btn-outline-primary btn-sm"
                @click="openModal(department)"
                :disabled="isLoading"
              >
                <i class="fas fa-edit"></i>
                แก้ไข
              </button>
              <button 
                class="btn btn-outline-danger btn-sm"
                @click="deleteDepartment(department.id, department.name)"
                :disabled="isLoading"
              >
                <i class="fas fa-trash"></i>
                ลบ
              </button>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div class="col-12" v-if="departments.length === 0 && !isLoading">
          <div class="empty-state">
            <div class="empty-icon">
              <i class="fas fa-building"></i>
            </div>
            <h4 class="empty-title">ไม่มีข้อมูลแผนก</h4>
            <p class="empty-subtitle">เริ่มต้นโดยการเพิ่มแผนกใหม่</p>
            <button class="btn btn-primary btn-lg" @click="openModal()">
              <i class="fas fa-plus me-2"></i>
              เพิ่มแผนกแรก
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div class="modal fade" :class="{ show: showModal }" :style="{ display: showModal ? 'block' : 'none' }" v-if="showModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">
              <i class="fas fa-building me-2"></i>
              {{ editingDepartment ? 'แก้ไขข้อมูลแผนก' : 'เพิ่มแผนกใหม่' }}
            </h5>
            <button type="button" class="btn-close btn-close-white" @click="closeModal()"></button>
          </div>
          
          <div class="modal-body">
            <!-- Alert Messages in Modal -->
            <div v-if="error" class="alert alert-danger" role="alert">
              <i class="fas fa-exclamation-triangle me-2"></i>
              {{ error }}
            </div>
            <div v-if="success" class="alert alert-success" role="alert">
              <i class="fas fa-check-circle me-2"></i>
              {{ success }}
            </div>
            
            <form @submit.prevent="saveDepartment()">
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="name" class="form-label">
                      <i class="fas fa-hospital me-1"></i>
                      ชื่อแผนก *
                    </label>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="name" 
                      v-model="formData.name" 
                      placeholder="เช่น แผนกอายุรกรรม"
                      required
                    >
                  </div>
                </div>
                
                <div class="col-md-6">
                  <div class="mb-3">
                    <label for="code" class="form-label">
                      <i class="fas fa-code me-1"></i>
                      รหัสแผนก *
                    </label>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="code" 
                      v-model="formData.code" 
                      placeholder="เช่น MED"
                      style="text-transform: uppercase;"
                      required
                    >
                  </div>
                </div>
              </div>
              
              <div class="mb-3">
                <label for="description" class="form-label">
                  <i class="fas fa-align-left me-1"></i>
                  คำอธิบาย
                </label>
                <textarea 
                  class="form-control" 
                  id="description" 
                  rows="4" 
                  v-model="formData.description"
                  placeholder="อธิบายเกี่ยวกับแผนกนี้..."
                ></textarea>
              </div>
            </form>
          </div>
          
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal()">
              <i class="fas fa-times me-2"></i>
              ยกเลิก
            </button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="saveDepartment()"
              :disabled="!formData.name.trim() || !formData.code.trim()"
            >
              <i class="fas fa-save me-2"></i>
              {{ editingDepartment ? 'บันทึกการแก้ไข' : 'เพิ่มแผนก' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade" :class="{ show: showModal }" v-if="showModal"></div>
  </div>
</template>

<style scoped>
/* Page Header */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 15px;
  margin-bottom: 30px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

.page-header h1 {
  font-weight: 700;
  font-size: 2.2rem;
}

.page-header p {
  font-size: 1.1rem;
  opacity: 0.9;
}

/* Alert Messages */
.alert {
  border: none;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 25px;
}

.alert-danger {
  background: linear-gradient(135deg, #ff6b6b, #ee5a52);
  color: white;
}

.alert-success {
  background: linear-gradient(135deg, #51cf66, #40c057);
  color: white;
}

/* Department Cards */
.department-card {
  background: white;
  border: none;
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  overflow: hidden;
  margin-bottom: 25px;
}

.department-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}

.department-header {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.department-icon {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
}

.department-info h5 {
  color: white;
  font-weight: 600;
  font-size: 1.3rem;
  margin: 0;
}

.department-code {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.department-body {
  padding: 25px;
}

.department-description {
  color: #6c757d;
  font-size: 1rem;
  line-height: 1.6;
  margin-bottom: 20px;
  min-height: 50px;
}

/* Statistics */
.department-stats {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6c757d;
  font-size: 0.9rem;
}

.stat-item i {
  color: #495057;
}

.department-footer {
  padding: 0 25px 25px;
  display: flex;
  gap: 10px;
}

/* Action Buttons */
.btn-outline-primary {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  border: none;
  color: #8b4513;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.btn-outline-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(252, 182, 159, 0.4);
  color: #8b4513;
}

.btn-outline-danger {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  border: none;
  color: #dc3545;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.btn-outline-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(255, 154, 158, 0.4);
  color: #dc3545;
}

/* Add Button */
.btn-light {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  font-weight: 600;
  border-radius: 12px;
  font-size: 1.1rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.btn-light:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
  color: white;
}

/* Loading and Empty States */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
}

.empty-icon i {
  font-size: 4rem;
  color: #dee2e6;
  margin-bottom: 20px;
}

.empty-title {
  color: #6c757d;
  font-weight: 600;
  margin-bottom: 10px;
}

.empty-subtitle {
  color: #adb5bd;
  font-size: 1.1rem;
}

/* Modal Styles */
.modal {
  z-index: 1050;
}

.modal-backdrop {
  z-index: 1040;
}

.modal-content {
  border: none;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  border-bottom: none;
  border-radius: 16px 16px 0 0;
  padding: 25px;
}

.modal-title {
  font-weight: 600;
  font-size: 1.4rem;
}

.modal-body {
  padding: 30px;
}

.modal-footer {
  border-top: none;
  padding: 20px 30px 30px;
}

/* Form Styles */
.form-label {
  font-weight: 600;
  color: #495057;
  margin-bottom: 8px;
}

.form-control {
  border: 2px solid #e9ecef;
  border-radius: 10px;
  padding: 12px 16px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

/* Responsive Design */
@media (max-width: 768px) {
  .page-header h1 {
    font-size: 1.8rem;
  }
  
  .department-card {
    margin-bottom: 20px;
  }
  
  .department-body {
    padding: 20px;
  }
  
  .department-stats {
    padding: 12px;
    flex-direction: column;
  }
  
  .department-footer {
    padding: 0 20px 20px;
    flex-direction: column;
  }
}
</style>