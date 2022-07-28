from setuptools import find_packages, setup

setup(
    name="ContentEngineerStudio",
    version="0.0.1",
    description="A workflow optimization tool",
    packages=find_packages(),
    include_package_data=True,
    exclude_package_data={"": [".gitignore"]},
    setup_requires=["setuptools-git"],
    install_requires=[
        "pandas",
        'pandasgui',
        "numpy",
        "selenium",
        "xlwings",
        "bs4",
        "PyQt5",
        "mmh3",
        "setuptools",
        "appdirs",
        "pynput",
        "typing-extensions",
        "qtstylish>=0.1.2",
        "pywin32; platform_system=='Windows'",
    ],
)
