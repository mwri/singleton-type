ifndef tests
tests="test"
endif


all: test lint coverage dist

venv: venv/bin/activate venv/lib/.deps

venv/bin/activate:
	python3 -m venv venv

.PHONY: deps
deps: venv/lib/.deps

venv/lib/.deps: venv/bin/activate singleton_type/pkg_meta.py
	touch venv/lib/.deps

.PHONY: dev_deps
dev_deps: venv/lib/.dev_deps

venv/lib/.dev_deps: venv/bin/activate singleton_type/pkg_meta.py
	. venv/bin/activate \
		&& pip install $$(python3 singleton_type/pkg_meta.py extras_require dev)
	touch venv/lib/.dev_deps

.PHONY: test
test: venv venv/lib/.dev_deps
	. venv/bin/activate \
		&& pytest \
		-m "$(mark)" \
		$(pytest_args) \
			$(tests)

.PHONY: coverage
coverage: venv venv/lib/.dev_deps
	. venv/bin/activate \
		&& coverage run \
			--branch \
			--source=singleton_type --omit=singleton_type/pkg_meta.py \
			-m pytest \
			-m "not soak" \
			$(pytest_args) \
			$(tests) \
		&& coverage report \
		&& coverage html \
		&& coverage xml

.PHONY: lint
lint: venv venv/lib/.dev_deps
	. venv/bin/activate \
		&& black --check \
			--line-length 120 \
			singleton_type test setup.py noxfile.py \
		&& isort --check \
			singleton_type test

.PHONY: mypy
mypy: venv venv/lib/.dev_deps
	. venv/bin/activate \
		&& mypy singleton_type

.PHONY: clean
clean:
	rm -rf ./venv ./*.egg-info ./build ./pip_dist ./htmlcov ./coverage.xml \
		$$(find singleton_type -name __pycache__) $$(find singleton_type -name '*.pyc') \
		$$(find test -name __pycache__) $$(find test -name '*.pyc')

.PHONY: dist
dist: venv
	. venv/bin/activate \
		&& pip install setuptools wheel \
		&& python3 setup.py sdist bdist_wheel
