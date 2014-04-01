.PHONY: build windows osx debian clean install

all: build windows debian osx

extensions: build_tree
	python3.3 build/scripts/zip_extensions.py

build: clean extensions assets
	python3.3 build/scripts/build.py build

assets: build_tree
	pyrcc4 -py3 commotion_client/assets/commotion_assets.qrc -o build/resources/commotion_assets_rc.py

test: clean build
	@echo "test build complete"

windows:
	@echo "windows compileing is not yet implemented"

osx:
	@echo "macintosh saddening is not yet implemented"

linux: build
	python3.3 setup.py build

debian:
	@echo "debian packaging is not yet implemented"

build_tree:
	mkdir build/resources || true
	mkdir build/exe || true

clean: 
	python3.3 build/scripts/build.py clean
	rm -fr build/resources/*
	rm -fr build/exe.* || true

