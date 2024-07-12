debug ?= false

ifeq ($(debug),true)
	test_extra_params := -- --pudb
else
	test_extra_params :=
endif

clean:
	@rm -rf build/ .eggs/ .pytest_cache/ *.egg-info *.egg coverage.xml
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -delete

create_envs:
	- pyenv virtualenv 3.12.2 ys-312
	PYENV_VERSION=ys-312 pip install -e ".[all]"

	- pyenv virtualenv 3.8.2 ys-38
	PYENV_VERSION=ys-38 pip install -e ".[all]"

test:
	PYENV_VERSION=ys-38 pytest
	PYENV_VERSION=ys-312 pytest

build:
	PYENV_VERSION=ys-312 python setup.py build
