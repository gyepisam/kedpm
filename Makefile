.PHONY: test
.PHONY: clean
.PHONY: install

test: 
	./run_tests
	
clean:
	find -name \*.pyc | xargs rm -v
	./setup.py clean
	rm -r build
	
install:
	./setup.py install
