import api from '@/lib/api';

export const reportService = {
  // Function to upload the file to http://localhost:8000/reports/upload
  upload: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/reports/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

    // NEW: Function to get all reports
  getAll: async () => {
    const response = await api.get('/reports/');
    return response.data;
  },

  getById: async (id: string) => {
    const response = await api.get(`/reports/${id}`);
    return response.data;
  }

};

// Add this inside the reportService object
  