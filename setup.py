import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="browser-history",  # Replace with your own username
    version="0.3.1",
    author="Samyak Sarnayak",
    author_email="samyak201@gmail.com",
    description="A python module to extract browser history",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pesos/browser-history",
    packages=setuptools.find_packages(exclude=["tests"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": ["browser-history=browser_history.cli:main"],
    },
)
