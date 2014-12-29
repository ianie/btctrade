from setuptools import setup, find_packages

setup(
    name='btctrade',
    version='0.1.0',
    packages=find_packages(),
    # scripts=['feemodel-cli', 'feemodel-txmempool'],
    install_requires=[
        'requests'
    ]
)