from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="prgavi",
    version="1.0.0",
    author="PRGAVI Contributors",
    author_email="",
    description="Professional gaming video creator with AI narration and beautiful captions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/PRGAVI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Content Creators",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "prgavi=shortscreator:main",
        ],
    },
    keywords="gaming video creator AI narration captions steam shorts",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/PRGAVI/issues",
        "Source": "https://github.com/yourusername/PRGAVI",
        "Documentation": "https://github.com/yourusername/PRGAVI/blob/main/README.md",
    },
) 