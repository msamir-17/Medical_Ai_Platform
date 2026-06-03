import api from '@/lib/api';

export const chatService = {
  /**
   * Sends a question to the backend RAG system
   * @param question - The user's medical query
   * @param userId - For now, we hardcode '123' until we add Auth
   * @param reportId - Optional ID of the report related to the question
   */
  askQuestion: async (question: string, userId: string ,reportId?: string) => {
    // This matches our FastAPI endpoint: POST /chat/query
    const response = await api.post('/chat/query', {
      user_id: userId,
      question: question,
      report_id: reportId
    });
    
    // Returns: { answer: "...", evidence: "..." }
    return response.data;
  },
};