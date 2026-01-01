/**
 * API Service Layer
 * Handles all communication with the backend FastAPI server
 */

// API Base URL - use environment variable or default to current host
const API_BASE_URL = import.meta.env.VITE_API_URL || (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000');

// Helper function to get auth token from localStorage
const getAuthToken = (): string | null => {
  return localStorage.getItem('authToken');
};

// Helper function to set auth token
export const setAuthToken = (token: string): void => {
  localStorage.setItem('authToken', token);
};

// Helper function to remove auth token
export const removeAuthToken = (): void => {
  localStorage.removeItem('authToken');
};

// Generic API request function
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { detail: `HTTP error! status: ${response.status}` };
      }
      throw new Error(errorData.detail || errorData.message || `HTTP error! status: ${response.status}`);
    }

    // Handle empty responses
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return response.json();
    } else {
      return response.text() as any;
    }
  } catch (error) {
    // Re-throw if it's already an Error with a message
    if (error instanceof Error) {
      // Handle specific network errors
      if (error.message.includes('ECONNREFUSED') || error.message.includes('Failed to fetch')) {
        throw new Error('Cannot connect to server. Please ensure the backend server is running on port 3000.');
      }
      throw error;
    }
    // Handle network errors
    throw new Error('Failed to fetch. Please check your connection and ensure the server is running.');
  }
}

// Authentication API
export const authAPI = {
  // Login with mobile and password
  login: async (mobile: string, password: string) => {
    return apiRequest<{ access_token: string; token_type: string; user: any }>('/api/users/login', {
      method: 'POST',
      body: JSON.stringify({ mobile, password }),
    });
  },

  // Register new user
  register: async (userData: {
    name: string;
    mobile: string;
    password: string;
    role?: string;
    email?: string;
    city?: string;
    state?: string;
    specialty?: string;
  }) => {
    return apiRequest<{ access_token: string; token_type: string; user: any; message?: string }>('/api/users/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  // Get current user info
  getCurrentUser: async () => {
    return apiRequest<any>('/api/users/me');
  },
};

// Hospitals API
export const hospitalsAPI = {
  // Get all approved hospitals
  getApproved: async () => {
    return apiRequest<any[]>('/api/hospitals/approved');
  },

  // Register new hospital
  register: async (hospitalData: any) => {
    return apiRequest<any>('/api/hospitals/register', {
      method: 'POST',
      body: JSON.stringify(hospitalData),
    });
  },

  // Get hospital by ID
  getById: async (id: number) => {
    return apiRequest<any>(`/api/hospitals/${id}`);
  },
};

// Doctors API
export const doctorsAPI = {
  // Get all doctors
  getAll: async () => {
    return apiRequest<any[]>('/api/users/doctors');
  },
};

// Appointments API
export const appointmentsAPI = {
  // Book appointment
  book: async (appointmentData: {
    doctor_id: number;
    date: string;
    time_slot: string;
    reason?: string;
  }) => {
    return apiRequest<any>('/api/appointments/book', {
      method: 'POST',
      body: JSON.stringify(appointmentData),
    });
  },

  // Get my appointments
  getMyAppointments: async () => {
    return apiRequest<any[]>('/api/appointments/my-appointments');
  },

  // Get doctor appointments
  getDoctorAppointments: async () => {
    return apiRequest<any[]>('/api/appointments/doctor-appointments');
  },

  // Get available slots
  getAvailableSlots: async (doctorId: number, date: string) => {
    return apiRequest<{
      doctor_id: number;
      doctor_name: string;
      date: string;
      available_slots: string[];
      booked_slots: string[];
    }>(`/api/appointments/available-slots?doctor_id=${doctorId}&date=${date}`);
  },

  // Confirm appointment
  confirm: async (appointmentId: number) => {
    return apiRequest<any>(`/api/appointments/${appointmentId}/confirm`, {
      method: 'PUT',
    });
  },

  // Cancel appointment
  cancel: async (appointmentId: number) => {
    return apiRequest<any>(`/api/appointments/${appointmentId}/cancel`, {
      method: 'PUT',
    });
  },

  // Mark as visited
  markVisited: async (appointmentId: number) => {
    return apiRequest<any>(`/api/appointments/${appointmentId}/mark-visited`, {
      method: 'PUT',
    });
  },
};

// Operations API
export const operationsAPI = {
  // Book operation
  book: async (operationData: {
    hospital_id: number;
    doctor_id: number;
    date: string;  // Fixed: was 'operation_date', matches actual usage and backend
    specialty: string;
    notes?: string;  // Fixed: was 'reason', matches backend schema
  }) => {
    return apiRequest<any>('/api/operations/book', {
      method: 'POST',
      body: JSON.stringify(operationData),
    });
  },

  // Get my operations
  getMyOperations: async () => {
    return apiRequest<any[]>('/api/operations/my-operations');
  },

  // Get doctor operations
  getDoctorOperations: async () => {
    return apiRequest<any[]>('/api/operations/doctor-operations');
  },

  // Confirm operation
  confirm: async (operationId: number) => {
    return apiRequest<any>(`/api/operations/${operationId}/confirm`, {
      method: 'PUT',
    });
  },

  // Cancel operation
  cancel: async (operationId: number) => {
    return apiRequest<any>(`/api/operations/${operationId}/cancel`, {
      method: 'PUT',
    });
  },
};

// Payments API
export const paymentsAPI = {
  // Create payment order
  createOrder: async (amount: number, hospitalId?: number) => {
    return apiRequest<any>('/api/payments/create', {  // Fixed: was '/create-order'
      method: 'POST',
      body: JSON.stringify({ amount, hospital_id: hospitalId }),
    });
  },

  // Create hospital registration payment order
  createHospitalRegistrationOrder: async (planName: string, amount: number) => {
    return apiRequest<any>('/api/payments/create-order-hospital', {
      method: 'POST',
      body: JSON.stringify({
        hospital_registration: true,
        plan_name: planName,
        amount: amount,
        currency: 'INR',
      }),
    });
  },

  // Verify payment
  verifyPayment: async (paymentId: number) => {  // Fixed: payment_id in URL path, not body
    return apiRequest<any>(`/api/payments/verify/${paymentId}`, {
      method: 'POST',
    });
  },

  // Get payment status
  getPaymentStatus: async (paymentId: number) => {
    return apiRequest<any>(`/api/payments/${paymentId}/status`);
  },
};

// Admin API
export const adminAPI = {
  // Get pricing (admin only)
  getPricing: async () => {
    return apiRequest<any>('/api/admin/pricing');
  },

  // Get public pricing (for hospital registration)
  getPublicPricing: async () => {
    return apiRequest<any>('/api/admin/pricing/public');
  },

  // Update pricing
  updatePricing: async (pricingData: any) => {
    return apiRequest<any>('/api/admin/update-pricing', {
      method: 'POST',
      body: JSON.stringify(pricingData),
    });
  },
};
