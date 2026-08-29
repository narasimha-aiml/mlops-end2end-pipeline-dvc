"""
Download and prepare Cats vs Dogs dataset from Kaggle via kagglehub.

This script downloads the dataset using kagglehub, then reorganizes it into
the data/raw/cats/ and data/raw/dogs/ structure expected by
src/data/preprocessing.py and dvc.yaml.

Requires: pip install kagglehub
"""

import shutil
import logging
from pathlib import Path

import kagglehub

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Common folder name variants this dataset (and similar ones) ship with.
CAT_DIR_CANDIDATES = ["Cat", "cat", "cats", "PetImages/Cat", "Cats"]
DOG_DIR_CANDIDATES = ["Dog", "dog", "dogs", "PetImages/Dog", "Dogs"]

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def _find_source_dir(download_path: Path, candidates: list) -> Path:
    """Search the downloaded dataset for the folder matching one of the candidates."""
    for candidate in candidates:
        p = download_path / candidate
        if p.exists() and p.is_dir():
            return p

    # Fallback: search recursively for any dir literally named one of the base names
    base_names = {c.split("/")[-1].lower() for c in candidates}
    for p in download_path.rglob("*"):
        if p.is_dir() and p.name.lower() in base_names:
            return p

    raise FileNotFoundError(
        f"Could not locate a source folder among {candidates} under {download_path}. "
        f"Inspect the download manually with: find '{download_path}' -maxdepth 3"
    )


def _copy_valid_images(src_dir: Path, dst_dir: Path, max_images: int = None) -> int:
    """Copy up to max_images valid, non-corrupt image files from src_dir to dst_dir.

    Args:
        src_dir: Source directory containing images
        dst_dir: Destination directory
        max_images: Maximum number of images to copy (None = copy all)

    Returns:
        Count of images copied
    """
    dst_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in sorted(src_dir.iterdir()):
        if max_images is not None and count >= max_images:
            break
        if f.is_file() and f.suffix.lower() in VALID_EXTENSIONS:
            # Skip zero-byte files; this dataset is known to have a couple of corrupt ones
            if f.stat().st_size == 0:
                logger.warning(f"Skipping zero-byte file: {f}")
                continue
            shutil.copy2(f, dst_dir / f.name)
            count += 1
    return count


def download_and_prepare_dataset(max_images_per_class: int = 600):
    """
    Download Cats vs Dogs dataset via kagglehub and prepare directory structure.

    Args:
        max_images_per_class: Cap on images copied per class, to keep local CPU
            training fast. Set to None to copy the full dataset (~12.5k per class).

    Returns:
        Tuple of (raw_dir, processed_dir) paths
    """
    data_dir = Path("data")
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Downloading dataset via kagglehub...")
    download_path = Path(
        kagglehub.dataset_download("bhavikjikadara/dog-and-cat-classification-dataset")
    )
    logger.info(f"Downloaded to: {download_path}")

    cat_src = _find_source_dir(download_path, CAT_DIR_CANDIDATES)
    dog_src = _find_source_dir(download_path, DOG_DIR_CANDIDATES)

    logger.info(f"Found cats at: {cat_src}")
    logger.info(f"Found dogs at: {dog_src}")

    n_cats = _copy_valid_images(cat_src, raw_dir / "cats", max_images_per_class)
    n_dogs = _copy_valid_images(dog_src, raw_dir / "dogs", max_images_per_class)

    logger.info(f"Copied {n_cats} cat images -> {raw_dir / 'cats'}")
    logger.info(f"Copied {n_dogs} dog images -> {raw_dir / 'dogs'}")
    logger.info(f"Raw data directory ready: {raw_dir}")

    return raw_dir, processed_dir


if __name__ == "__main__":
    # Adjust max_images_per_class here: None copies the full ~12.5k/class dataset.
    # 600/class (1,200 total) trains in a few minutes per epoch on CPU.
    raw_dir, processed_dir = download_and_prepare_dataset(max_images_per_class=600)
    logger.info(f"Raw data directory: {raw_dir}")
    logger.info(f"Processed data directory: {processed_dir}")