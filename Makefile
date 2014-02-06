.PHONY: build windows osx debian clean install

all: build windows debian osx

build:
	python3.3 build/build.py build

windows:
	@echo "windows compileing is not yet implemented"

osx:
	@echo "macintosh saddening is not yet implemented"

debian:
	@echo "debian packaging is not yet implemented"

clean:
	python3.3 build/build.py clean
