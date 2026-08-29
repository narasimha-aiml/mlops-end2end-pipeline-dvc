import pytest
import numpy as np
import cv2
import tempfile
from pathlib import Path

from src.data.preprocessing import ImagePreprocessor


@pytest.fixture
def preprocessor():
    """Create preprocessor instance."""
    return ImagePreprocessor(target_size=(224, 224))


@pytest.fixture
def sample_image():
    """Create a sample test image."""
    with tempfile.TemporaryDirectory() as tmpdir:
        image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        image_path = Path(tmpdir) / "test_image.jpg"
        cv2.imwrite(str(image_path), image)
        yield str(image_path)


def test_image_preprocessor_initialization(preprocessor):
    """Test preprocessor initialization."""
    assert preprocessor.target_size == (224, 224)


def test_load_and_preprocess_image(preprocessor, sample_image):
    """Test loading and preprocessing a single image."""
    image = preprocessor.load_and_preprocess_image(sample_image, normalize=True)

    assert image.shape == (224, 224, 3)
    assert image.dtype == np.float32
    assert image.min() >= 0.0
    assert image.max() <= 1.0


def test_load_image_without_normalization(preprocessor, sample_image):
    """Test loading image without normalization."""
    image = preprocessor.load_and_preprocess_image(sample_image, normalize=False)

    assert image.shape == (224, 224, 3)
    assert image.dtype == np.uint8


def test_preprocess_image_file_not_found(preprocessor):
    """Test error handling for missing image."""
    with pytest.raises(FileNotFoundError):
        preprocessor.load_and_preprocess_image("nonexistent_image.jpg")


def test_preprocess_batch(preprocessor, sample_image):
    """Test preprocessing multiple images."""
    image_paths = [sample_image, sample_image]

    images, valid_paths = preprocessor.preprocess_batch(image_paths, normalize=True)

    assert len(valid_paths) == 2
    assert images.shape == (2, 224, 224, 3)
    assert images.dtype == np.float32


def test_validate_image_valid(preprocessor, sample_image):
    """Test validation of valid image."""
    is_valid = preprocessor.validate_image(sample_image)
    assert is_valid is True


def test_validate_image_invalid_path(preprocessor):
    """Test validation of non-existent image."""
    is_valid = preprocessor.validate_image("nonexistent.jpg")
    assert is_valid is False


def test_preprocess_batch_empty(preprocessor):
    """Test error handling for empty batch."""
    with pytest.raises(ValueError):
        preprocessor.preprocess_batch([])


def test_image_resizing(preprocessor):
    """Test that images are correctly resized."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_image = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
        image_path = Path(tmpdir) / "large_image.jpg"
        cv2.imwrite(str(image_path), original_image)

        preprocessed = preprocessor.load_and_preprocess_image(str(image_path))

        assert preprocessed.shape == (224, 224, 3)
