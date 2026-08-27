import os
import cv2
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImagePreprocessor:
    """Preprocess images for CNN training."""

    def __init__(self, target_size=(224, 224)):
        self.target_size = target_size

    def load_and_preprocess_image(self, image_path, normalize=True):
        """
        Load and preprocess a single image.

        Args:
            image_path: Path to image file
            normalize: Whether to normalize to [0, 1]

        Returns:
            Preprocessed image array
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        try:
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, self.target_size)

            if normalize:
                image = image.astype(np.float32) / 255.0

            return image
        except Exception as e:
            logger.error(f"Error processing {image_path}: {str(e)}")
            raise

    def preprocess_batch(self, image_paths, normalize=True):
        """
        Preprocess multiple images.

        Args:
            image_paths: List of image file paths
            normalize: Whether to normalize

        Returns:
            Array of preprocessed images
        """
        images = []
        valid_paths = []

        for path in image_paths:
            try:
                img = self.load_and_preprocess_image(path, normalize)
                images.append(img)
                valid_paths.append(path)
            except Exception as e:
                logger.warning(f"Skipped {path}: {str(e)}")
                continue

        if not images:
            raise ValueError("No valid images to process")

        return np.array(images), valid_paths

    def validate_image(self, image_path):
        """
        Validate if image can be loaded and has correct format.

        Args:
            image_path: Path to image file

        Returns:
            True if valid, False otherwise
        """
        try:
            if not os.path.exists(image_path):
                return False

            image = cv2.imread(str(image_path))
            if image is None:
                return False

            if len(image.shape) != 3 or image.shape[2] != 3:
                return False

            return True
        except:
            return False


def create_data_splits(data_dir, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1):
    """
    Create train/val/test splits from image directory.

    Args:
        data_dir: Directory containing image subdirectories (cats/, dogs/)
        train_ratio: Training split ratio
        val_ratio: Validation split ratio
        test_ratio: Test split ratio

    Returns:
        Dictionary with split indices
    """
    import random

    train_ratio = 0.8
    val_ratio = 0.1
    test_ratio = 0.1

    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1.0"

    data_path = Path(data_dir)
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    splits = {'train': [], 'val': [], 'test': []}

    for class_dir in data_path.iterdir():
        if class_dir.is_dir():
            images = list(class_dir.glob('*.jpg')) + list(class_dir.glob('*.png'))

            random.shuffle(images)
            n = len(images)

            train_end = int(n * train_ratio)
            val_end = train_end + int(n * val_ratio)

            splits['train'].extend(images[:train_end])
            splits['val'].extend(images[train_end:val_end])
            splits['test'].extend(images[val_end:])

    logger.info(f"Created splits - Train: {len(splits['train'])}, "
                f"Val: {len(splits['val'])}, Test: {len(splits['test'])}")

    return splits


def _label_for_path(image_path: Path) -> int:
    """Infer binary label from the parent directory name (cat=0, dog=1)."""
    parent = image_path.parent.name.lower()
    if parent.startswith('cat'):
        return 0
    if parent.startswith('dog'):
        return 1
    raise ValueError(f"Cannot infer label from path: {image_path}")


def run_pipeline(raw_dir='data/raw', processed_dir='data/processed', target_size=(224, 224)):
    """
    Full prepare stage: split raw images into train/val/test, preprocess each,
    and save as .npy arrays under processed_dir. This is what dvc.yaml's
    `prepare` stage actually executes.
    """
    preprocessor = ImagePreprocessor(target_size=target_size)
    splits = create_data_splits(raw_dir)

    out_dir = Path(processed_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for split_name, paths in splits.items():
        if not paths:
            logger.warning(f"No images found for split '{split_name}', skipping")
            continue

        images, valid_paths = preprocessor.preprocess_batch(paths, normalize=True)
        labels = np.array([_label_for_path(p) for p in valid_paths], dtype=np.int64)

        np.save(out_dir / f"X_{split_name}.npy", images)
        np.save(out_dir / f"y_{split_name}.npy", labels)

        logger.info(f"Saved {split_name}: X={images.shape}, y={labels.shape} -> {out_dir}")

    logger.info(f"Preprocessing complete. Output written to {processed_dir}/")


if __name__ == "__main__":
    run_pipeline()