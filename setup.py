from setuptools import setup, find_packages

setup(
    name="stashpoint",
    version="0.1.0",
    description="A CLI tool for saving and restoring named sets of environment variables.",
    author="Your Name",
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
        ]
    },
    entry_points={
        "console_scripts": [
            "stashpoint=stashpoint.cli:cli",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
)
