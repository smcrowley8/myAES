# readme

Table of contents:

- [Installation](#Installation)
- [Guide](#Guide)
- [Developement](#Developement)

# Installation
requires python 3.8 or above

```bash
pip install poetry
poetry add <PROJECT-NAME>
```

# Guide

<!-- Subsection explaining how to use package -->

# Developement
To develop, install dependencies and enable pre-commit hooks

Requirements:
    - pyenv
    - python3.9.7 +



```bash
#assuming in pyenv
pip install -U pip
pip install poetry pre-commit
poetry install
pre-commit install -t pre-commit -t pre-push
```

To run tests:

```bash
poetry run pytest
```
