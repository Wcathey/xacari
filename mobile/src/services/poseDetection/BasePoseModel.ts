import { PoseData, PoseDetectionModel } from '../../types';

/**
 * Base class for pose detection models
 * This abstraction allows us to easily swap between different models
 * (MoveNet, RTMPose, or your custom Xacari model)
 */
export abstract class BasePoseModel implements PoseDetectionModel {
  abstract name: string;
  protected isLoaded: boolean = false;

  /**
   * Load the model and initialize
   */
  abstract load(): Promise<void>;

  /**
   * Estimate pose from video frame
   * @param videoFrame - Camera frame (implementation specific)
   * @returns Pose data with keypoints
   */
  abstract estimatePose(videoFrame: any): Promise<PoseData | null>;

  /**
   * Clean up and dispose of model resources
   */
  abstract dispose(): void;

  /**
   * Check if model is loaded
   */
  isModelLoaded(): boolean {
    return this.isLoaded;
  }

  /**
   * Get model info
   */
  getModelInfo(): { name: string; loaded: boolean } {
    return {
      name: this.name,
      loaded: this.isLoaded,
    };
  }
}

export default BasePoseModel;
