# setup.py
from setuptools import setup, find_packages

__version__="0.2.0"
setup(
    name='cocotbext_hyperbus',
    version=__version__,
    description='A cocotb extension for HyperBus controllers',
    keywords=['cocotb', 'HyperBus'],
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Meet Sangani',
    author_email='meet.sangani@outlook.com',
    license = 'MIT',
    url='https://github.com/meeeeet/cocotbext_hyperbus',
    packages=find_packages(),
    install_requires=[
        'cocotb',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: cocotb',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
    ],
    python_requires='>=3.8',
)

