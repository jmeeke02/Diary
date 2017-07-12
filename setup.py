from setuptools import setup

__version__ = "0.0.1"

setup(
    name = "Diary",
    version = __version__,
    description= "AWS Secret Manager",
    license ="MIT",
    packages=["diary"],
    install_requires=[
        'boto3',
    ],
    entry_points={
        'console_scripts': ['diary=diary.main:main'],
    }
)