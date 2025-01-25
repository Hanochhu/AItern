from setuptools import setup, find_packages

setup(
    name="aitern",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai",
        "pyyaml",
        "gitpython",
        "pygithub",
    ],
    python_requires=">=3.7",
) 