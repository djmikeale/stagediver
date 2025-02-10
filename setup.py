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
    description="Festival lineup tracking and schedule management tool",
    author="Mikael Thorup",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "pydantic>=2.6.0",
        "streamlit>=1.31.0",
        "ics>=0.7.2",
        "pytz>=2023.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "stagediver-scrape=stagediver.cli.scrape_lineup:main",
            "stagediver-history=stagediver.cli.generate_lineup_history:main",
        ]
    },
)
