<template>
  <div class="container-fluid">
    <!-- Header -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <h1 class="h3 mb-0">
              <i class="fas fa-users-cog me-2"></i>จัดการ Users
            </h1>
            <p class="text-muted mb-0">ระบบจัดการผู้ใช้งานในระบบ</p>
          </div>
          <div>
            <button type="button" class="btn btn-primary" @click="showAddUserModal">
              <i class="fas fa-user-plus me-2"></i>เพิ่ม User ใหม่
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Users Table -->
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="fas fa-list me-2"></i>รายการ Users ทั้งหมด
            </h5>
          </div>
          <div class="card-body">
            <div v-if="users.length > 0">
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>ID</th>
                      <th>Username</th>
                      <th>Email</th>
                      <th>Role</th>
                      <th>สถานะ</th>
                      <th>วันที่สร้าง</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="user in users" :key="user.id">
                      <td>
                        <span class="badge bg-secondary">#{{ user.id }}</span>
                      </td>
                      <td>
                        <strong class="text-primary">{{ user.username }}</strong>
                      </td>
                      <td>
                        {{ user.email || 'ไม่ระบุ' }}
                      </td>
                      <td>
                        <span :class="getRoleBadgeClass(user.role)">{{ getRoleText(user.role) }}</span>
                      </td>
                      <td>
                        <span :class="user.is_active ? 'badge bg-success' : 'badge bg-danger'">
                          {{ user.is_active ? 'เปิดใช้งาน' : 'ปิดใช้งาน' }}
                        </span>
                      </td>
                      <td>
                        <small class="text-muted">{{ formatDate(user.created_at) }}</small>
                      </td>
                      <td>
                        <div class="btn-group" role="group">
                          <button type="button" class="btn btn-sm btn-outline-primary" 
                                  @click="editUser(user.id)" title="แก้ไข">
                            <i class="fas fa-edit"></i>
                          </button>
                          <button v-if="user.id !== currentUserId" 
                                  type="button" class="btn btn-sm btn-outline-danger" 
                                  @click="confirmDelete(user.id, user.username)" title="ลบ">
                            <i class="fas fa-trash"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div v-else class="text-center py-4">
              <i class="fas fa-users fa-3x text-muted mb-3"></i>
              <h5 class="text-muted">ยังไม่มี Users ในระบบ</h5>
              <p class="text-muted">เริ่มต้นเพิ่ม User ใหม่ได้เลย</p>
              <button type="button" class="btn btn-primary" @click="showAddUserModal">
                <i class="fas fa-user-plus me-2"></i>เพิ่ม User ใหม่
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Add User Modal -->
  <div class="modal fade" id="addUserModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-user-plus me-2"></i>เพิ่ม User ใหม่
          </h5>
          <button type="button" class="btn-close" @click="hideAddUserModal"></button>
        </div>
        <form @submit.prevent="addUser">
          <div class="modal-body">
            <div class="mb-3">
              <label for="username" class="form-label">Username <span class="text-danger">*</span></label>
              <input type="text" class="form-control" id="username" v-model="newUser.username" required>
              <div class="form-text">ชื่อผู้ใช้สำหรับเข้าสู่ระบบ</div>
            </div>
            
            <div class="mb-3">
              <label for="password" class="form-label">รหัสผ่าน <span class="text-danger">*</span></label>
              <input type="password" class="form-control" id="password" v-model="newUser.password" required>
              <div class="form-text">รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร</div>
            </div>
            
            <div class="mb-3">
              <label for="confirm_password" class="form-label">ยืนยันรหัสผ่าน <span class="text-danger">*</span></label>
              <input type="password" class="form-control" id="confirm_password" v-model="newUser.confirmPassword" required>
              <div v-if="newUser.password && newUser.confirmPassword && newUser.password !== newUser.confirmPassword" 
                   class="text-danger small">รหัสผ่านไม่ตรงกัน</div>
            </div>
            
            <div class="mb-3">
              <label for="email" class="form-label">อีเมล</label>
              <input type="email" class="form-control" id="email" v-model="newUser.email">
              <div class="form-text">ไม่บังคับ แต่แนะนำให้กรอก</div>
            </div>
            
            <div class="mb-3">
              <label for="role" class="form-label">Role <span class="text-danger">*</span></label>
              <select class="form-select" id="role" v-model="newUser.role" required>
                <option value="">เลือก Role</option>
                <option value="admin">Admin - ผู้ดูแลระบบ</option>
                <option value="nurse">พยาบาล</option>
                <option value="doctor">แพทย์</option>
                <option value="staff">เจ้าหน้าที่</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="hideAddUserModal">ยกเลิก</button>
            <button type="submit" class="btn btn-primary" :disabled="!isFormValid">เพิ่ม User</button>
          </div>
        </form>
      </div>
    </div>
  </div>

  <!-- Delete Confirmation Modal -->
  <div class="modal fade" id="deleteModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="fas fa-exclamation-triangle text-danger me-2"></i>ยืนยันการลบ
          </h5>
          <button type="button" class="btn-close" @click="hideDeleteModal"></button>
        </div>
        <div class="modal-body">
          <p>คุณต้องการลบ User <strong>{{ deleteUser.username }}</strong> ใช่หรือไม่?</p>
          <p class="text-muted small">การดำเนินการนี้ไม่สามารถยกเลิกได้</p>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="hideDeleteModal">ยกเลิก</button>
          <button type="button" class="btn btn-danger" @click="deleteUser">
            <i class="fas fa-trash me-2"></i>ลบ
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import apiService from '../services/apiService'

export default {
  name: 'Users',
  setup() {
    const users = ref([])
    const loading = ref(true)
    const error = ref(null)
    const currentUserId = ref(null)
    
    const newUser = ref({
      username: '',
      password: '',
      confirmPassword: '',
      email: '',
      role: ''
    })
    
    const deleteUser = ref({
      id: null,
      username: ''
    })

    const fetchUsers = async () => {
      try {
        loading.value = true
        const response = await apiService.getUsers()
        users.value = response.data || response
        // Get current user ID from token or API
        const currentUserResponse = await apiService.getCurrentUser()
        currentUserId.value = currentUserResponse.id
      } catch (err) {
        console.error('Error fetching users:', err)
        error.value = 'เกิดข้อผิดพลาดในการโหลดข้อมูลผู้ใช้'
      } finally {
        loading.value = false
      }
    }

    const addUser = async () => {
      try {
        await apiService.createUser(newUser.value)
        await fetchUsers() // Refresh the list
        hideAddUserModal()
        resetNewUserForm()
      } catch (err) {
        console.error('Error adding user:', err)
        alert('เกิดข้อผิดพลาดในการเพิ่มผู้ใช้')
      }
    }

    const deleteUserConfirmed = async () => {
      try {
        await apiService.deleteUser(deleteUser.value.id)
        await fetchUsers() // Refresh the list
        hideDeleteModal()
      } catch (err) {
        console.error('Error deleting user:', err)
        alert('เกิดข้อผิดพลาดในการลบผู้ใช้')
      }
    }

    const showAddUserModal = () => {
      const modal = new bootstrap.Modal(document.getElementById('addUserModal'))
      modal.show()
    }

    const hideAddUserModal = () => {
      const modal = bootstrap.Modal.getInstance(document.getElementById('addUserModal'))
      if (modal) modal.hide()
    }

    const showDeleteModal = () => {
      const modal = new bootstrap.Modal(document.getElementById('deleteModal'))
      modal.show()
    }

    const hideDeleteModal = () => {
      const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'))
      if (modal) modal.hide()
    }

    const confirmDelete = (userId, username) => {
      deleteUser.value = { id: userId, username }
      showDeleteModal()
    }

    const editUser = (userId) => {
      // TODO: Implement edit user functionality
      alert('ฟีเจอร์แก้ไข User กำลังอยู่ในระหว่างการพัฒนา')
    }

    const resetNewUserForm = () => {
      newUser.value = {
        username: '',
        password: '',
        confirmPassword: '',
        email: '',
        role: ''
      }
    }

    const getRoleBadgeClass = (role) => {
      const classes = {
        'admin': 'badge bg-danger',
        'nurse': 'badge bg-primary',
        'doctor': 'badge bg-success',
        'staff': 'badge bg-secondary'
      }
      return classes[role] || 'badge bg-secondary'
    }

    const getRoleText = (role) => {
      const texts = {
        'admin': 'Admin',
        'nurse': 'พยาบาล',
        'doctor': 'แพทย์',
        'staff': 'เจ้าหน้าที่'
      }
      return texts[role] || 'เจ้าหน้าที่'
    }

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

    const isFormValid = computed(() => {
      return newUser.value.username && 
             newUser.value.password && 
             newUser.value.confirmPassword && 
             newUser.value.role &&
             newUser.value.password === newUser.value.confirmPassword &&
             newUser.value.password.length >= 6
    })

    onMounted(() => {
      fetchUsers()
    })

    return {
      users,
      loading,
      error,
      currentUserId,
      newUser,
      deleteUser: deleteUser,
      addUser,
      deleteUser: deleteUserConfirmed,
      showAddUserModal,
      hideAddUserModal,
      confirmDelete,
      editUser,
      getRoleBadgeClass,
      getRoleText,
      formatDate,
      isFormValid
    }
  }
}
</script>

<style scoped>
.badge {
  font-size: 0.8em;
}

.btn-group .btn {
  margin: 0 2px;
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.modal-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.text-danger {
  font-size: 0.875em;
}
</style>