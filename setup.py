from setuptools import setup, find_packages

setup(
    name='funpay-client',
    version='v0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    url='https://github.com/UnderAnder/funpay-client',
    license='GPLv3',
    author='UnderAnder',
    description='Client for funpay.ru',
)
