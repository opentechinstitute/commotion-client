.PHONY: build windows osx debian clean install

all: build windows debian osx extensions

extensions:
	echo "write the extension config section.... seriously"
#	Need to copy all core & listed contrib extension data into commotion_client/data/extensions/.
#	cp commotion_client/extensions/core/<extension>/*.conf commotion_client/data/extensions/.

build: clean
	python3.3 build/build.py build
	pyrcc4 -py3 commotion_client/assets/commotion_assets.qrc -o commotion_client/assets/commotion_assets_rc.py

test: clean build
	@echo "test build complete"

windows:
	@echo "windows compileing is not yet implemented"

osx:
	@echo "macintosh saddening is not yet implemented"

linux: clean_linux build
	python3.3 setup.py build

clean_linux:
	rm -fr build/exe.linux-x86_64-3.3/ || true

debian:
	@echo "debian packaging is not yet implemented"

clean: clean_linux
	python3.3 build/build.py clean
	rm commotion_client/assets/commotion_assets_rc.py || true
	rm commotion_client/commotion_assets_rc.py || true
