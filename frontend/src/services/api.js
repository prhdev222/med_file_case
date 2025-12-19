// API service layer for backend communication
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Helper method to make HTTP requests
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      credentials: 'include', // Include cookies for session management
      ...options,
    };

    if (config.body && typeof config.body === 'object') {
      config.body = JSON.stringify(config.body);
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Authentication methods
  async login(username, password) {
    return this.request('/api/admin/auth/login', {
      method: 'POST',
      body: { username, password },
    });
  }

  async logout() {
    return this.request('/api/admin/auth/logout', {
      method: 'POST',
    });
  }

  async getCurrentUser() {
    return this.request('/api/admin/auth/user');
  }

  // Dashboard methods
  async getDashboardStats() {
    return this.request('/api/admin/dashboard/stats');
  }

  async getDashboardActivities() {
    return this.request('/api/admin/dashboard/activities');
  }

  // Department methods
  async getDepartments() {
    return this.request('/api/admin/departments');
  }

  async createDepartment(departmentData) {
    return this.request('/api/admin/departments', {
      method: 'POST',
      body: departmentData,
    });
  }

  async updateDepartment(id, departmentData) {
    return this.request(`/api/admin/departments/${id}`, {
      method: 'PUT',
      body: departmentData,
    });
  }

  async deleteDepartment(id) {
    return this.request(`/api/admin/departments/${id}`, {
      method: 'DELETE',
    });
  }

  // Contact methods
  async getContacts(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/api/admin/contacts?${queryString}` : '/api/admin/contacts';
    return this.request(endpoint);
  }

  async createContact(contactData) {
    return this.request('/api/admin/contacts', {
      method: 'POST',
      body: contactData,
    });
  }

  async updateContact(id, contactData) {
    return this.request(`/api/admin/contacts/${id}`, {
      method: 'PUT',
      body: contactData,
    });
  }

  async deleteContact(id) {
    return this.request(`/api/admin/contacts/${id}`, {
      method: 'DELETE',
    });
  }

  // Case methods
  async getCases(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/api/admin/cases?${queryString}` : '/api/admin/cases';
    return this.request(endpoint);
  }

  async createCase(caseData) {
    return this.request('/api/admin/cases', {
      method: 'POST',
      body: caseData,
    });
  }

  async updateCase(id, caseData) {
    return this.request(`/api/admin/cases/${id}`, {
      method: 'PUT',
      body: caseData,
    });
  }

  async deleteCase(id) {
    return this.request(`/api/admin/cases/${id}`, {
      method: 'DELETE',
    });
  }

  // Backup methods
  async getBackups() {
    return this.request('/api/admin/backups');
  }

  async createBackup() {
    return this.request('/api/admin/backups/create', {
      method: 'POST',
    });
  }

  async downloadBackup(filename) {
    const url = `${this.baseURL}/api/admin/backups/${filename}/download`;
    const response = await fetch(url, {
      credentials: 'include',
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || 'Download failed');
    }

    return response.blob();
  }

  async restoreBackup(filename) {
    return this.request(`/api/admin/backups/${filename}/restore`, {
      method: 'POST',
    });
  }

  async deleteBackup(filename) {
    return this.request(`/api/admin/backups/${filename}`, {
      method: 'DELETE',
    });
  }

  // Public API methods (for non-authenticated requests)
  async getPublicStats() {
    return this.request('/api/public/stats');
  }

  async getRecentPatientsPublic() {
    return this.request('/api/notifications/recent-patients-public');
  }
}

// Create and export a singleton instance
const apiService = new ApiService();
export default apiService;

// Also export the class for testing purposes
export { ApiService };