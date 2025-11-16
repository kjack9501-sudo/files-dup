const API_BASE_URL = 'http://localhost:8000';

export interface UploadResponse {
  success: boolean;
  documentId?: string;
  filename?: string;
  chunksCount?: number;
  message?: string;
  error?: string;
}

export interface AskResponse {
  success: boolean;
  answer: string;
  sources?: Array<{
    filename: string;
    chunk_index: number;
    similarity: number;
  }>;
  contextUsed?: boolean;
  error?: string;
}

export interface StatisticsResponse {
  success: boolean;
  totalDocuments?: number;
  totalChunks?: number;
  embeddingDimension?: number;
  error?: string;
}

export interface SummaryResponse {
  success: boolean;
  summary?: string;
  documentCount?: number;
  totalChunks?: number;
  error?: string;
}

class ApiService {
  private isConnected: boolean = false;
  private connectionCheckPromise: Promise<boolean> | null = null;

  /**
   * Check if the backend is reachable
   */
  async checkHealth(): Promise<boolean> {
    try {
      // Create AbortController for timeout (more compatible than AbortSignal.timeout)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

      const response = await fetch(`${API_BASE_URL}/api/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const data = await response.json();
        this.isConnected = data.status === 'ok';
        return this.isConnected;
      }
      this.isConnected = false;
      return false;
    } catch (error: any) {
      this.isConnected = false;
      if (error.name === 'AbortError') {
        console.error('Health check timed out - backend may not be running');
      } else {
        console.error('Health check failed:', error);
      }
      return false;
    }
  }

  /**
   * Ensure backend is connected before making requests
   */
  private async ensureConnection(): Promise<void> {
    if (this.connectionCheckPromise) {
      const connected = await this.connectionCheckPromise;
      if (!connected) {
        throw new Error('Failed to connect to the API server. Please make sure the backend is running on http://localhost:8000');
      }
      return;
    }

    if (!this.isConnected) {
      this.connectionCheckPromise = this.checkHealth();
      const connected = await this.connectionCheckPromise;
      this.connectionCheckPromise = null;
      
      if (!connected) {
        throw new Error('Failed to connect to the API server. Please make sure the backend is running on http://localhost:8000');
      }
    }
  }

  private async makeRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
    // Check health before making request
    await this.ensureConnection();

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Don't set Content-Type for FormData (browser will set it with boundary)
    if (options?.body instanceof FormData) {
      delete headers['Content-Type'];
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers,
      ...options,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Request failed' }));
      throw new Error(error.error || error.detail || 'API request failed');
    }

    return response.json();
  }

  async uploadDocument(file: File): Promise<UploadResponse> {
    // Check health before upload
    await this.ensureConnection();

    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Upload failed' }));
      throw new Error(error.error || 'Upload failed');
    }

    return response.json();
  }

  async askQuestion(question: string): Promise<AskResponse> {
    return this.makeRequest<AskResponse>('/api/ask', {
      method: 'POST',
      body: JSON.stringify({ question }),
    });
  }

  async getStatistics(): Promise<StatisticsResponse> {
    return this.makeRequest<StatisticsResponse>('/api/statistics');
  }

  async generateSummary(type: string = 'comprehensive'): Promise<SummaryResponse> {
    return this.makeRequest<SummaryResponse>('/api/summary', {
      method: 'POST',
      body: JSON.stringify({ type }),
    });
  }

  async exportContent(content: string, format: string, filename: string): Promise<Blob> {
    // For now, we'll create a simple text blob
    // In a full implementation, you might want to add a backend endpoint for PDF/DOCX export
    if (format === 'txt' || format === 'text') {
      return new Blob([content], { type: 'text/plain' });
    } else if (format === 'markdown' || format === 'md') {
      return new Blob([content], { type: 'text/markdown' });
    } else {
      // Default to text
      return new Blob([content], { type: 'text/plain' });
    }
  }
}

export const apiService = new ApiService();

// Export health check function for use in components
export const checkBackendHealth = () => apiService.checkHealth();

