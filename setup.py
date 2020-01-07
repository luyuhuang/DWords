from DWords.version import VERSION
from setuptools import setup, find_packages
import os

here = os.path.dirname(__file__)

with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

with open(os.path.join(here, "requirements.txt")) as f:
    install_requires = [
        line.strip() for line in f.readlines() if not line.startswith("#")
    ]

setup(
    name="DWords",
    version=VERSION,
    description="Show words as Danmaku in the screen to helps you remember them.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luyuhuang/DWords",
    keywords="danmaku words english-learning vocabulary pyqt5",
    license="GPLv3",
    author="Luyu Huang",
    author_email="luyu_huang@foxmail.com",

    packages=find_packages(),
    install_requires=install_requires,
    package_data={
        '': ['img/*', 'data/*.db']
    },
    entry_points={
        "gui_scripts": ["DWords=DWords.__main__:main"]
    },

    classifiers=[
        "Intended Audience :: Education",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
    ]
)
