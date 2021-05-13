from setuptools import setup, find_packages


REQUIRES = []
with open('requirements.txt') as f:
    for line in f:
        line, _, _ = line.partition('#')
        line = line.strip()
        if ';' in line:
            requirement, _, specifier = line.partition(';')
            for_specifier = []
            for_specifier.append(requirement)
        else:
            REQUIRES.append(line)


setup(
    name='funpay-undercutter',
    version='0.1',
    install_requires=REQUIRES,
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    url='https://github.com/UnderAnder/funpay-undercutter',
    license='GPLv3',
    author='UnderAnder',
    description='Undercut game currency offers at https://funpay.ru',
)
