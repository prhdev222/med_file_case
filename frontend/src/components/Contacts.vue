<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const contacts = ref([])
const loading = ref(true)
const showModal = ref(false)
const editingContact = ref(null)
const searchQuery = ref('')
const selectedDepartment = ref('')
const departments = ref([])

const formData = ref({
  name: '',
  position: '',
  department: '',
  phone: '',
  email: '',
  extension: '',
  notes: ''
})

const filteredContacts = computed(() => {
  let filtered = contacts.value
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(contact => 
      contact.name.toLowerCase().includes(query) ||
      contact.position.toLowerCase().includes(query) ||
      contact.department.toLowerCase().includes(query) ||
      contact.phone.includes(query) ||
      contact.email.toLowerCase().includes(query)
    )
  }
  
  if (selectedDepartment.value) {
    filtered = filtered.filter(contact => contact.department === selectedDepartment.value)
  }
  
  return filtered
})

const loadContacts = async () => {
  try {
    const response = await axios.get('/api/contacts')
    contacts.value = response.data
  } catch (error) {
    console.error('Error loading contacts:', error)
  } finally {
    loading.value = false
  }
}

const loadDepartments = async () => {
  try {
    const response = await axios.get('/api/departments')
    departments.value = response.data
  } catch (error) {
    console.error('Error loading departments:', error)
  }
}

const openModal = (contact = null) => {
  editingContact.value = contact
  if (contact) {
    formData.value = { ...contact }
  } else {
    formData.value = {
      name: '',
      position: '',
      department: '',
      phone: '',
      email: '',
      extension: '',
      notes: ''
    }
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingContact.value = null
}

const saveContact = async () => {
  try {
    if (editingContact.value) {
      await axios.put(`/api/contacts/${editingContact.value.id}`, formData.value)
    } else {
      await axios.post('/api/contacts', formData.value)
    }
    closeModal()
    loadContacts()
  } catch (error) {
    console.error('Error saving contact:', error)
  }
}

const deleteContact = async (id) => {
  if (confirm('คุณแน่ใจหรือไม่ที่จะลบรายชื่อนี้?')) {
    try {
      await axios.delete(`/api/contacts/${id}`)
      loadContacts()
    } catch (error) {
      console.error('Error deleting contact:', error)
    }
  }
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedDepartment.value = ''
}

onMounted(() => {
  loadContacts()
  loadDepartments()
})
</script>

<template>
  <div class="contacts">
    <div class="container-fluid">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h1 class="h3 mb-0">
                <i class="bi bi-person-lines-fill me-2"></i>
                รายชื่อติดต่อ
              </h1>
              <p class="text-muted">จัดการรายชื่อบุคลากรและข้อมูลติดต่อ</p>
            </div>
            <button 
              class="btn btn-primary"
              @click="openModal()"
            >
              <i class="bi bi-plus-circle me-2"></i>
              เพิ่มรายชื่อใหม่
            </button>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card">
            <div class="card-body">
              <div class="row g-3">
                <div class="col-md-6">
                  <label for="search" class="form-label">ค้นหา</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-search"></i>
                    </span>
                    <input 
                      type="text" 
                      class="form-control" 
                      id="search"
                      placeholder="ค้นหาชื่อ, ตำแหน่ง, แผนก, โทรศัพท์, หรืออีเมล"
                      v-model="searchQuery"
                    >
                  </div>
                </div>
                <div class="col-md-4">
                  <label for="department" class="form-label">แผนก</label>
                  <select class="form-select" id="department" v-model="selectedDepartment">
                    <option value="">ทุกแผนก</option>
                    <option v-for="dept in departments" :key="dept.id" :value="dept.name">
                      {{ dept.name }}
                    </option>
                  </select>
                </div>
                <div class="col-md-2 d-flex align-items-end">
                  <button class="btn btn-outline-secondary w-100" @click="clearFilters()">
                    <i class="bi bi-x-circle me-2"></i>
                    ล้างตัวกรอง
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div class="row" v-if="loading">
        <div class="col-12 text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">กำลังโหลด...</span>
          </div>
          <p class="mt-2 text-muted">กำลังโหลดรายชื่อติดต่อ...</p>
        </div>
      </div>

      <!-- Contacts Table -->
      <div class="row" v-if="!loading">
        <div class="col-12">
          <div class="card shadow">
            <div class="card-header">
              <h6 class="m-0 font-weight-bold text-primary">
                <i class="bi bi-list-ul me-2"></i>
                รายชื่อติดต่อ ({{ filteredContacts.length }} รายการ)
              </h6>
            </div>
            <div class="card-body">
              <div class="table-responsive" v-if="filteredContacts.length > 0">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>ชื่อ</th>
                      <th>ตำแหน่ง</th>
                      <th>แผนก</th>
                      <th>โทรศัพท์</th>
                      <th>อีเมล</th>
                      <th>ต่อใน</th>
                      <th class="text-center">จัดการ</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="contact in filteredContacts" :key="contact.id">
                      <td>
                        <div class="d-flex align-items-center">
                          <div class="avatar-circle me-3">
                            {{ contact.name.charAt(0).toUpperCase() }}
                          </div>
                          <strong>{{ contact.name }}</strong>
                        </div>
                      </td>
                      <td>{{ contact.position }}</td>
                      <td>
                        <span class="badge bg-secondary">{{ contact.department }}</span>
                      </td>
                      <td>
                        <a :href="`tel:${contact.phone}`" class="text-decoration-none">
                          <i class="bi bi-telephone me-1"></i>
                          {{ contact.phone }}
                        </a>
                      </td>
                      <td>
                        <a :href="`mailto:${contact.email}`" class="text-decoration-none" v-if="contact.email">
                          <i class="bi bi-envelope me-1"></i>
                          {{ contact.email }}
                        </a>
                        <span class="text-muted" v-else>-</span>
                      </td>
                      <td>
                        <span v-if="contact.extension" class="badge bg-info">{{ contact.extension }}</span>
                        <span v-else class="text-muted">-</span>
                      </td>
                      <td class="text-center">
                        <div class="btn-group btn-group-sm" role="group">
                          <button 
                            class="btn btn-outline-primary"
                            @click="openModal(contact)"
                            title="แก้ไข"
                          >
                            <i class="bi bi-pencil"></i>
                          </button>
                          <button 
                            class="btn btn-outline-danger"
                            @click="deleteContact(contact.id)"
                            title="ลบ"
                          >
                            <i class="bi bi-trash"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <!-- Empty State -->
              <div v-else class="text-center py-5">
                <i class="bi bi-person-x display-4 text-muted"></i>
                <h4 class="mt-3 text-muted">ไม่พบรายชื่อติดต่อ</h4>
                <p class="text-muted">ลองเปลี่ยนเงื่อนไขการค้นหา หรือเพิ่มรายชื่อใหม่</p>
                <button class="btn btn-primary" @click="openModal()">
                  <i class="bi bi-plus-circle me-2"></i>
                  เพิ่มรายชื่อใหม่
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <div class="modal fade" :class="{ show: showModal }" :style="{ display: showModal ? 'block' : 'none' }" v-if="showModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="bi bi-person-plus me-2"></i>
              {{ editingContact ? 'แก้ไขรายชื่อติดต่อ' : 'เพิ่มรายชื่อใหม่' }}
            </h5>
            <button type="button" class="btn-close" @click="closeModal()"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveContact()">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="name" class="form-label">ชื่อ-นามสกุล *</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="name" 
                    v-model="formData.name" 
                    required
                  >
                </div>
                
                <div class="col-md-6 mb-3">
                  <label for="position" class="form-label">ตำแหน่ง *</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="position" 
                    v-model="formData.position" 
                    required
                  >
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="department" class="form-label">แผนก *</label>
                  <select class="form-select" id="department" v-model="formData.department" required>
                    <option value="">เลือกแผนก</option>
                    <option v-for="dept in departments" :key="dept.id" :value="dept.name">
                      {{ dept.name }}
                    </option>
                  </select>
                </div>
                
                <div class="col-md-6 mb-3">
                  <label for="phone" class="form-label">โทรศัพท์ *</label>
                  <input 
                    type="tel" 
                    class="form-control" 
                    id="phone" 
                    v-model="formData.phone" 
                    required
                  >
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-8 mb-3">
                  <label for="email" class="form-label">อีเมล</label>
                  <input 
                    type="email" 
                    class="form-control" 
                    id="email" 
                    v-model="formData.email"
                  >
                </div>
                
                <div class="col-md-4 mb-3">
                  <label for="extension" class="form-label">ต่อใน</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="extension" 
                    v-model="formData.extension"
                  >
                </div>
              </div>
              
              <div class="mb-3">
                <label for="notes" class="form-label">หมายเหตุ</label>
                <textarea 
                  class="form-control" 
                  id="notes" 
                  rows="3" 
                  v-model="formData.notes"
                ></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal()">
              ยกเลิก
            </button>
            <button type="button" class="btn btn-primary" @click="saveContact()">
              <i class="bi bi-check-circle me-2"></i>
              {{ editingContact ? 'บันทึกการแก้ไข' : 'เพิ่มรายชื่อ' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop fade" :class="{ show: showModal }" v-if="showModal"></div>
  </div>
</template>

<style scoped>
.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 16px;
}

.modal {
  z-index: 1050;
}

.modal-backdrop {
  z-index: 1040;
}

.table th {
  border-top: none;
  font-weight: 600;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
}
</style>