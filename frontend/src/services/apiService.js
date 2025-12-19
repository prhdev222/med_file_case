// API Service Layer for communicating with Flask backend
const API_BASE_URL = 'http://127.0.0.1:5000/api'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  // Get JWT token from storage
  getToken() {
    return localStorage.getItem('jwt_token') || sessionStorage.getItem('jwt_token')
  }

  // Set JWT token in storage
  setToken(token, remember = false) {
    const storage = remember ? localStorage : sessionStorage
    storage.setItem('jwt_token', token)
  }

  // Remove JWT token from storage
  removeToken() {
    localStorage.removeItem('jwt_token')
    sessionStorage.removeItem('jwt_token')
  }

  // Helper method to make HTTP requests
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const token = this.getToken()
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
      },
      credentials: 'include', // Include cookies for session management
      ...options
    }

    try {
      const response = await fetch(url, config)
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`)
      }
      
      return data
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // Authentication methods
  async login(username, password, remember = false) {
    const response = await this.request('/admin/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    })
    
    if (response.success && response.token) {
      this.setToken(response.token, remember)
    }
    
    return response
  }

  async logout() {
    try {
      await this.request('/admin/auth/logout', {
        method: 'POST'
      })
    } catch (error) {
      // Even if the API call fails, we should remove the token
      console.warn('Logout API call failed:', error)
    } finally {
      this.removeToken()
    }
  }

  // Department methods
  async getDepartments() {
    return this.request('/admin/departments')
  }

  // Activity methods
  async getActivities() {
    return this.request('/admin/activities')
  }

  async deleteActivity(id) {
    return this.request(`/admin/activities/${id}`, {
      method: 'DELETE'
    })
  }

  // Knowledge methods
  async getKnowledge() {
    return this.request('/admin/knowledge')
  }

  async deleteKnowledge(id) {
    return this.request(`/admin/knowledge/${id}`, {
      method: 'DELETE'
    })
  }

  // Guidelines methods
  async getGuidelines() {
    return this.request('/admin/guidelines')
  }

  async deleteGuideline(id) {
    return this.request(`/admin/guidelines/${id}`, {
      method: 'DELETE'
    })
  }

  // Users methods
  async getUsers() {
    return this.request('/admin/users')
  }

  async createUser(userData) {
    return this.request('/admin/users', {
      method: 'POST',
      body: JSON.stringify(userData)
    })
  }

  async deleteUser(id) {
    return this.request(`/admin/users/${id}`, {
      method: 'DELETE'
    })
  }

  async getCurrentUser() {
    return this.request('/auth/me')
  }

  async createDepartment(departmentData) {
    return this.request('/admin/departments', {
      method: 'POST',
      body: JSON.stringify(departmentData)
    })
  }

  async updateDepartment(id, departmentData) {
    return this.request(`/admin/departments/${id}`, {
      method: 'PUT',
      body: JSON.stringify(departmentData)
    })
  }

  async deleteDepartment(id) {
    return this.request(`/admin/departments/${id}`, {
      method: 'DELETE'
    })
  }

  // Contact methods
  async getContacts() {
    return this.request('/admin/contacts')
  }

  async createContact(contactData) {
    return this.request('/admin/contacts', {
      method: 'POST',
      body: JSON.stringify(contactData)
    })
  }

  async updateContact(id, contactData) {
    return this.request(`/admin/contacts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(contactData)
    })
  }

  async deleteContact(id) {
    return this.request(`/admin/contacts/${id}`, {
      method: 'DELETE'
    })
  }

  // Case methods
  async getCases() {
    return this.request('/admin/cases')
  }

  async createCase(caseData) {
    return this.request('/admin/cases', {
      method: 'POST',
      body: JSON.stringify(caseData)
    })
  }

  async updateCase(id, caseData) {
    return this.request(`/admin/cases/${id}`, {
      method: 'PUT',
      body: JSON.stringify(caseData)
    })
  }

  async deleteCase(id) {
    return this.request(`/admin/cases/${id}`, {
      method: 'DELETE'
    })
  }

  // Backup methods
  async getBackups() {
    return this.request('/admin/backups')
  }

  async createBackup() {
    return this.request('/admin/backups', {
      method: 'POST'
    })
  }

  async restoreBackup(backupId) {
    return this.request(`/admin/backups/${backupId}/restore`, {
      method: 'POST'
    })
  }

  async deleteBackup(backupId) {
    return this.request(`/admin/backups/${backupId}`, {
      method: 'DELETE'
    })
  }

  // Public API methods
  async getPublicStats() {
    return this.request('/public/stats')
  }

  async getRecentPatients() {
    return this.request('/notifications/recent-patients')
  }

  async getRecentPatientsPublic() {
    return this.request('/notifications/recent-patients-public')
  }
}

// Create and export a singleton instance
export const apiService = new ApiService()
export default apiService