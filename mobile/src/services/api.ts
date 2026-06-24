import CONFIG from '../config';
import {
  WorkoutSession,
  WorkoutSessionCreateRequest,
  ApiResponse,
  WorkoutType,
  ExerciseType,
} from '../types';

/**
 * API Service for HTTP requests to backend
 *
 * Handles all REST API communication with the FastAPI backend
 */

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = CONFIG.API.BASE_URL;
  }

  /**
   * Generic fetch wrapper with error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        return {
          error: {
            message: data.message || 'Request failed',
            code: response.status.toString(),
            details: data.details,
          },
        };
      }

      return { data };
    } catch (error: any) {
      console.error('API request failed:', error);
      return {
        error: {
          message: error.message || 'Network error',
          details: error,
        },
      };
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<ApiResponse<{ status: string; service: string }>> {
    return this.request('/health');
  }

  /**
   * Get API version
   */
  async getVersion(): Promise<ApiResponse<any>> {
    return this.request('/version');
  }

  /**
   * Create a new workout session
   */
  async createWorkoutSession(
    userId: string,
    workoutType: WorkoutType,
    exercises: ExerciseType[],
    repsPerExercise?: number[]
  ): Promise<ApiResponse<WorkoutSession>> {
    const payload: WorkoutSessionCreateRequest = {
      user_id: userId,
      workout_type: workoutType,
      exercises,
      reps_per_exercise: repsPerExercise,
    };

    return this.request('/api/workout/sessions', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  /**
   * Get workout session by ID
   */
  async getWorkoutSession(sessionId: string): Promise<ApiResponse<WorkoutSession>> {
    return this.request(`/api/workout/sessions/${sessionId}`);
  }

  /**
   * Start a workout session
   */
  async startWorkoutSession(sessionId: string): Promise<ApiResponse<WorkoutSession>> {
    return this.request(`/api/workout/sessions/${sessionId}/start`, {
      method: 'POST',
    });
  }

  /**
   * Pause a workout session
   */
  async pauseWorkoutSession(sessionId: string): Promise<ApiResponse<WorkoutSession>> {
    return this.request(`/api/workout/sessions/${sessionId}/pause`, {
      method: 'POST',
    });
  }

  /**
   * Resume a workout session
   */
  async resumeWorkoutSession(sessionId: string): Promise<ApiResponse<WorkoutSession>> {
    return this.request(`/api/workout/sessions/${sessionId}/resume`, {
      method: 'POST',
    });
  }

  /**
   * Complete a workout session
   */
  async completeWorkoutSession(
    sessionId: string
  ): Promise<ApiResponse<WorkoutSession>> {
    return this.request(`/api/workout/sessions/${sessionId}/complete`, {
      method: 'POST',
    });
  }

  /**
   * Move to next exercise
   */
  async nextExercise(sessionId: string): Promise<ApiResponse<WorkoutSession>> {
    return this.request(`/api/workout/sessions/${sessionId}/next`, {
      method: 'POST',
    });
  }

  /**
   * Get all workout sessions for a user
   */
  async getUserWorkoutSessions(
    userId: string
  ): Promise<ApiResponse<WorkoutSession[]>> {
    return this.request(`/api/workout/sessions/user/${userId}`);
  }

  /**
   * Get WebSocket status
   */
  async getWebSocketStatus(): Promise<
    ApiResponse<{ active_connections: number; active_sessions: string[] }>
  > {
    return this.request('/ws/status');
  }
}

// Singleton instance
const apiService = new ApiService();
export default apiService;
