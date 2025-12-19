<script>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiService } from '../services/apiService'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const isLoading = ref(false)
    const showPassword = ref(false)
    const errorMessage = ref('')
    
    const credentials = reactive({
      username: '',
      password: '',
      rememberMe: false
    })
    
    const errors = reactive({
      username: '',
      password: ''
    })

    const validateForm = () => {
      errors.username = ''
      errors.password = ''
      let isValid = true

      if (!credentials.username.trim()) {
        errors.username = 'กรุณากรอกชื่อผู้ใช้'
        isValid = false
      }

      if (!credentials.password.trim()) {
        errors.password = 'กรุณากรอกรหัสผ่าน'
        isValid = false
      } else if (credentials.password.length < 4) {
        errors.password = 'รหัสผ่านต้องมีอย่างน้อย 4 ตัวอักษร'
        isValid = false
      }

      return isValid
    }

    const handleLogin = async () => {
      if (!validateForm()) {
        return
      }

      isLoading.value = true
      errorMessage.value = ''

      try {
        const response = await apiService.login(
          credentials.username,
          credentials.password,
          credentials.rememberMe
        )

        if (response.success) {
          // Store user data
          const storage = credentials.rememberMe ? localStorage : sessionStorage
          storage.setItem('isAuthenticated', 'true')
          storage.setItem('user', JSON.stringify(response.user))
          
          // Redirect to dashboard
          router.push('/admin/dashboard')
        } else {
          errorMessage.value = response.message || 'เข้าสู่ระบบไม่สำเร็จ'
        }
      } catch (error) {
        console.error('Login error:', error)
        errorMessage.value = error.message || 'เกิดข้อผิดพลาดในการเชื่อมต่อ กรุณาลองใหม่อีกครั้ง'
      } finally {
        isLoading.value = false
      }
    }

    const togglePasswordVisibility = () => {
      showPassword.value = !showPassword.value
    }

    // Check if user is already logged in
    onMounted(() => {
      const userData = localStorage.getItem('user') || sessionStorage.getItem('user')
      if (userData) {
        router.push('/dashboard')
      }
    })

    return {
      credentials,
      errors,
      isLoading,
      showPassword,
      errorMessage,
      handleLogin,
      togglePasswordVisibility
    }
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <i class="fas fa-hospital fa-3x text-primary mb-3"></i>
        <h2 class="text-center mb-4">Hospital Admin System</h2>
        <p class="text-center text-muted mb-4">เข้าสู่ระบบเพื่อจัดการข้อมูลโรงพยาบาล</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="mb-3">
          <label for="username" class="form-label">
            <i class="fas fa-user"></i> ชื่อผู้ใช้
          </label>
          <input
            type="text"
            class="form-control"
            id="username"
            v-model="credentials.username"
            :class="{ 'is-invalid': errors.username }"
            placeholder="กรอกชื่อผู้ใช้"
            required
            autocomplete="username"
          >
          <div v-if="errors.username" class="invalid-feedback">
            {{ errors.username }}
          </div>
        </div>

        <div class="mb-3">
          <label for="password" class="form-label">
            <i class="fas fa-lock"></i> รหัสผ่าน
          </label>
          <div class="input-group">
            <input
              :type="showPassword ? 'text' : 'password'"
              class="form-control"
              id="password"
              v-model="credentials.password"
              :class="{ 'is-invalid': errors.password }"
              placeholder="กรอกรหัสผ่าน"
              required
              autocomplete="current-password"
            >
            <button
              type="button"
              class="btn btn-outline-secondary"
              @click="togglePasswordVisibility"
            >
              <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
            </button>
          </div>
          <div v-if="errors.password" class="invalid-feedback d-block">
            {{ errors.password }}
          </div>
        </div>

        <div class="mb-3 form-check">
          <input
            type="checkbox"
            class="form-check-input"
            id="rememberMe"
            v-model="credentials.rememberMe"
          >
          <label class="form-check-label" for="rememberMe">
            จดจำการเข้าสู่ระบบ
          </label>
        </div>

        <div v-if="errorMessage" class="alert alert-danger" role="alert">
          <i class="fas fa-exclamation-triangle"></i>
          {{ errorMessage }}
        </div>

        <button
          type="submit"
          class="btn btn-primary w-100 mb-3"
          :disabled="isLoading"
        >
          <span v-if="isLoading" class="spinner-border spinner-border-sm me-2" role="status"></span>
          <i v-else class="fas fa-sign-in-alt me-2"></i>
          {{ isLoading ? 'กำลังเข้าสู่ระบบ...' : 'เข้าสู่ระบบ' }}
        </button>
      </form>

      <div class="login-footer">
        <hr>
        <p class="text-center text-muted small">
          <i class="fas fa-shield-alt"></i>
          ระบบปลอดภัยด้วยการเข้ารหัสข้อมูล
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem 1rem;
}

.login-card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 3rem;
  width: 100%;
  max-width: 450px;
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-header h2 {
  color: #333;
  font-weight: 600;
}

.form-label {
  font-weight: 500;
  color: #555;
  margin-bottom: 0.5rem;
}

.form-control {
  border: 2px solid #e9ecef;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}

.form-control.is-invalid {
  border-color: #dc3545;
}

.input-group .btn {
  border: 2px solid #e9ecef;
  border-left: none;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 0.5rem;
  padding: 0.75rem 1.5rem;
  font-weight: 500;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.form-check-input:checked {
  background-color: #667eea;
  border-color: #667eea;
}

.alert {
  border-radius: 0.5rem;
  border: none;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
}

.login-footer {
  margin-top: 2rem;
}

.login-footer hr {
  margin: 1.5rem 0;
  opacity: 0.3;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

/* Responsive Design */
@media (max-width: 576px) {
  .login-card {
    padding: 2rem 1.5rem;
    margin: 1rem;
  }
  
  .login-header h2 {
    font-size: 1.5rem;
  }
}

/* Animation for error messages */
.alert {
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
</style>