.PHONY: build windows osx debian clean install tests

all: build

build: clean assets
	python3.3 build/scripts/build.py build
	python3.3 build/scripts/zip_extensions.py

assets:
	mkdir build/resources || true
	pyrcc4 -py3 commotion_client/assets/commotion_assets.qrc -o build/resources/commotion_assets_rc.py

windows:
	@echo "windows compileing is not yet implemented"

osx:
	@echo "macintosh saddening is not yet implemented"

linux: build
	python3.3 setup.py build

debian:
	@echo "debian packaging is not yet implemented"

test: tests
	@echo "test build complete"

tests: build
	mkdir tests/temp || true
	mkdir tests/mock/assets || true
	cp build/resources/commotion_assets_rc.py tests/mock/assets/. || true
	python3.3 tests/run_tests.py

clean:
	python3.3 build/scripts/build.py clean
	rm -fr build/resources/* || true
	rm -fr build/exe.* || true
	rm -fr tests/temp/* || true
