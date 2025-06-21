from setuptools import setup, find_packages
import os

# 读取README.md文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements.txt文
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith('#')]

setup(
    name="aitern",
    version="0.1.0",
    author="AItern Team",
    author_email="your.email@example.com",
    description="基于测试驱动开发的AI代码探索工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AItern",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "aitern=src.cli.main:main",
        ],
    },
) 