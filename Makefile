.PHONY: test
.PHONY: clean
.PHONY: install

test: 
	./run_tests
	
clean:
	./setup.py clean
	rm -r build
	
install:
	./setup.py install
