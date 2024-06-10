# setup.py
from setuptools import setup, find_packages

__version__="0.1.3"
setup(
    name='cocotbext_hyperbus',
    version=__version__,
    description='A cocotb extension for HyperBus controllers',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Meet Sangani',
    author_email='your.email@example.com',
    url='https://github.com/meeeeet/cocotbext_hyperbus',
    packages=find_packages(),
    install_requires=[
        'cocotb',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries',
    ],
    python_requires='>=3.8',
)

