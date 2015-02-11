all:
	@echo "Argument needed:"
	@echo "  clean - Clean the project"
	@echo "  env2 - Create python2 virtual environment"
	@echo "  env3 - Create python3 virtual environment"
	@echo "  tests - Run all tests"
	@echo "  tests2 - Run tests with python2"
	@echo "  tests3 - Run tests with python3"

clean:
	@rm -rf env2/ env3/ build/ *.egg-info *.egg
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -delete

env2:
	virtualenv-2.7 env2
	env2/bin/pip install -e .

tests2: env2
	env2/bin/python setup.py test

env3:
	virtualenv-3.4 env3
	env3/bin/pip install -e .

tests3: env3
	env3/bin/python setup.py test

tests: tests2 tests3

build:
	env3/bin/python setup.py build
