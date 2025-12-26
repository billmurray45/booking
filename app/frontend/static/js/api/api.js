/**
 * API Client
 * Handles all API requests with automatic token refresh
 */

const API_BASE_URL = '/api/v1';

// Generic API request with automatic token refresh
async function apiRequest(url, options = {}) {
    // Add default headers
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    // Add auth token if available
    const accessToken = getAccessToken();
    if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
    }

    // Make the request
    let response = await fetch(url, {
        ...options,
        headers
    });

    // If token expired (401), try to refresh
    if (response.status === 401 && getRefreshToken()) {
        const refreshed = await refreshAccessToken();
        if (refreshed) {
            // Retry the original request with new token
            headers['Authorization'] = `Bearer ${getAccessToken()}`;
            response = await fetch(url, {
                ...options,
                headers
            });
        } else {
            // Refresh failed, redirect to login
            clearTokens();
            window.location.href = '/login/';
            return null;
        }
    }

    return response;
}

// Refresh access token
async function refreshAccessToken() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
        return false;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ refresh: refreshToken })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.access);
            return true;
        } else {
            return false;
        }
    } catch (error) {
        console.error('Token refresh error:', error);
        return false;
    }
}

// API Methods
const API = {
    // Authentication
    register: async (userData) => {
        return await apiRequest(`${API_BASE_URL}/auth/register/`, {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    },

    login: async (credentials) => {
        return await apiRequest(`${API_BASE_URL}/auth/login/`, {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
    },

    logout: async (refreshToken) => {
        return await apiRequest(`${API_BASE_URL}/auth/logout/`, {
            method: 'POST',
            body: JSON.stringify({ refresh: refreshToken })
        });
    },

    // User Profile
    getProfile: async () => {
        return await apiRequest(`${API_BASE_URL}/auth/me/`);
    },

    updateProfile: async (userData) => {
        return await apiRequest(`${API_BASE_URL}/auth/me/`, {
            method: 'PATCH',
            body: JSON.stringify(userData)
        });
    },

    changePassword: async (passwordData) => {
        return await apiRequest(`${API_BASE_URL}/auth/change-password/`, {
            method: 'POST',
            body: JSON.stringify(passwordData)
        });
    }
};
