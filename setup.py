"""
Setup script for Codex-Arch
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="codex-arch",
    version="0.2.2",
    author="Codex-Arch Team",
    author_email="author@example.com",
    description="A tool for analyzing and visualizing code architecture",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/egouilliard/codex-arch",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "click>=8.0.0",
        "graphviz>=0.20.0",
        "tqdm>=4.66.0",
        "Flask>=2.3.0",
        "Flask-Cors>=4.0.0",
        "GitPython>=3.1.40",
    ],
    entry_points={
        "console_scripts": [
            "codex-arch=codex_arch.cli.main:main",
        ],
    },
) 