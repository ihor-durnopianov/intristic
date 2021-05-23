# -*- coding: utf-8 -*-
"""Setup script."""


from setuptools import setup, find_packages
from os import path


setup(
    name='intristic',  # Required

    version='0.0.1',  # Required

    description='One-off tool to plot crypto OHLC over intristic time',  # Optional

    py_modules=["intristic"],  # Required

    python_requires='>=3.6',

    install_requires=[],  # Optional

    entry_points={  # Optional
        'console_scripts': [
            'display-intristic=intristic:main',
        ],
    },
)
