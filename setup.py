try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = open('README.rst').read()

requirements = [
    "PyYAML",
]

test_requirements = [
    "nose",
    "mock",
]

setup(
    name='yamlsettings',
    version='0.2.3',
    description='Yaml Settings Configuration Module',
    long_description=readme,
    author='Kyle James Walker',
    author_email='KyleJamesWalker@gmail.com',
    url='https://github.com/KyleJamesWalker/yamlsettings',
    packages=['yamlsettings'],
    package_dir={'yamlsettings':
                 'yamlsettings'},
    include_package_data=True,
    install_requires=requirements,
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
