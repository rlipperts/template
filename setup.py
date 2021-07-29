import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

test_deps = [
    'pytest',
    'flake8',
    'pylint',
    'mypy',
]
extras = {
    'test': test_deps
}

setuptools.setup(
    name="template-loader",
    version="0.0.2",
    author="Ruben Lipperts",
    author_email="",
    description="Load json (and other) files and replace template values",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rlipperts/template",
    package_dir={'': 'src'},
    packages=['template_loader'],
    package_data={'template_loader': ['py.typed']},
    tests_require=test_deps,
    extras_require=extras,
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
