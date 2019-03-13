debug ?= false

ifeq ($(debug),true)
	test_extra_params := -- --pudb
else
	test_extra_params :=
endif

clean:
	@rm -rf build/ .tox/ .eggs/ .pytest_cache/ *.egg-info *.egg coverage.xml
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -delete

test3:
	-tox -e py37 $(test_extra_params)

test:
	tox -p auto

build:
	PYENV_VERSION=ys-dev python setup.py build
