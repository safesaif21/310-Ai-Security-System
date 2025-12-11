/**
 * API utility functions with automatic authentication
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Get auth token from localStorage
 */
const getToken = () => {
    return localStorage.getItem('auth_token');
};

/**
 * Authenticated fetch wrapper
 * Automatically adds Authorization header if token exists
 */
export const apiFetch = async (endpoint, options = {}) => {
    const token = getToken();

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    // Add auth token if available
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        ...options,
        headers,
    };

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

        // Handle 401 Unauthorized - redirect to login
        if (response.status === 401) {
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user');
            window.location.href = '/';
            throw new Error('Session expired. Please login again.');
        }

        return response;
    } catch (error) {
        console.error('API fetch error:', error);
        throw error;
    }
};

/**
 * Helper for GET requests
 */
export const apiGet = async (endpoint) => {
    const response = await apiFetch(endpoint);
    return response.json();
};

/**
 * Helper for POST requests
 */
export const apiPost = async (endpoint, data) => {
    const response = await apiFetch(endpoint, {
        method: 'POST',
        body: JSON.stringify(data),
    });
    return response.json();
};

/**
 * Helper for PUT requests
 */
export const apiPut = async (endpoint, data) => {
    const response = await apiFetch(endpoint, {
        method: 'PUT',
        body: JSON.stringify(data),
    });
    return response.json();
};

/**
 * Helper for DELETE requests
 */
export const apiDelete = async (endpoint) => {
    const response = await apiFetch(endpoint, {
        method: 'DELETE',
    });
    return response.json();
};

export default {
    fetch: apiFetch,
    get: apiGet,
    post: apiPost,
    put: apiPut,
    delete: apiDelete,
};
