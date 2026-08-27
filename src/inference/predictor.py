import os
import logging
import numpy as np
from pathlib import Path
from typing import Tuple, List

import tensorflow as tf
import cv2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelPredictor:
    """Load and use trained model for inference."""

    def __init__(self, model_path: str = None):
        self.model = None
        self.model_path = model_path
        self.class_names = ['cat', 'dog']
        self.input_shape = (224, 224, 3)

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)

    def load_model(self, model_path: str):
        """Load TensorFlow model from disk."""
        try:
            self.model = tf.keras.models.load_model(model_path)
            self.model_path = model_path
            logger.info(f"Model loaded successfully from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model from {model_path}: {str(e)}")
            raise

    def is_ready(self) -> bool:
        """Check if model is loaded and ready."""
        return self.model is not None

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Load and preprocess image for inference.

        Args:
            image_path: Path to image file

        Returns:
            Preprocessed image array
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to read image: {image_path}")

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (self.input_shape[0], self.input_shape[1]))
            image = image.astype(np.float32) / 255.0

            return np.expand_dims(image, axis=0)
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {str(e)}")
            raise

    def predict_image(self, image_path: str) -> dict:
        """
        Predict class and confidence for an image.

        Args:
            image_path: Path to image file

        Returns:
            Dictionary with predictions
        """
        if not self.is_ready():
            raise ValueError("Model not loaded. Call load_model() first.")

        try:
            image = self.preprocess_image(image_path)
            probabilities = self.model.predict(image, verbose=0)

            predicted_class_idx = np.argmax(probabilities[0])
            predicted_class = self.class_names[predicted_class_idx]
            confidence = float(probabilities[0][predicted_class_idx])

            return {
                'class': predicted_class,
                'confidence': confidence,
                'probabilities': {
                    self.class_names[i]: float(probabilities[0][i])
                    for i in range(len(self.class_names))
                }
            }
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise

    def predict_array(self, images: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict for batch of images.

        Args:
            images: Array of preprocessed images

        Returns:
            Predicted classes and probabilities
        """
        if not self.is_ready():
            raise ValueError("Model not loaded")

        probabilities = self.model.predict(images, verbose=0)
        predicted_classes = np.argmax(probabilities, axis=1)

        return predicted_classes, probabilities

    def predict_batch_from_paths(self, image_paths: List[str]) -> list:
        """
        Predict for multiple image paths.

        Args:
            image_paths: List of image file paths

        Returns:
            List of prediction results
        """
        if not self.is_ready():
            raise ValueError("Model not loaded. Call load_model() first.")

        results = []

        for path in image_paths:
            try:
                result = self.predict_image(path)
                results.append({
                    'image_path': path,
                    'prediction': result
                })
            except Exception as e:
                logger.warning(f"Failed to predict for {path}: {str(e)}")
                results.append({
                    'image_path': path,
                    'error': str(e)
                })

        return results

    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        if not self.is_ready():
            return {'status': 'Model not loaded'}

        return {
            'status': 'Ready',
            'model_path': self.model_path,
            'input_shape': self.input_shape,
            'classes': self.class_names,
            'num_parameters': int(self.model.count_params())
        }