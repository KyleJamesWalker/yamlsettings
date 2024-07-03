try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = open('README.rst').read()

requirements = {
    "package": [
        "PyYAML>=5",
        "six",
    ],
    "test": [
        "nose",
        "mock",
        "pytest",
        "pytest-mock",
    ],
    "setup": [
        "pytest-runner",
    ],
}

requirements.update(all=sorted(set().union(*requirements.values())))

setup(
    name='yamlsettings',
    version='2.1.1',
    description='Yaml Settings Configuration Module',
    long_description=readme,
    author='Kyle James Walker',
    author_email='KyleJamesWalker@gmail.com',
    url='https://github.com/KyleJamesWalker/yamlsettings',
    packages=['yamlsettings', 'yamlsettings.extensions'],
    package_dir={'yamlsettings':
                 'yamlsettings'},
    include_package_data=True,
    install_requires=requirements['package'],
    extras_require=requirements,
    setup_requires=requirements['setup'],
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    test_suite='tests',
    tests_require=requirements['test'],
)
