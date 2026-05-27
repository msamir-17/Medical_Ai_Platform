import api from '@/lib/api';

export const chatService = {
  /**
   * Sends a question to the backend RAG system
   * @param question - The user's medical query
   * @param userId - For now, we hardcode '123' until we add Auth
   */
  askQuestion: async (question: string, userId: string = "123") => {
    // This matches our FastAPI endpoint: POST /chat/query
    const response = await api.post('/chat/query', {
      user_id: userId,
      question: question,
    });
    
    // Returns: { answer: "...", evidence: "..." }
    return response.data;
  },
};