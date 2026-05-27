import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers:{
        'content-type': 'application/json'
    },
});

// Response interceptor for easy error handling

api.interceptors.response.use(
    (Response) => Response,
    (error) => {
        console.error('API Error:', error.response?.data?.detail || error.message);
        return Promise.reject(error);
    }
);

export default api;