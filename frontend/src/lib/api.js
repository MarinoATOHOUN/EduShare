/**
 * API Service for PDF Course Sharing Platform
 * Developed by Marino ATOHOUN
 */

import axios from 'axios';

// const API_BASE_URL = 'https://8000-ip0z7m5i0g6fdklzgg6jk-6b0cb216.manus.computer/api';
const API_BASE_URL = 'https://rinoatohoun.pythonanywhere.com/api';
// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {
            refresh: refreshToken,
          });
          
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: async (username, password) => {
    const response = await api.post('/auth/login/', { username, password });
    const { access, refresh } = response.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },

  getCurrentUser: async () => {
    const response = await api.get('/profile/');
    return response.data;
  },

  updateProfile: async (profileData) => {
    const response = await api.patch('/profile/', profileData);
    return response.data;
  },
};

// Courses API
export const coursesAPI = {
  getAll: async () => {
    const response = await api.get('/courses/');
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/courses/${id}/`);
    return response.data;
  },

  create: async (courseData) => {
    const response = await api.post('/courses/', courseData);
    return response.data;
  },

  update: async (id, courseData) => {
    const response = await api.patch(`/courses/${id}/`, courseData);
    return response.data;
  },

  delete: async (id) => {
    const response = await api.delete(`/courses/${id}/`);
    return response.data;
  },
};

// Documents API
export const documentsAPI = {
  getAll: async (params = {}) => {
    const response = await api.get('/documents/', { params });
    return response.data;
  },

  getById: async (id) => {
    const response = await api.get(`/documents/${id}/`);
    return response.data;
  },

  create: async (documentData) => {
    const formData = new FormData();
    Object.keys(documentData).forEach(key => {
      formData.append(key, documentData[key]);
    });
    
    const response = await api.post('/documents/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  update: async (id, documentData) => {
    const response = await api.patch(`/documents/${id}/`, documentData);
    return response.data;
  },

  delete: async (id) => {
    const response = await api.delete(`/documents/${id}/`);
    return response.data;
  },

  download: (id) => {
    return `${API_BASE_URL}/documents/${id}/download/`;
  },

  preview: (id) => {
    return `${API_BASE_URL}/documents/${id}/preview/`;
  },

  getUserDocuments: async () => {
    const response = await api.get('/my-documents/');
    return response.data;
  },
};

// Stats API
export const statsAPI = {
  getStats: async () => {
    const response = await api.get('/stats/');
    return response.data;
  },
};

export default api;

