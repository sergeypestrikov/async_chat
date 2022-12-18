from setuptools import setup, find_packages

setup(
    name='my_chat_project',
    version='0.0.1',
    description='my_chat_project',
    author='Sergey Pestrikov',
    author_email='gambarus@mail.ru',
    packages=find_packages(),
    install_requires=['PyQt6', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
    )