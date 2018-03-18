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

pyenv_envs:
	pip install -U detox tox tox-pyenv
	CFLAGS="-I$(shell brew --prefix openssl)/include" LDFLAGS="-L$(shell brew --prefix openssl)/lib" pyenv install 2.7.14
	CFLAGS="-I$(shell brew --prefix openssl)/include" LDFLAGS="-L$(shell brew --prefix openssl)/lib" pyenv install 3.4.3
	CFLAGS="-I$(shell brew --prefix openssl)/include" LDFLAGS="-L$(shell brew --prefix openssl)/lib" pyenv install 3.5.4
	CFLAGS="-I$(shell brew --prefix openssl)/include" LDFLAGS="-L$(shell brew --prefix openssl)/lib" pyenv install 3.6.3
	pyenv local 2.7.14 3.4.3 3.5.4 3.6.3
	pip install -U detox tox tox-pyenv pip setuptools

test3:
	-tox -e py36 $(test_extra_params)

test:
	detox

build:
	PYENV_VERSION=yset-36 python setup.py build
