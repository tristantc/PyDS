from setuptools import setup

# Read the long description from README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="PyDS",
    version="0.1.0",
    description="Parse SVG datasheet curves and extract plot coordinates.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Dr. Anatolii Tcai",
    url="https://github.com/HereIsAnatolii/PyDS",
    project_urls={
        "Source": "https://github.com/HereIsAnatolii/PyDS",
        "Issues": "https://github.com/HereIsAnatolii/PyDS/issues",
    },
    license="MIT",
    python_requires=">=3.8",
    install_requires=[
        "svgpathtools",
        "numpy",
        "matplotlib",
    ],
    # Provide both the original single-file module and the convenience package
    py_modules=["PyDS"],
    packages=["pyds"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords=["svg", "datasheet", "curves", "extract", "numpy", "matplotlib"],
)
