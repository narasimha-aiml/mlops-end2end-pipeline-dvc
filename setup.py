from setuptools import setup, find_packages

setup(
    name="cats-dogs-classifier",
    version="1.0.0",
    description="MLOps pipeline for binary image classification (Cats vs Dogs)",
    author="ML Team",
    author_email="ml@example.com",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "tensorflow>=2.14.0",
        "keras>=2.14.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "opencv-python>=4.8.0",
        "scikit-learn>=1.3.0",
        "matplotlib>=3.7.0",
        "fastapi>=0.103.0",
        "uvicorn>=0.23.0",
        "pydantic>=2.3.0",
        "pytest>=7.4.0",
        "dvc>=3.38.0",
        "mlflow>=2.9.0",
    ],
    extras_require={
        "dev": [
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "train-model=src.models.train:main",
        ],
    },
)
