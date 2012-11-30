.PHONY: test
.PHONY: clean
.PHONY: install

test: 
	./run_tests

clean:
	./setup.py clean
	-find -name \*.pyc | xargs rm -fv
	-rm -fr build

install:
	./setup.py install --root=$(DESTDIR:=/) --prefix=/usr --install-layout=deb
