import { BasePoseModel } from './BasePoseModel';
import { XacariPoseModel } from './XacariPoseModel';
import CONFIG from '../../config';

/**
 * Pose Detection Service
 *
 * Factory for creating pose detection models.
 * This abstraction allows easy switching between different models.
 */

let currentModel: BasePoseModel | null = null;

export class PoseDetectionService {
  /**
   * Get or create the current pose detection model
   */
  static async getModel(): Promise<BasePoseModel> {
    if (currentModel && currentModel.isModelLoaded()) {
      return currentModel;
    }

    // Create model based on configuration
    // For now, always use Xacari model (placeholder for RTMPose)
    currentModel = new XacariPoseModel();

    await currentModel.load();
    return currentModel;
  }

  /**
   * Dispose current model and free resources
   */
  static disposeModel(): void {
    if (currentModel) {
      currentModel.dispose();
      currentModel = null;
    }
  }

  /**
   * Get current model info without loading
   */
  static getCurrentModelInfo(): { name: string; loaded: boolean } | null {
    if (!currentModel) return null;
    return currentModel.getModelInfo();
  }
}

export { BasePoseModel, XacariPoseModel };
export default PoseDetectionService;
