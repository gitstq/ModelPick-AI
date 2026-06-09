#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ModelPick-AI 安装脚本 / Setup script for ModelPick-AI
"""

from setuptools import setup, find_packages

setup(
    name="modelpick-ai",
    version="1.0.0",
    description="轻量级终端AI模型智能推荐引擎 / Lightweight Terminal AI Model Recommendation Engine",
    long_description=open("README.md", encoding="utf-8").read() if True else "",
    long_description_content_type="text/markdown",
    author="ModelPick-AI Team",
    license="MIT",
    python_requires=">=3.8",
    packages=find_packages(),
    package_data={
        "modelpick_ai": ["../data/models.json"],
    },
    include_package_data=True,
    install_requires=[
        "rich>=13.0.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "modelpick=modelpick_ai.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
