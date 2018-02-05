all:
	@echo "Argument needed:"
	@echo "  clean - Clean the project"
	@echo "  env2 - Create python2 virtual environment"
	@echo "  env3 - Create python3 virtual environment"
	@echo "  tests - Run all tests"
	@echo "  tests2 - Run tests with python2"
	@echo "  tests3 - Run tests with python3"

clean:
	@rm -rf build/ *.egg-info *.egg
	@pyenv uninstall -f yset-27 || True
	@pyenv uninstall -f yset-36 || True
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -delete

env2:
	@pyenv virtualenv -f 2.7.14 yset-27 || True
	PYENV_VERSION=yset-27 pip install --upgrade pip setuptools pbr
	PYENV_VERSION=yset-27 pip install -e .

tests2: env2
	PYENV_VERSION=yset-27 python setup.py test

env3:
	@pyenv virtualenv -f 3.6.3 yset-36 || True
	PYENV_VERSION=yset-36 pip install --upgrade pip setuptools pbr
	PYENV_VERSION=yset-36 pip install -e .

tests3: env3
	PYENV_VERSION=yset-36 python setup.py test

tests: tests2 tests3

build:
	PYENV_VERSION=yset-36 python setup.py build
