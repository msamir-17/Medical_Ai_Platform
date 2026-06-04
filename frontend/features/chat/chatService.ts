import api from '@/lib/api';

export const chatService = {
  /**
   * Sends a question to the backend RAG system
   * @param question - The user's medical query
   * @param reportId - Optional ID of the report related to the question
   */
  askQuestion: async (question: string, reportId?: string) => {
    const response = await api.post('/chat/query', {
      // ONLY send what the Backend needs. Token handles the ID!
      question: question,
      report_id: reportId
    });
    return response.data;
  },
};