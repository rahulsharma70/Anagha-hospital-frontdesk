// API Base URL
const API_BASE = '/api';

// Store authentication token
let authToken = localStorage.getItem('authToken');

// Set auth token for API calls
function setAuthToken(token) {
    authToken = token;
    localStorage.setItem('authToken', token);
}

// Remove auth token
function removeAuthToken() {
    authToken = null;
    localStorage.removeItem('authToken');
}

// Make authenticated API request
async function apiRequest(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const response = await fetch(`${API_BASE}${url}`, {
        ...options,
        headers
    });
    
    if (response.status === 401) {
        // Unauthorized - redirect to login
        removeAuthToken();
        window.location.href = '/login';
        return;
    }
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'An error occurred');
    }
    
    return response.json();
}

// Login function
async function login(mobile, password) {
    const response = await apiRequest('/users/login', {
        method: 'POST',
        body: JSON.stringify({ mobile, password })
    });
    
    setAuthToken(response.access_token);
    return response.user;
}

// Register function
async function register(userData) {
    return await apiRequest('/users/register', {
        method: 'POST',
        body: JSON.stringify(userData)
    });
}

// Get current user
async function getCurrentUser() {
    return await apiRequest('/users/me');
}

// Book appointment
async function bookAppointment(appointmentData) {
    return await apiRequest('/appointments/book', {
        method: 'POST',
        body: JSON.stringify(appointmentData)
    });
}

// Get my appointments
async function getMyAppointments() {
    return await apiRequest('/appointments/my-appointments');
}

// Get available slots
async function getAvailableSlots(doctorId, date) {
    return await apiRequest(`/appointments/available-slots?doctor_id=${doctorId}&appointment_date=${date}`);
}

// Book operation
async function bookOperation(operationData) {
    return await apiRequest('/operations/book', {
        method: 'POST',
        body: JSON.stringify(operationData)
    });
}

// Get my operations
async function getMyOperations() {
    return await apiRequest('/operations/my-operations');
}

// Get all doctors
async function getDoctors() {
    return await apiRequest('/users/doctors');
}

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
}

// Format time slot
function formatTimeSlot(timeSlot) {
    const [hours, minutes] = timeSlot.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Initialize time slots
function initializeTimeSlots(containerId, selectedSlot = null, disabledSlots = []) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const morningSlots = [
        '09:30', '10:00', '10:30', '11:00', '11:30', '12:00',
        '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30'
    ];
    
    const eveningSlots = [
        '18:00', '18:30', '19:00', '19:30', '20:00', '20:30'
    ];
    
    container.innerHTML = '';
    
    // Morning section
    const morningDiv = document.createElement('div');
    morningDiv.innerHTML = '<h4 style="margin-bottom: 1rem; color: var(--text-dark);">Morning Slots (9:30 AM - 3:30 PM)</h4>';
    const morningGrid = document.createElement('div');
    morningGrid.className = 'time-slots';
    
    morningSlots.forEach(slot => {
        const slotDiv = document.createElement('div');
        slotDiv.className = 'time-slot';
        slotDiv.textContent = formatTimeSlot(slot);
        slotDiv.dataset.slot = slot;
        
        if (disabledSlots.includes(slot)) {
            slotDiv.classList.add('disabled');
        } else {
            slotDiv.addEventListener('click', () => {
                document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
                slotDiv.classList.add('selected');
                if (document.getElementById('time_slot')) {
                    document.getElementById('time_slot').value = slot;
                }
            });
        }
        
        if (selectedSlot === slot) {
            slotDiv.classList.add('selected');
        }
        
        morningGrid.appendChild(slotDiv);
    });
    
    morningDiv.appendChild(morningGrid);
    container.appendChild(morningDiv);
    
    // Evening section
    const eveningDiv = document.createElement('div');
    eveningDiv.style.marginTop = '2rem';
    eveningDiv.innerHTML = '<h4 style="margin-bottom: 1rem; color: var(--text-dark);">Evening Slots (6:00 PM - 8:30 PM)</h4>';
    const eveningGrid = document.createElement('div');
    eveningGrid.className = 'time-slots';
    
    eveningSlots.forEach(slot => {
        const slotDiv = document.createElement('div');
        slotDiv.className = 'time-slot';
        slotDiv.textContent = formatTimeSlot(slot);
        slotDiv.dataset.slot = slot;
        
        if (disabledSlots.includes(slot)) {
            slotDiv.classList.add('disabled');
        } else {
            slotDiv.addEventListener('click', () => {
                document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
                slotDiv.classList.add('selected');
                if (document.getElementById('time_slot')) {
                    document.getElementById('time_slot').value = slot;
                }
            });
        }
        
        if (selectedSlot === slot) {
            slotDiv.classList.add('selected');
        }
        
        eveningGrid.appendChild(slotDiv);
    });
    
    eveningDiv.appendChild(eveningGrid);
    container.appendChild(eveningDiv);
}

