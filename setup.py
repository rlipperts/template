import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="template-loader",
    version="0.0.2",
    author="Ruben Lipperts",
    author_email="",
    description="Load json (and other) files and replace template values",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rlipperts/template",
    packages=setuptools.find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pyyaml',
        'toml',
    ],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing",
    ],
    python_requires='~=3.9',
)
