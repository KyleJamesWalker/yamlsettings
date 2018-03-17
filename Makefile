clean:
	@rm -rf build/ *.egg-info *.egg
	@pyenv uninstall -f yset-27 || True
	@pyenv uninstall -f yset-36 || True
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


env3:
	@pyenv virtualenv -f 3.6.3 yset-36 || True
	PYENV_VERSION=yset-36 pip install --upgrade pip setuptools pbr flake8 coverage
	PYENV_VERSION=yset-36 pip install -e .

tests3:
	PYENV_VERSION=yset-36 flake8
	PYENV_VERSION=yset-36 coverage run setup.py test
	PYENV_VERSION=yset-36 coverage report -m

tests:
	detox

build:
	PYENV_VERSION=yset-36 python setup.py build
