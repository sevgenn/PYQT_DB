from setuptools import setup, find_packages

setup(
    name="serv_mess",
    version="0.1",
    description="serv_mess",
    author="John Smith",
    author_email="sevgenn@gmail.com",
    packages=find_packages(),
    install_requires=["PyQt5", "sqlalchemy", "pycryptodome", "pycryptodomex"]
)
