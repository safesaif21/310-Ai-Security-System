/**
 * API utility functions for the Microservices architecture
 */

const getBaseUrl = (port) => {
    return `http://${window.location.hostname}:${port}`;
};

// Helper to clean up empty strings or undefined from env vars
const getDefinedOrFallback = (envValue, fallback) => {
    if (!envValue || envValue === "" || envValue === "undefined") return fallback;
    return envValue;
};

export const SERVICES = {
    AUTH: getDefinedOrFallback(import.meta.env.VITE_AUTH_API_URL, getBaseUrl(8040)),
    CAMERA: getDefinedOrFallback(import.meta.env.VITE_CAMERA_API_URL, getBaseUrl(8041)),
    ANALYSIS: getDefinedOrFallback(import.meta.env.VITE_ANALYSIS_API_URL, getBaseUrl(8042)),
    DVR: getDefinedOrFallback(import.meta.env.VITE_DVR_API_URL, getBaseUrl(8043)),
};

console.log('Security System Service URLs:', SERVICES);

/**
 * Get auth token from localStorage
 */
const getToken = () => {
    return localStorage.getItem('auth_token');
};

/**
 * Authenticated fetch wrapper
 */
export const apiFetch = async (serviceBaseUrl, endpoint, options = {}) => {
    const token = getToken();

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
        ...options,
        headers,
    };

    try {
        const response = await fetch(`${serviceBaseUrl}${endpoint}`, config);

        if (response.status === 401 && serviceBaseUrl === SERVICES.AUTH) {
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user');
            window.location.href = '/';
            throw new Error('Session expired. Please login again.');
        }

        return response;
    } catch (error) {
        console.error(`API fetch error (${serviceBaseUrl}):`, error);
        throw error;
    }
};

const createHelper = (serviceBaseUrl) => ({
    get: (endpoint) => apiFetch(serviceBaseUrl, endpoint).then(r => r.json()),
    post: (endpoint, data) => apiFetch(serviceBaseUrl, endpoint, {
        method: 'POST',
        body: data ? JSON.stringify(data) : undefined
    }).then(r => r.json()),
    put: (endpoint, data) => apiFetch(serviceBaseUrl, endpoint, {
        method: 'PUT',
        body: data ? JSON.stringify(data) : undefined
    }).then(r => r.json()),
    delete: (endpoint) => apiFetch(serviceBaseUrl, endpoint, { method: 'DELETE' }).then(r => r.json()),
});

export const authApi = createHelper(SERVICES.AUTH);
export const cameraApi = createHelper(SERVICES.CAMERA);
export const analysisApi = createHelper(SERVICES.ANALYSIS);
export const dvrApi = createHelper(SERVICES.DVR);

export default {
    auth: authApi,
    camera: cameraApi,
    analysis: analysisApi,
    dvr: dvrApi,
    SERVICES
};
