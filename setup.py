from setuptools import setup, find_packages
import pathlib

# Read the contents of your README file
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name='nicegui-router',
    version='0.0.4',
    description='File-based routing and theming for NiceGUI, bringing structured navigation and consistent page themes',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Pablo Schaffner',
    author_email='pablo@puntorigen.com',
    url='https://github.com/puntorigen/nicegui-router',
    packages=find_packages(),
    install_requires=[
        'nicegui>=2.3.0',
        'PyJWT==2.9.0',
        'uvicorn==0.34.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
