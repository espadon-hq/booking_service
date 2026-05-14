from setuptools import find_packages, setup

setup(
    name='booking_service',
    version='1.0.0',
    license='MIT',
    author='Shimanskyi Vitaliy',
    author_email='vitashi02@gmail.com',
    description='Online hotel booking service',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
)
