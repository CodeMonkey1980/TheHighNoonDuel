from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

setup(
    name='The High Noon Duel',
    version='0.1.0',
    description='A reaction speed game set in the old old west.',
    long_descriptio=readme,
    author='Sebastiaan Vreeken',
    author_email='s.j.w.vreeken@hotmail.com',
    url='https://github.com/CodeMonkey1980/TheHighNoonDuel',
    install_requires=[
        'pygame==2.0.0.dev6',
        'cx-freeze==6.2'
    ],
    packages=find_packages(exclude=('tests', 'docs'))
)
