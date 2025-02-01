"""
Package configuration and metadata for distribution.
Contains:
- Package dependencies
- Version information
- Project metadata (author, description, etc.)
- Entry points for CLI tools
"""

from setuptools import setup, find_packages

setup(
    name="stagediver",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "pydantic>=2.6.0",
    ],
)
