import { useState, useCallback } from 'react';
import { chatApi } from '@/lib/api';
import { ChatMessage, ChatConversation, ChatResponse } from '@/lib/types';
import { toast } from 'sonner';

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversations, setConversations] = useState<ChatConversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  // Send a message to the AI assistant
  const sendMessage = useCallback(async (message: string) => {
    if (!message.trim()) return;

    setIsLoading(true);
    setIsTyping(true);

    try {
      // Add user message to UI immediately
      const userMessage: ChatMessage = {
        id: Date.now(), // Temporary ID
        conversation_id: currentConversationId || 0,
        role: 'user',
        content: message,
        created_at: new Date().toISOString()
      };

      setMessages(prev => [...prev, userMessage]);

      // Send to API
      const response = await chatApi.sendMessage(message, currentConversationId || undefined);
      
      // Update conversation ID if this is a new conversation
      if (!currentConversationId) {
        setCurrentConversationId(response.data.conversation_id);
      }

      // Add AI response to UI
      const aiMessage: ChatMessage = {
        id: Date.now() + 1, // Temporary ID
        conversation_id: response.data.conversation_id,
        role: 'assistant',
        content: response.data.response,
        created_at: new Date().toISOString()
      };

      setMessages(prev => [...prev, aiMessage]);

      // Refresh conversations list
      await loadConversations();

      if (response.data.error) {
        toast.error('AI encountered an error processing your request');
      }

    } catch (error: any) {
      console.error('Error sending message:', error);
      toast.error(error.response?.data?.error || 'Failed to send message');
      
      // Remove the user message if there was an error
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  }, [currentConversationId]);

  // Load all conversations for the user
  const loadConversations = useCallback(async () => {
    try {
      const response = await chatApi.getConversations();
      setConversations(response.data);
    } catch (error: any) {
      console.error('Error loading conversations:', error);
      toast.error('Failed to load conversations');
    }
  }, []);

  // Load a specific conversation
  const loadConversation = useCallback(async (conversationId: number) => {
    try {
      const response = await chatApi.getConversation(conversationId);
      setMessages(response.data.messages);
      setCurrentConversationId(conversationId);
    } catch (error: any) {
      console.error('Error loading conversation:', error);
      toast.error('Failed to load conversation');
    }
  }, []);

  // Start a new conversation
  const startNewConversation = useCallback(() => {
    setMessages([]);
    setCurrentConversationId(null);
  }, []);

  // Clear current conversation (but keep it in history)
  const clearCurrentConversation = useCallback(() => {
    setMessages([]);
    setCurrentConversationId(null);
  }, []);

  // Delete a conversation
  const deleteConversation = useCallback(async (conversationId: number) => {
    try {
      await chatApi.deleteConversation(conversationId);
      await loadConversations();
      
      // If we're viewing the deleted conversation, clear it
      if (currentConversationId === conversationId) {
        startNewConversation();
      }
      
      toast.success('Conversation deleted');
    } catch (error: any) {
      console.error('Error deleting conversation:', error);
      toast.error('Failed to delete conversation');
    }
  }, [currentConversationId, loadConversations, startNewConversation]);

  // Save/unsave a conversation
  const toggleSaveConversation = useCallback(async (conversationId: number, isSaved: boolean) => {
    try {
      if (isSaved) {
        await chatApi.unsaveConversation(conversationId);
        toast.success('Conversation unsaved');
      } else {
        await chatApi.saveConversation(conversationId);
        toast.success('Conversation saved');
      }
      await loadConversations();
    } catch (error: any) {
      console.error('Error toggling save conversation:', error);
      toast.error('Failed to update conversation');
    }
  }, [loadConversations]);

  return {
    messages,
    conversations,
    currentConversationId,
    isLoading,
    isTyping,
    sendMessage,
    loadConversations,
    loadConversation,
    startNewConversation,
    clearCurrentConversation,
    deleteConversation,
    toggleSaveConversation
  };
}
