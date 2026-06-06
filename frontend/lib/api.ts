    import axios from 'axios';
    import { useAuthStore } from '@/store/authStore';

    // const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

    // const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://samirk10-medical-ai-backend.hf.space';


    const api = axios.create({
        baseURL: API_BASE_URL,
        headers:{
            'content-type': 'application/json'
        },
    });

    api.interceptors.request.use((config) => {
    // Access the token from our Zustand store
    const token = useAuthStore.getState().token;
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
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