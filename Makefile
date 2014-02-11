.PHONY: build windows osx debian clean install

all: build windows debian osx

build: clean
	python3.3 build/build.py build
	pyrcc4 -py3 commotion_client/assets/commotion_assets.qrc -o commotion_client/assets/commotion_assets_rc.py

test: clean build
	cp commotion_client/assets/commotion_assets_rc.py commotion_client/.

windows:
	@echo "windows compileing is not yet implemented"

osx:
	@echo "macintosh saddening is not yet implemented"

debian:
	@echo "debian packaging is not yet implemented"

clean:
	python3.3 build/build.py clean
	rm commotion_client/assets/commotion_assets_rc.py || true
	rm commotion_client/commotion_assets_rc.py || true
