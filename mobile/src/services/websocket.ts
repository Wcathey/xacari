import CONFIG from '../config';
import {
  WebSocketMessage,
  PoseDataMessage,
  CommandMessage,
  FeedbackMessage,
  PoseData,
} from '../types';

/**
 * WebSocket Service for real-time communication with backend
 *
 * Handles:
 * - Connection management
 * - Sending pose data
 * - Receiving feedback
 * - Reconnection logic
 */

type MessageHandler = (message: WebSocketMessage) => void;

export class WebSocketService {
  private ws: WebSocket | null = null;
  private sessionId: string | null = null;
  private userId: string | null = null;
  private messageHandlers: Set<MessageHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private pingInterval: NodeJS.Timeout | null = null;

  /**
   * Connect to WebSocket server
   */
  connect(sessionId: string, userId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.sessionId = sessionId;
      this.userId = userId;

      const wsUrl = `${CONFIG.API.WS_URL}/${sessionId}?user_id=${userId}`;
      console.log('🔌 Connecting to WebSocket:', wsUrl);

      try {
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('✅ WebSocket connected');
          this.reconnectAttempts = 0;
          this.reconnectDelay = 1000;
          this.startPingInterval();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('❌ WebSocket error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('🔌 WebSocket disconnected');
          this.stopPingInterval();
          this.attemptReconnect();
        };
      } catch (error) {
        console.error('Failed to create WebSocket:', error);
        reject(error);
      }
    });
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect(): void {
    this.stopPingInterval();

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }

    this.sessionId = null;
    this.userId = null;
    this.reconnectAttempts = 0;
  }

  /**
   * Send pose data to backend
   */
  sendPoseData(poseData: PoseData): void {
    const message: PoseDataMessage = {
      type: 'pose_data',
      ...poseData,
    };

    this.send(message);
  }

  /**
   * Send command to backend
   */
  sendCommand(command: 'start' | 'pause' | 'resume' | 'stop'): void {
    const message: CommandMessage = {
      type: 'command',
      command,
    };

    this.send(message);
  }

  /**
   * Send ping to keep connection alive
   */
  private sendPing(): void {
    this.send({
      type: 'ping',
      timestamp: new Date().toISOString(),
    });
  }

  /**
   * Generic send message
   */
  private send(message: WebSocketMessage): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected, cannot send message');
      return;
    }

    try {
      this.ws.send(JSON.stringify(message));
    } catch (error) {
      console.error('Failed to send WebSocket message:', error);
    }
  }

  /**
   * Handle incoming messages
   */
  private handleMessage(message: WebSocketMessage): void {
    // Notify all registered handlers
    this.messageHandlers.forEach((handler) => {
      try {
        handler(message);
      } catch (error) {
        console.error('Message handler error:', error);
      }
    });
  }

  /**
   * Subscribe to WebSocket messages
   */
  onMessage(handler: MessageHandler): () => void {
    this.messageHandlers.add(handler);

    // Return unsubscribe function
    return () => {
      this.messageHandlers.delete(handler);
    };
  }

  /**
   * Attempt to reconnect
   */
  private attemptReconnect(): void {
    if (!this.sessionId || !this.userId) {
      return; // Don't reconnect if explicitly disconnected
    }

    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      if (this.sessionId && this.userId) {
        this.connect(this.sessionId, this.userId).catch((error) => {
          console.error('Reconnection failed:', error);
        });
      }
    }, delay);
  }

  /**
   * Start ping interval to keep connection alive
   */
  private startPingInterval(): void {
    this.stopPingInterval();

    this.pingInterval = setInterval(() => {
      this.sendPing();
    }, 30000); // Ping every 30 seconds
  }

  /**
   * Stop ping interval
   */
  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Get connection state
   */
  getState(): 'connecting' | 'open' | 'closing' | 'closed' {
    if (!this.ws) return 'closed';

    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'open';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'closed';
      default:
        return 'closed';
    }
  }
}

// Singleton instance
const websocketService = new WebSocketService();
export default websocketService;
