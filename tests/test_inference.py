import pytest
import numpy as np
import tempfile
from pathlib import Path

from src.inference.predictor import ModelPredictor


@pytest.fixture
def predictor():
    """Create predictor instance without loading a model."""
    return ModelPredictor()


def test_predictor_initialization(predictor):
    """Test predictor initialization."""
    assert predictor.model is None
    assert predictor.class_names == ['cat', 'dog']
    assert predictor.input_shape == (224, 224, 3)


def test_is_not_ready(predictor):
    """Test is_ready() when model not loaded."""
    assert predictor.is_ready() is False


def test_get_model_info_not_loaded(predictor):
    """Test getting model info when not loaded."""
    info = predictor.get_model_info()
    assert info['status'] == 'Model not loaded'


def test_predict_without_model(predictor):
    """Test prediction fails without model."""
    with pytest.raises(ValueError):
        predictor.predict_image("dummy_path.jpg")


def test_preprocess_nonexistent_image(predictor):
    """Test preprocessing fails for non-existent image."""
    with pytest.raises(FileNotFoundError):
        predictor.preprocess_image("nonexistent.jpg")


def test_predict_batch_without_model(predictor):
    """Test batch prediction fails without model."""
    images = np.random.randn(2, 224, 224, 3)

    with pytest.raises(ValueError):
        predictor.predict_array(images)


def test_predict_batch_from_paths_without_model(predictor):
    """Test batch path prediction fails without model."""
    with pytest.raises(ValueError):
        predictor.predict_batch_from_paths(["image1.jpg", "image2.jpg"])


def test_class_names(predictor):
    """Test class names are correct."""
    assert len(predictor.class_names) == 2
    assert 'cat' in predictor.class_names
    assert 'dog' in predictor.class_names


def test_input_shape(predictor):
    """Test input shape dimensions."""
    assert predictor.input_shape == (224, 224, 3)
    assert len(predictor.input_shape) == 3
