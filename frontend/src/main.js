import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'

// Import Bootstrap CSS and JS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Import Font Awesome
import '@fortawesome/fontawesome-free/css/all.min.css'

// Configure axios defaults
axios.defaults.baseURL = 'http://localhost:5000'
axios.defaults.withCredentials = true

const app = createApp(App)

// Use router
app.use(router)

// Make axios available globally
app.config.globalProperties.$http = axios

// Mount the app
app.mount('#app')
