from setuptools import find_packages, setup

setup(
    name='booking_service',
    version='0.0.1',
    license='MIT',
    author='Shimanskyi Vitaliy',
    author_email='vitashi02@gmail.com',
    description='Online hotel booking service',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
)
```

---

### `requirements.txt`
```
flake8==7.1.1
pytest==8.3.4
setuptools==58.0.4
tox==4.24.1
python-dotenv