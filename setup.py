from setuptools import setup, find_packages

setup(
    name="swiggy-analyzer",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.31.0",
        "httpx>=0.24.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "questionary>=2.0.0",
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.0",
        "pyyaml>=6.0",
        "keyring>=24.0.0",
        "cryptography>=41.0.0",
        "authlib>=1.2.0",
        "loguru>=0.7.0",
    ],
    entry_points={
        "console_scripts": [
            "swiggy-analyzer=swiggy_analyzer.cli.main:cli",
        ],
    },
    python_requires=">=3.9",
)
