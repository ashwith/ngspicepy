from setuptools import setup, find_packages

requires = ["numpy"]

setup(
        name="ngspicepy",
        version="1.0",
        description="Python library for ngspice.",
        url="https://github.com/ashwith/ngspicepy",
        author="Ashwith Rego, Jyoti Dhakal",
        author_email="ashwith@gmail.com, jyoti.dhakal09@gmail.com",
        license="GPL3",
        install_requires=requires,
        packages=find_packages(),
        )
