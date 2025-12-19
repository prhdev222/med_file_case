<template>
  <div class="container-fluid">
    <!-- Header Section -->
    <div class="row">
      <div class="col-12">
        <div class="text-center mb-5">
          <h1 class="display-4 text-primary">
            <i class="fas fa-hospital me-3"></i>แผนกอายุรกรรม
          </h1>
          <p class="lead">โรงพยาบาลสงฆ์</p>
          <p class="text-muted">ระบบจัดการไฟล์และข้อมูลสำหรับบุคลากรทางการแพทย์</p>
        </div>
      </div>
    </div>

    <!-- Departments Section -->
    <div class="row">
      <div class="col-12">
        <h2 class="mb-4 text-center">หน่วยงานในแผนกอายุรกรรม</h2>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">กำลังโหลด...</span>
      </div>
    </div>

    <!-- Departments Grid -->
    <div v-else class="row g-4">
      <div v-for="dept in departments" :key="dept.id" class="col-md-6 col-lg-4">
        <div class="card h-100 shadow-sm hover-card">
          <div class="card-body text-center">
            <div class="mb-3">
              <i :class="getDepartmentIcon(dept.code)" v-if="!isKidneyDept(dept.code)"></i>
              <i v-else class="fas fa-kidneys fa-3x text-info"></i>
            </div>
            <h5 class="card-title">{{ dept.name }}</h5>
            <p class="card-text text-muted">{{ dept.description }}</p>
            <router-link :to="`/department/${dept.id}`" class="btn btn-primary">
              <i class="fas fa-arrow-right me-2"></i>เข้าดูข้อมูล
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Login Section -->
    <div class="row mt-5">
      <div class="col-12 text-center">
        <div class="card bg-primary text-white">
          <div class="card-body">
            <h4><i class="fas fa-user-lock me-2"></i>สำหรับบุคลากรทางการแพทย์</h4>
            <p class="mb-3">เข้าสู่ระบบเพื่อจัดการข้อมูลและไฟล์ของแผนก</p>
            <router-link to="/login" class="btn btn-light btn-lg">
              <i class="fas fa-sign-in-alt me-2"></i>เข้าสู่ระบบ
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Info Section -->
    <div class="row mt-4">
      <div class="col-12">
        <div class="card bg-light">
          <div class="card-body text-center">
            <h4><i class="fas fa-info-circle me-2"></i>ข้อมูลเพิ่มเติม</h4>
            <p class="mb-0">ระบบนี้จัดทำขึ้นเพื่ออำนวยความสะดวกในการเข้าถึงข้อมูลและไฟล์ต่างๆ ของแผนกอายุรกรรม</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'Home',
  setup() {
    const departments = ref([
      { id: 1, code: 'DM', name: 'หน่วยเบาหวาน', description: 'หน่วยดูแลผู้ป่วยเบาหวาน' },
      { id: 2, code: 'COPD', name: 'หน่วยปอดอุดกั้นเรื้อรัง', description: 'หน่วยดูแลผู้ป่วยโรคปอดอุดกั้นเรื้อรัง' },
      { id: 3, code: 'UGIB', name: 'หน่วยเลือดออกทางเดินอาหาร', description: 'หน่วยดูแลผู้ป่วยเลือดออกทางเดินอาหารส่วนต้น' },
      { id: 4, code: 'CKD', name: 'หน่วยไตเรื้อรัง', description: 'หน่วยดูแลผู้ป่วยไตเรื้อรัง' },
      { id: 5, code: 'STEMI_NSTEMI', name: 'หน่วยหัวใจ', description: 'หน่วยดูแลผู้ป่วยโรคหัวใจ' },
      { id: 6, code: 'STROKE', name: 'หน่วยสมอง', description: 'หน่วยดูแลผู้ป่วยโรคหลอดเลือดสมอง' }
    ])
    const loading = ref(false)

    const getDepartmentIcon = (code) => {
      const iconMap = {
        'DM': 'fas fa-syringe fa-3x text-danger',
        'COPD': 'fas fa-lungs fa-3x text-info',
        'UGIB': 'fas fa-tint fa-3x text-danger',
        'STEMI_NSTEMI': 'fas fa-heartbeat fa-3x text-danger',
        'STROKE': 'fas fa-brain fa-3x text-primary',
        'TB': 'fas fa-bacteria fa-3x text-success',
        'CHEMO': 'fas fa-pills fa-3x text-purple',
        'HTN': 'fas fa-heart-pulse fa-3x text-danger',
        'SEPSIS': 'fas fa-virus fa-3x text-warning',
        'RHEUMATO': 'fas fa-bone fa-3x text-info',
        'OBESITY': 'fas fa-weight fa-3x text-secondary'
      }
      return iconMap[code] || 'fas fa-hospital fa-3x text-primary'
    }

    const isKidneyDept = (code) => {
      return code === 'CKD'
    }



    return {
      departments,
      loading,
      getDepartmentIcon,
      isKidneyDept
    }
  }
}
</script>

<style scoped>
.hover-card {
  transition: transform 0.2s ease-in-out;
}

.hover-card:hover {
  transform: translateY(-5px);
}

.department-icon {
  width: 80px;
  height: 80px;
  object-fit: contain;
}

.text-purple {
  color: #6f42c1 !important;
}
</style>