"""
Setup configuration for SpectralZK.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="spectralzk",
    version="0.1.0",
    author="Daniel Skryseth",
    description="Experimental zero-knowledge proofs from aperiodic tilings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Danielskry/SpectralZK",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0.0",
            "flake8>=3.8.0",
        ],
    },
)
