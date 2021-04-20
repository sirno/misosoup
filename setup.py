import setuptools

from setuptools import find_packages

setuptools.setup(
    name="misosoup",
    packages=find_packages(),
    version="0.2.0",
    author="Nicolas Ochsner",
    author_email="ochsnern@student.ethz.ch",
    scripts=[
        "scripts/misosoup",
        "scripts/taste_soup",
        "scripts/filter_soup",
        "scripts/select_ingredients",
    ],
    install_requires=[
        "pyyaml",
        "pandas",
        "tqdm",
    ],
    extras_require={"dev": ["black", "pylint", "pytest", "tox"]},
)
