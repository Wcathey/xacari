import { create } from 'zustand';
import { WorkoutSession, PoseData, ExerciseType, WorkoutType } from '../types';
import apiService from '../services/api';
import websocketService from '../services/websocket';

/**
 * Workout Store
 *
 * Manages workout session state and real-time pose data
 */

interface WorkoutState {
  currentSession: WorkoutSession | null;
  isSessionActive: boolean;
  currentPoseData: PoseData | null;
  isConnected: boolean;
  feedbackMessages: string[];
  isLoading: boolean;
  error: string | null;

  // Actions
  createSession: (
    userId: string,
    workoutType: WorkoutType,
    exercises: ExerciseType[],
    reps?: number[]
  ) => Promise<void>;
  startSession: () => Promise<void>;
  pauseSession: () => Promise<void>;
  resumeSession: () => Promise<void>;
  completeSession: () => Promise<void>;
  nextExercise: () => Promise<void>;
  connectWebSocket: (userId: string) => Promise<void>;
  disconnectWebSocket: () => void;
  updatePoseData: (poseData: PoseData) => void;
  addFeedback: (message: string) => void;
  clearSession: () => void;
  clearError: () => void;
}

export const useWorkoutStore = create<WorkoutState>((set, get) => ({
  currentSession: null,
  isSessionActive: false,
  currentPoseData: null,
  isConnected: false,
  feedbackMessages: [],
  isLoading: false,
  error: null,

  createSession: async (userId, workoutType, exercises, reps) => {
    set({ isLoading: true, error: null });

    try {
      const response = await apiService.createWorkoutSession(
        userId,
        workoutType,
        exercises,
        reps
      );

      if (response.error) {
        throw new Error(response.error.message);
      }

      set({ currentSession: response.data });
    } catch (error: any) {
      console.error('Create session error:', error);
      set({ error: error.message });
    } finally {
      set({ isLoading: false });
    }
  },

  startSession: async () => {
    const { currentSession } = get();
    if (!currentSession) return;

    set({ isLoading: true, error: null });

    try {
      const response = await apiService.startWorkoutSession(currentSession.id);

      if (response.error) {
        throw new Error(response.error.message);
      }

      set({ currentSession: response.data, isSessionActive: true });

      // Send start command via WebSocket
      websocketService.sendCommand('start');
    } catch (error: any) {
      console.error('Start session error:', error);
      set({ error: error.message });
    } finally {
      set({ isLoading: false });
    }
  },

  pauseSession: async () => {
    const { currentSession } = get();
    if (!currentSession) return;

    set({ isLoading: true, error: null });

    try {
      const response = await apiService.pauseWorkoutSession(currentSession.id);

      if (response.error) {
        throw new Error(response.error.message);
      }

      set({ currentSession: response.data, isSessionActive: false });

      // Send pause command via WebSocket
      websocketService.sendCommand('pause');
    } catch (error: any) {
      console.error('Pause session error:', error);
      set({ error: error.message });
    } finally {
      set({ isLoading: false });
    }
  },

  resumeSession: async () => {
    const { currentSession } = get();
    if (!currentSession) return;

    set({ isLoading: true, error: null });

    try {
      const response = await apiService.resumeWorkoutSession(currentSession.id);

      if (response.error) {
        throw new Error(response.error.message);
      }

      set({ currentSession: response.data, isSessionActive: true });

      // Send resume command via WebSocket
      websocketService.sendCommand('resume');
    } catch (error: any) {
      console.error('Resume session error:', error);
      set({ error: error.message });
    } finally {
      set({ isLoading: false });
    }
  },

  completeSession: async () => {
    const { currentSession } = get();
    if (!currentSession) return;

    set({ isLoading: true, error: null });

    try {
      const response = await apiService.completeWorkoutSession(currentSession.id);

      if (response.error) {
        throw new Error(response.error.message);
      }

      set({ currentSession: response.data, isSessionActive: false });

      // Send stop command via WebSocket
      websocketService.sendCommand('stop');

      // Disconnect WebSocket
      get().disconnectWebSocket();
    } catch (error: any) {
      console.error('Complete session error:', error);
      set({ error: error.message });
    } finally {
      set({ isLoading: false });
    }
  },

  nextExercise: async () => {
    const { currentSession } = get();
    if (!currentSession) return;

    set({ isLoading: true, error: null });

    try {
      const response = await apiService.nextExercise(currentSession.id);

      if (response.error) {
        throw new Error(response.error.message);
      }

      set({ currentSession: response.data });
    } catch (error: any) {
      console.error('Next exercise error:', error);
      set({ error: error.message });
    } finally {
      set({ isLoading: false });
    }
  },

  connectWebSocket: async (userId: string) => {
    const { currentSession } = get();
    if (!currentSession) return;

    try {
      await websocketService.connect(currentSession.id, userId);

      // Subscribe to messages
      websocketService.onMessage((message) => {
        if (message.type === 'feedback') {
          get().addFeedback(message.message);
        }
      });

      set({ isConnected: true });
    } catch (error: any) {
      console.error('WebSocket connection error:', error);
      set({ error: error.message, isConnected: false });
    }
  },

  disconnectWebSocket: () => {
    websocketService.disconnect();
    set({ isConnected: false });
  },

  updatePoseData: (poseData: PoseData) => {
    set({ currentPoseData: poseData });

    // Send pose data via WebSocket if connected
    if (websocketService.isConnected()) {
      websocketService.sendPoseData(poseData);
    }
  },

  addFeedback: (message: string) => {
    set((state) => ({
      feedbackMessages: [...state.feedbackMessages, message],
    }));
  },

  clearSession: () => {
    get().disconnectWebSocket();
    set({
      currentSession: null,
      isSessionActive: false,
      currentPoseData: null,
      feedbackMessages: [],
    });
  },

  clearError: () => set({ error: null }),
}));

export default useWorkoutStore;
