import api from '@/lib/api';

export const chatService = {
  askQuestion: async (question: string, userId: string = "123") => {
    const response = await api.post('/chat/query', {
      user_id: userId,
      question: question,
    });
    return response.data; // This will return { answer: "...", evidence: "..." }
  },
};