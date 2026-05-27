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
};