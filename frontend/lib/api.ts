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
    (response) => response,
    (error) => {
        // Agar status 401 hai (Token expire ya invalid)
        if (error.response?.status === 401) {
            console.error("🔒 Auth Guard: Session invalid or expired.");
            
            // 1. Clear Zustand Store (Wallet khali karo)
            const { logout } = useAuthStore.getState();
            logout();

            // 2. Redirect to Login
            if (typeof window !== 'undefined') {
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    });

    export default api;